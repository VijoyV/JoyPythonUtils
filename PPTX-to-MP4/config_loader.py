import json
import os


def load_config(config_file="config-azure.json"):
    """Loads and parses the JSON configuration file."""
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file {config_file} not found.")

    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    config = load_config()
    print("Loaded configuration:")
    print(json.dumps(config, indent=4))
