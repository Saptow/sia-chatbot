import os
from typing import Any, List, Optional, Union
from pydantic import BaseModel
from neo4j_graphrag.embeddings.base import Embedder
from neo4j_graphrag.retrievers.base import Retriever
from neo4j_graphrag.message_history import MessageHistory
from neo4j_graphrag.types import LLMMessage, RetrieverResult
from neo4j import Driver, GraphDatabase
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.retrievers import VectorCypherRetriever
from neo4j_graphrag.embeddings.sentence_transformers import SentenceTransformerEmbeddings

from utils.graphrag.schemas import GraphRAG, RagResultModel, RagTemplate
from utils.graphrag.helper import generic_result_formatter
from utils.graphrag.constants import QUERY_TEMPLATE, PROMPT_TEMPLATE

class ChatRequest(BaseModel):
    timestamp: str
    user_id: int # mock user id for demo purposes
    message: str


class ChatResponse(BaseModel):
    timestamp: str
    response: str


# Error Schemas
class EmbedderInitializationError(Exception):
    """Raised when there is an error initializing the embedder."""
    pass

class RetrieverInitializationError(Exception):
    """Raised when there is an error initializing the retriever."""
    pass

class ResponseGenerationError(Exception):
    """Raised when there is an error generating the response."""
    pass
class UserInfoRetrievalError(Exception):
    """Raised when there is an error retrieving user information."""
    pass
class RagChatbotError(Exception):
    """Raised when there is a general RAG chatbot error."""
    pass

class GraphRAGChatbot(GraphRAG):
    driver: Driver 
    embedder: Embedder
    retriever_config: Optional[dict[str, Any]] = None
    return_context: Optional[bool] = None
    response_fallback: Optional[str] = None

    def __init__(self):
        # Initialise Neo4j specific components for driver, embedder, retriever, llm, rag
        driver = GraphDatabase.driver(
            uri='neo4j+ssc://e0a0bc0d.databases.neo4j.io',
            auth=(os.getenv('NEO4J_USERNAME',''), os.getenv('NEO4J_PASSWORD',''))
        )
        try:
            driver.verify_connectivity()
            print("Connected to Neo4j database.")
        except Exception as e:
            print("Error connecting to Neo4j database:", e)
            raise e
        try: 
            embedder=SentenceTransformerEmbeddings(model='intfloat/e5-base-v2')
        except EmbedderInitializationError as e:
            print("Error initializing embedder:", e)
            raise e
        
        try: 
            retriever=VectorCypherRetriever(
                driver=driver,
                embedder=embedder,
                retrieval_query=QUERY_TEMPLATE,
                result_formatter=generic_result_formatter,
                index_name='chunk_vec',
            )
        except RetrieverInitializationError as e:
            print("Error initializing retriever:", e)
            raise e
        
        llm=OpenAILLM(
            model_name=os.getenv('DOCUMENT_RAG_MODEL','gpt-5.2')
        )

        prompt_template = RagTemplate(
            template=PROMPT_TEMPLATE,
            expected_inputs=['context', 'query_text', 'roster_info', 'exercise_info', 'sleep_info']
        )

        super().__init__(retriever, llm, prompt_template)
        self.embedder = embedder
        self.retriever_config = {
                "query_params": { # Cypher query parameters
                    "limit": 100,
                    },
        }
        
    def chat(self, 
            current_query: str, 
            messages: List[dict] = [],
            roster_info: str = "", 
            exercise_info: str = "",
            sleep_info: str = ""
            ) -> RagResultModel:
        """Perform a RAG search and return the response."""

        # Transform messages to LLMMessage objects
        message_history = [LLMMessage(**msg) for msg in messages] if messages else []

        return super().search(
            query_text=current_query,
            message_history=message_history,
            roster_info=roster_info,
            exercise_info=exercise_info,
            sleep_info=sleep_info,
            retriever_config=self.retriever_config
        )
    

