"""Variacion paso 1 · stream: ver el state despues de cada nodo, paso a paso."""
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
grafo = importlib.import_module("01_grafo_simple").grafo

# stream_mode="updates": en cada paso, que nodo se ha ejecutado y que ha cambiado
for i, paso in enumerate(grafo.stream({"texto": "hola langgraph"}, stream_mode="updates"), 1):
    for nodo, cambio in paso.items():
        print(f"Paso {i} · nodo '{nodo}' devuelve -> {cambio}")
