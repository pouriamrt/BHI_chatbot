# from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import chainlit as cl
from chainlit.types import ThreadDict
from typing import Dict, Optional
from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.retrievers import ContextualCompressionRetriever
from langchain_core.runnables.config import RunnableConfig
from langchain.memory import ConversationBufferMemory
import warnings
import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from tqdm import tqdm
import textwrap
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain, RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import GraphCypherQAChain
from langchain_community.vectorstores import PGVector
from agent_graph import graph_construct


logging.basicConfig(level=logging.WARNING)
warnings.filterwarnings("ignore")

load_dotenv()
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "Pouria.1378"
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE') or 'neo4j'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Global constants
VECTOR_INDEX_NAME = 'paper_chunks_vec'
VECTOR_NODE_LABEL = 'Chunk'
VECTOR_SOURCE_PROPERTY = 'text'
VECTOR_EMBEDDING_PROPERTY = 'textEmbedding'


llm = ChatOpenAI(model="gpt-4o", temperature=0)

kg = Neo4jGraph(
    url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE
)

metadata_field_info = [
    AttributeInfo(
        name="Publication Year",
        description="The year that the paper was published.",
        type="integer",
    ),
    AttributeInfo(
        name="Date Added",
        description="The year that the paper was added to the collection.",
        type="integer",
    ),
    AttributeInfo(
        name="Author",
        description="Authors of the paper, it could be couple of people.",
        type="string",
    ),
    AttributeInfo(
        name="Title", 
        description="Title of the paper that the paper is about.", 
        type="string",
    ),
]

# persist_directory = './chroma/'
# embedding = OpenAIEmbeddings()
# vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
# CONNECTION_STRING = "postgresql+psycopg://postgres:Pouria.1378@localhost:6024/vector_db"
CONNECTION_STRING = "postgresql+psycopg://bsituser:M4pbcMDsbm30zDV6@awseb-e-mmtzduxdgy-stack-awsebrdsdatabase-a1ggrejgeign.cp5mioiwgdbp.ca-central-1.rds.amazonaws.com:5432/vector_db"
COLLECTION_NAME = 'state_of_union_vectors'
embeddings = OpenAIEmbeddings()

vectorstore = PGVector(
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
#     use_jsonb=True,
)

### Contextualize question ###
contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is. Pay attention to details of the conversation."""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

### Answer question ###
qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know.

{context}"""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

retrieval_query_window = """
MATCH window=
    (:Chunk)-[:NEXT*0..1]->(node)-[:NEXT*0..1]->(:Chunk)
WITH node, score, window as longestWindow 
  ORDER BY length(window) DESC LIMIT 3
WITH nodes(longestWindow) as chunkList, node, score
  UNWIND chunkList as chunkRows
WITH collect(chunkRows.text) as textList, node, score
RETURN apoc.text.join(textList, " \n ") as text,
    score,
    node {.authors, .date_added, .page, .publication_year, .title} AS metadata
"""

vector_store_window = Neo4jVector.from_existing_index(
    embedding=OpenAIEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database="neo4j",
    index_name=VECTOR_INDEX_NAME,
    text_node_property=VECTOR_SOURCE_PROPERTY,
    retrieval_query=retrieval_query_window,
)

CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher statements for particular questions:

# Find all chunks containing the word 'consort'.
MATCH (c:Chunk)
    WHERE c.text CONTAINS 'consort'
RETURN c.text

# Retrieve chunks and their titles that contain a specific keyword.
MATCH (c:Chunk)-[:BELONGS_TO]->(t:Title)
    WHERE c.text CONTAINS 'specific keyword'
RETURN t.name, c.text


# How many papers published in 2021?
MATCH (t:Title)-[:PUBLISHED_IN]->(y:Year)
    WHERE y.value = 2021
RETURN COUNT(t)

# What papers did a specific author write?
MATCH (a:Author)-[:WROTE]->(t:Title)
    WHERE a.name = 'Author Name'
RETURN t.name

# Which papers were published in a specific year?
MATCH (t:Title)-[:PUBLISHED_IN]->(y:Year {{value: 2021}})
RETURN t.name

# Retrieve all chunks belonging to a specific paper.
MATCH (t:Title {{name: 'Paper Title'}})<-[:BELONGS_TO]-(c:Chunk)
RETURN c.text

# List all authors who wrote papers in a given year.
MATCH (a:Author)-[:WROTE]->(t:Title)-[:PUBLISHED_IN]->(y:Year {{value: 2022}})
RETURN a.name

The question is:
{question}"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], 
    template=CYPHER_GENERATION_TEMPLATE
)


answer_prefix_tokens=["FINAL", "ANSWER"]


def setup_runnable():
    document_content_description = "Brain Heart Interconnectome (BHI) research papers"

    retriever = SelfQueryRetriever.from_llm(
        llm,
        vectorstore,
        document_content_description,
        metadata_field_info,
        #search_kwargs={"k": 10}
        #enable_limit=True,
    )

    _filter = LLMChainFilter.from_llm(llm)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=_filter,
        base_retriever=retriever
    )

    ### Statefully manage chat history ###
    memory = cl.user_session.get("memory")
    
    store = {}


    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            # store[session_id] = ChatMessageHistory()
            store[session_id] = memory.chat_memory
        return store[session_id]

    ############## rag ###############
    history_aware_retriever = create_history_aware_retriever(
        llm, compression_retriever, contextualize_q_prompt
    )
    
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    
    ############## graph rag ###############
    retriever_window = vector_store_window.as_retriever()
    
    history_aware_graph_retriever = create_history_aware_retriever(
        llm, retriever_window, contextualize_q_prompt
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain_for_graph = create_retrieval_chain(history_aware_graph_retriever, question_answer_chain)

    graph_rag_chain = RunnableWithMessageHistory(
        rag_chain_for_graph,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    
    ############ cypher chain ###########
    cypherChain = GraphCypherQAChain.from_llm(
        ChatOpenAI(temperature=0),
        graph=kg,
        verbose=True,
        return_intermediate_steps=True,
        output_key="answer",
        cypher_prompt=CYPHER_GENERATION_PROMPT,
    )
    
    
    runnable = graph_construct(conversational_rag_chain, graph_rag_chain, cypherChain, model="gpt-4o")
    
    
    cl.user_session.set("runnable", runnable)


@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
    ) -> Optional[cl.User]:
    return default_user


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.on_chat_start
async def quey_llm():
    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
    setup_runnable()
    
    app_user = cl.user_session.get("user")
    await cl.Message(content=f"Hello {app_user.identifier.split('@')[0]}").send()
    
    
@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    memory = ConversationBufferMemory(return_messages=True)
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "user_message":
            memory.chat_memory.add_user_message(message["output"])
        else:
            memory.chat_memory.add_ai_message(message["output"])

    cl.user_session.set("memory", memory)

    setup_runnable()
    
    
@cl.on_message
async def query_llm(message: cl.Message):
    memory = cl.user_session.get("memory")
    app_user = cl.user_session.get("user")
    
    runnable = cl.user_session.get("runnable")
    response = await runnable.ainvoke({"input": message.content + f" \n\n `session_id` is: {app_user.identifier}"}, 
                                      config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler(
                                                            stream_final_answer=True,
                                                            answer_prefix_tokens=answer_prefix_tokens,
                                                        )]),
                                      )
    try:
        msg = cl.Message(response["agent_out"]['answer'])
    except:
        msg = cl.Message(response["agent_out"])
    await msg.send()
    
    
    memory.chat_memory.add_user_message(message.content)
    memory.chat_memory.add_ai_message(msg.content)
    