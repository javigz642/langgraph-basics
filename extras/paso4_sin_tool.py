"""Variacion paso 4 · la arista condicional decide: una pregunta que NO necesita tool."""
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
paso4 = importlib.import_module("04_herramientas")

config = {"configurable": {"thread_id": "cliente-7"}}
paso4.conversar("Hola, ¿con qué me puedes ayudar?", config)   # sin pedido -> chatbot -> END
paso4.conversar("¿Cómo va el pedido 5678?", config)           # con pedido -> chatbot -> tools -> chatbot
