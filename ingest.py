import os
import uuid
import requests
import chromadb
import psycopg2
from psycopg2.extras import execute_values

# ---------------- CONFIG ----------------
CLIENT_ID = uuid.UUID("43010f4c-ebbd-4edf-b6c9-ea2805ab74a1")

DATA_DIR = "data"
VECTOR_DB_DIR = "vectordb"

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

PG_CONN = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="acm_ai",
    user="postgres",
    password="postgres",
)

# ---------------- HELPERS ----------------
def embed(text: str):
    r = requests.post(
        OLLAMA_EMBED_URL,
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["embedding"]


def chunk_text(text, size=500):
    return [text[i : i + size] for i in range(0, len(text), size)]


# ---------------- VECTOR DB ----------------
chroma = chromadb.PersistentClient(path=VECTOR_DB_DIR)
collection = chroma.get_or_create_collection(
    name="toko_abc",
    metadata={"hnsw:space": "cosine"},
)

# ---------------- INGESTION ----------------
cur = PG_CONN.cursor()

for fname in os.listdir(DATA_DIR):
    path = os.path.join(DATA_DIR, fname)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    document_id = uuid.uuid4()

    # 1. insert document
    cur.execute(
        """
        INSERT INTO documents (id, client_id, title, source, chunk_count)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            document_id,
            CLIENT_ID,
            fname,
            fname,
            len(chunks),
        ),
    )

    chunk_rows = []
    vector_ids = []
    embeddings = []
    metadatas = []

    for idx, chunk in enumerate(chunks):
        chunk_id = uuid.uuid4()

        chunk_rows.append(
            (
                chunk_id,
                document_id,
                idx,
                chunk,
            )
        )

        vector_ids.append(str(chunk_id))
        embeddings.append(embed(chunk))
        metadatas.append(
            {
                "client_id": str(CLIENT_ID),
                "document_id": str(document_id),
            }
        )

    # 2. bulk insert chunks
    execute_values(
        cur,
        """
        INSERT INTO document_chunks (id, document_id, chunk_index, content)
        VALUES %s
        """,
        chunk_rows,
    )

    # 3. commit SQL FIRST
    PG_CONN.commit()

    # 4. insert vectors
    collection.add(
        ids=vector_ids,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"{fname} → {len(chunks)} chunks ingested")

cur.close()
PG_CONN.close()

print("Ingestion selesai.")
print("Total vectors:", collection.count())
