@echo off
set CRYPTGRAPHY_DONT_BUILD_RUST=1
venv\Scripts\python.exe -m pip install fastapi uvicorn passlib python-jose[cryptography] azure-storage-blob openai
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause