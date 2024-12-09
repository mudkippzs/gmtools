import asyncio
import json
import os
import random
import time
from jsonschema import Draft7Validator, ValidationError
from functools import lru_cache
from src.models.content_parser import ContentParser
from src.services.file_manager import FileManager
from src.services.gpt_service import GPTService
from src.services.logger import logger
from src.services.prompt_templates import SCHEMA_PROMPT
from src.utils import load_config


class SchemaService:
    def __init__(self):
        self.config = load_config("src/config/config.json")
        self.gpt_service = GPTService()
        self.parser = ContentParser()
        self.retry_count = self.config["app-settings"].get("llm_retry_count", 3)
        self.retry_delay = self.config["app-settings"].get("llm_retry_delay", 2)
        self.schema_enabled = self.config["schema-validation"].get("enable", False)
        self.schema_prompt_template = FileManager().load_default_schema()
        self.default_schema_path = self.config["schema-validation"].get("default_schema", "")
        self._schema_cache = {}

    async def get_schema(self, content_type, context_str):
        if not self.schema_enabled:
            return self._load_default_schema()

        key = (content_type.lower().strip(), context_str.lower().strip())
        if key in self._schema_cache:
            return self._schema_cache[key]

        schema = await self._fetch_schema_from_llm(content_type, context_str)

        if not schema:
            logger.warning("Falling back to default schema due to LLM failures.")
            schema = self._load_default_schema()

        # Validate that schema is valid JSON schema and meets our ui_order requirements
        if not self._is_valid_schema(schema):
            logger.warning("Fetched schema is not valid or does not meet ui_order requirements. Falling back to default schema.")
            schema = await self._load_default_schema()

        self._schema_cache[key] = schema
        return schema

    def validate_data(self, schema, data):
        Draft7Validator.check_schema(schema)
        validator = Draft7Validator(schema)
        validator.validate(data)

    async def _fetch_schema_from_llm(self, content_type, context_str):
        system = self.config.get("default_system", "D&D 3.5e")
        setting = self.config.get("default_setting", "a generic fantasy setting")

        prompt = SCHEMA_PROMPT.format(
            system=system,
            setting=setting,
            content_type=content_type,
            context=context_str,
            schema=self.schema_prompt_template
        )
        for attempt in range(self.retry_count):
            try:
                temp = random.uniform(0.1, 0.7)
                response = await self.gpt_service.send_prompt_async(prompt, temp)
                if response:
                    schema = self.parser.parse_json(response)
                    if schema and self._is_valid_schema(schema):
                        return schema
                    else:
                        logger.error(f"Received schema is invalid or doesn't meet requirements. Attempt {attempt+1}/{self.retry_count}")
                else:
                    logger.error(f"No response from LLM for schema generation. Attempt {attempt+1}/{self.retry_count}")
            except Exception as e:
                logger.error(f"Error fetching schema from LLM: {e}. Attempt {attempt+1}/{self.retry_count}")
            await asyncio.sleep(self.retry_delay)
        return None

    def _is_valid_schema(self, schema):
        # Basic checks:
        # 1. It's a valid draft-07 schema
        # 2. "name" and "description" are required, have ui_order 1 and 2 respectively.
        # 3. additionalProperties = false
        # 4. Each property has ui_order and properties sorted by ui_order.
        try:
            Draft7Validator.check_schema(schema)
        except Exception as e:
            logger.error(f"Invalid schema format: {e}")
            return False

        if schema.get("additionalProperties", True) is not False:
            logger.error("Schema must have additionalProperties=false.")
            return False

        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if "name" not in properties or "description" not in properties:
            logger.error("'name' and 'description' must be defined in the schema.")
            return False
        if "name" not in required or "description" not in required:
            logger.error("'name' and 'description' must be required properties.")
            return False

        # Check ui_order fields
        # Collect ui_orders to ensure uniqueness and correctness
        ui_orders = []
        for prop_name, prop_def in properties.items():
            if "ui_order" not in prop_def:
                logger.error(f"Property '{prop_name}' missing ui_order.")
                return False
            ui = prop_def["ui_order"]
            if not isinstance(ui, int):
                logger.error(f"Property '{prop_name}' ui_order must be an integer.")
                return False
            ui_orders.append((ui, prop_name))

        # Check that name and description are ui_order=1 and ui_order=2
        ui_dict = {p: d["ui_order"] for p, d in properties.items()}
        if ui_dict.get("name", None) != 1 or ui_dict.get("description", None) != 2:
            logger.error("name must have ui_order=1 and description ui_order=2.")
            return False

        # Check ui_orders are unique and sorted without gaps
        ui_orders_sorted = sorted(ui_orders, key=lambda x: x[0])
        for i, (u, p) in enumerate(ui_orders_sorted, start=1):
            if u != i:
                logger.error(f"ui_order must form a continuous sequence starting at 1. Found a gap at '{p}' with ui_order={u}.")
                return False

        return True

    def _load_default_schema(self):
        if not os.path.exists(self.default_schema_path):
            logger.error(f"Default schema file not found at {self.default_schema_path}. Using minimal fallback schema.")
            return {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "name": {"type": "string", "ui_order": 1},
                    "description": {"type": "string", "ui_order": 2}
                },
                "required": ["name", "description"],
                "additionalProperties": false
            }
        with open(self.default_schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        if not self._is_valid_schema(schema):
            logger.error("Default schema is invalid. Using minimal fallback schema.")
            return {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "name": {"type": "string", "ui_order": 1},
                    "description": {"type": "string", "ui_order": 2}
                },
                "required": ["name", "description"],
                "additionalProperties": False
            }
        return schema
