@echo off
cd ..
cd Gandhar_terminal
call venv\Scripts\activate
REM Open URL in Google Chrome
start "" "chrome.exe" "http://127.0.0.1:8000/"
python manage.py runserver
REM Wait for server to start (adjust time if needed)
timeout /t 5 /nobreak >nul