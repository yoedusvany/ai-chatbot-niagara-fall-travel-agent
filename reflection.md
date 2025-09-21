# Documento de Reflexión: Chatbot de Agente de Viajes

Este documento detalla el proceso de diseño, implementación y evaluación del chatbot de agente de viajes para las Cataratas del Niágara.

## 1. Desafíos Enfrentados

*(Aquí puedes describir los obstáculos que encontraste. Por ejemplo:)*

- **Recopilación de Datos:** Encontrar una fuente de datos única, completa y estructurada fue un desafío inicial. La información en la web a menudo está fragmentada, por lo que fue necesario consolidar y limpiar el contenido de una guía de viaje para crear una base de conocimientos coherente.
- **Configuración del Entorno:** Asegurarse de que todas las dependencias, especialmente las relacionadas con `langchain` y `faiss-cpu`, fueran compatibles y se instalaran correctamente requirió algo de depuración.
- **Optimización del Prompt:** Lograr que el chatbot respondiera de manera concisa y se adhiriera a su persona de "agente de viajes" sin inventar información requirió varias iteraciones en el diseño del prompt.

## 2. ¿Cómo Funciona el Chatbot?

*(Explica la arquitectura general del chatbot. Puedes reutilizar parte de la explicación del README, pero con más detalle técnico.)*

El chatbot opera sobre un pipeline de Generación Aumentada por Recuperación (RAG). El flujo de trabajo es el siguiente:

1.  **Fase de Indexación (se ejecuta una sola vez):**
    - El sistema carga el contenido de la guía de viaje desde un archivo de texto.
    - El texto se divide en fragmentos (`chunks`) de aproximadamente 1000 caracteres, con una superposición de 200 caracteres para mantener el contexto entre ellos.
    - Cada fragmento es procesado por el modelo de embeddings `models/embedding-001` de Google para generar un vector numérico.
    - Estos vectores se almacenan en un índice de FAISS, que se guarda en el disco para un acceso rápido en futuras ejecuciones.

2.  **Fase de Inferencia (se ejecuta para cada pregunta):**
    - La pregunta del usuario se convierte en un vector utilizando el mismo modelo de embeddings.
    - Se realiza una búsqueda de similitud en el índice FAISS para encontrar los 3 fragmentos de texto más relevantes para la pregunta.
    - Estos fragmentos, junto con la pregunta original, se insertan en una plantilla de prompt.
    - El prompt completo se envía al modelo `gemini-pro`, que genera una respuesta en lenguaje natural basada en el contexto proporcionado.

## 3. Aplicación de Conceptos Clave

*(Detalla cómo usaste cada una de las tecnologías requeridas.)*

- **Chunking:** Utilicé `RecursiveCharacterTextSplitter` de LangChain. Esta estrategia es efectiva porque intenta dividir el texto en separadores semánticos (como párrafos y saltos de línea) antes de recurrir a divisiones por caracteres, lo que ayuda a mantener la coherencia de los fragmentos.

- **Embeddings:** Se empleó el modelo `models/embedding-001` de Google a través de `GoogleGenerativeAIEmbeddings` de LangChain. Este modelo es eficiente y está optimizado para funcionar con el ecosistema de Gemini, garantizando una buena calidad en la representación semántica del texto.

- **RAG:** La arquitectura RAG fue fundamental. En lugar de reentrenar un modelo, lo que sería costoso y complejo, RAG nos permite "aumentar" el conocimiento de un LLM existente con información específica y actualizada de nuestro dominio. Esto hace que el chatbot sea preciso y evita que alucine respuestas.

- **Prompt Engineering:** El diseño del prompt fue clave para guiar el comportamiento del modelo. Se utilizó un rol explícito ("Eres un amigable y servicial agente de viajes...") y se le dieron instrucciones claras sobre qué hacer si no encontraba la respuesta en el contexto. Esto mejora la fiabilidad y la experiencia del usuario.

## 4. Ejemplo con Diferentes Temperaturas

*(Aquí puedes mostrar cómo cambia la respuesta del chatbot al ajustar el parámetro `temperature` en el modelo `ChatGoogleGenerativeAI`.)*

El parámetro `temperature` controla la creatividad o aleatoriedad de las respuestas del modelo. Un valor bajo produce respuestas más deterministas y predecibles, mientras que un valor alto genera respuestas más variadas y creativas.

**Pregunta:** `¿Qué es lo más emocionante que puedo hacer?`

- **Temperatura = 0.3 (usada en el chatbot):**
  > *"Para una experiencia emocionante, te recomiendo la lancha rápida por el río Niágara, donde atravesarás los rápidos a toda velocidad. También puedes probar la tirolina para sobrevolar las cataratas a 670 metros de altura. Ambas son actividades muy populares para los aventureros."*
  *(Respuesta directa, basada en los hechos del texto.)*

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
