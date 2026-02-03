"""
Chat Service

Handles RAG (Retrieval Augmented Generation), embeddings, and LLM calls.
"""

import requests
import chromadb
from backend.config import OLLAMA_URL, MODEL, VECTOR_DB_DIR

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=VECTOR_DB_DIR)

# Try to get or create default collection
try:
    collection = chroma_client.get_or_create_collection(name="default")
except Exception as e:
    print(f"Warning: Could not create default collection: {e}")
    collection = None


def embed(text: str) -> list:
    """Get embedding from Ollama using nomic-embed-text model"""
    r = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["embedding"]


def retrieve_context(query: str, client_id: str = None, k: int = 8) -> str:
    """
    Retrieve relevant context from vector DB using client-specific collection.
    
    Args:
        query: User's question
        client_id: Client UUID for client-specific collection
        k: Number of results to retrieve
        
    Returns:
        Context string joined from retrieved documents
    """
    try:
        q_emb = embed(query)
        
        # Use client-specific collection if client_id provided
        if client_id:
            collection_name = f"client_{client_id.replace('-', '_')}"
            try:
                client_collection = chroma_client.get_collection(name=collection_name)
                result = client_collection.query(
                    query_embeddings=[q_emb],
                    n_results=k,
                )
                # Debug: print retrieved context
                if result and result.get("documents"):
                    print(f"\n🔍 Context retrieved for query: '{query}'")
                    print(f"   Found {len(result['documents'][0])} documents")
                    for i, doc in enumerate(result['documents'][0][:3]):
                        print(f"   {i+1}. {doc[:100]}...")
                else:
                    print(f"\n⚠️  No context found for query: '{query}'")
            except Exception as e:
                # Collection doesn't exist yet, return empty
                print(f"\n❌ Collection error for {collection_name}: {e}")
                return ""
        else:
            # Fallback to default collection
            result = collection.query(
                query_embeddings=[q_emb],
                n_results=k,
            )
        
        docs_list = result.get("documents")
        if not docs_list:
            docs_list = [[]]
        first_docs = (
            docs_list[0] if isinstance(docs_list, list) and len(docs_list) > 0 else []
        )
        context = "\n\n".join(first_docs) if first_docs else ""
        print(f"   Context length: {len(context)} chars\n")
        return context
    except Exception as e:
        print(f"Context retrieval error: {e}")
        return ""


def call_ollama(prompt: str) -> str:
    """Call Ollama LLM with the given prompt"""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["response"]
