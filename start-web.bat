@echo off
REM Reels Brain — spustenie web appky (Windows). Dvojklik.
cd /d "%~dp0"
set PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
echo Stavam vyhladavaci index z vaultu...
"%PY%" webapp\store.py
echo Spustam appku na http://127.0.0.1:5000
start "" http://127.0.0.1:5000
"%PY%" webapp\app.py
