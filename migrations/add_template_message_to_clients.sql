-- Add template_message column to clients table for initial chat greeting

BEGIN;

ALTER TABLE clients 
ADD COLUMN template_message TEXT;

-- Set default template for TOKO ABC
UPDATE clients 
SET template_message = 'Halo! Selamat datang di TOKO ABC. Apakah saya bisa membantu Anda dengan pertanyaan atau kebutuhan layanan laptop Anda?'
WHERE name = 'Toko ABC (Test)';

COMMIT;
