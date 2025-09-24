import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

DATA_PATH = "data/niagara_falls_travel_guide.txt"

def setup_vector_store():
    """Crea y puebla el almacén de vectores en MongoDB Atlas si no existe."""
    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")
    collection_name = os.getenv("COLLECTION_NAME")
    if not all([mongo_uri, db_name, collection_name]):
        raise ValueError("Las variables de entorno de MongoDB no están configuradas correctamente.")

    # Conectar a MongoDB
    ca = certifi.where()
    client = MongoClient(mongo_uri, tlsCAFile=ca)
    collection = client[db_name][collection_name]

    # Comprobar si la colección ya tiene documentos
    if collection.count_documents({}) > 0:
        print("El almacén de vectores ya existe y está poblado. No se requiere ninguna acción.")
        return

    print("Creando nuevo almacén de vectores en MongoDB Atlas.")
    
    # Cargar y dividir los documentos
    loader = TextLoader(DATA_PATH)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # Crear embeddings y poblar la base de datos
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    print(f"Creando embeddings para {len(texts)} fragmentos de texto. Esto puede tardar un momento...")
    MongoDBAtlasVectorSearch.from_documents(
        documents=texts,
        embedding=embeddings,
        collection=collection,
        index_name="default"
    )
    
    print("¡Almacén de vectores creado y poblado con éxito en MongoDB Atlas!")

if __name__ == "__main__":
    setup_vector_store()
