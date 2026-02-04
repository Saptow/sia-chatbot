from typing import List, Optional, Union, Generator, Iterator, Tuple
import os
from pydantic import BaseModel
from utils.graphrag.helper import generic_result_formatter, parse_user_info
from utils.graphrag.constants import QUERY_TEMPLATE, PROMPT_TEMPLATE, USER_INFO_DICTIONARY, DEFAULT_PROMPT
from neo4j_graphrag.types import LLMMessage

class Pipeline:
    class Valves(BaseModel):
        OPENAI_API_KEY: str
        DOCUMENT_RAG_MODEL: str
        NEO4J_USERNAME: str
        NEO4J_PASSWORD: str
        user_id: int

    def __init__(self):
        self.name='Graph RAG'
        self.driver = None
        self.embedder = None
        # self.retriever = None
        # self.llm = None
        self.rag = None
        self.valves=self.Valves(
            **{
                'pipelines': ['*'],
                "OPENAI_API_KEY":os.getenv('OPENAI_API_KEY',''),
                'DOCUMENT_RAG_MODEL': "gpt-5",
                'NEO4J_USERNAME': os.getenv('NEO4J_USERNAME', ''),
                'NEO4J_PASSWORD': os.getenv('NEO4J_PASSWORD', ''),
                'user_id': 1, # Default user_id
            }
        )

    async def on_startup(self):
        # Set up the graph-based RAG pipeline here (using Neo4j)
        from neo4j_graphrag.retrievers import VectorCypherRetriever
        from neo4j import GraphDatabase
        from neo4j_graphrag.llm import OpenAILLM
        from utils.graphrag.schemas import GraphRAG, RagTemplate
        from neo4j_graphrag.embeddings.sentence_transformers import SentenceTransformerEmbeddings
        os.environ["OPENAI_API_KEY"] = self.valves.OPENAI_API_KEY


        # Connect to Neo4j database
        driver=GraphDatabase.driver(
            uri='neo4j+s://e0a0bc0d.databases.neo4j.io',
            auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
            )
        
        # Initialise embedder
        try:
            embedder=SentenceTransformerEmbeddings(model='intfloat/e5-base-v2')
        except Exception as e:
            print("Error initializing embedder:", e)
            raise e
        
        # Initalise the retriever
        try:
            retriever=VectorCypherRetriever(
                driver=driver,
                embedder=embedder,
                retrieval_query=QUERY_TEMPLATE,
                result_formatter=generic_result_formatter,
                index_name='chunk_vec',
                )
        except Exception as e:
            print("Error initializing retriever:", e)
            raise e
        
        # Initialise LLM instance
        llm=OpenAILLM(
            model_name=self.valves.DOCUMENT_RAG_MODEL,
            # model_params={"stream": True, 
            #               # "response_format": {"type": "json_object"
            # }
            )
        
        # Define prompt template
        prompt_template=RagTemplate(
            template=PROMPT_TEMPLATE, 
            expected_inputs=['context', 'query_text', 'roster_info', 'personal_info']
        )
        # Initialise RAG component
        rag=GraphRAG(
            retriever=retriever,
            llm=llm,
            prompt_template=prompt_template
        )
        self.driver=driver
        self.embedder=embedder
        self.rag=rag

        pass

    async def on_shutdown(self):
        # Function to close the Neo4j driver connection
        if self.driver:
            self.driver.close()
        pass

    def pipe(
        self, 
        model_id: str,
        user_message: str,
        messages: List[dict] = [], #TODO: Change to List[],
        body: dict = {} 
    ) -> Union[str, Generator, Iterator]:
        # Define the RAG pipeline here
        user_id=self.valves.user_id
        user_info=USER_INFO_DICTIONARY.get(user_id, None)
        roster_info=user_info.get('roster_info', None) if user_info else None
        
        # Fetching user
        # Embedding the query
        if not self.embedder or not self.rag:
            raise ValueError("Embedder or RAG component not initialized.")
        
        if messages:
            messages=[LLMMessage(**msg) for msg in messages]
        if user_info:
            user_info_str=parse_user_info(user_info)
        if roster_info:
            roster_info_str=parse_user_info(roster_info)

        # Perform the RAG search
        rag_result = self.rag.search(
            message_history=messages,
            query_text=user_message,
            personal_info=user_info_str if user_info else "",
            roster_info=roster_info_str if roster_info else "",
            retriever_config={
                "query_params": { # Cypher query parameters
                    "limit": 100,
                    },
        },
        )
        return rag_result.answer