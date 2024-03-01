from flask import Blueprint
from .mongo_storage import get_vector_storage, get_summary_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import download_loader, load_index_from_storage
from llama_index.core import VectorStoreIndex, SummaryIndex, DocumentSummaryIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata

import logging
from .chat_context import get_gloabl_chat_agent_instance
from ..models.types import *
logger = logging.getLogger('root')

node_parser = SentenceSplitter(chunk_size=512)
MarkdownReader = download_loader('MarkdownReader')
markdown_loader = MarkdownReader()
PDFReader = download_loader("PDFReader")
pdf_loader = PDFReader()


def loadDoc(file):
    if file.file_name.endswith('.md') or file.file_name.endswith('.txt'):
        d = markdown_loader.load_data(file=file.file_full_path)
        return d
    elif file.file_name.endswith('.pdf'):
        d = pdf_loader.load_data(file=file.file_full_path)
        return d
    else:
        return None


def loadNodes(file):
    d = loadDoc(file)
    if d:
        return node_parser.get_nodes_from_documents(
            documents=d, show_progress=True)
    return None


def remove_index(user_id, file_id):
    vetor_storage = get_vector_storage(user_id)
    try:
        vectorStoreIndex = load_index_from_storage(vetor_storage)
    except Exception as e:
        logger.error(e)
        return {'msg': 'vector index not found'}

    summary_storage = get_summary_storage(user_id)
    try:
        summaryStoreIndex = load_index_from_storage(summary_storage)
    except Exception as e:
        logger.error(e)
        return {'msg': 'summary index not found'}
    file = File.objects(user_id=user_id, id=file_id).first()
    if not file:
        return {'msg': 'file not exsit'}
    elif not file.indexed:
        return {'msg': 'file not indexed'}
    else:
        # nodes = loadNodes(file)
        if not file.ref_doc_ids:
            return {'msg': 'unsupport file type '+file}
        # Can't use vectorStoreIndex.delete_nodes
        # NotImplementedError: Vector indices currently only support delete_ref_doc, which deletes nodes using the ref_doc_id of ingested documents.
        for doc_id in file.ref_doc_ids:
            vectorStoreIndex.delete_ref_doc(doc_id, True)
            summaryStoreIndex.delete_ref_doc(doc_id, True)
        # vectorStoreIndex.delete(file['doc_id'])
        vetor_storage.persist()
        file.indexed = False
        file.node_ids = []
        file.ref_doc_ids = []
        file.save()
        get_gloabl_chat_agent_instance().refreshAgent(user_id)
        return {'msg': 'remove success', 'data': file.to_dict()}


def add_index(user_id, file_id):
    vetor_storage = get_vector_storage(user_id)
    summary_storage = get_summary_storage(user_id)
    try:
        vectorStoreIndex = load_index_from_storage(vetor_storage)
    except Exception as e:
        logger.error('add_index load vectorStoreIndex error')
        logger.error(e)
        vectorStoreIndex = VectorStoreIndex.from_documents(
            documents=[], storage_context=vetor_storage, show_progress=True)
    try:
        summaryStoreIndex = load_index_from_storage(summary_storage)
    except Exception as e:
        logger.error('add_index load summaryStoreIndex error')
        logger.error(e)
        summaryStoreIndex = SummaryIndex.from_documents(
            documents=[], storage_context=summary_storage, show_progress=True)

    file = File.objects(user_id=user_id, id=file_id).first()
    if not file:
        return {'msg': 'file not exsit'}
    elif not ('indexed' in file and file.indexed):
        nodes = loadNodes(file)
        if not nodes:
            return {'msg': 'unsupport file type '+file.file_name}
        node_ids = []
        ref_doc_ids = []
        for n in nodes:
            ref_doc_ids.append(n.ref_doc_id)
            node_ids.append(n.node_id)
        vectorStoreIndex.insert_nodes(nodes)
        vetor_storage.persist()
        summaryStoreIndex.insert_nodes(nodes)
        summary_storage.persist()
        file.indexed = True
        file.node_ids = node_ids
        file.ref_doc_ids = ref_doc_ids
        file.save()
        get_gloabl_chat_agent_instance().refreshAgent(user_id)
        return {'msg': 'index success', 'data': file.to_dict()}
    else:
        return {'msg': 'index exist', 'data': file.to_dict()}
