from llama_index.core import Settings
from mongoengine import QuerySet
from llama_index.core import download_loader, set_global_service_context, ServiceContext, load_index_from_storage
from llama_index.core.agent import ReActAgent
from llama_index.core.types import ChatMessage
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SummaryIndex, KnowledgeGraphIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.models.types import ChatHistory, MessageRole
from .mongo_storage import *
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
        tools = self.loadQueryEngineTool(user_id)
        logger.info('tools -> '+str(len(tools)))
        for t in tools:
            logger.info(t.metadata.description)
        agent = ReActAgent.from_tools(
            tools,
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
        return agent

    def loadQueryEngineTool(self, user_id):
        vetor_storage = get_vector_storage(user_id)
        summary_storage = get_summary_storage(user_id)
        knowledge_storage = get_knowledge_storage(user_id)
        try:
            vectorStoreIndex = load_index_from_storage(vetor_storage)
        except Exception as e:
            logger.error('loadQueryEngineTool load vectorStoreIndex error')
            logger.error(e)
            vectorStoreIndex = VectorStoreIndex.from_documents(
                documents=[], storage_context=vetor_storage, show_progress=True)
        try:
            summaryStoreIndex = load_index_from_storage(summary_storage)
        except Exception as e:
            logger.error('loadQueryEngineTool load summaryStoreIndex error')
            logger.error(e)
            summaryStoreIndex = SummaryIndex.from_documents(
                documents=[], storage_context=vetor_storage, show_progress=True)
        try:
            knowledge_index = load_index_from_storage(knowledge_storage)
            logger.info("---------knowledge_index--------")
            logger.info("knowledge_index count"+str(len(knowledge_index.ref_doc_info.items())))
            logger.info(knowledge_index.ref_doc_info.items())
        except Exception as e:
            logger.error('loadQueryEngineTool load knowledge_index error')
            logger.error(e)
            knowledge_index = KnowledgeGraphIndex.from_documents(
                documents=[], storage_context=knowledge_storage, show_progress=True)

        return [
            # QueryEngineTool(
            # query_engine=vectorStoreIndex.as_chat_engine(),
            # metadata=ToolMetadata(
            #     name="vecotr_index_tool",
            #     description='This tool is used to query all index of documents',
            # )),
            # QueryEngineTool(
            # query_engine=summaryStoreIndex.as_chat_engine(
            #     include_text=True,
            #     response_mode="tree_summarize",
            #     embedding_mode="embedding",
            #     similarity_top_k=5
            # ),
            # metadata=ToolMetadata(
            #     name="summary_tool",
            #     description='This tool is used to query all summary of documents',
            # )),
            QueryEngineTool(
                query_engine=knowledge_index.as_chat_engine(
                    include_text=True,
                    response_mode="refine",
                    embedding_mode="hybrid",
                    similarity_top_k=100
                ),
                metadata=ToolMetadata(
                    name="knowledge_tool",
                    description='This tool is used to query all knowledge of documents',
                )),
        ]


gloabl_chat_agent_instance = GloablChatAgent()


def get_gloabl_chat_agent_instance():
    return gloabl_chat_agent_instance
