from flask_login import LoginManager
from .models.types import User
from flask_jwt_extended import JWTManager
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
login_manager = LoginManager()
login_manager.login_view = 'login'
jwt_manager = JWTManager()


def config_extensions(app):
    login_manager.init_app(app)
    jwt_manager.init_app(app)
    # class FlaskTask(Task):
    #     def __call__(self, *args: object, **kwargs: object) -> object:
    #         with app.app_context():
    #             return self.run(*args, **kwargs)
    # celery = Celery('tasks', broker='redis://127.0.0.1:6379/0',
    #                 backend='redis://127.0.0.1:6379/1', task_cls=FlaskTask)
    # celery.set_default()
    # app.extensions['celery'] = celery
    # celery.config_from_object(app.config)


text_splitter = SentenceSplitter()
# llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")
llm = Ollama(temperature=0.1, model="mistral:7b", request_timeout=300.0)

embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-mpnet-base-v2", max_length=512
)
Settings.llm = llm
Settings.embed_model = embed_model
Settings.text_splitter = text_splitter
