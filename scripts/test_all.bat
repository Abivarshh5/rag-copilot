@echo off
echo Running Quality Gate...

echo 1. Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 exit /b %errorlevel%

echo 2. Running API Tests...
python test_api.py
if %errorlevel% neq 0 exit /b %errorlevel%

echo 3. Running RAG Verification...
python verify_rag.py
if %errorlevel% neq 0 exit /b %errorlevel%

echo Quality Gate Passed!
cd ..
