import os
import json
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from pypdf import PdfReader

# Setup
DATA_DIR = "data"
DOCS_DIR = "data/docs" # Standard JSON docs
DB_PATH = "data/chroma_db"
COLLECTION_NAME = "docs_collection"

# Initialize model
# We initialize it at module level so it loads once when the app starts
print("Loading Embedding Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model Loaded")

# Initialize Chroma
client = chromadb.PersistentClient(path=DB_PATH)
# Use cosine similarity for better score mapping (similarity = 1 - distance)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME, 
    metadata={"hnsw:space": "cosine"}
)

# BM25 Global State
bm25 = None
bm25_chunks = []
bm25_metadatas = []

def init_bm25():
    """Initializes BM25 from existing ChromaDB data."""
    global bm25, bm25_chunks, bm25_metadatas
    try:
        results = collection.get()
        if results and results['documents']:
            bm25_chunks = results['documents']
            bm25_metadatas = results['metadatas']
            tokenized_corpus = [doc.split() for doc in bm25_chunks]
            bm25 = BM25Okapi(tokenized_corpus)
            print(f"BM25 initialized with {len(bm25_chunks)} chunks.")
    except Exception as e:
        print(f"BM25 Init Error: {e}")

# Call init on startup
init_bm25()

def load_docs() -> List[Dict]:
    """Loads both JSON and PDF documents from their respective directories."""
    docs = []
    
    # 1. Load JSONs from data/docs
    if os.path.exists(DOCS_DIR):
        for filename in os.listdir(DOCS_DIR):
            if filename.endswith(".json"):
                path = os.path.join(DOCS_DIR, filename)
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        docs.append(data)
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
    
    # 2. Load PDFs from data/
    if os.path.exists(DATA_DIR):
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".pdf"):
                path = os.path.join(DATA_DIR, filename)
                try:
                    reader = PdfReader(path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    
                    if text.strip():
                        docs.append({
                            "id": filename,
                            "title": filename,
                            "body": text
                        })
                        print(f"Loaded PDF: {filename}")
                except Exception as e:
                    print(f"Error loading PDF {filename}: {e}")
                    
    return docs

def chunk_text(text: str, chunk_size: int = 150, overlap: int = 30) -> List[str]:
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

    if all_chunks:
        # Generate embeddings with normalization for better cosine similarity
        embeddings = model.encode(all_chunks, normalize_embeddings=True).tolist()
        
        # Add to Chroma (upsert overwrites if ID exists)
        collection.upsert(
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=all_metadatas,
            ids=all_ids
        )
        # Refresh BM25
        init_bm25()
        
    return {"doc_count": doc_count, "chunk_count": chunk_count}

def retrieve_docs(query: str, k: int = 3):
    # Embed query with normalization
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()
    
    # Search
    results = collection.query(
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
    """Combines BM25 and Vector Search results."""
    # 1. Vector Search
    vector_hits = retrieve_docs(query, k=k)
    
    # 2. BM25 Search
    bm25_hits = []
    if bm25:
        tokenized_query = query.split()
        # Get top results from BM25
        scores = bm25.get_scores(tokenized_query)
        # Sort by score and get top k
        top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        
        for i in top_n:
            if scores[i] > 0:
                bm25_hits.append({
                    "text": bm25_chunks[i],
                    "metadata": bm25_metadatas[i] if i < len(bm25_metadatas) else {},
                    "score": float(scores[i]),
                    "type": "keyword"
                })

    # 3. Combine (Union and remove duplicates)
    combined = []
    seen = set()
    
    # Priority for vector hits (they have better metadata and distance)
    for hit in vector_hits:
        combined.append(hit)
        seen.add(hit["text"])
        
    for hit in bm25_hits:
        if hit["text"] not in seen:
            combined.append(hit)
            seen.add(hit["text"])
            
    # Scale back to k if overloaded
    return combined[:k]
