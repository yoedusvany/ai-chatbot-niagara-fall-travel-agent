# Chatbot de Agente de Viajes para las Cataratas del Niágara

Este proyecto es un chatbot impulsado por IA diseñado para actuar como un agente de viajes experto en las Cataratas del Niágara. Utiliza un pipeline de Generación Aumentada por Recuperación (RAG) para responder preguntas de los usuarios basándose en una base de conocimientos extraída de una guía de viaje.

## Características

- **Dominio Específico:** Entrenado con información detallada sobre atracciones, precios, horarios y consejos para visitar las Cataratas del Niágara.
- **Generación Aumentada por Recuperación (RAG):** Utiliza una base de datos vectorial para encontrar la información más relevante y la proporciona a un Modelo de Lenguaje Grande (LLM) para generar respuestas precisas y contextualizadas.
- **Modelo de Lenguaje:** Impulsado por la API de Gemini de Google (`gemini-pro`).
- **Embeddings:** Usa `models/embedding-001` de Google para la generación de embeddings.
- **Base de Datos Vectorial:** Implementado con FAISS para un almacenamiento y recuperación eficiente de vectores en memoria.
- **Prompt Engineering:** El chatbot adopta la personalidad de un "amigable y servicial agente de viajes" para ofrecer una experiencia de usuario agradable.
- **Interfaz de Usuario:** Interacción a través de una sencilla aplicación de línea de comandos (CLI).

## ¿Cómo Funciona?

El chatbot sigue un proceso de RAG para responder a las preguntas:

1.  **Carga de Datos:** Lee un documento de texto (`.txt`) que contiene la guía de viaje de las Cataratas del Niágara.
2.  **Chunking:** Divide el documento en fragmentos de texto más pequeños para facilitar el procesamiento.
3.  **Embeddings y Almacenamiento:** Cada fragmento se convierte en un vector numérico (embedding) y se almacena en un índice de FAISS. Este índice se guarda localmente para evitar tener que regenerarlo en cada ejecución.
4.  **Recuperación:** Cuando un usuario hace una pregunta, el chatbot convierte la pregunta en un embedding y busca en el índice de FAISS los fragmentos de texto más similares semánticamente.
5.  **Generación:** Los fragmentos recuperados (el contexto) y la pregunta original del usuario se envían al LLM (Gemini) a través de un prompt diseñado específicamente. El modelo utiliza esta información para generar una respuesta coherente y precisa.

## Instalación

Sigue estos pasos para configurar el entorno de desarrollo local.

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd ai-chatbot-niagara-fall-travel-agent
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura tu clave de API:**
    - Renombra el archivo `.env.example` a `.env`.
    - Abre el archivo `.env` y reemplaza `"YOUR_API_KEY_HERE"` con tu clave de la API de Google Gemini. Puedes obtener una en [Google AI Studio](https://aistudio.google.com/app/apikey).

## Uso

Para iniciar el chatbot, ejecuta el siguiente comando desde el directorio raíz del proyecto:

```bash
python src/chatbot.py
```

La primera vez que lo ejecutes, creará y guardará el índice FAISS. Las siguientes veces, lo cargará desde el disco, haciendo el inicio más rápido.

Una vez iniciado, puedes hacerle preguntas sobre las Cataratas del Niágara. Para salir, escribe `salir`.

**Ejemplos de preguntas:**
- `¿Qué puedo hacer en las cataratas del Niágara?`
- `¿Cuánto cuesta el paseo en barco?`
- `¿Cuál es la mejor época para visitar?`
- `¿Cómo llego desde Toronto?`

