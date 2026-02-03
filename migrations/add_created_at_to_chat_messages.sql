-- Add created_at column to chat_messages table
-- Migration: Add timestamp tracking for chat messages

ALTER TABLE chat_messages 
ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW();

-- Add index for better query performance on created_at
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);

-- Add comment for documentation
COMMENT ON COLUMN chat_messages.created_at IS 'Timestamp when the message was created';
