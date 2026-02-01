import os
import sys

# Ensure backend dir is in path
sys.path.append(os.getcwd())

from app.rag.engine import ingest_docs, get_collection

def reingest():
    print("--- Starting Re-ingestion ---")
    
    # 1. Clear old data? 
    # Optional: col = get_collection(); col.delete(where={}) 
    # upsert handles overwriting by ID, but for clean chunks we should delete everything first
    try:
        col = get_collection()
        print(f"Clearing collection '{col.name}'...")
        # Since we use doc_id + index, and index might change with new chunking, 
        # delete_all is safer.
        all_docs = col.get()
        if all_docs['ids']:
            col.delete(ids=all_docs['ids'])
            print(f"Deleted {len(all_docs['ids'])} old chunks.")
    except Exception as e:
        print(f"Could not clear collection (might be empty): {e}")

    # 2. Ingest with new 300-word chunk size
    print("Ingesting documents...")
    stats = ingest_docs()
    print(f"SUCCESS: {stats}")

if __name__ == "__main__":
    reingest()
