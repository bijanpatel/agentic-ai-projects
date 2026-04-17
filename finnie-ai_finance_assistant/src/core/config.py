import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    config["openai_api_key"] = os.getenv("OPENAI_API_KEY", "").strip()
    config["tavily_api_key"] = os.getenv("TAVILY_API_KEY", "").strip()
    config["model_name"] = os.getenv("MODEL_NAME", config["model"]["model_name"]).strip()

    return config