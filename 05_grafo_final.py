"""Paso 5 · Cierre: dibujar el grafo final y guardarlo como PNG."""
import importlib

# Reutilizamos el grafo del paso 4 (el nombre empieza por numero, por eso importlib)
grafo = importlib.import_module("04_herramientas").grafo

# draw_mermaid_png usa por defecto el servicio web mermaid.ink para renderizar la imagen
png = grafo.get_graph().draw_mermaid_png(max_retries=5, retry_delay=2.0)  # reintenta si el servicio tarda
with open("grafo.png", "wb") as f:
    f.write(png)
print("Guardado grafo.png")
