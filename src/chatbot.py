import os
from dotenv import load_dotenv
import google.generativeai as genai

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate
from pymongo import MongoClient
import certifi

DATA_PATH = "data/niagara_falls_travel_guide.txt"

def get_vector_store():
    """Carga un almacén de vectores existente desde MongoDB Atlas."""
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")
    collection_name = os.getenv("COLLECTION_NAME")

    if not all([mongo_uri, db_name, collection_name]):
        raise ValueError("Las variables de entorno de MongoDB no están configuradas correctamente.")

    # Usar certifi para resolver problemas de SSL en macOS
    ca = certifi.where()
    client = MongoClient(mongo_uri, tlsCAFile=ca)
    collection = client[db_name][collection_name]
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("Cargando almacén de vectores desde MongoDB Atlas.")
    vector_store = MongoDBAtlasVectorSearch(collection, embeddings)
    
    return vector_store

def get_conversational_chain(vector_store):
    """
    Crea y retorna una cadena de recuperación y conversación (RAG).
    """
    prompt_template = """
    Eres un amigable y servicial agente de viajes especializado en las Cataratas del Niágara.
    Tu objetivo es dar respuestas claras, concisas y útiles basadas en el contexto proporcionado.
    Si la respuesta no está en el contexto, di amablemente: 'Lo siento, no tengo información sobre eso. ¿Hay algo más en lo que pueda ayudarte sobre las Cataratas del Niágara?'.

    Contexto:
    {context}

    Pregunta:
    {input}

    Respuesta:
    """

    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "input"])
    
    # Cadena para procesar los documentos y la pregunta
    document_chain = create_stuff_documents_chain(model, prompt)
    
    # Cadena de recuperación que obtiene documentos y los pasa a la otra cadena
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    return retrieval_chain

def user_input(user_question, chain):
    """
    Procesa la pregunta del usuario usando la cadena de recuperación y devuelve la respuesta.
    """
    response = chain.invoke({"input": user_question})
    return response["answer"]

def main():
    """Función principal para configurar y ejecutar el chatbot."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No se encontró la GOOGLE_API_KEY en el archivo .env")
    genai.configure(api_key=api_key)

    vector_store = get_vector_store()
    chain = get_conversational_chain(vector_store)

    print("¡Hola! Soy tu agente de viajes para las Cataratas del Niágara. ¿En qué puedo ayudarte hoy?")
    print("Escribe 'salir' para terminar la conversación.")

    while True:
        question = input("Tú: ")
        if question.lower() == 'salir':
            print("¡Hasta luego! Espero que disfrutes tu viaje a las Cataratas del Niágara.")
            break
        
        answer = user_input(question, chain)
        print(f"Chatbot: {answer}")

if __name__ == "__main__":
    main()
