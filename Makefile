.PHONY: install test run-backend run-frontend

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

test:
	cd backend && python test_api.py
	cd backend && python verify_rag.py

run-backend:
	cd backend && python -m uvicorn app.main:app --reload

run-frontend:
	cd frontend && npm run dev
