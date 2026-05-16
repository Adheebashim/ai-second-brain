import chromadb
from sentence_transformers import SentenceTransformer
import uuid

# Initialize the sentence transformer model for embeddings
# This is a lightweight model perfect for semantic search
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Initialize local ChromaDB client
# This will create a "chroma_db" folder in the current directory to persist data
client = chromadb.PersistentClient(path="./chroma_db")

# Get or create a collection for our memories
collection = client.get_or_create_collection(name="memories")

def save_memory(text: str) -> None:
    """
    Saves a text string into the vector database.
    """
    if not text or text.strip() == "":
        return
        
    # Generate embedding for the text
    embedding = model.encode(text).tolist()
    
    # Store in ChromaDB with a unique ID
    memory_id = str(uuid.uuid4())
    collection.add(
        embeddings=[embedding],
        documents=[text],
        ids=[memory_id]
    )

def retrieve_memories(query: str, n_results: int = 3) -> list[str]:
    """
    Retrieves the most relevant memories based on semantic similarity.
    """
    if not query or query.strip() == "":
        return []
        
    # Generate embedding for the query
    query_embedding = model.encode(query).tolist()
    
    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    # Extract documents from results
    # results['documents'] is a list of lists: [['doc1', 'doc2']]
    if results and results.get('documents') and len(results['documents']) > 0:
        return results['documents'][0]
    
    return []
