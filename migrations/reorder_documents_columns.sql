-- Reorder documents table columns: move content after title

BEGIN;

-- Create new table with desired column order
CREATE TABLE documents_new (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    title TEXT,
    content TEXT,
    source TEXT,
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Copy data from old table
INSERT INTO documents_new (id, client_id, title, content, source, chunk_count, created_at)
SELECT id, client_id, title, content, source, chunk_count, created_at
FROM documents;

-- Drop old table (CASCADE will drop dependent foreign keys)
DROP TABLE documents CASCADE;

-- Rename new table
ALTER TABLE documents_new RENAME TO documents;

-- Recreate indexes
CREATE INDEX idx_documents_client_id ON documents(client_id);
CREATE INDEX idx_documents_created_at ON documents(created_at);

-- Recreate foreign key constraint from document_chunks
ALTER TABLE document_chunks 
ADD CONSTRAINT document_chunks_document_id_fkey 
FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE;

COMMIT;
