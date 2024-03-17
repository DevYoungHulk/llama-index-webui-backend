from flask_login import LoginManager
from .models.types import User
from flask_jwt_extended import JWTManager
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings, ServiceContext, set_global_service_context
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
login_manager = LoginManager()
login_manager.login_view = 'login'
jwt_manager = JWTManager()


def config_extensions(app):
    login_manager.init_app(app)
    jwt_manager.init_app(app)


text_splitter = SentenceSplitter()
llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")
# llm = Ollama(temperature=0.1, model="mistral:7b", request_timeout=300.0)

embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-mpnet-base-v2", max_length=512
)
Settings.llm = llm
Settings.embed_model = embed_model
Settings.text_splitter = text_splitter

service_context = ServiceContext.from_defaults(
    llm=llm,
    embed_model=embed_model
)
set_global_service_context(service_context)
