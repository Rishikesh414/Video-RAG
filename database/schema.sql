-- =====================================================================
-- VideoRAG Database Schema & Necessary Queries
-- Compatible with PostgreSQL and SQLite
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. TABLE DEFINITIONS (DDL)
-- ---------------------------------------------------------------------

-- Users Table: Stores student, faculty, and admin accounts
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'faculty')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Uploads Table: Tracks uploaded lecture videos and PDF notes
CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL CHECK (file_type IN ('video', 'pdf')),
    file_path VARCHAR(1000) NOT NULL,
    status VARCHAR(50) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat Messages Table: Stores Q&A history, AI answers, clip timestamps, and sources
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    sources TEXT, -- JSON formatted list of retrieved metadata chunks
    video_timestamp FLOAT, -- Start timestamp in seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- 2. INDEXES (Performance Optimization)
-- ---------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_uploads_user_id ON uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(status);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

-- ---------------------------------------------------------------------
-- 3. SEED DATA (Default Accounts: password is "password123")
-- ---------------------------------------------------------------------

INSERT INTO users (name, email, hashed_password, role)
VALUES 
    ('Student User', 'student@videorag.com', '$2b$12$cxGkeZJTNqu61ZFqsEgUd.dW65gTaCvZ3LK5qouCjJKtG/K./EgwW', 'student'),
    ('Faculty Member', 'faculty@videorag.com', '$2b$12$cxGkeZJTNqu61ZFqsEgUd.dW65gTaCvZ3LK5qouCjJKtG/K./EgwW', 'faculty'),
    ('System Administrator', 'admin@videorag.com', '$2b$12$cxGkeZJTNqu61ZFqsEgUd.dW65gTaCvZ3LK5qouCjJKtG/K./EgwW', 'faculty'),
    ('Demo Student', 'demo@videorag.com', '$2b$12$cxGkeZJTNqu61ZFqsEgUd.dW65gTaCvZ3LK5qouCjJKtG/K./EgwW', 'student')
ON CONFLICT (email) DO NOTHING;

-- ---------------------------------------------------------------------
-- 4. NECESSARY APPLICATION QUERIES (Reference Guide)
-- ---------------------------------------------------------------------

-- ================= AUTHENTICATION =================

-- Query 1: User Login (Find by Email)
-- Used by: /api/v1/auth/login
SELECT id, name, email, hashed_password, role, created_at 
FROM users 
WHERE email = :email 
LIMIT 1;

-- Query 2: User Registration (Create New User)
-- Used by: /api/v1/auth/register
INSERT INTO users (name, email, hashed_password, role)
VALUES (:name, :email, :hashed_password, :role)
RETURNING id, name, email, role, created_at;

-- Query 3: Check If User Exists
SELECT 1 FROM users WHERE email = :email LIMIT 1;

-- Query 4: Get User by ID (Token Verification)
SELECT id, name, email, role, created_at 
FROM users 
WHERE id = :user_id;

-- ================= UPLOADS =================

-- Query 5: Record New Upload (Video / PDF)
-- Used by: /api/v1/upload/video and /api/v1/upload/pdf
INSERT INTO uploads (user_id, filename, file_type, file_path, status)
VALUES (:user_id, :filename, :file_type, :file_path, 'processing')
RETURNING id, filename, file_type, status, created_at;

-- Query 6: Update Upload Status
UPDATE uploads 
SET status = :status 
WHERE id = :upload_id;

-- Query 7: List Uploads for Current User
-- Used by: /api/v1/upload/list
SELECT id, filename, file_type, file_path, status, created_at 
FROM uploads 
WHERE user_id = :user_id 
ORDER BY created_at DESC;

-- Query 8: List All Uploaded Videos for Indexing
SELECT id, filename, file_path, status 
FROM uploads 
WHERE file_type = 'video' AND status = 'completed';

-- ================= CHAT & Q&A HISTORY =================

-- Query 9: Save Student Question
INSERT INTO chat_messages (user_id, role, content)
VALUES (:user_id, 'user', :question);

-- Query 10: Save AI Assistant Answer with Evidence Clip Timestamp
INSERT INTO chat_messages (user_id, role, content, sources, video_timestamp)
VALUES (:user_id, 'assistant', :answer, :sources_json, :timestamp_seconds);

-- Query 11: Get Chat History for a User
-- Used by: /api/v1/chat/history
SELECT id, role, content, sources, video_timestamp, created_at 
FROM chat_messages 
WHERE user_id = :user_id 
ORDER BY created_at ASC;

-- Query 12: Clear Chat History for a User
-- Used by: DELETE /api/v1/chat/history
DELETE FROM chat_messages 
WHERE user_id = :user_id;

-- ================= ANALYTICS & ADMIN =================

-- Query 13: Count Total Users by Role
SELECT role, COUNT(*) AS count 
FROM users 
GROUP BY role;

-- Query 14: Count Total Uploads by Status
SELECT status, COUNT(*) AS count 
FROM uploads 
GROUP BY status;
