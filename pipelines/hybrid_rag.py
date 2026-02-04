from typing import List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
import os
from pydantic import BaseModel


class Pipeline:
    class Valves(BaseModel):
        OPENAI_API_KEY: str
        DOCUMENT_RAG_MODEL: str
        
    def __init__(self):
        self.name = "Hybrid RAG"
        self.basic_rag_pipeline = None
        self.valves=self.Valves(
            **{
                "pipelines": ["*"],
                "OPENAI_API_KEY":os.getenv('OPENAI_API_KEY',''),
                "DOCUMENT_RAG_MODEL": os.getenv("DOCUMENT_RAG_MODEL", "gpt-4o"),
            }
        )

    async def on_startup(self):
        from utils.pipelines.components import ThresholdFilter
        from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
        from haystack.components.rankers import SentenceTransformersSimilarityRanker
        from haystack_integrations.document_stores.chroma import ChromaDocumentStore
        from haystack_integrations.components.retrievers.chroma import ChromaEmbeddingRetriever
        from haystack.components.builders import PromptBuilder
        from haystack.components.generators import OpenAIGenerator
        from haystack import Pipeline
        os.environ["OPENAI_API_KEY"] = self.valves.OPENAI_API_KEY

        # Embedder to convert query text to embeddings
        text_embedder = SentenceTransformersTextEmbedder(
            model="intfloat/e5-large-v2"
        )

        # Literature Document Store and Retriever
        lit_document_store=ChromaDocumentStore(persist_path="./chroma_db/literature")
        lit_retriever = ChromaEmbeddingRetriever(lit_document_store, top_k=5)

        # Internal Document Store and Retriever
        int_document_store=ChromaDocumentStore(persist_path="./chroma_db/internal")
        int_retriever = ChromaEmbeddingRetriever(int_document_store, top_k=5)

        # Threshold Filter
        threshold_filter = ThresholdFilter(threshold=0)

        # Reranker
        # reranker=SentenceTransformersSimilarityRanker(model='baai/bge-reranker-v2-m3')
        # reranker.warm_up()

        # Define prompt template here #TODO: shift to constants file if needed
        template = (
            "You are a knowledgeable assistant. There are 2 types of documents provided as context: \n"
            "1. Internal Documents: These are documents from the company's internal knowledge base. They contain information on the Standard Operating Procedures"
            "of the company regarding mental health practices.\n"
            "2. Literature Documents: These are documents from external sources, such as research papers, articles, and books, that provide additional context and information on mental health practices.\n"
            "Prioritise information from Internal Documents over Literature Documents when answering questions.\n"
            "Address the user query based on the context provided using a concise, warm and empathetic tone.\n"
        )
        template += """
        Context:
        **Internal Documents:**
        {% for document in internal_documents %}
            {{ document.content }}
        {% endfor %}
        **Literature Documents:**
        {% for document in literature_documents %}
            {{ document.content }}
        {% endfor %}

        Question: {{question}}
        Answer:
        """
        
        prompt_builder = PromptBuilder(template=template)

        generator = OpenAIGenerator(model="gpt-4o", generation_kwargs={'temperature':0})


        ### Pipeline definition and components ###
        self.basic_rag_pipeline = Pipeline()
        self.basic_rag_pipeline.add_component("text_embedder", text_embedder)
        self.basic_rag_pipeline.add_component("int_retriever", int_retriever)
        self.basic_rag_pipeline.add_component("lit_retriever", lit_retriever)
        self.basic_rag_pipeline.add_component('threshold_filter', threshold_filter)
        # self.basic_rag_pipeline.add_component('reranker', reranker)
        self.basic_rag_pipeline.add_component("prompt_builder", prompt_builder)
        self.basic_rag_pipeline.add_component("llm", generator)

        ### Pipeline connections ###
        # Embedding to retrievers
        self.basic_rag_pipeline.connect(
            "text_embedder.embedding", "int_retriever.query_embedding"
        )
        self.basic_rag_pipeline.connect(
            "text_embedder.embedding", "lit_retriever.query_embedding"
        )

        # Internal Document Retriever to Threshold Filter
        self.basic_rag_pipeline.connect("int_retriever", "threshold_filter.documents")

        # Prompt Builder
        self.basic_rag_pipeline.connect("threshold_filter.documents", "prompt_builder.internal_documents")
        self.basic_rag_pipeline.connect("lit_retriever", "prompt_builder.literature_documents")

        # Retrievers to reranker
        # self.basic_rag_pipeline.connect("lit_retriever", "reranker.documents") 

        #TODO: Change this logic to apply reranking logic if need be
        # Reranker to prompt builder
        # self.basic_rag_pipeline.connect("reranker", "prompt_builder.documents")

        # Prompt builder to LLM
        self.basic_rag_pipeline.connect("prompt_builder", "llm")

        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:

        question = user_message
        response = self.basic_rag_pipeline.run(
            {
                "text_embedder": {"text": question},
                "prompt_builder": {"question": question},
            }
        )
        return response["llm"]["replies"][0]
