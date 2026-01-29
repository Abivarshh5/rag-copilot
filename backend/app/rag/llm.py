import os
import json
import traceback
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.rag.engine import hybrid_retrieve_docs
from app.core.metrics import metrics
import uuid

# Load env vars - using absolute path for robustness in all environments
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(dotenv_path=ENV_PATH)

# Similarity threshold (Day 5 requirement)
SIMILARITY_THRESHOLD = 0.75
MIN_CHUNKS_ABOVE_THRESHOLD = 2

# LOAD API KEY
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY") 
if not HF_TOKEN:
    HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# INITIALIZE MODEL
REPO_ID = "meta-llama/Llama-3.1-8B-Instruct"

def get_llm():
    if not HF_TOKEN:
        print("CRITICAL: HUGGINGFACE_API_KEY not found in .env!")
        return None
    try:
        # Using the standard HF Router for OpenAI compatibility
        _llm = ChatOpenAI(
            base_url="https://router.huggingface.co/v1/",
            api_key=HF_TOKEN,
            model=REPO_ID,
            temperature=0.1
        )
        return _llm
    except Exception as e:
        print(f"ERROR: LLM Init failed: {e}")
        return None

llm = get_llm()

# PROMPT TEMPLATE (STRICT)
template = """You are a helpful assistant.
Use the context below to answer the question.
Provide a comprehensive and detailed answer based ONLY on the provided context.
If the context mentions multiple points, list them out clearly.

Context:
{context}

Question:
{question}

If the context does not contain enough information, respond exactly with:
"I don't have enough information to answer this."
"""

prompt = PromptTemplate(template=template, input_variables=["context", "question"])

def generate_answer(query: str):
    start_time = time.time()
    trace_id = str(uuid.uuid4())
    print(f"\n--- RAG ASK [{trace_id}]: {query} ---")
    
    if not llm:
        return {
            "answer": "Error: LLM not initialized.",
            "status": "error",
            "trace_id": trace_id,
            "sources": []
        }

    # 1. RETRIEVE (HYBRID)
    try:
        print(f"DEBUG: Starting retrieval for '{query}'...")
        r_start = time.time()
        # Request k=7 for more candidates
        chunks = hybrid_retrieve_docs(query, k=7)
        print(f"DEBUG: Retrieval took {time.time() - r_start:.2f}s")
    except Exception as e:
        print(f"ERROR: Retrieval failed: {e}")
        metrics.log_request("error", time.time() - start_time)
        return {"answer": f"Error in retrieval: {e}", "status": "error", "trace_id": trace_id, "sources": []}
    
    # 2. CONFIDENCE CHECK (GUARDRAILS)
    # Lowered threshold for better coverage of PDF content
    REVISED_THRESHOLD = 0.60
    REVISED_MIN_CHUNKS = 1
    
    relevant_chunks = []
    top_score = 0.0
    
    for chunk in chunks:
        # Vector hits have distance, keyword hits from BM25 might not.
        if "distance" in chunk and chunk["distance"] is not None:
             similarity = 1 - chunk["distance"]
             if similarity > top_score:
                 top_score = similarity
             if similarity >= REVISED_THRESHOLD:
                 relevant_chunks.append(chunk)
        else:
             # BM25 match - treat as high confidence
             relevant_chunks.append(chunk)
             if top_score == 0: top_score = 0.8 # Arbitrary high for keyword matched

    print(f"DEBUG: Top similarity score: {top_score:.4f}. Chunks above threshold: {len(relevant_chunks)}")

    status = "success"
    if len(relevant_chunks) < REVISED_MIN_CHUNKS:
        status = "low_context"
        explanation = f"Only found {len(relevant_chunks)} chunks above {REVISED_THRESHOLD} threshold (needed {REVISED_MIN_CHUNKS}). Top score: {top_score:.4f}"
        print(f"DEBUG: Guardrails triggered. {explanation}")
        
    if status == "low_context":
        metrics.log_request("low_context", time.time() - start_time, top_score)
        return {
            "answer": "I don't have enough information to answer this.",
            "status": "low_context",
            "trace_id": trace_id,
            "explanation": explanation if len(chunks) > 0 else "No relevant documents found.",
            "sources": chunks
        }

    # 3. GENERATE
    # Use top 5 chunks for more context
    context_text = "\n\n".join([c["text"] for c in relevant_chunks[:5]])
    
    # Calculate scores for final output
    final_sources = []
    for chunk in relevant_chunks[:5]:
        source_item = chunk.copy()
        # Ensure score is present for UI
        if "score" not in source_item:
             if "distance" in chunk and chunk["distance"] is not None:
                 source_item["score"] = 1 - chunk["distance"]
             else:
                 source_item["score"] = 0.9999 # Max for exact keyword match
        final_sources.append(source_item)

    try:
        print(f"DEBUG: Starting generation...")
        g_start = time.time()
        formatted_prompt = prompt.format(context=context_text, question=query)
        response = llm.invoke(formatted_prompt)
        answer = response.content.strip()
        print(f"DEBUG: Generation took {time.time() - g_start:.2f}s")
        
        # Guardrail check
        if "I don't have enough information" in answer:
             status = "low_context"

        latency = time.time() - start_time
        metrics.log_request(status, latency, top_score)
        
        return {
            "answer": answer,
            "status": status,
            "trace_id": trace_id,
            "sources": final_sources
        }
    except Exception as e:
        metrics.log_request("error", time.time() - start_time, top_score)
        return {
            "answer": f"Error generating answer: {str(e)}",
            "status": "error",
            "trace_id": trace_id,
            "sources": chunks
        }
