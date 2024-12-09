import json
import re
from src.services.logger import logger

class ContentParser:
    def parse_json(self, raw_text):
        # Attempt to clean the input from Markdown code fences and other extraneous formatting.
        cleaned = self._strip_code_fences(raw_text)

        # Attempt direct parsing
        data = self._try_parse_json(cleaned)
        if data is not None:
            return data

        # If direct parsing fails, try extracting a likely JSON object
        extracted = self._extract_json_object(cleaned)
        if extracted:
            data = self._try_parse_json(extracted)
            if data is not None:
                return data

        # If still no success, log and return None
        logger.error(f"Failed to parse JSON after extraction attempts.\nOriginal Data:\n{raw_text}")
        return None

    def _strip_code_fences(self, text):
        # Remove ```json ... ``` and ``` ... ```
        pattern = r"```(?:json)?\s*(.*?)\s*```"
        cleaned = re.sub(pattern, r"\1", text, flags=re.DOTALL|re.IGNORECASE)
        return cleaned.strip()

    def _try_parse_json(self, text):
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.debug(f"JSON decode attempt failed: {e}")
            return None

    def _extract_json_object(self, text):
        # Attempt to find the first balanced { ... } section
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and start < end:
            candidate = text[start:end+1].strip()
            return candidate
        return None
