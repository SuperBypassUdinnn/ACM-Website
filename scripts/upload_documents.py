"""
Document Upload Script - CSV to Database

Uploads CSV documents to PostgreSQL database based on folder structure.
Folder name must match client name in database.

Structure:
    data/
    ├── <Client Name>/
    │   ├── document1.csv
    │   ├── document2.csv
    │   └── ...

CSV Format:
    title,content,category
    "FAQ 1","Content here","faq"
    "FAQ 2","More content","faq"

Usage:
    python upload_documents.py                              # Upload all clients, all files
    python upload_documents.py "Client Name"                # Upload specific client, all files
    python upload_documents.py "Client Name" file.csv       # Upload specific client, specific file
    python upload_documents.py "Client Name" --clean-reprocess YES_DELETE_ALL    # Clean reprocess for client
"""

import sys
import os
import csv
import asyncio
import asyncpg
import uuid
from pathlib import Path
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

DATA_DIR = "data"


# ---------------- HELPERS ----------------
async def get_client_by_name(conn: asyncpg.Connection, client_name: str):
    """Find client by name in database"""
    client = await conn.fetchrow(
        "SELECT id, name, plan FROM clients WHERE name = $1",
        client_name
    )
    return client


async def upload_csv_document(conn: asyncpg.Connection, client_id: str, client_name: str, csv_path: str):
    """
    Upload documents from CSV file to database
    
    CSV Format:
        title,content,category (optional)
    """
    documents_added = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Check if required columns exist
        if 'title' not in reader.fieldnames or 'content' not in reader.fieldnames:
            print(f"  ⚠️  Skipping {csv_path}: Missing required columns (title, content)")
            return 0
        
        for row in reader:
            title = row.get('title', '').strip()
            content = row.get('content', '').strip()
            
            if not title or not content:
                continue
            
            # Create document
            doc_id = uuid.uuid4()
            
            # Format source as: foldername_filename
            # e.g., "Toko ABC (Test)_faq"
            filename = Path(csv_path).stem
            source_name = f"{client_name}_{filename}"
            
            # Content is ONLY the content, NOT including title
            # Title is stored in separate column
            
            # Insert document
            await conn.execute(
                """
                INSERT INTO documents (id, client_id, title, source, content)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO NOTHING
                """,
                str(doc_id),
                str(client_id),
                title,
                source_name,
                content  # Only content, no title duplication
            )
            
            documents_added += 1
    
    return documents_added


async def process_client_folder(conn: asyncpg.Connection, folder_path: str):
    """Process all CSV files in a client folder"""
    
    folder_name = Path(folder_path).name
    
    # Get client from database by folder name
    client = await get_client_by_name(conn, folder_name)
    
    if not client:
        print(f"\n⚠️  Client '{folder_name}' not found in database. Skipping...")
        print(f"   Register a user with company name: '{folder_name}' first.")
        return
    
    print(f"\n{'='*60}")
    print(f"📁 Processing: {folder_name}")
    print(f"   Client ID: {client['id']}")
    print(f"   Plan: {client['plan']}")
    print(f"{'='*60}\n")
    
    # Find all CSV files
    csv_files = list(Path(folder_path).glob("*.csv"))
    
    if not csv_files:
        print(f"  ℹ️  No CSV files found in {folder_path}")
        return
    
    print(f"📄 Found {len(csv_files)} CSV file(s)\n")
    
    total_docs = 0
    
    for csv_file in csv_files:
        print(f"  📄 Uploading: {csv_file.name}")
        docs_count = await upload_csv_document(conn, client['id'], folder_name, str(csv_file))
        print(f"     ✅ {docs_count} document(s) added")
        total_docs += docs_count
    
    print(f"\n✅ Total documents uploaded: {total_docs}\n")


async def main():
    """Main entry point"""
    
    # Parse arguments
    target_client = None
    target_file = None
    clean_reprocess = False
    
    if len(sys.argv) > 1:
        target_client = sys.argv[1]
        
        # Check for file_name or clean-reprocess flag
        if len(sys.argv) > 2:
            if sys.argv[2] == "--clean-reprocess":
                # Validate safety confirmation
                if len(sys.argv) <= 3 or sys.argv[3] != "YES_DELETE_ALL":
                    print("❌ ERROR: Clean reprocess requires confirmation!")
                    print("   Usage: python upload_documents.py \"Client Name\" --clean-reprocess YES_DELETE_ALL")
                    print("   ⚠️  WARNING: This will DELETE all documents and chunks for this client!")
                    return
                clean_reprocess = True
            else:
                target_file = sys.argv[2]
    
    if not Path(DATA_DIR).exists():
        print(f"❌ Data directory '{DATA_DIR}' not found")
        return
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        if target_client:
            folder_path = Path(DATA_DIR) / target_client
            if not folder_path.exists():
                print(f"❌ Folder '{folder_path}' not found")
                return
            
            # Get client first
            client = await get_client_by_name(conn, target_client)
            if not client:
                print(f"\n⚠️  Client '{target_client}' not found in database. Skipping...")
                return
            
            # Handle clean reprocess
            if clean_reprocess:
                print(f"\n{'='*60}")
                print(f"🗑️  CLEAN REPROCESS MODE")
                print(f"   Client: {target_client}")
                print(f"   This will DELETE all documents and chunks!")
                print(f"{'='*60}\n")
                
                # Delete all document chunks first (foreign key constraint)
                await conn.execute(
                    """
                    DELETE FROM document_chunks 
                    WHERE document_id IN (
                        SELECT id FROM documents WHERE client_id = $1
                    )
                    """,
                    client['id']
                )
                
                # Delete all documents
                result = await conn.execute(
                    "DELETE FROM documents WHERE client_id = $1",
                    client['id']
                )
                print(f"✅ Deleted all existing documents and chunks\n")
            
            # Process specific file or all files
            if target_file:
                csv_path = folder_path / target_file
                if not csv_path.exists():
                    print(f"❌ File '{csv_path}' not found")
                    return
                
                print(f"\n{'='*60}")
                print(f"📁 Processing: {target_client}")
                print(f"   Client ID: {client['id']}")
                print(f"   Plan: {client['plan']}")
                print(f"   File: {target_file}")
                print(f"{'='*60}\n")
                
                docs_count = await upload_csv_document(conn, client['id'], target_client, str(csv_path))
                print(f"\n✅ Total documents uploaded: {docs_count}\n")
            else:
                await process_client_folder(conn, str(folder_path))
        else:
            # Process all client folders
            client_folders = [f for f in Path(DATA_DIR).iterdir() if f.is_dir()]
            
            if not client_folders:
                print(f"❌ No client folders found in '{DATA_DIR}'")
                return
            
            print(f"🔄 Processing {len(client_folders)} client folder(s)...\n")
            
            for folder in client_folders:
                await process_client_folder(conn, str(folder))
        
        print("=" * 60)
        print("🎉 Upload completed!")
        print("=" * 60)
        print("\nNext step: Run embedding script")
        print("  python ingest.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
