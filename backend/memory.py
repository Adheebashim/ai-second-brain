import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import uuid
from dotenv import load_dotenv

load_dotenv()

# Initialize the sentence transformer model for embeddings
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY", ""))

index_name = "ai-second-brain"

# Check if index exists, if not, create it
# all-MiniLM-L6-v2 outputs 384 dimensions
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1' # Typical free tier region
        )
    )

index = pc.Index(index_name)

def save_memory(text: str) -> None:
    """
    Saves a text string into the vector database.
    """
    if not text or text.strip() == "":
        return
        
    # Generate embedding for the text
    embedding = model.encode(text).tolist()
    
    # Store in Pinecone with a unique ID and text as metadata
    memory_id = str(uuid.uuid4())
    index.upsert(
        vectors=[
            {
                "id": memory_id, 
                "values": embedding, 
                "metadata": {"text": text}
            }
        ]
    )

def retrieve_memories(query: str, n_results: int = 3) -> list[str]:
    """
    Retrieves the most relevant memories based on semantic similarity.
    """
    if not query or query.strip() == "":
        return []
        
    # Generate embedding for the query
    query_embedding = model.encode(query).tolist()
    
    # Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=n_results,
        include_metadata=True
    )
    
    # Extract documents from results metadata
    memories = []
    if results and 'matches' in results:
        for match in results['matches']:
            if 'metadata' in match and 'text' in match['metadata']:
                memories.append(match['metadata']['text'])
                
    return memories
