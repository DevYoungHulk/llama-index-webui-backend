from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoTokenizer, AutoModelForCausalLM
from flask_login import LoginManager
from .models.types import User
from flask_jwt_extended import JWTManager
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings, ServiceContext, set_global_service_context
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core.node_parser import SentenceWindowNodeParser, SentenceSplitter

login_manager = LoginManager()
login_manager.login_view = 'login'
jwt_manager = JWTManager()


def config_extensions(app):
    login_manager.init_app(app)
    jwt_manager.init_app(app)
    # config_ai()


def config_ai():
    text_splitter = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=50,
    )
    llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")
    # llm = Ollama(temperature=0.1, model="mistral:7b", request_timeout=300.0)
    # model_name = 'Qwen/Qwen1.5-0.5B-Chat'
    # model_name = 'Qwen/Qwen1.5-7B-Chat'
    # tokenizer = AutoTokenizer.from_pretrained(
    #     model_name, torch_dtype="auto",    device_map="auto", mirror="tuna")
    # model = AutoModelForCausalLM.from_pretrained(model_name)
    # llm = HuggingFaceLLM(model=model, tokenizer=tokenizer)

    embed_model = HuggingFaceEmbedding(
        # model_name="sentence-transformers/all-mpnet-base-v2", max_length=512
        # model_name="aspire/acge_text_embedding", max_length=1024
        model_name="moka-ai/m3e-base", max_length=512
    )

    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )

    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.text_splitter = text_splitter
    Settings.node_parser = node_parser
    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model
    )
    set_global_service_context(service_context)
