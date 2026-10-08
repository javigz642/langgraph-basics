"""Paso 3 · Memoria: el checkpointer guarda el state por thread_id entre llamadas."""
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


modelo = ChatOllama(model="llama3.1", temperature=0)
SYSTEM = SystemMessage("Eres un asistente amable. Responde en español y en una o dos frases.")


def chatbot(state: State) -> dict:
    #Con SYSTEM crea una lista nueva solo para enviarla al modelo, el SystemMessage no se guarda en el state.
    return {"messages": [modelo.invoke([SYSTEM] + state["messages"])]} 


builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# La UNICA diferencia con el paso 2: compilar con un checkpointer, es lo que añade la memoria
# MemorySaver guarda las "fotos/capturas" en la RAM: 
# - Perfecto para aprender y pruebas
# - Cuando el script termina se pierde todo. En producción se usan checkpointers que guardan en DDBB
grafo = builder.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "alumno-1"}}   # thread_id = una conversacion
    turnos = [
        "Hola, me llamo Ignacio y doy clase de LangGraph.",
        "¿Qué ventaja tiene un grafo frente a una cadena? Responde breve.",
        "¿Cómo me llamo y de qué doy clase?",
    ]
    for i, texto in enumerate(turnos, 1):
        salida = grafo.invoke({"messages": [HumanMessage(texto)]}, config=config)  # solo el mensaje NUEVO
        print(f"[Turno {i}] Tú  : {texto}")
        print(f"[Turno {i}] Bot : {salida['messages'][-1].content}\n")
        print("SALIDA = ", len(salida["messages"]))

    otro = grafo.invoke({"messages": [HumanMessage("¿Cómo me llamo?")]},
                        config={"configurable": {"thread_id": "alumno-2"}})
    print(f"[Otro thread] Bot : {otro['messages'][-1].content}")
    print(f"\nMensajes guardados en 'alumno-1': {len(grafo.get_state(config).values['messages'])}")
    print(f"Mensajes guardados en 'alumno-2': {len(grafo.get_state(config).values['messages'])}")
