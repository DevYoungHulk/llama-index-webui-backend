import hashlib
import os
from configparser import ConfigParser
from llama_index.core import StorageContext
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from flask import current_app
import pymongo


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


def create_storage(base_dir) -> StorageContext:
    storage_context = StorageContext.from_defaults(persist_dir=base_dir)
    return storage_context

def create_mongo_index_store(uri, db_name, namespace) -> MongoDocumentStore:
    doc_store = MongoIndexStore.from_uri(
        uri, db_name=db_name, index_name=namespace+'.index')
    return doc_store

def create_mongo_vector_store(uri, db_name, namespace) -> MongoDBAtlasVectorSearch:
    mongodb_client = pymongo.MongoClient(uri)
    index_store = MongoDBAtlasVectorSearch(
        mongodb_client, db_name=db_name, index_name=namespace+'.vector')
    return index_store




def create_mongo_doc_store(uri, db_name, namespace) -> MongoDocumentStore:
    doc_store = MongoDocumentStore.from_uri(
        uri, db_name=db_name, index_name=namespace+'.doc')
    return doc_store


def create_neo4j_store(uri, username, password):
    graph_store = Neo4jGraphStore(
        url=uri, username=username, password=password,
        node_label="Node"
    )
    return graph_store
