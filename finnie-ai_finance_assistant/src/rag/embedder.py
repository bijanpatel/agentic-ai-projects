from langchain_openai import OpenAIEmbeddings
from src.core.config import load_config


def get_embeddings():
    config = load_config()
    return OpenAIEmbeddings(
        api_key=config["openai_api_key"]
    )