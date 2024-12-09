#!/usr/bin/env bash

# Exit on error
set -e

# Variables
PROJECT_NAME="dnd_content_generator"
PYTHON_BIN="python3"
VENV_DIR=".venv"

echo "Setting up project directory for ${PROJECT_NAME}..."

# Create project root directory
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Create a virtual environment
echo "Creating virtual environment..."
$PYTHON_BIN -m venv $VENV_DIR

# Activate the environment
source $VENV_DIR/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install PySide6 or PyQt5 as desired
# Uncomment one of the lines below depending on your preference:
pip install PySide6

# pip install PyQt5

# Install additional dependencies you might need (e.g., openai, requests, etc.)
# Since GPT interaction and openai might still be needed:
pip install openai requests

# Create directories for the new project structure
echo "Creating directories..."
mkdir -p src
mkdir -p src/ui
mkdir -p src/controllers
mkdir -p src/models
mkdir -p src/services
mkdir -p src/resources
mkdir -p src/config
mkdir -p logs

# Create placeholder files
touch src/__init__.py
touch src/ui/__init__.py
touch src/controllers/__init__.py
touch src/models/__init__.py
touch src/services/__init__.py
touch src/resources/.keep
touch src/config/__init__.py

# Example config files
cat > src/config/config.json <<EOF
{
    "gpt-api": {
        "api-key": "YOUR_API_KEY_HERE"
    },
    "app-settings": {
        "max-tokens": 1000,
        "n-results": 1,
        "temperature": 0.27,
        "model": "gpt-4"
    },
    "log-directories": {
        "weapons": "./logs/weapons/",
        "npcs": "./logs/npcs/",
        "potions": "./logs/potions/",
        "armor": "./logs/armor/",
        "locations": "./logs/locations/"
    },
    "categories-file": "src/resources/categories.json",
    "contexts-file": "src/resources/contexts.json"
}
EOF

# Example empty categories and contexts JSON files
cat > src/resources/categories.json <<EOF
{
    "Items": ["Weapon", "Armor", "Potion"],
    "Characters": ["NPC", "Villain", "Ally"]
}
EOF

cat > src/resources/contexts.json <<EOF
{
    "General Contexts": ["Dark", "Magic", "Mundane"],
    "Thematic Contexts": ["Ancient", "Evil", "Holy"]
}
EOF

# Create a main entry point
cat > src/main.py <<EOF
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
EOF

# Create a basic MainWindow UI file
cat > src/ui/main_window.py <<EOF
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("D&D Content Generator")
        central_widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Welcome to the D&D Content Generator!")
        layout.addWidget(label)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
EOF

# Create placeholders for controller, services, models
cat > src/controllers/app_controller.py <<EOF
class AppController:
    def __init__(self, config):
        self.config = config
        # Initialize services, models, and load data
        # e.g., self.file_manager = FileManager(config)
        # self.gpt = GPTInteraction(config)
        # self.data_controller = DataController(...)
EOF

cat > src/services/gpt_service.py <<EOF
class GPTService:
    def __init__(self, api_key, model="gpt-4", temperature=0.27, max_tokens=1000):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def send_prompt(self, prompt):
        # Implement GPT call here
        pass
EOF

cat > src/services/file_manager.py <<EOF
import json
import os

class FileManager:
    def __init__(self, config):
        self.config = config

    def load_categories(self):
        with open(self.config["categories-file"], "r") as f:
            return json.load(f)

    def load_contexts(self):
        with open(self.config["contexts-file"], "r") as f:
            return json.load(f)

    def write_to_log_file(self, category, content):
        # Implement logging logic here
        pass
EOF

cat > src/models/content_parser.py <<EOF
class ContentParser:
    def parse_json(self, json_response):
        # Implement parsing logic
        pass
EOF

echo "Project setup complete!"

echo "To start working:"
echo "1) cd ${PROJECT_NAME}"
echo "2) source ${VENV_DIR}/bin/activate"
echo "3) python src/main.py"
