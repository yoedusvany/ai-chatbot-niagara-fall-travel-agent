# Documento de Reflexión: Chatbot de Agente de Viajes

Este documento detalla el proceso de diseño, implementación y evaluación del chatbot de agente de viajes para las Cataratas del Niágara.

## 1. ¿Qué desafíos enfrentaste construyendo el chatbot?

Durante el desarrollo del chatbot, me encontré con varios desafíos técnicos significativos que requirieron un proceso de depuración iterativo:

1.  **Agotamiento de la Cuota de la API de Google (Error `ResourceExhausted`):**
    - **Problema:** El script inicial intentaba generar embeddings en cada ejecución, lo que agotó rápidamente la cuota del nivel gratuito de la API de Google AI para el modelo de embeddings.
    - **Solución:** El primer paso fue separar la lógica de indexación (creación de embeddings) en un script `setup_vector_store.py` para que se ejecutara una sola vez. Sin embargo, la cuota ya estaba agotada. La solución definitiva fue **reemplazar los embeddings de Google por un modelo de código abierto** (`sentence-transformers/all-MiniLM-L6-v2`) a través de la clase `HuggingFaceEmbeddings`. Esto eliminó la dependencia de la API de Google para esta tarea, resolviendo por completo el problema de la cuota y haciendo el sistema más robusto.

2.  **Modelo de Lenguaje no Encontrado (Error `NotFound`):**
    - **Problema:** Después de solucionar el problema de los embeddings, el chatbot fallaba al generar respuestas con un error 404, indicando que el modelo `gemini-pro` (y luego `gemini-1.0-pro`) no se encontraba para la versión `v1beta` de la API.
    - **Solución:** Identifiqué que el problema probablemente se debía al uso de funciones obsoletas de LangChain (`load_qa_chain`) que podrían estar llamando a una versión antigua de la API. La solución fue **refactorizar todo el pipeline de RAG para usar la sintaxis moderna de LangChain (LCEL)**, utilizando `create_stuff_documents_chain` y `create_retrieval_chain`. Como parte de esta modernización, también actualicé el nombre del modelo a `gemini-1.5-flash-latest`, una versión más reciente y estable.

3.  **Error de Variable en el Prompt (Error `KeyError`):**
    - **Problema:** La nueva cadena LCEL esperaba que la pregunta del usuario se pasara con la clave `input`, pero mi plantilla de prompt todavía usaba `{question}`.
    - **Solución:** Fue un ajuste sencillo pero crucial: actualicé la plantilla del prompt para que usara `{input}` en lugar de `{question}`, sincronizando así la entrada de la cadena con las expectativas de la plantilla.

## 2. ¿Cómo Funciona el Chatbot?

El chatbot opera sobre un pipeline de Generación Aumentada por Recuperación (RAG) modernizado. El flujo de trabajo se divide en dos fases:

1.  **Fase de Indexación (ejecutada una sola vez con `setup_vector_store.py`):**
    - Un script de configuración carga el contenido de la guía de viaje desde un archivo de texto.
    - El texto se divide en fragmentos (`chunks`) utilizando `RecursiveCharacterTextSplitter`.
    - Cada fragmento es procesado por el modelo de embeddings de código abierto **`sentence-transformers/all-MiniLM-L6-v2`** a través de `HuggingFaceEmbeddings`. Este proceso se ejecuta localmente, sin consumir cuotas de API.
    - Los vectores resultantes se almacenan en una colección de **MongoDB Atlas**, que actúa como nuestra base de datos vectorial.

2.  **Fase de Inferencia (ejecutada por `chatbot.py` para cada pregunta):**
    - El script principal se conecta a la base de datos de MongoDB Atlas ya poblada.
    - La pregunta del usuario se pasa a una cadena de LangChain (LCEL).
    - La cadena primero convierte la pregunta en un vector (usando el mismo modelo de Hugging Face) y busca en MongoDB Atlas los 3 fragmentos de texto más relevantes.
    - Estos fragmentos (el `contexto`) y la pregunta del usuario (el `input`) se insertan automáticamente en una plantilla de prompt.
    - El prompt completo se envía al modelo **`gemini-1.5-flash-latest`**, que genera una respuesta en lenguaje natural basada en el contexto proporcionado.

## 3. Aplicación de Conceptos Clave

- **Chunking:** Utilicé `RecursiveCharacterTextSplitter` de LangChain. Esta estrategia es efectiva porque intenta dividir el texto en separadores semánticos (como párrafos y saltos de línea) antes de recurrir a divisiones por caracteres, lo que ayuda a mantener la coherencia de los fragmentos.

- **Embeddings:** Se optó por **`HuggingFaceEmbeddings`** con el modelo `sentence-transformers/all-MiniLM-L6-v2`. Esta fue una decisión estratégica clave para evitar las limitaciones de la API de Google. El modelo se ejecuta localmente, es rápido y ofrece una excelente calidad para tareas de búsqueda semántica, sin coste ni cuotas.

- **RAG:** La arquitectura RAG fue implementada utilizando las herramientas modernas de LangChain (LCEL) con `create_retrieval_chain`. Esta cadena abstrae de forma elegante el proceso de: 1) tomar la pregunta del usuario, 2) recuperar documentos relevantes del `retriever` (nuestro vector store de MongoDB), y 3) pasar todo al `document_chain` para la generación final de la respuesta.

- **Prompt Engineering:** El diseño del prompt fue clave para guiar el comportamiento del modelo. Se utilizó un rol explícito ("Eres un amigable y servicial agente de viajes...") y se le dieron instrucciones claras sobre qué hacer si no encontraba la respuesta en el contexto. Esto mejora la fiabilidad y la experiencia del usuario.

## 4. Ejemplo con Diferentes Temperaturas

El parámetro `temperature` en el modelo `ChatGoogleGenerativeAI` controla la creatividad de las respuestas. Un valor bajo produce respuestas más predecibles, mientras que un valor alto genera respuestas más variadas.

**Pregunta:** `¿Qué se puede hacer en el lado canadiense?`

- **`temperature=0.1` (Baja creatividad):**
  > *Respuesta esperada:* "En el lado canadiense, puedes visitar la Torre Skylon para obtener vistas panorámicas, disfrutar de las atracciones en Clifton Hill y tomar el crucero Hornblower Niagara para acercarte a las cataratas."
  > *(La respuesta es muy directa y se ciñe estrictamente a los hechos del texto.)*

- **`temperature=0.9` (Alta creatividad):**
  > *Respuesta esperada:* "¡El lado canadiense es una maravilla! Imagínate subir a la majestuosa Torre Skylon para sentir que tocas el cielo y contemplar las cataratas desde arriba. Después, podrías sumergirte en la vibrante energía de Clifton Hill, que es como un parque de diversiones gigante. Y para una experiencia realmente inolvidable, ¡no te puedes perder el paseo en barco de Hornblower que te lleva justo al corazón rugiente de las cataratas!"
  > *(La respuesta es más entusiasta, usa un lenguaje más descriptivo y añade un toque de emoción, aunque la información de fondo es la misma.)*

**Pregunta:** `¿Qué es lo más emocionante que puedo hacer?`

- **Temperatura = 0.3 (usada en el chatbot):**
  > *"Para una experiencia emocionante, te recomiendo la lancha rápida por el río Niágara, donde atravesarás los rápidos a toda velocidad. También puedes probar la tirolina para sobrevolar las cataratas a 670 metros de altura. Ambas son actividades muy populares para los aventureros."*
  > *(Respuesta directa, basada en los hechos del texto.)*

- **Temperatura = 0.9 (más creativa):**
  > *"¡Prepárate para la aventura! Si buscas adrenalina pura, imagínate surcando los furiosos rápidos del río Niágara en una lancha a motor, sintiendo la fuerza del agua a tu alrededor. O quizás prefieras volar como un pájaro sobre el majestuoso abismo de las cataratas en una tirolina que te dejará sin aliento. ¡Cualquiera de las dos será una historia increíble que contar!"*
  *(Respuesta más evocadora y con un lenguaje más florido, aunque basada en la misma información.)*

## 5. Efectividad del Prompt Engineering

*(Expande sobre cómo el prompt ayudó a modelar el comportamiento del chatbot.)*

El prompt engineering fue efectivo en varios aspectos:

1.  **Definición de la Persona:** Al establecer el rol de "agente de viajes amigable", el tono de las respuestas se volvió consistentemente servicial y positivo.
2.  **Restricción al Contexto:** La instrucción de basar las respuestas únicamente en el texto proporcionado fue crucial para evitar que el modelo inventara información o respondiera con su conocimiento general, lo que aumenta la fiabilidad del chatbot.
3.  **Manejo de Incertidumbre:** La instrucción explícita sobre qué decir cuando la respuesta no está en el contexto (`'Lo siento, no tengo información sobre eso...'`) proporciona una salida elegante y honesta, gestionando las expectativas del usuario.

## 6. Mejoras Futuras

*(Piensa en qué harías si tuvieras más tiempo o recursos.)*

- **Ampliar la Base de Conocimientos:** Integrar más guías de viaje, folletos o incluso conectar una API de eventos en tiempo real para ofrecer información sobre actividades especiales o cierres temporales.
- **Implementar Memoria de Conversación:** Añadir la capacidad de recordar preguntas anteriores en la misma conversación para permitir un diálogo más fluido y contextual (por ejemplo, si pregunto `"¿Y cuánto cuesta?"` después de preguntar por el barco).
- **Interfaz Gráfica Web:** Desarrollar una interfaz web con React o Angular para hacer el chatbot más accesible y visualmente atractivo.
- **Comportamiento Agente (Bonus):** Implementar una herramienta de búsqueda web (usando un agente de LangChain) para que, si la información no está en la base de conocimientos, el chatbot pueda buscarla en internet en tiempo real.
