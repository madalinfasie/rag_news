import asyncio
import typing as t

from chatpage.services import qdrant
from django.conf import settings
from langchain.agents import create_agent
from langchain.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.graph import START, StateGraph

mcp_client = MultiServerMCPClient(
    {
        "weather": {
            "url": settings.WEATHER_MCP_SERVER,
            "transport": "streamable_http",
        }
    }
)


async def get_llm_agent():
    tools = await mcp_client.get_tools()
    llm = ChatOllama(model=settings.MODEL_NAME, base_url=settings.OLLAMA_URL)
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


def _retrieve(state: State) -> State:
    retrieved_docs = qdrant.vector_store.similarity_search(state["question"], k=5)
    state["context"] = retrieved_docs
    return state


async def _generate(state: State) -> State:
    agent = await get_llm_agent()
    docs_content = "\n\n".join([doc.page_content for doc in state["context"]])
    prompt_with_context = system_prompt.format(context=docs_content)
    messages = [SystemMessage(prompt_with_context), HumanMessage(state["question"])]
    res = await agent.ainvoke({"messages": messages})

    state["answer"] = res["messages"][-1].content
    return state


def _build_graph():
    graph_builder = StateGraph(State).add_sequence([_retrieve, _generate])
    graph_builder.add_edge(START, "_retrieve")
    return graph_builder.compile()


graph = _build_graph()
