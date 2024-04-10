import logging
from .storage_manager import *
from llama_index.core import load_index_from_storage, Settings
from llama_index.core import VectorStoreIndex,  KnowledgeGraphIndex
from llama_index.readers.confluence import ConfluenceReader
from llama_index.readers.file.markdown import MarkdownReader
from llama_index.readers.file.pymu_pdf import PyMuPDFReader
from llama_index.readers.file import PandasCSVReader, UnstructuredReader
# from .chat_context import get_gloabl_chat_agent_instance
from app.models.types import *
from typing import Tuple
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import (
    BaseNode,
)
import pandas as pd
from typing import List
logger = logging.getLogger('root')


def getConfluenceLoader(group_id) -> ConfluenceReader:
    config: None | ConfuluenceLoaderConfig = ConfuluenceLoaderConfig.objects(
        group_id=group_id).first()
    if not config or not hasattr(config, 'base_url'):
        raise Exception('confluence config error')
    else:
        os.environ['CONFLUENCE_API_TOKEN'] = config.api_token
        return ConfluenceReader(base_url=config.base_url)


def add_confluence_loader_conf(group_id, json):
    config: None | ConfuluenceLoaderConfig = ConfuluenceLoaderConfig.objects(
        group_id=group_id).first()
    if config:
        config.base_url = json['base_url']
        config.api_token = json['api_token']
    else:
        config = ConfuluenceLoaderConfig(group_id=group_id,
                                         base_url=json['base_url'],
                                         api_token=json['api_token'])
    return config.save()


class ExcelReader(BaseReader):
    def load_data(self, file_path: str, extra_info: dict = None):
        data = pd.read_excel(file_path).to_string()
        return [Document(text=data, metadata=extra_info)]


def loadDoc(file: BaseFile) -> List[Document]:
    if file._cls == 'BaseFile.NormalFile':
        if file.file_name.endswith('.md') or file.file_name.endswith('.txt'):
            d = MarkdownReader().load_data(file=file.file_full_path)
            return d
        elif file.file_name.endswith('.pdf'):
            d = PyMuPDFReader().load_data(file_path=file.file_full_path)
            return d
        elif file.file_name.endswith('.csv'):
            d = PandasCSVReader().load_data(file=file.file_full_path)
            return d
        elif file.file_name.endswith('.xls') or file.file_name.endswith('.xlsx'):
            d = ExcelReader().load_data(file=file.file_full_path)
            return d
        else:
            d = UnstructuredReader().load_data(file=file.file_full_path)

    elif file._cls == 'BaseFile.Confuluence':
        if file.space:
            d = getConfluenceLoader(file.group_id).load_data(
                space_key=file.space,
                # page_ids=[file.page_id],
                include_children=file.include_children,
                include_attachments=file.include_attachments)
            return d
        elif file.page_id:
            d = getConfluenceLoader(file.group_id).load_data(
                page_ids=file.page_id.split(','),
                include_children=file.include_children,
                include_attachments=file.include_attachments)
            return d
    else:
        raise Exception('unsupport file type')


def loadNodes(file: BaseFile) -> List[BaseNode]:
    d = loadDoc(file)
    if d:
        return Settings.text_splitter.get_nodes_from_documents(
            documents=d, show_progress=True)
    return None


def remove_index(group_id, file_id):
    vetor_storage = get_vector_storage(group_id)
    try:
        vectorStoreIndex = load_index_from_storage(vetor_storage)
    except Exception as e:
        logger.error(e)
        return {'msg': 'vector index not found'}

    knowledge_storage = get_knowledge_storage(group_id)
    try:
        knowledgeStoreIndex = load_index_from_storage(knowledge_storage)
    except Exception as e:
        logger.error(e)
        return {'msg': 'knowledge index not found'}
    file: None | BaseFile = BaseFile.objects(
        group_id=group_id, id=file_id).first()
    if not file:
        return {'msg': 'file not exsit'}
    elif not file.indexed:
        return {'msg': 'file not indexed'}
    else:
        if not file.ref_doc_ids:
            return {'msg': 'unsupport file type '+file}
        # Can't use vectorStoreIndex.delete_nodes
        # NotImplementedError: Vector indices currently only support delete_ref_doc, which deletes nodes using the ref_doc_id of ingested documents.
        for doc_id in file.ref_doc_ids:
            vectorStoreIndex.delete_ref_doc(doc_id, True)
            knowledgeStoreIndex.delete_ref_doc(doc_id, True)
        vetor_storage.persist()
        knowledge_storage.persist()
        file.indexed = False
        file.node_ids = []
        file.ref_doc_ids = []
        file.save()
        # get_gloabl_chat_agent_instance().refreshAgent(group_id)
        return {'msg': 'remove success', 'data': file.to_dict()}


def lockFile(group_id, file_id) -> Tuple[bool, str]:
    file: None | BaseFile = BaseFile.objects(
        group_id=group_id, id=file_id).first()
    if not file:
        return False, 'file not exsit'
    elif file.indexed:
        return False, 'file already indexed'
    else:
        file.indexing = True
        file.save()
        return True, None


def unlockFile(group_id, file_id) -> Tuple[bool, str]:
    file: None | BaseFile = BaseFile.objects(
        group_id=group_id, id=file_id).first()
    if not file:
        return False, 'file not exsit'
    else:
        file.indexing = False
        file.save()
        return True, None


def islockedFile(group_id, file_id) -> Tuple[bool, str]:
    file: None | BaseFile = BaseFile.objects(
        group_id=group_id, id=file_id).first()
    if not file:
        return True, 'file not exsit'
    elif file.indexing:
        return True, 'file is indexing'
    else:
        return False, None


def isIndexed(group_id, file_id) -> Tuple[bool, str]:
    file: None | BaseFile = BaseFile.objects(
        group_id=group_id, id=file_id).first()
    if not file:
        return False, 'file not exsit'
    else:
        return file.indexed, None


def add_index_safe(group_id, file_id):
    try:
        return add_index(group_id, file_id)
    except Exception as e:
        unlockFile(group_id, file_id)
        logger.error(e)
        return {'msg': 'indexing failed'}, 500


def add_index(group_id, file_id):
    locked, msg = islockedFile(group_id, file_id)
    if locked:
        return {'msg':  msg}
    locked, msg = lockFile(group_id, file_id)
    if not locked:
        return {'msg': msg}
    file: None | BaseFile = BaseFile.objects(
        group_id=group_id, id=file_id).first()
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

        config: ChatConfig = ChatConfig.objects(group_id=group_id).first()
        storages = config_storages(config)

        for storage in storages:
            storage_index: VectorStoreIndex | KnowledgeGraphIndex = None

            try:
                storage_index = load_index_from_storage(storage)
            except Exception as e:
                logger.error('add_index load storage error')
                logger.error(e)
                if storage.vector_store:
                    storage_index = VectorStoreIndex.from_documents(
                        documents=[], storage_context=storage, show_progress=True)
                    file: None | BaseFile = BaseFile.objects(
                        group_id=group_id, id=file_id).first()
                elif storage.graph_store:
                    storage_index = KnowledgeGraphIndex.from_documents(
                        documents=[], storage_context=storage, show_progress=True)

            if not storage_index:
                return {'msg': 'storage not exsit'}
            if storage.vector_store:
                storage_index.insert_nodes(nodes)
            elif storage.graph_store:
                storage_index.build_index_from_nodes(nodes)

            storage.persist()

        file.node_ids = node_ids
        file.ref_doc_ids = ref_doc_ids
        file.indexed = True
        file.save()
        unlockFile(group_id, file_id)

    # vetor_storage = get_vector_storage(group_id)
    # knowledge_storage = get_knowledge_storage(group_id)
    # try:
    #     vectorStoreIndex = load_index_from_storage(vetor_storage)
    # except Exception as e:
    #     logger.error('add_index load vectorStoreIndex error')
    #     logger.error(e)
    #     vectorStoreIndex = VectorStoreIndex.from_documents(
    #         documents=[], storage_context=vetor_storage, show_progress=True)
    # try:
    #     knowledgeStoreIndex = load_index_from_storage(knowledge_storage)
    # except Exception as e:
    #     logger.error('add_index load knowledgeStoreIndex error')
    #     logger.error(e)
    #     knowledgeStoreIndex = KnowledgeGraphIndex.from_documents(
    #         documents=[], storage_context=knowledge_storage, show_progress=True)
    # file: None | BaseFile = BaseFile.objects(
    #     group_id=group_id, id=file_id).first()
    # if not file:
    #     return {'msg': 'file not exsit'}
    # elif not ('indexed' in file and file.indexed):
    #     nodes = loadNodes(file)
    #     if not nodes:
    #         return {'msg': 'load confuluence error'}
    #     node_ids = []
    #     ref_doc_ids = []
    #     for n in nodes:
    #         ref_doc_ids.append(n.ref_doc_id)
    #         node_ids.append(n.node_id)
    #     vectorStoreIndex.insert_nodes(nodes)
    #     vetor_storage.persist()
    #     kg = knowledgeStoreIndex.build_index_from_nodes(nodes)
    #     logger.info('-----------kg-----------')
    #     logger.info(kg)
    #     knowledge_storage.persist()
    #     file.node_ids = node_ids
    #     file.ref_doc_ids = ref_doc_ids
    #     file.save()
    #     file.indexed = True
    #     file.save()
        # unlockFile(group_id, file_id)
        # get_gloabl_chat_agent_instance().refreshAgent(group_id)
        return {'msg': 'index success', 'data': file.to_dict()}
    else:
        unlockFile(group_id, file_id)
        return {'msg': 'index exist', 'data': file.to_dict()}


def add_index_for_confuluence(group_id, confuluence_id):
    confuluence: None | Confuluence = Confuluence.objects(
        group_id=group_id, id=confuluence_id).first()
    if not confuluence:
        return {'msg': 'confuluence not exsit'}
