"Ejercicio 2"
from typing import TypedDict, Annotated
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import START, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
import pandas as pd
from pathlib import Path


RUTA_DATOS = Path(__file__).resolve().parent.parent / "datos.csv"
df = pd.read_csv(RUTA_DATOS)
class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def informacion_trabajador(empleado:str):
    """Devuelve la informacion de las horas de determinado empleado"""
    filas_empleado = df[df["empleado"] == empleado]

    if filas_empleado.empty:
        return {"error": f"No existe el empleado {empleado}",
                "empleados_validos": df["empleado"].unique().tolist()}
    horas_totales = filas_empleado["horas"].sum()
    horas_facturables = filas_empleado[filas_empleado["facturable"] == "sí"]["horas"].sum()
    horas_no_facturables = filas_empleado[filas_empleado["facturable"] == "no"]["horas"].sum()
    horas_por_proyecto = filas_empleado.groupby("proyecto")["horas"].sum().to_dict()

    return {
        "empleado": empleado,
        "horas_totales" : horas_totales,
        "horas_facturables" : horas_facturables,
        "horas_no_facturables" : horas_no_facturables,
        "horas_por_proyecto" : horas_por_proyecto
    }

tools = [informacion_trabajador]

modelo = ChatOllama(model="llama3.1", temperature=0).bind_tools(tools)
SYSTEM = SystemMessage("Eres un asistente de proyectos. Responde en español. Usa la herramienta de " \
"informacion_trabajador para obtener la informacion de un trabajador")

def chatbot(state: State):
    return {"messages": [modelo.invoke([SYSTEM] + state["messages"])]}


builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")

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
    config = {"configurable": {"thread_id": "cliente1"}}
    conversar("Me llamo Javier, dime mi información de cuantas horas he trabajado en total", config)
    conversar("¿En que proyectos ha trabajado Lucía?", config)
    conversar("¿He trabajado más que Diego o no?", config)
    config2 = {"configurable": {"thread_id": "cliente2"}}
    conversar("¿Cuántas horas ha trabajado Sergio?", config2)
    conversar("¿Sabes como me llamo?", config2)

    png = grafo.get_graph().draw_mermaid_png(max_retries=5, retry_delay=2.0)
    with open("capturas/grafo_ejercicio2.png", "wb") as f:
        f.write(png)
    print("Guardado capturas/grafo_ejercicio2.png")




