import os
import traceback
from dotenv import load_dotenv
load_dotenv(dotenv_path="d:/repo/backend/.env")
from langchain_openai import ChatOpenAI

HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
REPO_ID = "meta-llama/Llama-3.1-8B-Instruct"

print(f"Token Length: {len(HF_TOKEN) if HF_TOKEN else 0}")
print(f"Model: {REPO_ID}")

try:
    print("Initializing OpenAI-compatible HF LLM (Llama)...")
    llm = ChatOpenAI(
        base_url="https://router.huggingface.co/v1/",
        api_key=HF_TOKEN,
        model=REPO_ID,
        temperature=0.1
    )
    print("Invoking model...")
    # Llama expects chat messages usually, but LangChain handles it
    res = llm.invoke("What is FastAPI?")
    print("\n[SUCCESS]")
    print("Result:", res.content)
except Exception as e:
    print(f"\n[FAILED]")
    traceback.print_exc()
