import json
import os
import datetime
import glob
from src.services.logger import logger
from src.utils import load_config

class FileManager:
    def __init__(self, config_path="src/config/config.json"):
        self.config = load_config(config_path)
        self.log_directories = self.config["log-directories"]
        self.schema_file = self.config["schema-validation"]["default_schema"]

        # Initialize with defaults from config
        self.categories_file = self.config["default_categories_file"]
        self.contexts_file = self.config["default_contexts_file"]

    def set_categories_file(self, filename):
        """Set the categories file to a selected filename. Assumes file exists in src/resources."""
        self.categories_file = os.path.join("src", "resources", filename)

    def set_contexts_file(self, filename):
        """Set the contexts file to a selected filename. Assumes file exists in src/resources."""
        self.contexts_file = os.path.join("src", "resources", filename)

    def load_categories(self):
        with open(self.categories_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_contexts(self):
        with open(self.contexts_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_default_schema(self):
        with open(self.schema_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def write_to_log_file(self, category, content, detailed=False):
        directory = self.log_directories.get(category.lower(), "./logs/")
        os.makedirs(directory, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        extension = ".json" if detailed else ".csv"
        filename = f"{category.lower()}_{timestamp}{extension}"
        path = os.path.join(directory, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Exported {category} to {path}")

    def get_available_categories_files(self):
        """Return a list of available category JSON files found in src/resources."""
        files = glob.glob("src/resources/*_categories.json")
        return [os.path.basename(f) for f in files]

    def get_available_contexts_files(self):
        """Return a list of available context JSON files found in src/resources."""
        files = glob.glob("src/resources/*_contexts.json")
        return [os.path.basename(f) for f in files]
