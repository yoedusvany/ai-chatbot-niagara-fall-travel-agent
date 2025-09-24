# Chatbot de Agente de Viajes para las Cataratas del Niágara

Este proyecto es un chatbot impulsado por IA diseñado para actuar como un agente de viajes experto en las Cataratas del Niágara. Utiliza un pipeline de Generación Aumentada por Recuperación (RAG) para responder preguntas de los usuarios basándose en una base de conocimientos extraída de una guía de viaje.

## Características

- **Dominio Específico:** Entrenado con información detallada sobre atracciones, precios, horarios y consejos para visitar las Cataratas del Niágara.
- **Generación Aumentada por Recuperación (RAG):** Utiliza una base de datos vectorial para encontrar la información más relevante y la proporciona a un Modelo de Lenguaje Grande (LLM) para generar respuestas precisas.
- **Modelo de Lenguaje:** Impulsado por la API de Gemini de Google (`gemini-1.5-flash-latest`).
- **Embeddings Locales:** Usa `HuggingFaceEmbeddings` con el modelo `sentence-transformers/all-MiniLM-L6-v2` para generar embeddings localmente, sin coste ni cuotas de API.
- **Base de Datos Vectorial:** Utiliza **MongoDB Atlas** para un almacenamiento y recuperación eficiente de vectores en la nube.
- **Prompt Engineering:** El chatbot adopta la personalidad de un "amigable y servicial agente de viajes" para ofrecer una experiencia de usuario agradable.
- **Interfaz de Usuario:** Interacción a través de una sencilla aplicación de línea de comandos (CLI).

## ¿Cómo Funciona?

El chatbot sigue un proceso de RAG que se divide en dos etapas principales:

1.  **Fase de Indexación (una sola vez):**
    - Se ejecuta el script `src/setup_vector_store.py`.
    - Este script carga la guía de viaje, la divide en fragmentos (`chunks`), y genera embeddings para cada uno utilizando el modelo de Hugging Face.
    - Finalmente, almacena estos embeddings en la colección especificada de MongoDB Atlas.

2.  **Fase de Inferencia (en cada ejecución):**
    - Se ejecuta el script principal `src/chatbot.py`.
    - El chatbot se conecta a la base de datos vectorial de MongoDB Atlas ya existente.
    - Cuando un usuario hace una pregunta, el sistema busca los documentos más relevantes en la base de datos.
    - Estos documentos (el contexto) y la pregunta del usuario se envían al LLM (`gemini-1.5-flash-latest`), que genera una respuesta coherente y precisa.

## Instalación

Sigue estos pasos para configurar el entorno de desarrollo local.

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd ai-chatbot-niagara-fall-travel-agent
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura las variables de entorno:**
    - Renombra el archivo `.env.example` a `.env`.
    - Abre el archivo `.env` y añade tus credenciales:
      - `GOOGLE_API_KEY`: Tu clave de la API de Google Gemini. Puedes obtener una en [Google AI Studio](https://aistudio.google.com/app/apikey).
      - `MONGO_URI`: Tu cadena de conexión a MongoDB Atlas.
      - `DB_NAME`: El nombre de tu base de datos en Atlas.
      - `COLLECTION_NAME`: El nombre de la colección donde se guardarán los vectores.

## Uso

El proceso de ejecución se realiza en dos pasos:

1.  **Poblar la base de datos (solo la primera vez):**
    Ejecuta el siguiente comando para procesar tu documento y almacenar los embeddings en MongoDB Atlas. La primera vez, descargará el modelo de embeddings, lo cual puede tardar un momento.
    ```bash
    python3 src/setup_vector_store.py
    ```

2.  **Iniciar el chatbot:**
    Una vez que la base de datos esté poblada, puedes iniciar el chatbot en cualquier momento con este comando:
    ```bash
    python3 src/chatbot.py
    ```

Una vez iniciado, puedes hacerle preguntas sobre las Cataratas del Niágara. Para salir, escribe `salir`.

**Ejemplos de preguntas:**
- `¿Qué miradores gratuitos hay?`
- `¿Cuánto cuesta el paseo en barco?`
- `¿Cuál es la mejor época para visitar?`

