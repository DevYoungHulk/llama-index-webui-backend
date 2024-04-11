from llama_index.core import Settings
from mongoengine import QuerySet
from llama_index.core import download_loader, set_global_service_context, ServiceContext, load_index_from_storage, load_graph_from_storage, load_indices_from_storage
from llama_index.core.agent import ReActAgent
from llama_index.core.types import ChatMessage
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.llms import LLM
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import VectorStoreIndex, SummaryIndex, KnowledgeGraphIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.models.types import *
from .storage_manager import *
from app.services.model_manager import *
import traceback
from ..models.types import BaseFile
from llama_index.core.indices.base import BaseIndex
from llama_index.core.retrievers import BaseRetriever
from .custom_retrivers import build_query_engine
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging
logger = logging.getLogger('root')


class GloablChatAgent:
    global_agents = {}

    # model = "mistral:7b"  # mistral llama2
    # llm = Ollama(temperature=0.1, model=model, request_timeout=3000.0)
    # llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")

    # def __init__(self) -> None:
    # node_parser = SentenceSplitter(chunk_size=512)
    # embed_model = OllamaEmbedding(model_name=self.model)
    # service_context = ServiceContext.from_defaults(
    #     llm=Settings.llm,
    #     embed_model=Settings.embed_model
    # )
    # set_global_service_context(service_context)

    def refreshAgent(self, user_id):
        return self.getAgent(user_id, True)

    def getAgent(self, user_id, refresh=False):
        if user_id in self.global_agents and not refresh:
            return self.global_agents[user_id]
        histories: QuerySet[ChatHistory] = ChatHistory.objects(
            user_id=user_id).order_by('date')
        chat_history = []
        for h in histories:
            chat_history.append(h.toChatMessage())
        # tools = self.loadQueryEngineTool(user_id)
        # logger.info('tools -> '+str(len(tools)))
        # for t in tools:
        #     logger.info(t.metadata.description)
        query_engine = self.loadQueryEngineTool(user_id)

        qt = QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(
            name="knowledge_tool",
            description='This tool is used to query all knowledge of documents',
        ))
        agent = ReActAgent.from_tools(
            [qt],
            llm=Settings.llm,
            verbose=True,
            chat_history=chat_history,
            # callback_manager=callback_manager,
            system_prompt='''
            You are an in-house consultant at Lenovo.
            You can help users answer questions they encounter while developing software.
            To answer a question you need to query against the standardized documentation in knowledge_tool and then answer the user.
            Don't answer if you can't find documents from knowledge_tool.
            ''',
        )
        self.global_agents[user_id] = agent
        # self.global_agents[user_id] = query_engine
        return agent

    def loadQueryEngineTool(self, user_id):
        vetor_storage = get_vector_storage(user_id)
        knowledge_storage = get_knowledge_storage(user_id)
        files = BaseFile.objects(user_id=user_id)
        node_ids = []
        for f in files:
            if f.indexed:
                node_ids.extend(f.ref_doc_ids)

        try:
            vectorStoreIndex = load_index_from_storage(
                storage_context=vetor_storage)
        except Exception as e:
            logger.error('loadQueryEngineTool load vectorStoreIndex error')
            logger.error(e)
            vectorStoreIndex = VectorStoreIndex.from_documents(
                documents=[], storage_context=vetor_storage, show_progress=True)
        try:
            # space_name = "llamaindex"
            # edge_types, rel_prop_names = ["relationship"], [
            #     "relationship"
            # ]  # default, could be omit if create from an empty kg
            # # default, could be omit if create from an empty kg
            # tags = ['entity']
            knowledge_index = load_index_from_storage(
                storage_context=knowledge_storage,
                max_triplets_per_chunk=10,
                # space_name=space_name,
                # edge_types=edge_types,
                # rel_prop_names=rel_prop_names,
                # tags=tags,
                verbose=True)
            logger.info("---------knowledge_index--------")
            # for k in knowledge_index:
            #     logger.info(type(k))
            #     logger.info(len(k.ref_doc_info.items()))
            #     logger.info(k.ref_doc_info.items())

        except Exception as e:
            logger.error('loadQueryEngineTool load knowledge_index error')
            logger.error(e)
            traceback.format_exc()
            knowledge_index = KnowledgeGraphIndex.from_documents(
                documents=[], storage_context=knowledge_storage, show_progress=True)
        return build_query_engine(vectorStoreIndex, knowledge_index)


gloabl_chat_agent_instance = GloablChatAgent()


def get_gloabl_chat_agent_instance():
    return gloabl_chat_agent_instance


def create_agent(chat_config: ChatConfig):
    tools = query_engine_tools(chat_config)
    logger.info('tools -> '+str(len(tools)))
    llm_model_config: ChatModelConfig = chat_config.chat_model
    llm: LLM = get_llm_model(llm_model_config)
    if llm_model_config.model_type == ModelType.OPENAI:
        llm = OpenAI(
            temperature=0.0,
            model_name=llm_model_config.model_name,
            api_key=llm_model_config.openai_api_key,
        )
    elif llm_model_config.model_type == ModelType.HUGGINGFACE:
        tokenizer = AutoTokenizer.from_pretrained(
            llm_model_config.model_name, torch_dtype="auto", device_map="auto", mirror="tuna")
        model = AutoModelForCausalLM.from_pretrained(
            llm_model_config.model_name)
        llm = HuggingFaceLLM(model=model, tokenizer=tokenizer)
    elif llm_model_config.model_type == ModelType.OLLAMA:
        llm = Ollama(temperature=0.1,
                     model=llm_model_config.model_name, request_timeout=300.0)
    else:
        raise Exception(f'model type {llm_model_config.model_type} not support')
    chatAgent = ReActAgent.from_tools(
        tools=tools,
        llm=llm,
        verbose=True,
        system_prompt=chat_config.system_prompt,

    )

    return chatAgent
