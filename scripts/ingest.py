"""
Document Embedding Script - Multi-tenant Version

Reads documents from PostgreSQL database and creates embeddings for each client.
Metadata stored in document_chunks table, vectors stored in ChromaDB with
separate collections per client.

Usage:
    python ingest.py                                        # Process all clients, all documents
    python ingest.py <client_id_or_name>                    # Process specific client, all documents
    python ingest.py <client_id_or_name> file.csv           # Process specific client, specific source file
    python ingest.py <client_id_or_name> --clean-reprocess YES_DELETE_ALL    # Clean reprocess for client
"""

import sys
import os
import uuid
import asyncio
import asyncpg
import requests
import chromadb
from dotenv import load_dotenv

load_dotenv()

# ---------------- CONFIG ----------------
DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": int(os.getenv("DATABASE_PORT", 5432)),
    "database": os.getenv("DATABASE_NAME", "acm_ai"),
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", "postgres"),
}

VECTOR_DB_DIR = "vectordb"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500  # Characters per chunk


# ---------------- HELPERS ----------------
def embed(text: str):
    """Generate embedding using Ollama"""
    try:
        r = requests.post(
            OLLAMA_EMBED_URL,
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["embedding"]
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        raise


def chunk_text(text: str, size: int = CHUNK_SIZE):
    """Split text into chunks"""
    return [text[i : i + size] for i in range(0, len(text), size)]


async def get_client_by_name_or_id(conn: asyncpg.Connection, identifier: str):
    """Get client by name or UUID"""
    # Try as UUID first
    try:
        client = await conn.fetchrow(
            "SELECT id, name, plan FROM clients WHERE id = $1",
            uuid.UUID(identifier)
        )
        if client:
            return client
    except ValueError:
        pass  # Not a valid UUID, try as name
    
    # Try as client name
    client = await conn.fetchrow(
        "SELECT id, name, plan FROM clients WHERE name = $1",
        identifier
    )
    return client


# ---------------- MAIN PROCESSING ----------------
async def process_client(client_id: str, conn: asyncpg.Connection, source_filter: str = None, clean_reprocess: bool = False):
    """
    Process all documents for a specific client:
    1. Fetch documents without chunks (or all if clean reprocess)
    2. Chunk the content
    3. Generate embeddings
    4. Store chunks in PostgreSQL
    5. Store vectors in ChromaDB (client-specific collection)
    
    Args:
        client_id: UUID of the client
        conn: Database connection
        source_filter: Optional source filename to filter (e.g., "faq.csv")
        clean_reprocess: If True, delete existing chunks/vectors and reprocess all
    """
    
    # Get client info (accepts UUID or name)
    client = await get_client_by_name_or_id(conn, client_id)
    
    if not client:
        print(f"❌ Client '{client_id}' not found")
        return
    
    print(f"\n{'='*60}")
    print(f"📦 Processing Client: {client['name']} (Plan: {client['plan']})")
    print(f"   Client ID: {client['id']}")
    if source_filter:
        print(f"  Source Filter: {source_filter}")
    if clean_reprocess:
        print(f"   ⚠️  CLEAN REPROCESS MODE")
    print(f"{'='*60}\n")
    
    # Initialize ChromaDB first
    chroma = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    collection_name = f"client_{str(client['id']).replace('-', '_')}"
    
    # Handle clean reprocess
    if clean_reprocess:
        print(f"🗑️  Deleting existing chunks and vectors...\n")
        
        # Delete from PostgreSQL
        await conn.execute(
            """
            DELETE FROM document_chunks 
            WHERE document_id IN (
                SELECT id FROM documents WHERE client_id = $1
            )
            """,
            client['id']
        )
        
        # Delete ChromaDB collection
        try:
            chroma.delete_collection(name=collection_name)
            print(f"   ✅ Deleted ChromaDB collection: {collection_name}")
        except Exception as e:
            print(f"   ℹ️  Collection didn't exist or error: {e}")
        
        # Delete persistent vectordb files for this client
        import shutil
        import sqlite3
        from pathlib import Path
        vectordb_path = Path(VECTOR_DB_DIR)
        
        # ChromaDB stores data in VECTOR_DB_DIR/chroma.sqlite3 and other files
        # Just deleting the collection is enough, but for complete cleanup:
        if vectordb_path.exists():
            # Check if there are any other active collections
            try:
                remaining_collections = chroma.list_collections()
                if not remaining_collections:
                    # No other collections, safe to clean entire vectordb
                    print(f"   ℹ️  No other collections found, cleaning entire vectordb directory...")
                    for item in vectordb_path.iterdir():
                        if item.is_file():
                            item.unlink()
                            print(f"   🗑️  Deleted: {item.name}")
                        elif item.is_dir():
                            shutil.rmtree(item)
                            print(f"   🗑️  Deleted directory: {item.name}")
                else:
                    print(f"   ℹ️  {len(remaining_collections)} other collection(s) exist, keeping vectordb structure")
                    # Optimize SQLite database to reclaim space
                    sqlite_path = vectordb_path / "chroma.sqlite3"
                    if sqlite_path.exists():
                        try:
                            conn_sqlite = sqlite3.connect(str(sqlite_path))
                            conn_sqlite.execute("VACUUM")
                            conn_sqlite.close()
                            print(f"   ✅ Optimized vectordb file (reclaimed deleted space)")
                        except Exception as vacuum_err:
                            print(f"   ⚠️  Could not vacuum database: {vacuum_err}")
            except Exception as e:
                print(f"   ⚠️  Could not clean vectordb files: {e}")
        
        print(f"   ✅ Deleted all chunks from PostgreSQL\n")
    
    # Build query based on clean_reprocess and source_filter
    if clean_reprocess:
        # For clean reprocess, get ALL documents (ignore existing chunks)
        if source_filter:
            documents = await conn.fetch(
                """
                SELECT d.id, d.title, d.source, d.content
                FROM documents d
                WHERE d.client_id = $1 AND d.source LIKE $2
               ORDER BY d.created_at
                """,
                client['id'],
                f"%{source_filter}%"
            )
        else:
            documents = await conn.fetch(
                """
                SELECT d.id, d.title, d.source, d.content
                FROM documents d
                WHERE d.client_id = $1
                ORDER BY d.created_at
                """,
                client['id']
            )
    else:
        # Normal mode: only get documents without chunks
        if source_filter:
            documents = await conn.fetch(
                """
                SELECT d.id, d.title, d.source, d.content
                FROM documents d
                LEFT JOIN document_chunks dc ON d.id = dc.document_id
                WHERE d.client_id = $1 AND d.source LIKE $2
                GROUP BY d.id, d.title, d.source, d.content
                HAVING COUNT(dc.id) = 0
                ORDER BY d.created_at
                """,
                client['id'],
                f"%{source_filter}%"
            )
        else:
            documents = await conn.fetch(
                """
                SELECT d.id, d.title, d.source, d.content
                FROM documents d
                LEFT JOIN document_chunks dc ON d.id = dc.document_id
                WHERE d.client_id = $1
                GROUP BY d.id, d.title, d.source, d.content
                HAVING COUNT(dc.id) = 0
                ORDER BY d.created_at
                """,
                client['id']
            )
    
    if not documents:
        print(f"ℹ️  No new documents to process for {client['name']}")
        return
    
    print(f"📄 Found {len(documents)} document(s) to process\n")
    
    # Get or create ChromaDB collection (already initialized earlier)
    collection = chroma.get_or_create_collection(
        name=collection_name,
        metadata={
            "hnsw:space": "cosine",
            "client_id": str(client['id']),
            "client_name": client['name'],
        },
    )
    
    print(f"🗂️  ChromaDB Collection: {collection_name}\n")
    
    total_chunks = 0
    
    # Process each document
    for doc in documents:
        doc_id = doc['id']
        print(f"  📄 Processing: {doc['title']}")
        
        # Get content from database or use fallback
        content = doc.get('content') or f"Document: {doc['title']}\nSource: {doc['source']}\n\n[No content available]"
        
        # Skip if content is empty
        if not content or len(content.strip()) < 10:
            print(f"     ⚠️  Skipped - No content")
            continue
        
        # Chunk the content
        chunks = chunk_text(content, CHUNK_SIZE)
        print(f"     → {len(chunks)} chunks")
        
        # Process each chunk
        chunk_rows = []
        vector_ids = []
        embeddings_list = []
        metadatas = []
        documents_list = []
        
        for idx, chunk_content in enumerate(chunks):
            chunk_id = uuid.uuid4()
            
            # Prepare for PostgreSQL
            chunk_rows.append({
                'id': chunk_id,
                'document_id': doc_id,
                'chunk_index': idx,
                'content': chunk_content,
            })
            
            # Generate embedding
            embedding = embed(chunk_content)
            
            # Prepare for ChromaDB
            vector_ids.append(str(chunk_id))
            embeddings_list.append(embedding)
            metadatas.append({
                "client_id": str(client['id']),
                "document_id": str(doc_id),
                "document_title": doc['title'],
                "chunk_index": idx,
            })
            documents_list.append(chunk_content)
        
        # Bulk insert chunks to PostgreSQL
        await conn.executemany(
            """
            INSERT INTO document_chunks (id, document_id, chunk_index, content)
            VALUES ($1, $2, $3, $4)
            """,
            [(str(row['id']), str(row['document_id']), row['chunk_index'], row['content']) 
             for row in chunk_rows]
        )
        
        # Add vectors to ChromaDB
        collection.add(
            ids=vector_ids,
            embeddings=embeddings_list,
            metadatas=metadatas,
            documents=documents_list,
        )
        
        total_chunks += len(chunks)
        print(f"     ✅ {len(chunks)} chunks embedded and stored")
    
    print(f"\n✅ Completed! Total chunks: {total_chunks}")
    print(f"   Vector Collection: {collection_name}")
    print(f"   Total Vectors: {collection.count()}\n")


async def main():
    """Main entry point"""
    
    # Parse arguments
    target_client_id = None
    target_source = None
    clean_reprocess = False
    
    if len(sys.argv) > 1:
        target_client_id = sys.argv[1]
        
        # Check for source file or clean-reprocess flag
        if len(sys.argv) > 2:
            if sys.argv[2] == "--clean-reprocess":
                # Validate safety confirmation
                if len(sys.argv) <= 3 or sys.argv[3] != "YES_DELETE_ALL":
                    print("❌ ERROR: Clean reprocess requires confirmation!")
                    print("   Usage: python ingest.py <client_id> --clean-reprocess YES_DELETE_ALL")
                    print("   ⚠️  WARNING: This will DELETE all chunks and vectors for this client!")
                    return
                clean_reprocess = True
            else:
                target_source = sys.argv[2]
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        if target_client_id:
            # Process specific client with optional source filter and/or clean reprocess
            await process_client(target_client_id, conn, target_source, clean_reprocess)
        else:
            # Process all clients
            clients = await conn.fetch(
                "SELECT id FROM clients WHERE status = 'active' ORDER BY created_at"
            )
            
            if not clients:
                print("❌ No active clients found in database")
                return
            
            print(f"🔄 Processing {len(clients)} active client(s)...\n")
            
            for client in clients:
                await process_client(str(client['id']), conn)
        
        print("=" * 60)
        print("🎉 Embedding process completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
