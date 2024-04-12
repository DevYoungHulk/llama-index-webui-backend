import pymongo
from llama_index.core import StorageContext, load_index_from_storage, load_graph_from_storage, load_indices_from_storage, get_response_synthesizer
from llama_index.core.callbacks import CallbackManager
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.indices.base import BaseIndex
from flask import current_app
from typing import List
from ..models.types import *
import logging
logger = logging.getLogger('root')
import traceback

def get_vector_storage(namespace) -> StorageContext:
    db_name = current_app.config['MONGO_DB_NAME']
    uri = current_app.config['MONGO_URI']
    assert uri is not None, 'no db uri specified!'
    assert db_name is not None, 'no db name specified!'

    # mongodb doc store and document store
    doc_store = MongoDocumentStore.from_uri(
        uri=uri, db_name=db_name, namespace=namespace+'.doc')
    index_store = MongoIndexStore.from_uri(
        uri=uri, db_name=db_name, namespace=namespace+'.index')

    storage_context = StorageContext.from_defaults(
        # docstore=doc_store,
        index_store=index_store,
    )
    return storage_context


# os.environ["NEBULA_USER"] = "root"
# os.environ["NEBULA_PASSWORD"] = "nebula"  # default is "nebula"
# os.environ[
#     "NEBULA_ADDRESS"
# ] = "127.0.0.1:9669"  # assumed we have NebulaGraph installed locally


def get_knowledge_storage(namespace) -> StorageContext:
    db_name = 'llama-index-dev'
    uri = current_app.config['MONGO_URI']
    assert uri is not None, 'no db uri specified!'
    assert db_name is not None, 'no db name specified!'
    index_store = MongoIndexStore.from_uri(
        uri=uri, db_name=db_name, namespace=namespace+'.knowledge')
    doc_store = MongoDocumentStore.from_uri(
        uri=uri, db_name=db_name, namespace=namespace+'.knowledge_doc')
    graph_store = Neo4jGraphStore(
        url="bolt://127.0.0.1:7687", username="neo4j", password="password",
        node_label="Node"
    )

    # space_name = "llamaindex"
    # edge_types, rel_prop_names = ["relationship"], [
    #     "relationship"
    # ]  # default, could be omit if create from an empty kg
    # tags = ['entity']  # default, could be omit if create from an empty kg

    # graph_store = NebulaGraphStore(
    #     space_name=space_name,
    #     edge_types=edge_types,
    #     rel_prop_names=rel_prop_names,
    #     tags=tags,
    # )
    storage_context = StorageContext.from_defaults(
        graph_store=graph_store,
        docstore=doc_store,
        index_store=index_store
    )
    return storage_context


def create_storage(group_id) -> StorageContext:
    storage_context = StorageContext.from_defaults(
        persist_dir=persistDir(group_id))
    return storage_context


def create_mongo_index_store(uri, db_name, namespace) -> MongoDocumentStore:
    doc_store = MongoIndexStore.from_uri(
        uri, db_name=db_name, namespace=namespace+'.index')
    return doc_store


def create_mongo_vector_store(uri, db_name, namespace) -> MongoDBAtlasVectorSearch:
    mongodb_client = pymongo.MongoClient(uri)
    index_store = MongoDBAtlasVectorSearch(
        mongodb_client, db_name=db_name, collection_name=namespace+'.vector', index_name=namespace)
    return index_store


def create_mongo_doc_store(uri, db_name, namespace) -> MongoDocumentStore:
    doc_store = MongoDocumentStore.from_uri(
        uri, db_name=db_name, namespace=namespace+'.doc')
    return doc_store


def create_neo4j_store(uri, username, password):
    graph_store = Neo4jGraphStore(
        url=uri, username=username, password=password,
        node_label="Node"
    )
    return graph_store


def config_storages(chat_config: ChatConfig):
    storages = []
    for index_config in chat_config.store_configs:
        storage = config_storage(chat_config, index_config)
        storages.append(storage)
    return storages


def persistDir(group_id: str):
    base_dir = './storage/' + group_id
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return base_dir


def config_storage(chat_config: ChatConfig, index_config: IndexConfig):
    base_index_s_config: IndexConfig = chat_config.index_store_configs
    if base_index_s_config.storage_type == IndexStorageType.LOCAL:
        local_persist_dir = persistDir(chat_config.group_id)
        try:
            storage = StorageContext.from_defaults(
                persist_dir=local_persist_dir)
        except Exception as e:
            logger.error(e)
            logger.info('create local storage for index')
            storage = StorageContext.from_defaults()
            storage.persist(persist_dir=local_persist_dir)
            storage = StorageContext.from_defaults(
                persist_dir=local_persist_dir)
        logger.info('use local storage for index')
    elif base_index_s_config.storage_type == IndexStorageType.MONGO:
        index_store = create_mongo_index_store(
            index_config.uri,
            index_config.database,
            chat_config.group_id)
        storage = StorageContext.from_defaults(index_store=index_store)

    if index_config.config_type == IndexType.VECTOR:
        if index_config.storage_type == IndexStorageType.MONGO:
            vector_store = create_mongo_vector_store(
                index_config.uri,
                index_config.database,
                chat_config.group_id)
            storage.vector_store = vector_store
    elif index_config.config_type == IndexType.SUMMARY:
        if index_config.storage_type == IndexStorageType.MONGO:
            doc_store = create_mongo_doc_store(
                index_config.uri,
                index_config.database,
                chat_config.group_id)
            storage.docstore = doc_store
    elif index_config.config_type == IndexType.KNOWLEDGE_GRAPH:
        if index_config.storage_type == IndexStorageType.NEO4j:
            graph_store = create_neo4j_store(index_config.uri,
                                             index_config.username,
                                             index_config.password)
            storage.graph_store = graph_store
    return storage


def query_engine_tools(chat_config: ChatConfig):
    tools = []
    for index_config in chat_config.store_configs:
        storage = config_storage(chat_config, index_config)
        try:
            index: BaseIndex = load_index_from_storage(storage)
            response_synthesizer = get_response_synthesizer()
            node_postprocessor = SimilarityPostprocessor(
                        similarity_cutoff=0.5)
            node_postprocessor.callback_manager = CallbackManager()
            tool = QueryEngineTool(
                query_engine=RetrieverQueryEngine(
                    retriever=index.as_retriever(
                        similarity_top_k=index_config.similarity_top_k,
                    ),
                    response_synthesizer=response_synthesizer,
                    node_postprocessors= [node_postprocessor]
                ),
                metadata=ToolMetadata(
                    name='tool_'+index_config.config_type.value,
                    description=(
                        index_config.description
                    ),
                ),
            )
            tools.append(tool)
        except Exception as e:
            traceback_text = traceback.format_exc()
            logger.info('load index from storage error')
            logger.error(traceback_text)
            logger.info(e)
    return tools
