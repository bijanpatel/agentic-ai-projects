import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    config["openai_api_key"] = os.getenv("OPENAI_API_KEY")
    config["model_name"] = os.getenv("MODEL_NAME", config["model"]["model_name"])
    return config