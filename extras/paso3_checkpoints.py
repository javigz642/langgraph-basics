"""Variacion paso 3 · el checkpointer guarda una foto del state en CADA paso."""
import importlib
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
grafo = importlib.import_module("03_memoria").grafo

config = {"configurable": {"thread_id": "demo-checkpoints"}}
for texto in ["Hola, me llamo Ignacio.", "¿Cómo me llamo?"]:
    grafo.invoke({"messages": [HumanMessage(texto)]}, config=config)

historial = list(grafo.get_state_history(config))   # del mas reciente al mas antiguo
print(f"Checkpoints guardados en el thread: {len(historial)}\n")
for snap in reversed(historial):
    paso = snap.metadata.get("step")
    origen = snap.metadata.get("source")
    siguiente = snap.next[0] if snap.next else "FIN"
    n = len(snap.values.get("messages", []))
    print(f"  step {paso:>2} | {origen:<6} | mensajes: {n} | siguiente nodo: {siguiente}")
