import logging
from .mongo_storage import *
from llama_index.core.node_parser import SentenceSplitter, SentenceWindowNodeParser
from llama_index.core import download_loader, load_index_from_storage, ServiceContext, set_global_service_context
from llama_index.core import VectorStoreIndex, SummaryIndex, KnowledgeGraphIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.readers.confluence import ConfluenceReader
from llama_index.readers.file.markdown import MarkdownReader
from llama_index.readers.file.pymu_pdf import PyMuPDFReader
from .chat_context import get_gloabl_chat_agent_instance
from app.models.types import *
from typing import Union, Tuple
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.ollama import OllamaEmbedding

logger = logging.getLogger('root')

# node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
node_parser = SentenceWindowNodeParser.from_defaults(
    window_size=3,
    window_metadata_key="window",
    original_text_metadata_key="original_text",
)

# model = "mistral:7b"  # mistral llama2
# llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")

# node_parser = SentenceSplitter(chunk_size=512)

# llm = Ollama(temperature=0.1, model=model, request_timeout=3000.0)
# embed_model = OllamaEmbedding(model_name=model)

# embed_model = HuggingFaceEmbedding(
#     model_name="sentence-transformers/all-mpnet-base-v2", max_length=512
# )

# service_context = ServiceContext.from_defaults(
#     llm=llm,
#     embed_model=embed_model
# )
# set_global_service_context(service_context)


def configLoader(loaderName, config: ConfuluenceLoaderConfig = None):
    if loaderName == 'markdown':
        return MarkdownReader()
    elif loaderName == 'pdf':
        return PyMuPDFReader()
    elif loaderName == 'confluence':
        if not config or not hasattr(config, 'base_url'):
            raise Exception('confluence config error')
        else:
            os.environ['CONFLUENCE_API_TOKEN'] = config.api_token
            return ConfluenceReader(base_url=config.base_url)
    else:
        raise Exception('unknown loader')


def getMarkdownLoader() -> MarkdownReader:
    return configLoader(loaderName='markdown')


def getPDFLoader() -> PyMuPDFReader:
    return configLoader(loaderName='pdf')


def getConfluenceLoader(user_id) -> ConfluenceReader:
    config: None | ConfuluenceLoaderConfig = ConfuluenceLoaderConfig.objects(
        user_id=user_id).first()
    if not config:
        raise FileNotFoundError('confluence config not found')
    return configLoader(loaderName='confluence', config=config)


def add_confluence_loader_conf(user_id, json):
    config: None | ConfuluenceLoaderConfig = ConfuluenceLoaderConfig.objects(
        user_id=user_id).first()
    if config:
        config.base_url = json['base_url']
        config.api_token = json['api_token']
    else:
        config = ConfuluenceLoaderConfig(user_id=user_id,
                                         base_url=json['base_url'],
                                         api_token=json['api_token'])
    return config.save()


def loadDoc(file: BaseFile):
    if file._cls == 'BaseFile.NormalFile':
        if file.file_name.endswith('.md') or file.file_name.endswith('.txt'):
            d = getMarkdownLoader().load_data(file=file.file_full_path)
            return d
        elif file.file_name.endswith('.pdf'):
            d = getPDFLoader().load_data(file_path=file.file_full_path)
            return d
    elif file._cls == 'BaseFile.Confuluence':
        if file.space:
            d = getConfluenceLoader(file.user_id).load_data(
                space_key=file.space,
                # page_ids=[file.page_id],
                include_children=file.include_children,
                include_attachments=file.include_attachments)
            return d
        elif file.page_id:
            d = getConfluenceLoader(file.user_id).load_data(
                page_ids=file.page_id.split(','),
                include_children=file.include_children,
                include_attachments=file.include_attachments)
            return d
    else:
        raise Exception('unsupport file type')


def loadNodes(file: BaseFile):
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
    knowledge_storage = get_knowledge_storage(user_id)
    try:
        knowledgeStoreIndex = load_index_from_storage(knowledge_storage)
    except Exception as e:
        logger.error(e)
        return {'msg': 'knowledge index not found'}
    file: None | BaseFile = BaseFile.objects(
        user_id=user_id, id=file_id).first()
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
            knowledgeStoreIndex.delete_ref_doc(doc_id, True)
        # vectorStoreIndex.delete(file['doc_id'])
        vetor_storage.persist()
        file.indexed = False
        file.node_ids = []
        file.ref_doc_ids = []
        file.save()
        get_gloabl_chat_agent_instance().refreshAgent(user_id)
        return {'msg': 'remove success', 'data': file.to_dict()}


def lockFile(user_id, file_id) -> Tuple[bool, str]:
    file: None | BaseFile = BaseFile.objects(
        user_id=user_id, id=file_id).first()
    if not file:
        return False, 'file not exsit'
    elif file.indexed:
        return False, 'file already indexed'
    else:
        file.indexing = True
        file.save()
        return True, None


def unlockFile(user_id, file_id) -> Tuple[bool, str]:
    file: None | BaseFile = BaseFile.objects(
        user_id=user_id, id=file_id).first()
    if not file:
        return False, 'file not exsit'
    elif file.indexed:
        return False, 'file already indexed'
    else:
        file.indexing = False
        file.save()
        return True, None


def islockedFile(user_id, file_id) -> Tuple[bool, str]:
    file: None | BaseFile = BaseFile.objects(
        user_id=user_id, id=file_id).first()
    if not file:
        return False, 'file not exsit'
    else:
        return file.indexing, None


def add_index(user_id, file_id):
    lock, msg = islockedFile(user_id, file_id)
    if lock:
        return {'msg': msg}
    locked, msg = lockFile(user_id, file_id)
    if not locked:
        return {'msg': msg}
    vetor_storage = get_vector_storage(user_id)
    summary_storage = get_summary_storage(user_id)
    knowledge_storage = get_knowledge_storage(user_id)
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
    try:
        knowledgeStoreIndex = load_index_from_storage(knowledge_storage)
    except Exception as e:
        logger.error('add_index load knowledgeStoreIndex error')
        logger.error(e)
        knowledgeStoreIndex = KnowledgeGraphIndex.from_documents(
            documents=[], storage_context=knowledge_storage, show_progress=True)
    file: None | BaseFile = BaseFile.objects(
        user_id=user_id, id=file_id).first()
    if not file:
        return {'msg': 'file not exsit'}
    elif not ('indexed' in file and file.indexed):
        nodes = loadNodes(file)
        if not nodes:
            return {'msg': 'load confuluence error'}
        node_ids = []
        ref_doc_ids = []
        for n in nodes:
            ref_doc_ids.append(n.ref_doc_id)
            node_ids.append(n.node_id)
        # vectorStoreIndex.insert_nodes(nodes)
        # vetor_storage.persist()
        # summaryStoreIndex.insert_nodes(nodes)
        # summary_storage.persist()
        knowledgeStoreIndex.build_index_from_nodes(nodes)
        knowledge_storage.persist()
        file.node_ids = node_ids
        file.ref_doc_ids = ref_doc_ids
        file.save()
        file.indexed = True
        file.save()
        get_gloabl_chat_agent_instance().refreshAgent(user_id)
        unlockFile(user_id, file_id)
        return {'msg': 'index success', 'data': file.to_dict()}
    else:
        unlockFile(user_id, file_id)
        return {'msg': 'index exist', 'data': file.to_dict()}


def add_index_for_confuluence(user_id, confuluence_id):
    confuluence: None | Confuluence = Confuluence.objects(
        user_id=user_id, id=confuluence_id).first()
    if not confuluence:
        return {'msg': 'confuluence not exsit'}
