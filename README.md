---
title: Rag Backend
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# RAG Copilot with Authentication

A full-stack AI Copilot application featuring Retrieval-Augmented Generation (RAG) for PDF knowledge bases, complete with user authentication, precision scoring, and a modern React frontend.

![Frontend UI](https://via.placeholder.com/800x400?text=RAG+Copilot+UI+Mockup)

## Features

- **Document Q&A**: Upload PDFs and ask questions about them.
- **RAG Engine**: Hybrid search (BM25 + Semantic) for high-accuracy retrieval.
- **Precision Scoring**: Displays relevance scores (0-100%) and transparency for every answer.
- **Verification**: Refuses to answer if context is insufficient ("I don't have enough information").
- **Authentication**: JWT-based Signup and Login flows.
- **Modern UI**: Glassmorphism design using React and CSS modules.

## Architecture

```mermaid
graph TD
    User[User] -->|HTTPS| FE[React Frontend]
    FE -->|Requests| BE[FastAPI Backend]
    
    subgraph Backend
        BE -->|Auth| DB[(SQLite/Postgres)]
        BE -->|Ask| RAG[RAG Engine]
    end
    
    subgraph RAG Pipeline
        Docs[PDF Documents] -->|Ingest| Chunks[Text Chunks]
        Chunks -->|Embed| Chroma[(ChromaDB)]
        Chunks -->|Tokenize| BM25[BM25 Index]
        Chroma & BM25 -->|Retrieve| Hyb[Hybrid Search]
        Hyb -->|Context| LLM["LLM (Llama/OpenAI)"]
    end
```

## Quick Start / Quality Gate

Run the automated quality gate to verify the system:

**Windows (PowerShell)**:
```powershell
./scripts/test_all.bat
```

**Linux/Mac**:
```bash
make test
```

### Manual Setup
 **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload
   ```
 **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Live Deployment

### 🚀 Production App
- **Live URL**: [https://huggingface.co/spaces/abiramavarshini/rag-backend](https://huggingface.co/spaces/abiramavarshini/rag-backend)
- **Direct App Link**: [https://abiramavarshini-rag-backend.hf.space](https://abiramavarshini-rag-backend.hf.space)
- **Status**: Running 🟢

### Anyone with the link can:
1. **Sign up** or **Log in** (No email verification required for demo).
2. **Chat** with the AI about the 38 pre-trained documents.
3. **Verify Sources**: Every answer includes the source PDF name and confidence score.

## API Documentation

### Auth
- `POST /auth/signup`: Register a new user.
- `POST /auth/login`: Get access token.

### RAG
- `POST /rag/ingest`: Trigger PDF ingestion.
- `POST /rag/ask`: Ask a question.
  ```json
  {
    "query": "What is the policy on X?"
  }
  ```

## Ingestion & Evaluation
- **Ingestion**: PDFs in `backend/data/` are read, split into **300-word chunks** with 50-word overlap for deep context.
- **Evaluation**: Hybrid retrieval (Vector + BM25) with **Reciprocal Rank Fusion (RRF)** ensures high precision. 
- **Out-of-Context Handling**: The LLM provides helpful general knowledge if documents don't have the answer, but marks it clearly as such.
