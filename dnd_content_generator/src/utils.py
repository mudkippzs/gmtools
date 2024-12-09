import json

def load_config(self, path='src/config/config.json'):
    with open(path, "r") as f:
        return json.load(f)