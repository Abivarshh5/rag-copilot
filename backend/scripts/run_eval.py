import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"
EVAL_FILE = "data/eval.json"

def run_eval():
    if not os.path.exists(EVAL_FILE):
        print(f"Error: {EVAL_FILE} not found.")
        return

    with open(EVAL_FILE, "r") as f:
        eval_set = json.load(f)

    print(f"=== Starting RAG Evaluation (N={len(eval_set)}) ===\n")
    
    results = []
    start_time = time.time()

    for entry in eval_set:
        query = entry["question"]
        expected = entry["expected"]
        print(f"Question: {query}")
        
        try:
            r = requests.post(f"{BASE_URL}/rag/ask", json={"query": query}, timeout=90)
            if r.status_code == 200:
                data = r.json()
                status = data.get("status")
                answer = data.get("answer", "")
                
                # Metric tracking
                is_refusal = (status == "low_context")
                is_expected_refusal = (expected == "low_context")
                
                match_type = "mismatch"
                if is_refusal and is_expected_refusal:
                    match_type = "correct_refusal"
                elif not is_refusal and not is_expected_refusal:
                    match_type = "correct_answer"
                elif is_refusal and not is_expected_refusal:
                    match_type = "false_refusal"
                else:
                    match_type = "false_answer"
                
                results.append({
                    "query": query,
                    "status": status,
                    "match": match_type,
                    "answer_preview": answer[:50] + "..."
                })
                print(f"  [Status: {status}] -> {match_type}")
            else:
                print(f"  [Error: {r.status_code}]")
        except Exception as e:
            print(f"  [Exception: {e}]")

    duration = time.time() - start_time
    
    # Calculate Final Metrics
    total = len(results)
    correct_ans = sum(1 for r in results if r["match"] == "correct_answer")
    correct_ref = sum(1 for r in results if r["match"] == "correct_refusal")
    false_ans = sum(1 for r in results if r["match"] == "false_answer")
    false_ref = sum(1 for r in results if r["match"] == "false_refusal")
    
    print("\n=== EVALUATION SUMMARY ===")
    print(f"Total Queries: {total}")
    print(f"Time Taken: {duration:.2f}s")
    print(f"Correct Answers: {correct_ans}")
    print(f"Correct Refusals: {correct_ref}")
    print(f"False Answers (Possible Hallucinations): {false_ans}")
    print(f"False Refusals (Too Strict): {false_ref}")
    print(f"Overall Accuracy: {(correct_ans + correct_ref)/total:.2%}")
    
    # Push metrics to server (optional log)
    try:
        metrics_resp = requests.get(f"{BASE_URL}/rag/metrics")
        print("\n=== SYSTEM METRICS (FROM SERVER) ===")
        print(json.dumps(metrics_resp.json(), indent=2))
    except:
        pass

if __name__ == "__main__":
    run_eval()
