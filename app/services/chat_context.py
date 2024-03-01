from llama_index.core import download_loader, set_global_service_context, ServiceContext, load_index_from_storage
from llama_index.core.agent import ReActAgent
from llama_index.core.types import ChatMessage
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SummaryIndex, DocumentSummaryIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from .mongo_storage import get_vector_storage, get_summary_storage
from ..db import db
import pymongo
import logging
logger = logging.getLogger('root')

class GloablChatAgent:
    global_agents = {}

    model = "mistral:7b"  # mistral llama2
    # llm = Ollama(temperature=0.1, model=model, request_timeout=300.0)
    llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")

    def __init__(self) -> None:
        node_parser = SentenceSplitter(chunk_size=512)
        # embed_model = OllamaEmbedding(model_name=self.model)
        service_context = ServiceContext.from_defaults(
            llm=self.llm,
            # embed_model=embed_model
        )
        set_global_service_context(service_context)

    def refreshAgent(self, user_id):
        return self.getAgent(user_id, True)

    def getAgent(self, user_id, refresh=False):
        if user_id in self.global_agents and not refresh:
            return self.global_agents[user_id]

        histories = db.chat_history.find({'user_id': user_id}).sort(
            [('date', pymongo.ASCENDING)])
        chat_history = []
        for h in histories:
            chat_history.append(ChatMessage(
                role=h['role'], content=h['content']))
        tools = self.loadQueryEngineTool(user_id)
        logger.info('tools -> '+str(len(tools)))
        for t in tools:
            logger.info(t.metadata.description)
        agent = ReActAgent.from_tools(
            tools,
            llm=self.llm,
            verbose=True,
            chat_history=chat_history,
            # callback_manager=callback_manager,
            system_prompt='''
            You can help users answer questions based on their private document index.
            You are allowed to fetch the document via vecotr_index_tool and summary_tool.
            ''',
        )
        self.global_agents[user_id] = agent
        return agent

    def loadQueryEngineTool(self, user_id):
        vetor_storage = get_vector_storage(user_id)
        summary_storage = get_summary_storage(user_id)
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
        return [QueryEngineTool(
            query_engine=vectorStoreIndex.as_query_engine(),
            metadata=ToolMetadata(
                name="vecotr_index_tool",
                description='This tool is used to query all index of documents',
            )),
            QueryEngineTool(
            query_engine=summaryStoreIndex.as_query_engine(),
            metadata=ToolMetadata(
                name="summary_tool",
                description='This tool is used to query all summary of documents',
            )),
        ]


gloabl_chat_agent_instance = GloablChatAgent()


def get_gloabl_chat_agent_instance():
    return gloabl_chat_agent_instance
