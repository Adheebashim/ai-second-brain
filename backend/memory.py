import os
from pinecone import Pinecone, ServerlessSpec
from groq import Groq
import uuid
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq for cloud-based embeddings
# This completely replaces local sentence-transformers and PyTorch,
# reducing RAM usage by 95% and avoiding Render free tier OOM crashes!
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY", ""))

index_name = "ai-second-brain"

def get_embedding(text: str) -> list[float]:
    """
    Generates a 768-dimension embedding using Groq's high-speed 'nomic-embed-text-v1.5' model.
    """
    if not text or not text.strip():
        return []
    try:
        response = groq_client.embeddings.create(
            model="nomic-embed-text-v1.5",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding via Groq: {e}")
        return []

# --- Pinecone Index Initialization ---
try:
    existing_indexes = pc.list_indexes().names()
    
    # If the index exists but has the old 384-dimension size from sentence-transformers,
    # delete it so it can be re-created with 768 dimensions for nomic-embed-text.
    if index_name in existing_indexes:
        desc = pc.describe_index(index_name)
        if desc.dimension != 768:
            print(f"Index {index_name} has old dimension {desc.dimension}. Re-creating with 768...")
            pc.delete_index(index_name)
            existing_indexes.remove(index_name)
            
    # Create the 768-dimension index if not present
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(
                cloud='aws', 
                region='us-east-1' # Standard free tier region
            )
        )
except Exception as e:
    print(f"Warning during Pinecone index setup check: {e}")

index = pc.Index(index_name)

def save_memory(text: str) -> None:
    """
    Generates cloud embeddings for the text and saves it into the Pinecone vector database.
    """
    if not text or not text.strip():
        return
        
    embedding = get_embedding(text)
    if not embedding:
        print("Skipping save: failed to generate vector embedding.")
        return
        
    memory_id = str(uuid.uuid4())
    try:
        index.upsert(
            vectors=[
                {
                    "id": memory_id, 
                    "values": embedding, 
                    "metadata": {"text": text}
                }
            ]
        )
    except Exception as e:
        print(f"Failed to upsert memory to Pinecone: {e}")

def retrieve_memories(query: str, n_results: int = 3) -> list[str]:
    """
    Retrieves the most relevant past memories based on semantic similarity.
    """
    if not query or not query.strip():
        return []
        
    query_embedding = get_embedding(query)
    if not query_embedding:
        return []
        
    try:
        results = index.query(
            vector=query_embedding,
            top_k=n_results,
            include_metadata=True
        )
        
        memories = []
        if results and 'matches' in results:
            for match in results['matches']:
                if 'metadata' in match and 'text' in match['metadata']:
                    memories.append(match['metadata']['text'])
                    
        return memories
    except Exception as e:
        print(f"Failed to query memories from Pinecone: {e}")
        return []
