"""Paso 4 · Herramientas: ToolNode + arista condicional = el ciclo del agente."""
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Base de datos de juguete: el agente de pedidos de la teoria
PEDIDOS = {
    "1234": {"estado": "enviado", "transportista": "SEUR", "llegada": "jueves"},
    "5678": {"estado": "en preparación", "transportista": "-", "llegada": "la semana que viene"},
}


@tool
def consulta_pedido(numero: str) -> dict:
    """Devuelve el estado, el transportista y la fecha de llegada de un pedido a partir de su número."""
    return PEDIDOS.get(numero, {"error": f"No existe el pedido {numero}"})


tools = [consulta_pedido]


class State(TypedDict):
    messages: Annotated[list, add_messages]


modelo = ChatOllama(model="llama3.1", temperature=0).bind_tools(tools)
SYSTEM = SystemMessage("Eres el asistente de soporte de una tienda online. Responde en español, breve. "
                       "Usa la herramienta consulta_pedido cuando te pregunten por un pedido.")


def chatbot(state: State) -> dict:
    return {"messages": [modelo.invoke([SYSTEM] + state["messages"])]}


builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))                # nodo que EJECUTA las tools que pide el modelo
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)  # ¿pidio tool? -> "tools" ; si no -> END
builder.add_edge("tools", "chatbot")                      # tras la tool, vuelve al modelo: EL CICLO
grafo = builder.compile(checkpointer=MemorySaver())


def conversar(texto: str, config: dict) -> None:
    print(f"Tú: {texto}")
    # stream_mode="updates": vemos que nodo se ejecuta en cada paso del grafo
    for paso in grafo.stream({"messages": [HumanMessage(texto)]}, config=config, stream_mode="updates"):
        for nodo, cambio in paso.items():
            msg = cambio["messages"][-1]
            if getattr(msg, "tool_calls", None):
                llamada = msg.tool_calls[0]
                print(f"  [{nodo}] pide tool -> {llamada['name']}({llamada['args']})")
            elif nodo == "tools":
                print(f"  [{nodo}] resultado -> {msg.content}")
            else:
                print(f"  [{nodo}] responde -> {msg.content}")
    print()


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "cliente-42"}}
    conversar("Hola, ¿cómo va mi pedido 1234?", config)
    conversar("¿Y qué transportista lo lleva?", config)   # la respuesta ya esta en la memoria
