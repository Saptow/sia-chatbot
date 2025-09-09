from typing import List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
import os
import asyncio
from pydantic import BaseModel

class Pipeline:
    class Valves(BaseModel):
        OPENAI_API_KEY: str
        DOCUMENT_RAG_MODEL: str
    def __init__(self):
        self.basic_rag_pipeline = None
        self.valves=self.Valves(
            **{
                "pipelines": ["*"],
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
                "DOCUMENT_RAG_MODEL": os.getenv("DOCUMENT_RAG_MODEL", "gpt-4o"),
            }
        )

    async def on_startup(self):
        from haystack.components.embedders import SentenceTransformersDocumentEmbedder
        from haystack.components.embedders import SentenceTransformersTextEmbedder
        from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
        from haystack.components.builders import PromptBuilder
        from haystack.components.generators import OpenAIGenerator
        from langchain_text_splitters import MarkdownHeaderTextSplitter
        from haystack.document_stores.in_memory import InMemoryDocumentStore

        from haystack import Document
        from haystack import Pipeline

        document_store = InMemoryDocumentStore()

        # Load all the markdowns under the markdown directory 
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        docs=[]
        markdown_dir = "../markdown"

        for filename in os.listdir(markdown_dir):
            # Read file content
            if not filename.endswith(".md"):
                continue
            with open(os.path.join(markdown_dir, filename), "r", encoding="utf-8") as f:
                content = f.read()

            # Split content into smaller chunks using MarkdownHeaderTextSplitter
            text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
            chunks = text_splitter.split_text(content)
            count=1
            for chunk in chunks:
                docs.append(Document(content=chunk, meta={"doc_name": filename, "chunk_id": count}))
                count += 1
            print(f"Processed {filename}, total chunks: {len(chunks)}")
        
        print(f"Total documents/chunks to index: {len(docs)}")

        doc_embedder = SentenceTransformersDocumentEmbedder(
            model="intfloat/e5-large-v2"
        )
        doc_embedder.warm_up()

        docs_with_embeddings = doc_embedder.run(docs)
        document_store.write_documents(docs_with_embeddings["documents"])

        text_embedder = SentenceTransformersTextEmbedder(
            model="intfloat/e5-large-v2"
        )

        retriever = InMemoryEmbeddingRetriever(document_store)

        template = """
        Given the following information, answer the question.

        Context:
        {% for document in documents %}
            {{ document.content }}
        {% endfor %}

        Question: {{question}}
        Answer:
        """

        prompt_builder = PromptBuilder(template=template)

        generator = OpenAIGenerator(model="gpt-4o")

        self.basic_rag_pipeline = Pipeline()
        # Add components to your pipeline
        self.basic_rag_pipeline.add_component("text_embedder", text_embedder)
        self.basic_rag_pipeline.add_component("retriever", retriever)
        self.basic_rag_pipeline.add_component("prompt_builder", prompt_builder)
        self.basic_rag_pipeline.add_component("llm", generator)

        # Now, connect the components to each other
        self.basic_rag_pipeline.connect(
            "text_embedder.embedding", "retriever.query_embedding"
        )
        self.basic_rag_pipeline.connect("retriever", "prompt_builder.documents")
        self.basic_rag_pipeline.connect("prompt_builder", "llm")

        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        # This is where you can add your custom RAG pipeline.
        # Typically, you would retrieve relevant information from your knowledge base and synthesize it to generate a response.

        print(messages)
        print(user_message)

        question = user_message
        response = self.basic_rag_pipeline.run(
            {
                "text_embedder": {"text": question},
                "prompt_builder": {"question": question},
            }
        )

        return response["llm"]["replies"][0]
