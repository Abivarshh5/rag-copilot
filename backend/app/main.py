from fastapi import FastAPI

app = FastAPI(title="SaaS Support Copilot")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"message": "Welcome to SaaS Support Copilot"}
