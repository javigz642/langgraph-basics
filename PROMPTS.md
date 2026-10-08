# Sesión 2 · LangGraph: state machines para agentes · Prompts para Claude Code

Estos son los prompts que usamos en la práctica, en el mismo orden que en clase. Cópialos y pégalos en Claude Code uno a uno.

**Cómo usarlos**
1. Pega el prompt del paso y deja que Claude Code proponga los cambios.
2. **Lee el código antes de aceptar** (y los comandos, como `pip install`, antes de permitirlos).
3. Ejecuta y compara con el apartado *Qué deberías ver*.
4. Si no sale lo esperado, vuelve a pedírselo con lo que has aprendido.

> Antes de empezar: el entorno de la Sesión 1 (Ollama con `llama3.1`). Lo único nuevo es `pip install langgraph`. Abre Claude Code en una carpeta vacía.

El resultado de referencia, con todo el código comentado, está en la carpeta `langgraph-basics` del material de la sesión.

---

## Paso 1 · Grafo simple

**Qué construye**

- State minimo: un TypedDict con un campo
- Dos nodos que transforman el state
- START -> nodos -> END y compilar
- Invocar y dibujar el grafo

**Prompt**

```text
Crea un proyecto Python nuevo llamado langgraph-basics con entorno virtual e instala langgraph, langchain-core y langchain-ollama. Define un StateGraph con un State (TypedDict con un campo) y uno o dos nodos que lean y modifiquen el state. Conecta START y END, compila el grafo e invocalo con un ejemplo. Dibuja el grafo con draw_mermaid_png y guardalo como imagen.
```

**Qué deberías ver**

Cada nodo transforma el state y pasa el testigo: 'hola langgraph' sale como 'HOLA LANGGRAPH!!!'.

### Variación en vivo: el grafo paso a paso

```text
Ejecuta el grafo con stream en modo updates y muestra que devuelve cada nodo en cada paso.
```

**Qué demuestra**

Stream ensena el grafo por dentro: primero actua mayusculas y luego exclamar, y cada uno devuelve solo la clave que cambia.

---

## Paso 2 · Evolucionar a chatbot

**Qué construye**

- State con una lista de mensajes (add_messages)
- Un nodo que llama a ChatOllama
- START -> chatbot -> END
- Un turno de conversacion

**Prompt**

```text
Evoluciona el grafo a un chatbot: cambia el State para que acumule una lista de mensajes con add_messages, crea un nodo que llame a ChatOllama(llama3.1) y devuelva su respuesta, conectalo entre START y END. Invoca el grafo con un mensaje del usuario y muestra la respuesta.
```

**Qué deberías ver**

El grafo funciona... y el modelo se inventa que es LangGraph. No lo conoce y responde con total seguridad.

### Variación en vivo: sin add_messages

```text
Crea dos grafos con dos nodos que responden seguidos: uno con add_messages en el State y otro sin el. Muestra los mensajes finales de cada uno.
```

**Qué demuestra**

Sin reducer, cada nodo sustituye la lista: queda 1 mensaje. Con add_messages se acumulan los 3. Una linea en el State decide si hay historial.

---

## Paso 3 · Añadir memoria

**Qué construye**

- Compilar con un checkpointer MemorySaver
- Un thread_id por conversacion
- 3 turnos: recuerda nombre y contexto
- Control: otro thread_id empieza de cero

**Prompt**

```text
Anade memoria al chatbot: compila el grafo con un checkpointer MemorySaver y pasa un thread_id en la config. Demuestra en 3 turnos, usando el mismo thread_id, que el grafo recuerda lo que dije antes (por ejemplo mi nombre), y que otro thread_id no comparte memoria.
```

**Qué deberías ver**

Mismo resultado que en la sesion 1, pero sin aviso amarillo: esta es la forma actual de dar memoria.

### Variación en vivo: una foto en cada paso

```text
Tras 2 turnos, recorre get_state_history del thread y muestra cada checkpoint: step, origen, numero de mensajes y siguiente nodo.
```

**Qué demuestra**

2 turnos = 6 checkpoints. Se guarda una foto del state antes y despues de cada nodo: por eso se puede reanudar si algo se cae.

---

## Paso 4 · Añadir herramientas

**Qué construye**

- Tool consulta_pedido con @tool
- ToolNode: el nodo que ejecuta tools
- Arista condicional: tool o respuesta
- Vuelta de tools al modelo: el ciclo

**Prompt**

```text
Anade herramientas: define una tool consulta_pedido con @tool que consulte el estado de un pedido en un diccionario de ejemplo, crea un nodo de herramientas (ToolNode) y una arista condicional que, si el modelo pide usar una tool, dirija al nodo tool y luego vuelva al modelo. Haz una pregunta que obligue a usar la tool y muestra el ciclo en el log.
```

**Qué deberías ver**

En el turno 2 no se dice el numero de pedido: lo saca de la memoria. Tools y checkpointer trabajando juntos.

### Variación en vivo: la arista decide

```text
Con el mismo grafo, lanza una pregunta que no necesite tool y otra sobre el pedido 5678, y compara el camino que sigue cada una.
```

**Qué demuestra**

Sin pedido: chatbot y fin. Con pedido: chatbot, tools, chatbot. El mismo grafo toma caminos distintos segun lo que decide el modelo.

---

## Paso 5 · Cierre y material

**Qué construye**

- Dibujar el grafo final con draw_mermaid_png
- Comentarios didacticos en el codigo
- README: State, nodos, aristas y checkpointer
- Repo listo para compartir

**Prompt**

```text
Genera la visualizacion final del grafo completo con draw_mermaid_png, anade comentarios didacticos a todo el codigo y un README breve que explique State, nodos, aristas y checkpointer. Deja el proyecto limpio para compartirlo como material de clase.
```

**Qué deberías ver**

El diagrama final: las flechas punteadas son la arista condicional; la de tools a chatbot, el ciclo.

---

*Material del Master AI Engineer · The Power · Ignacio de Pastors*
