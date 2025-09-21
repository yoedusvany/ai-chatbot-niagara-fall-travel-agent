import os
from dotenv import load_dotenv
import google.generativeai as genai

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from pymongo import MongoClient
import certifi

DATA_PATH = "data/niagara_falls_travel_guide.txt"

def get_vector_store():
    """Crea y carga el almacén de vectores desde MongoDB Atlas."""
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")
    collection_name = os.getenv("COLLECTION_NAME")

    if not all([mongo_uri, db_name, collection_name]):
        raise ValueError("Las variables de entorno de MongoDB no están configuradas correctamente.")

    # Usar certifi para resolver problemas de SSL en macOS
    ca = certifi.where()
    client = MongoClient(mongo_uri, tlsCAFile=ca)
    collection = client[db_name][collection_name]
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Comprobar si la colección ya tiene documentos (y, por tanto, un índice)
    if collection.count_documents({}) > 0:
        print("Cargando almacén de vectores desde MongoDB Atlas.")
        vector_store = MongoDBAtlasVectorSearch(collection, embeddings)
    else:
        print("Creando nuevo almacén de vectores en MongoDB Atlas.")
        # Cargar, dividir y almacenar los documentos si la colección está vacía
        loader = TextLoader(DATA_PATH)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        
        print(f"Creando embeddings para {len(texts)} fragmentos de texto. Esto puede tardar un momento y consumir cuota de la API...")
        vector_store = MongoDBAtlasVectorSearch.from_documents(
            documents=texts,
            embedding=embeddings,
            collection=collection,
            index_name="default" # Puedes nombrar tu índice vectorial aquí
        )
        print("Almacén de vectores creado y poblado en MongoDB Atlas.")
        
    return vector_store

def get_conversational_chain():
    """
    Crea y retorna una cadena de conversación para preguntas y respuestas.
    """
    prompt_template = """
    Eres un amigable y servicial agente de viajes especializado en las Cataratas del Niágara.
    Tu objetivo es dar respuestas claras, concisas y útiles basadas en el contexto proporcionado.
    Si la respuesta no está en el contexto, di amablemente: 'Lo siento, no tengo información sobre eso. ¿Hay algo más en lo que pueda ayudarte sobre las Cataratas del Niágara?'.

    Contexto:
    {context}

    Pregunta:
    {question}

    Respuesta:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question, vector_store, chain):
    """
    Procesa la pregunta del usuario, busca en el almacén de vectores y devuelve la respuesta.
    """
    docs = vector_store.similarity_search(user_question, k=3)
    response = chain(
        {"input_documents": docs, "question": user_question},
        return_only_outputs=True
    )
    return response["output_text"]

def main():
    """Función principal para configurar y ejecutar el chatbot."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No se encontró la GOOGLE_API_KEY en el archivo .env")
    genai.configure(api_key=api_key)

    vector_store = get_vector_store()
    chain = get_conversational_chain()

    print("¡Hola! Soy tu agente de viajes para las Cataratas del Niágara. ¿En qué puedo ayudarte hoy?")
    print("Escribe 'salir' para terminar la conversación.")

    while True:
        question = input("Tú: ")
        if question.lower() == 'salir':
            print("¡Hasta luego! Espero que disfrutes tu viaje a las Cataratas del Niágara.")
            break
        
        answer = user_input(question, vector_store, chain)
        print(f"Chatbot: {answer}")

if __name__ == "__main__":
    main()
