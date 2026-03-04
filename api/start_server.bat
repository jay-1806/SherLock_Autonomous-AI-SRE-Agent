@echo off
cd /d C:\Users\Lenovo\Desktop\Part2_SRE\SherLock\api
.\.venv\Scripts\python.exe -m uvicorn src.app.main:app --port 8000 --host 127.0.0.1
