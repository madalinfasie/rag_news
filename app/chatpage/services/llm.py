import asyncio
import time
import typing as t

from chatpage.services import qdrant
from django.conf import settings
from langchain.agents import create_agent
from langchain.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.graph import START, StateGraph
from sentence_transformers.cross_encoder import CrossEncoder

mcp_client = MultiServerMCPClient(
    {
        "weather": {
            "url": settings.WEATHER_MCP_SERVER,
            "transport": "streamable_http",
        }
    }
)

llm = ChatOllama(model=settings.MODEL_NAME, base_url=settings.OLLAMA_URL)
reranker = CrossEncoder(settings.RERANKER_MODEL)


async def get_llm_agent():
    tools = await mcp_client.get_tools()
    return create_agent(model=llm, tools=tools)


system_prompt = """You are a helpful news reporter. Answer the question at the end following the steps:
1. Before anything else, try to find useful tools to answer the question. If you find a useful tool, use it to answer the question. Use only the question to extract tool parameters.
2. If no tool is found, use the pieces of context to answer the question at the end. If you don't know the answer, just say you don't know, don't try to make up the answer.
3. At the end, note the tools you found in the first step

{context}
"""


def ask(question: str) -> str:
    new_state = asyncio.run(
        graph.ainvoke({"question": question, "context": [], "answer": ""})
    )
    return new_state["answer"]


class State(t.TypedDict):
    question: str
    context: list[Document]
    answer: str


async def _retrieve(state: State) -> State:
    start = time.perf_counter()
    retrieved_docs = qdrant.vector_store.similarity_search(state["question"], k=100)
    state["context"] = retrieved_docs
    print(f"Retrieved in {time.perf_counter() - start}")
    return state


async def _rerank(state: State) -> State:
    start = time.perf_counter()
    query = state["question"]
    documents = state["context"]

    text_docs = [doc.page_content for doc in documents]
    ranks = reranker.rank(query, text_docs)

    filtered_documents = [documents[rank["corpus_id"]] for rank in ranks[:5]]
    state["context"] = filtered_documents
    print(f"Reranking in {time.perf_counter() - start}")
    return state


async def _generate(state: State) -> State:
    start = time.perf_counter()
    agent = await get_llm_agent()
    docs_content = "\n\n".join([doc.page_content for doc in state["context"]])
    prompt_with_context = system_prompt.format(context=docs_content)
    messages = [SystemMessage(prompt_with_context), HumanMessage(state["question"])]
    res = await agent.ainvoke({"messages": messages})

    state["answer"] = res["messages"][-1].content
    print(f"Generated answer in {time.perf_counter() - start}")
    return state


def _build_graph():
    graph_builder = StateGraph(State).add_sequence([_retrieve, _rerank, _generate])
    graph_builder.add_edge(START, "_retrieve")
    return graph_builder.compile()


graph = _build_graph()
