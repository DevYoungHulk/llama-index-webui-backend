import hashlib
from configparser import ConfigParser
from llama_index.core import StorageContext
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.graph_stores.neo4j import Neo4jGraphStore


def get_vector_storage(namespace) -> StorageContext:
    db_name = 'llama-index-dev'
    uri = 'mongodb://root:example@127.0.0.1:27017/llama-index-dev?authSource=admin'
    assert uri is not None, 'no db uri specified!'
    assert db_name is not None, 'no db name specified!'

    # mongodb doc store and document store
    doc_store = MongoDocumentStore.from_uri(
        uri=uri, db_name=db_name, namespace=namespace+'.doc')
    index_store = MongoIndexStore.from_uri(
        uri=uri, db_name=db_name, namespace=namespace+'.index')

    storage_context = StorageContext.from_defaults(
        docstore=doc_store,
        index_store=index_store,
    )
    return storage_context


def get_summary_storage(namespace) -> StorageContext:
    db_name = 'llama-index-dev'
    uri = 'mongodb://root:example@127.0.0.1:27017/llama-index-dev?authSource=admin'
    assert uri is not None, 'no db uri specified!'
    assert db_name is not None, 'no db name specified!'

    # mongodb doc store and document store
    doc_store = MongoDocumentStore.from_uri(
        uri=uri, db_name=db_name, namespace=namespace+'.summary_doc')
    index_store = MongoIndexStore.from_uri(
        uri=uri, db_name=db_name, namespace=namespace+'.summary')

    storage_context = StorageContext.from_defaults(
        docstore=doc_store,
        index_store=index_store,
    )
    return storage_context


def get_knowledge_storage(namespace) -> StorageContext:
    db_name = 'llama-index-dev'
    uri = 'mongodb://root:example@127.0.0.1:27017/llama-index-dev?authSource=admin'
    assert uri is not None, 'no db uri specified!'
    assert db_name is not None, 'no db name specified!'
    index_store = MongoIndexStore.from_uri(
        uri=uri, db_name=db_name, namespace=namespace+'.knowledge')
    doc_store = MongoDocumentStore.from_uri(
        uri=uri, db_name=db_name, namespace=namespace+'.knowledge_doc')
    neo_store = Neo4jGraphStore(
        url="bolt://127.0.0.1:7687", username="neo4j", password="password",
        node_label="Node"
    )
    storage_context = StorageContext.from_defaults(
        graph_store=neo_store,
        docstore=doc_store,
        index_store=index_store
    )
    return storage_context
