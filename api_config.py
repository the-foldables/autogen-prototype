import os

from llama_index.llms.litellm import LiteLLM
from llama_index.embeddings.litellm import LiteLLMEmbedding

def get_api_config(cborg):
    api_key = os.environ["API_KEY"] # do not insert API key in plaintext!

    if cborg:
        base_url = "https://api.cborg.lbl.gov"
        model = "openai/lbl/cborg-chat:latest"
        model_gpt = "openai/gpt-4o-mini"
        embedding_model = "openai/lbl/nomic-embed-text"
    else:
        base_url = "https://api.openai.com/v1"
        model = "gpt-4o-mini"
        model_gpt = model
        embedding_model = "text-embedding-3-small"

    config_list = [
        {
            "model": model, "api_key": api_key, 
            "base_url": base_url,
            "api_rate_limit":60.0, "price" : [0, 0]
        },
        {
            "model": model_gpt, "api_key": api_key, 
            "base_url": base_url,
            "api_rate_limit":60.0, "price" : [0, 0]
        }
    ]

    config_list_gpt = [
        {
            "model": model_gpt, "api_key": api_key, 
            "base_url": base_url,
            "api_rate_limit":60.0, "price" : [0, 0]
        }
    ]

    llm_config = {
        "temperature": 0,
        "config_list": config_list,
    }

    llm_config_gpt = {
        "temperature": 0,
        "config_list": config_list_gpt,
    }

    llm = LiteLLM(
        model=model,
        api_key=api_key, 
        api_base=base_url,
    )

    embedding = LiteLLMEmbedding(
        model_name=embedding_model,
        api_key=api_key,
        api_base=base_url,
    )

    return llm_config, llm_config_gpt, llm, embedding
