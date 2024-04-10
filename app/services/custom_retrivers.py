from llama_index.core.retrievers import BaseRetriever, VectorIndexRetriever, KnowledgeGraphRAGRetriever
from llama_index.core.schema import QueryBundle, NodeWithScore
from llama_index.core import KnowledgeGraphIndex, VectorStoreIndex
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.prompts import PromptTemplate
from typing import List


class VectorAndKnowledgeGraphRetriever(BaseRetriever):
    """Custom retriever that performs both semantic search and hybrid search."""

    def __init__(
        self,
        vector_retriever: VectorIndexRetriever,
        knowledge_retriever: KnowledgeGraphRAGRetriever,
        mode: str = "OR",
    ) -> None:
        """Init params."""

        self._vector_retriever = vector_retriever
        self.knowledge_retriever = knowledge_retriever
        if mode not in ("AND", "OR"):
            raise ValueError("Invalid mode.")
        self._mode = mode
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes given query."""

        vector_nodes = self._vector_retriever.retrieve(query_bundle)
        knowledge_nodes = self.knowledge_retriever.retrieve(query_bundle)

        vector_ids = {n.node.node_id for n in vector_nodes}
        knowledge_ids = {n.node.node_id for n in knowledge_nodes}

        combined_dict = {n.node.node_id: n for n in vector_nodes}
        combined_dict.update({n.node.node_id: n for n in knowledge_nodes})

        if self._mode == "AND":
            retrieve_ids = vector_ids.intersection(knowledge_ids)
        else:
            retrieve_ids = vector_ids.union(knowledge_ids)

        retrieve_nodes = [combined_dict[rid] for rid in retrieve_ids]
        return retrieve_nodes


def build_reteriver(vector_Index: VectorStoreIndex, knowledge_index: KnowledgeGraphIndex) -> VectorAndKnowledgeGraphRetriever:
    vector_retriever = VectorIndexRetriever(
        index=vector_Index, similarity_top_k=100)
    knowledge_retriever = KnowledgeGraphRAGRetriever(
        index=knowledge_index, storage_context=knowledge_index.storage_context)
    custom_retriever = VectorAndKnowledgeGraphRetriever(
        vector_retriever, knowledge_retriever)
    return custom_retriever


text_qa_template_str = (
    "Context information is"
    " below.\n---------------------\n{context_str}\n---------------------\nUsing"
    " both the context information and also using your own knowledge, answer"
    " the question: {query_str}\nIf the context isn't helpful, you can also"
    " answer the question on your own.\n"
)
refine_template_str = (
    "The original question is as follows: {query_str}\nWe have provided an"
    " existing answer: {existing_answer}\nWe have the opportunity to refine"
    " the existing answer (only if needed) with some more context"
    " below.\n------------\n{context_msg}\n------------\nUsing both the new"
    " context and your own knowledge, update or repeat the existing answer.\n"
)


def build_query_engine(vector_Index: VectorStoreIndex, knowledge_index: KnowledgeGraphIndex) -> RetrieverQueryEngine:
    response_synthesizer = get_response_synthesizer(
        text_qa_template=PromptTemplate(text_qa_template_str),
        refine_template=PromptTemplate(refine_template_str),
    )
    vk_query_engine = RetrieverQueryEngine(
        retriever=build_reteriver(vector_Index, knowledge_index),
        response_synthesizer=response_synthesizer,
    )
    return vk_query_engine
