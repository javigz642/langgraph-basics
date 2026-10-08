"""Solucion del Ejercicio 1 · Un grafo que clasifica y responde (pregunta / queja)."""
from pathlib import Path
from typing import Literal, TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

modelo = ChatOllama(model="llama3.1", temperature=0)


# 1) STATE: el mensaje, su tipo y la respuesta final
class State(TypedDict):
    mensaje: str
    tipo: str
    respuesta: str


# 2) NODO CLASIFICADOR: el modelo etiqueta el mensaje
clasificar_chain = ChatPromptTemplate.from_template(
    "Clasifica el mensaje de un cliente como 'pregunta' o 'queja'. "
    "Responde SOLO con una de esas dos palabras.\n\nMensaje: {mensaje}"
) | modelo | StrOutputParser()


def clasificar(state: State) -> dict:
    etiqueta = clasificar_chain.invoke({"mensaje": state["mensaje"]}).strip().lower()
    return {"tipo": "queja" if "queja" in etiqueta else "pregunta"}


# 3) DOS NODOS DE RESPUESTA, cada uno con su tono
def responder_pregunta(state: State) -> dict:
    r = modelo.invoke(f"Eres el soporte de una tienda online. Responde a esta pregunta en una frase, "
                      f"en español y con tono informativo: {state['mensaje']}")
    return {"respuesta": r.content}


def responder_queja(state: State) -> dict:
    r = modelo.invoke(f"Eres el soporte de una tienda online. Responde a esta queja en una o dos frases, "
                      f"en español: pide disculpas y ofrece una solución concreta: {state['mensaje']}")
    return {"respuesta": r.content}


# 4) ARISTA CONDICIONAL: segun el tipo, a un nodo u otro
def enrutar(state: State) -> Literal["responder_pregunta", "responder_queja"]:
    return "responder_queja" if state["tipo"] == "queja" else "responder_pregunta"


builder = StateGraph(State)
builder.add_node("clasificar", clasificar)
builder.add_node("responder_pregunta", responder_pregunta)
builder.add_node("responder_queja", responder_queja)
builder.add_edge(START, "clasificar")
builder.add_conditional_edges("clasificar", enrutar)
builder.add_edge("responder_pregunta", END)
builder.add_edge("responder_queja", END)
grafo = builder.compile()

if __name__ == "__main__":
    for mensaje in ["¿Hacéis envíos a Portugal?",
                    "Mi pedido llegó roto y nadie me contesta los correos."]:
        final = grafo.invoke({"mensaje": mensaje})
        print(f"Mensaje  : {mensaje}")
        print(f"Tipo     : {final['tipo']}  ->  rama responder_{final['tipo']}")
        print(f"Respuesta: {final['respuesta']}\n")

    # Diagrama del grafo (parte del entregable)
    png = grafo.get_graph().draw_mermaid_png(max_retries=5, retry_delay=2.0)
    with open(Path(__file__).with_name("grafo_clasificador.png"), "wb") as f:
        f.write(png)
    print("Diagrama guardado en grafo_clasificador.png")
