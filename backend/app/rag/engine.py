import os
import json
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from pypdf import PdfReader

# Setup - Detect if running on Hugging Face Spaces
IS_HF_SPACE = os.getenv("SPACE_ID") is not None

# Robust path logic using the file location itself
_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BASE_DIR = os.path.dirname(_APP_DIR)
DATA_DIR = os.path.join(_BASE_DIR, "data")
DOCS_DIR = os.path.join(DATA_DIR, "docs")
DB_PATH = os.path.join(DATA_DIR, "chroma_db")

if IS_HF_SPACE:
    print(f"HF RAG PATHS: DATA={DATA_DIR}, DB={DB_PATH}")
    # Ensure directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(DB_PATH, exist_ok=True)

COLLECTION_NAME = "docs_collection"

# Lazy initialization
_model = None
_collection = None

def get_model():
    global _model
    if _model is None:
        print("Loading Embedding Model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model Loaded")
    return _model

def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=DB_PATH)
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME, 
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

# BM25 Global State
bm25 = None
bm25_chunks = []
bm25_metadatas = []

def init_bm25():
    """Initializes BM25 from existing ChromaDB data."""
    global bm25, bm25_chunks, bm25_metadatas
    try:
        col = get_collection()
        results = col.get()
        if results and results['documents']:
            bm25_chunks = results['documents']
            bm25_metadatas = results['metadatas']
            tokenized_corpus = [doc.split() for doc in bm25_chunks]
            bm25 = BM25Okapi(tokenized_corpus)
            print(f"BM25 initialized with {len(bm25_chunks)} chunks.")
    except Exception as e:
        print(f"BM25 Init Error: {e}")

# Call init on startup? No, move to FastAPI startup_event to avoid import-time crashes.
# init_bm25()

def load_docs() -> List[Dict]:
    """Loads both JSON and PDF documents from their respective directories."""
    docs = []
    print(f"DEBUG: load_docs searching in DATA_DIR={DATA_DIR}")
    
    # 1. Load JSONs from data/docs
    if os.path.exists(DOCS_DIR):
        print(f"DEBUG: Found DOCS_DIR={DOCS_DIR}")
        for filename in os.listdir(DOCS_DIR):
            if filename.endswith(".json"):
                path = os.path.join(DOCS_DIR, filename)
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        docs.append(data)
                        print(f"DEBUG: Loaded JSON: {filename}")
                    except Exception as e:
                        print(f"ERROR: Failed to load JSON {filename}: {e}")
    else:
        print(f"DEBUG: DOCS_DIR NOT FOUND: {DOCS_DIR}")
    
    # 2. Load PDFs from data/
    if os.path.exists(DATA_DIR):
        print(f"DEBUG: Searching for PDFs in {DATA_DIR}")
        all_files = os.listdir(DATA_DIR)
        print(f"DEBUG: Files in DATA_DIR: {all_files}")
        for filename in all_files:
            if filename.lower().endswith(".pdf"):
                path = os.path.join(DATA_DIR, filename)
                try:
                    print(f"DEBUG: Attempting to read PDF: {filename} (Size: {os.path.getsize(path)} bytes)")
                    reader = PdfReader(path)
                    text = ""
                    for i, page in enumerate(reader.pages):
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                    
                    if text.strip():
                        docs.append({
                            "id": filename,
                            "title": filename,
                            "body": text
                        })
                        print(f"DEBUG: Successfully loaded PDF: {filename} ({len(text)} chars)")
                    else:
                        print(f"DEBUG: PDF {filename} is EMPTY or NO TEXT EXTRACTED.")
                except Exception as e:
                    print(f"ERROR: Failed to load PDF {filename}: {e}")
    else:
        print(f"DEBUG: DATA_DIR NOT FOUND: {DATA_DIR}")
                    
    return docs

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """Splits text into overlapping chunks of words. Increased size for better context."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def ingest_docs():
    """Reads docs, chunks them, embeds, and stores in Chroma."""
    docs = load_docs()
    all_chunks = []
    all_ids = []
    all_metadatas = []
    
    files_processed = []
    errors = []
    doc_count = 0
    chunk_count = 0
    
    for doc in docs:
        doc_id = str(doc.get("id"))
        title = doc.get("title", "Untitled")
        body = doc.get("body", "")
        
        chunks = chunk_text(body)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{i}"
            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadatas.append({"doc_id": doc_id, "title": title, "chunk_index": i})
            
        doc_count += 1
        chunk_count += len(chunks)
        files_processed.append(title)

    if all_chunks:
        try:
            # Generate embeddings with normalization for better cosine similarity
            m = get_model()
            embeddings = m.encode(all_chunks, normalize_embeddings=True).tolist()
            
            # Add to Chroma (upsert overwrites if ID exists)
            col = get_collection()
            col.upsert(
                documents=all_chunks,
                embeddings=embeddings,
                metadatas=all_metadatas,
                ids=all_ids
            )
            # Refresh BM25
            init_bm25()
        except Exception as e:
            errors.append(f"Chroma/Embedding Error: {str(e)}")
        
    return {
        "doc_count": doc_count, 
        "chunk_count": chunk_count,
        "files_processed": files_processed,
        "errors": errors
    }

def retrieve_docs(query: str, k: int = 3):
    # Embed query with normalization
    m = get_model()
    query_embedding = m.encode([query], normalize_embeddings=True).tolist()
    
    # Search
    col = get_collection()
    results = col.query(
        query_embeddings=query_embedding,
        n_results=k
    )
    
    # Format results
    hits = []
    if results['documents']:
        for i in range(len(results['documents'][0])):
            hits.append({
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if results['distances'] else None
            })
            
    return hits

def hybrid_retrieve_docs(query: str, k: int = 5):
    """Combines BM25 and Vector Search results using Reciprocal Rank Fusion (RRF)."""
    # 1. Vector Search
    vector_hits = retrieve_docs(query, k=k*2)
    
    # 2. BM25 Search
    bm25_hits = []
    if bm25:
        tokenized_query = query.split()
        scores = bm25.get_scores(tokenized_query)
        top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k*2]
        for i in top_n:
            if scores[i] > 0:
                bm25_hits.append({
                    "text": bm25_chunks[i],
                    "metadata": bm25_metadatas[i] if i < len(bm25_metadatas) else {},
                    "score": float(scores[i])
                })

    # 3. RRF Combination
    # RRF Score = sum(1 / (k + rank))
    rrf_k = 60
    scores = {} # text -> score
    doc_map = {} # text -> full hit object
    
    # Vector ranks
    for rank, hit in enumerate(vector_hits):
        txt = hit["text"]
        scores[txt] = scores.get(txt, 0) + 1.0 / (rrf_k + rank + 1)
        doc_map[txt] = hit
        
    # BM25 ranks
    for rank, hit in enumerate(bm25_hits):
        txt = hit["text"]
        scores[txt] = scores.get(txt, 0) + 1.0 / (rrf_k + rank + 1)
        if txt not in doc_map:
             doc_map[txt] = hit
             # Ensure distances/scores are normalized later
             doc_map[txt]["distance"] = 0.5 # Default middle for keyword hits

    # Sort by RRF score
    sorted_texts = sorted(scores.keys(), key=lambda t: scores[t], reverse=True)
    
    results = []
    for txt in sorted_texts[:k]:
        hit = doc_map[txt]
        hit["rrf_score"] = scores[txt]
        results.append(hit)
        
    return results
