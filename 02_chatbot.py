"""Paso 2 · Chatbot: el State acumula mensajes y un nodo llama al modelo."""
from typing import Annotated, TypedDict #Annotated permite añadir informacion extra de un tipo

from langchain_core.messages import HumanMessage #HumanMessage un objeto que representa "messaje escrito por humano"
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages #reducer

# add_messages es un "reducer": SUMA los mensajes nuevos a la lista en vez de sustituirla
class State(TypedDict):
    #messages es una lista y cunado alguien la actualice, usa add_messages para combinarla
    messages: Annotated[list, add_messages]


modelo = ChatOllama(model="llama3.1", temperature=0)


# El nodo recibe TODO el historial y devuelve solo la respuesta nueva
def chatbot(state: State) -> dict:
    return {"messages": [modelo.invoke(state["messages"])]}


builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)
grafo = builder.compile()

if __name__ == "__main__":
    resultado = grafo.invoke({"messages": [HumanMessage("Explícame en una frase qué es LangGraph.")]})
    for m in resultado["messages"]:
        print(f"{type(m).__name__:<13}| {m.content}")
    print(f"\nMensajes en el state al terminar: {len(resultado['messages'])}")
