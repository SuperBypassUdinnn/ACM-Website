# ACM AI Chatbot - SaaS Platform

Multi-tenant AI chatbot SaaS platform dengan PostgreSQL database dan ChromaDB vector store.

## Tech Stack

**Backend:**

- FastAPI (Python)
- PostgreSQL (Database)
- ChromaDB (Vector Store)
- Ollama (LLM & Embeddings)
- asyncpg, bcrypt, JWT

**Frontend:**

- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- React

## Setup

### 1. Backend Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate.fish  # or activate.bat on Windows

# Install dependencies
pip install -r requirements.txt

# Setup database (PostgreSQL required)
cp .env.example .env
# Edit .env with your database credentials

# Seed initial data
python scripts/seed_db.py

# Start backend
uvicorn app:app --reload
```

### 2. Frontend Setup

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

### 3. Ollama Setup

```bash
# Pull required models
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

## Project Structure

```
acm-web/
├── app/                    # Next.js pages & routes
├── components/             # React components
├── lib/                    # Client utilities (auth, etc)
├── scripts/                # Python utility scripts
│   ├── seed_db.py         # Database seeding
│   ├── upload_documents.py # CSV → PostgreSQL
│   ├── ingest.py          # Generate embeddings
│   ├── get_client_id.py   # List clients
│   └── clear_db.py        # Clear database
├── data/                   # Client documents (CSV)
├── vectordb/               # ChromaDB storage
├── app.py                  # FastAPI backend
└── requirements.txt        # Python dependencies
```

## Workflows

### Register New User

1. Visit `http://localhost:3000/register`
2. Choose plan (Free/Basic/Pro)
3. Auto-create client + API key

### Upload Documents

```bash
# 1. Create folder: data/<Client Name>/
# 2. Add CSV files (title,content,category)
python scripts/upload_documents.py "<Client Name>"

# 3. Generate embeddings
python scripts/ingest.py
```

### Test Chat API

```bash
curl -X POST http://localhost:8000/chat \
  -H "x-api-key: <your-key>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'
```

## Features

- ✅ Multi-tenant data isolation
- ✅ JWT authentication
- ✅ Auto client provisioning
- ✅ Client-specific vector collections
- ✅ CSV document upload
- ✅ RAG-based context retrieval
- ✅ Session management
- ✅ Usage tracking

## API Endpoints

**Auth:**

- `POST /auth/register` - Register + auto-provision
- `POST /auth/login` - Login with JWT
- `GET /auth/me` - Get current user

**Chat:**

- `POST /chat` - Send message (requires API key)

**Health:**

- `GET /health` - Health check
- `GET /` - API info

## Environment Variables

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=acm_ai
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres

JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

OLLAMA_BASE_URL=http://localhost:11434
```

## License

MIT
