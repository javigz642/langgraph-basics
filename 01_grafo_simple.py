"""Paso 1 · Grafo simple: State + 2 nodos + edges. Sin LLM todavia."""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


# 1) STATE: la "mochila" que viaja por el grafo. Aqui, un solo campo
# TypedDict define la forma que tendrá un diccionairio "este diccionario tiene una clave texto
# y su valor es un string"
class State(TypedDict):
    texto: str


# 2) NODOS: funciones que leen el state y devuelven SOLO las claves que cambian
# El nodo NO modifica el state directamentte, solo devuelve lo que cambia
# LangGraph se encarga de mezclarlo con el state actual
def mayusculas(state: State) -> dict:
    return {"texto": state["texto"].upper()}


def exclamar(state: State) -> dict:
    return {"texto": state["texto"] + "!!!"}


# 3) EDGES: que va despues de que. START y END marcan la entrada y la salida
builder = StateGraph(State) # Creo un "constructor de grafos y le paso el tipo de state que va a circular"
builder.add_node("mayusculas", mayusculas) # registro las cajas con su (nombre, funcion_que_ejecuta)
builder.add_node("exclamar", exclamar)
builder.add_edge(START, "exclamar") # dibujo las flechas 
builder.add_edge("exclamar", "mayusculas")
builder.add_edge("mayusculas", END)

# 4) COMPILAR: el grafo compilado se ejecuta con invoke, igual que una cadena
# convierte el plano el algo ejecutable, comprueba que tenga sentido (builder: plano, grafo: maquina montada)
grafo = builder.compile()

if __name__ == "__main__":
    resultado = grafo.invoke({"texto": "hola langgraph"})
    print("ENTRADA :", {"texto": "hola langgraph"})
    print("SALIDA  :", resultado)
    # Dibujar el grafo: draw_mermaid() da el texto; draw_mermaid_png() la imagen (via mermaid.ink)
    png = grafo.get_graph().draw_mermaid_png(max_retries=5, retry_delay=2.0)
    with open("grafo_simple.png", "wb") as f:
        f.write(png)
    print("DIAGRAMA: guardado en grafo_simple.png")
