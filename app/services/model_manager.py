
from app.models.types import *
from llama_index.core.llms import LLM
from llama_index.core.embeddings import BaseEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from transformers import AutoTokenizer, AutoModelForCausalLM


def get_embbedding_model(embed_model_config: ChatModelConfig) -> BaseEmbedding:
    if embed_model_config.model_type == ModelType.OPENAI:
        return OpenAIEmbedding(model=embed_model_config.model_name,
                               api_key=embed_model_config.openai_api_key)
    elif embed_model_config.model_type == ModelType.HUGGINGFACE:
        tokenizer = AutoTokenizer.from_pretrained(
            embed_model_config.model_name)
        model = AutoModelForCausalLM.from_pretrained(
            embed_model_config.model_name)
        return HuggingFaceEmbedding(model=model, tokenizer=tokenizer)
    elif embed_model_config.model_type == ModelType.OLLAMA:
        return OllamaEmbedding(model_name=embed_model_config.model_name,base_url=embed_model_config.ollama_url)


def get_llm_model(llm_model_config: ChatModelConfig) -> LLM:
    if llm_model_config.model_type == ModelType.OPENAI:
        return OpenAI(
            temperature=0.0,
            model_name=llm_model_config.model_name,
            api_key=llm_model_config.openai_api_key,
        )
    elif llm_model_config.model_type == ModelType.HUGGINGFACE:
        tokenizer = AutoTokenizer.from_pretrained(
            llm_model_config.model_name, torch_dtype="auto", device_map="auto", mirror="tuna")
        model = AutoModelForCausalLM.from_pretrained(
            llm_model_config.model_name)
        return HuggingFaceLLM(model=model, tokenizer=tokenizer)
    elif llm_model_config.model_type == ModelType.OLLAMA:
        return Ollama(temperature=0.1,
                      model=llm_model_config.model_name, request_timeout=300.0)
    else:
        raise Exception(
            f'model type {llm_model_config.model_type} not support')
