import asyncio
import json
import random
from jsonschema import ValidationError
from src.models.content_parser import ContentParser
from src.services.schema_service import SchemaService
from src.services.logger import logger
from src.services.prompt_templates import BASE_PROMPT, FULL_STATBLOCK_PROMPT

class DataController:
    def __init__(self, gpt_service, app_controller):
        self.gpt_service = gpt_service
        self.parser = ContentParser()
        self.schema_service = SchemaService()
        self.app_controller = app_controller  # Reference to get campaign prompt and breadcrumb

        config = self.schema_service.config
        self.retry_count = config["app-settings"].get("llm_retry_count", 3)
        self.retry_delay = config["app-settings"].get("llm_retry_delay", 2)

    def generate_content(self, content_type, context_str, n_results=3):
        return asyncio.run(self.generate_content_async(content_type, context_str, n_results))

    async def generate_content_async(self, content_type, context_str, n_results=3):
        schema = await self.schema_service.get_schema(content_type, context_str)
        if not schema:
            logger.error("No valid schema available. Cannot generate content.")
            return []

        breadcrumb = getattr(self.app_controller.state, 'breadcrumb', '')
        breadcrumb_str = f"Selected category/type hierarchy: {breadcrumb}" if breadcrumb else ""
        campaign_text = self.app_controller.state.campaign_prompt.strip()
        system = self.app_controller.state.system.strip()
        setting = self.app_controller.state.setting.strip()

        base_prompt = BASE_PROMPT.format(
            system=system if system else "D&D 3.5e",
            setting=setting if setting else "a generic fantasy setting",
            content_type=content_type,
            context=context_str,
            schema=json.dumps(schema)
        )

        if breadcrumb_str:
            base_prompt += "\n\n" + breadcrumb_str
        if campaign_text:
            base_prompt += "\n\n" + campaign_text

        tasks = [self._attempt_content_generation_async(base_prompt, schema) for _ in range(n_results)]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]


    def get_full_statblock(self, content_type, context_str, base_content):
        return asyncio.run(self.get_full_statblock_async(content_type, context_str, base_content))

    async def get_full_statblock_async(self, content_type, context_str, base_content):
        schema = await self.schema_service.get_schema(content_type, context_str)
        if not schema:
            logger.error("No valid schema available for statblock generation.")
            return None

        breadcrumb = getattr(self.app_controller.state, 'breadcrumb', '')
        breadcrumb_str = f"Selected category/type hierarchy: {breadcrumb}" if breadcrumb else ""
        campaign_text = self.app_controller.state.campaign_prompt.strip()
        system = self.app_controller.state.system.strip()
        setting = self.app_controller.state.setting.strip()

        statblock_prompt = FULL_STATBLOCK_PROMPT.format(
            system=system if system else "D&D 3.5e",
            setting=setting if setting else "a generic fantasy setting",
            content_type=content_type,
            context=context_str,
            statblock_stats=base_content
        )

        # Incorporate breadcrumb if available
        if breadcrumb_str:
            statblock_prompt += "\n\n" + breadcrumb_str

        # Append campaign-specific prompt here as well
        campaign_text = self.app_controller.state.campaign_prompt.strip()
        if campaign_text:
            statblock_prompt += "\n\n" + campaign_text

        error_messages = []
        for attempt in range(self.retry_count):
            prompt = statblock_prompt
            if error_messages:
                prompt += "\n\n# Errors so far:\n" + "\n".join(error_messages)

            response = await self.gpt_service.send_prompt_async(prompt)
            if response:
                data = self.parser.parse_json(response)
                if data:
                    try:
                        self.schema_service.validate_data(schema, data)
                        normalized = self._normalize_data(data, schema)
                        return normalized
                    except ValidationError as ve:
                        logger.error(f"Statblock validation failed (attempt {attempt+1}): {ve.message}")
                        error_messages.append(f"Validation error: {ve.message}")
                else:
                    logger.error(f"Failed to parse JSON for statblock (attempt {attempt+1}).")
                    error_messages.append("Failed to parse JSON.")
            else:
                logger.error(f"No response from LLM for statblock (attempt {attempt+1}).")
                error_messages.append("No response from LLM.")

            await asyncio.sleep(self.retry_delay)

        logger.error("Failed to generate a valid statblock after all retries.")
        return None

    async def _attempt_content_generation_async(self, base_prompt, schema):
        error_messages = []
        for attempt in range(self.retry_count):
            prompt = base_prompt
            if error_messages:
                prompt += "\n\n# Errors so far:\n" + "\n".join(error_messages)

            temp = random.uniform(0.45, 0.85)

            response = await self.gpt_service.send_prompt_async(prompt, temp)
            if not response:
                logger.error(f"No response from LLM (attempt {attempt+1}/{self.retry_count}).")
                error_messages.append("No response from LLM.")
                await asyncio.sleep(self.retry_delay)
                continue

            data = self.parser.parse_json(response)
            if not data:
                logger.error(f"Failed to parse JSON (attempt {attempt+1}/{self.retry_count}).")
                error_messages.append("Failed to parse JSON.")
                await asyncio.sleep(self.retry_delay)
                continue

            try:
                self.schema_service.validate_data(schema, data)
                normalized = self._normalize_data(data, schema)
                return normalized
            except ValidationError as ve:
                logger.error(f"Validation failed (attempt {attempt+1}/{self.retry_count}): {ve.message}")
                error_messages.append(f"Validation error: {ve.message}")
                await asyncio.sleep(self.retry_delay)

        return None

    def _normalize_data(self, data, schema):
        properties = schema.get("properties", {})
        ordered_props = sorted(properties.items(), key=lambda x: x[1]["ui_order"])

        normalized_list = []
        for prop_name, prop_def in ordered_props:
            val = data.get(prop_name, "")
            val_str = self._to_plaintext_string(val)
            display_key = prop_name.replace("_", " ").title()
            normalized_list.append((display_key, val_str))

        normalized = {k: v for k, v in normalized_list}

        # Ensure Name and Description are first
        if "Name" in normalized and "Description" in normalized:
            name_val = normalized.pop("Name")
            desc_val = normalized.pop("Description")
            normalized = {"Name": name_val, "Description": desc_val, **normalized}

        return normalized

    def _to_plaintext_string(self, val):
        if isinstance(val, dict):
            parts = [f"{k.title()}: {self._to_plaintext_string(v)}" for k, v in val.items()]
            return "; ".join(parts)
        elif isinstance(val, list):
            return ", ".join([self._to_plaintext_string(item) for item in val])
        else:
            return str(val)
