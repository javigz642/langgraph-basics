"""Variacion paso 2 · que pasa si quitamos add_messages del State."""
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class StateSinReducer(TypedDict):
    messages: list                               # sin reducer: cada nodo SUSTITUYE la lista


class StateConReducer(TypedDict):
    messages: Annotated[list, add_messages]      # con reducer: cada nodo SUMA a la lista


# Dos nodos que responden uno detras de otro (sin LLM, para ver solo el mecanismo)
def nodo_a(state):
    return {"messages": [AIMessage("respuesta del nodo A")]}


def nodo_b(state):
    return {"messages": [AIMessage("respuesta del nodo B")]}


def construir(state_cls):
    b = StateGraph(state_cls)
    b.add_node("a", nodo_a)
    b.add_node("b", nodo_b)
    b.add_edge(START, "a")
    b.add_edge("a", "b")
    b.add_edge("b", END)
    return b.compile()


entrada = {"messages": [HumanMessage("hola")]}
for nombre, cls in [("SIN add_messages", StateSinReducer), ("CON add_messages", StateConReducer)]:
    final = construir(cls).invoke(entrada)
    print(f"── {nombre} ── mensajes al final: {len(final['messages'])}")
    for m in final["messages"]:
        print(f"   {type(m).__name__:<13}| {m.content}")
    print()
