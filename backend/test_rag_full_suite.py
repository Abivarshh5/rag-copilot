import requests
import json
import time

BASE_URL = "http://localhost:8000"

ANSWERABLE_QUESTIONS = [
    "What is FastAPI?",
    "Mention two key features of FastAPI.",
    "Is FastAPI compatible with OpenAPI?",
    "What are Newton's laws of motion?",
    "Define Newton's first law.",
    "What is the equation for Newton's second law?",
    "What does the third law of motion state?",
    "What is a vector database?",
    "Mention one capability of a vector database besides storing embeddings.",
    "How do vector databases differ from traditional ones regarding indexing?"
]

UNANSWERABLE_QUESTIONS = [
    "Who is the president of Mars?",
    "What is the recipe for chocolate cake?",
    "How many people live in Tokyo?",
    "What is the stock price of Apple today?",
    "Who won the World Cup in 1998?"
]

def run_suite():
    print("=== STARTING FULL RAG TEST SUITE ===\n")
    results = []

    # 1. Answerable Questions
    print("--- TESTING ANSWERABLE QUESTIONS ---")
    for q in ANSWERABLE_QUESTIONS:
        print(f"Query: {q}")
        try:
            r = requests.post(f"{BASE_URL}/rag/ask", json={"query": q}, timeout=60)
            if r.status_code == 200:
                data = r.json()
                status = data.get("status")
                answer = data.get("answer", "")
                
                # Check if it succeeded or was marked as low_context
                # (Note: thresholding might be strict, so we track both)
                result_entry = {
                    "query": q,
                    "type": "answerable",
                    "status": status,
                    "answer": answer[:100] + "..." if len(answer) > 100 else answer
                }
                print(f"  [STATUS: {status}]")
                if status == "success":
                    print(f"  [ANSWER: {answer[:70]}...]")
                else:
                    print(f"  [REFUSAL: {answer}]")
            else:
                print(f"  [SERVER ERROR: {r.status_code}]")
                result_entry = {"query": q, "type": "answerable", "status": "server_error", "answer": ""}
        except Exception as e:
            print(f"  [REQUEST FAILED: {e}]")
            result_entry = {"query": q, "type": "answerable", "status": "failed", "answer": ""}
        
        results.append(result_entry)
        print("-" * 30)

    # 2. Unanswerable Questions
    print("\n--- TESTING UNANSWERABLE QUESTIONS ---")
    for q in UNANSWERABLE_QUESTIONS:
        print(f"Query: {q}")
        try:
            r = requests.post(f"{BASE_URL}/rag/ask", json={"query": q}, timeout=60)
            if r.status_code == 200:
                data = r.json()
                status = data.get("status")
                answer = data.get("answer", "")
                
                result_entry = {
                    "query": q,
                    "type": "unanswerable",
                    "status": status,
                    "answer": answer
                }
                print(f"  [STATUS: {status}]")
                print(f"  [RESPONSE: {answer}]")
                
                # Verify refusal logic
                if status == "low_context" or "I don't have enough information" in answer:
                    print("  [SUCCESS] CORRECT BEHAVIOR: Refused properly.")
                else:
                    print("  [WARNING] POSSIBLE HALLUCINATION: Model attempted an answer.")
            else:
                print(f"  [SERVER ERROR: {r.status_code}]")
                result_entry = {"query": q, "type": "unanswerable", "status": "server_error", "answer": ""}
        except Exception as e:
            print(f"  [REQUEST FAILED: {e}]")
            result_entry = {"query": q, "type": "unanswerable", "status": "failed", "answer": ""}
            
        results.append(result_entry)
        print("-" * 30)

    # Summary
    print("\n=== TEST SUMMARY ===")
    ans_count = sum(1 for r in results if r["type"] == "answerable" and r["status"] == "success")
    ref_count = sum(1 for r in results if r["type"] == "unanswerable" and (r["status"] == "low_context" or "I don't have enough information" in r["answer"]))
    
    print(f"Answerable Questions success: {ans_count}/{len(ANSWERABLE_QUESTIONS)}")
    print(f"Unanswerable Questions refused: {ref_count}/{len(UNANSWERABLE_QUESTIONS)}")
    
    with open("full_suite_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nDetailed results saved to full_suite_results.json")

if __name__ == "__main__":
    run_suite()
