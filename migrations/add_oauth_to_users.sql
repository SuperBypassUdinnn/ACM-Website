-- Add OAuth support to users table

BEGIN;

-- Add OAuth columns
ALTER TABLE users
ADD COLUMN oauth_provider VARCHAR(50),
ADD COLUMN oauth_id VARCHAR(255),
ADD COLUMN avatar_url TEXT,
ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;

-- Make password nullable for OAuth-only users
ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;

-- Add unique constraint for OAuth users
CREATE UNIQUE INDEX users_oauth_provider_id_unique 
ON users(oauth_provider, oauth_id) 
WHERE oauth_provider IS NOT NULL;

-- Update existing users to mark them as email-based
UPDATE users 
SET oauth_provider = 'email', 
    email_verified = TRUE 
WHERE oauth_provider IS NULL;

-- Add comment
COMMENT ON COLUMN users.oauth_provider IS 'OAuth provider: google, microsoft, github, or email for traditional login';
COMMENT ON COLUMN users.oauth_id IS 'Unique ID from OAuth provider';
COMMENT ON COLUMN users.avatar_url IS 'Profile picture URL from OAuth provider';

COMMIT;
