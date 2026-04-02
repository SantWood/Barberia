@echo off
cd /d C:\xampp\htdocs\barberia
call venv\Scripts\activate
start cmd /k python app.py
timeout /t 3 /nobreak
start http://localhost:5000
