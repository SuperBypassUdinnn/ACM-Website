-- Add UNIQUE constraint to client name

BEGIN;

-- Add unique constraint on name column
ALTER TABLE clients 
ADD CONSTRAINT clients_name_unique UNIQUE (name);

COMMIT;
