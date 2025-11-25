import typing as t

from chatpage.services import qdrant
from django.conf import settings
from langchain.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from langgraph.graph import START, StateGraph

llm = ChatOllama(model=settings.MODEL_NAME, base_url=settings.OLLAMA_URL)

system_prompt = """You are a helpful news reporter, use the following pieces of context to answer the question at the end.
If you don't know the answer, just say you don't know, don't try to make up the answer.

{context}
"""


def ask(question: str) -> str:
    new_state = graph.invoke({"question": question, "context": {}, "answer": ""})
    return new_state["answer"]


class State(t.TypedDict):
    question: str
    context: list[Document]
    answer: str


def _retrieve(state: State) -> State:
    print("STATE IN RETRIEVE ", state)
    retrieved_docs = qdrant.vector_store.similarity_search(state["question"], k=5)
    state["context"] = retrieved_docs
    return state


def _generate(state: State) -> State:
    print("STATE IN GENERATE ", state)
    docs_content = "\n\n".join([doc.page_content for doc in state["context"]])
    prompt_with_context = system_prompt.format(context=docs_content)
    messages = [SystemMessage(prompt_with_context), HumanMessage(state["question"])]
    state["answer"] = llm.invoke(messages).content
    return state


def _build_graph():
    graph_builder = StateGraph(State).add_sequence([_retrieve, _generate])
    graph_builder.add_edge(START, "_retrieve")
    return graph_builder.compile()


graph = _build_graph()
