import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from config import config

# OpenAI-compatible endpoint; defaults to Blablador, set OPENAI_API_BASE=https://api.openai.com/v1 for OpenAI
os.environ["OPENAI_API_BASE"] = config.get("OPENAI_API_BASE", "https://api.blablador.fz-juelich.de/v1")

def get_chat_llm() -> ChatOpenAI:
    """
    Creates a ChatOpenAI LLM using the provided OpenAI API key and model.

    Returns:
        ChatOpenAI: The ChatOpenAI LLM
    """
    return ChatOpenAI(
        openai_api_key=config["OPENAI_API_KEY"],
        model_name=config["OPENAI_MODEL"],
        streaming=True,
        temperature=0,
    )


def create_embeddings() -> OpenAIEmbeddings:
    """
    Creates an OpenAIEmbeddings model using the provided OpenAI API key.

    Returns:
        OpenAIEmbeddings: The OpenAIEmbeddings model
    """
    return OpenAIEmbeddings(openai_api_key=config["OPENAI_API_KEY"])


# create the llm, and the embeddings
# may now be imported as
# from llm import llm, embeddings
llm = get_chat_llm()
embeddings = create_embeddings()
