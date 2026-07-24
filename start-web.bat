@echo off
REM Reels Brain — spustenie web appky (Windows). Dvojklik.
cd /d "%~dp0"
set PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
echo Stavam vyhladavaci index z vaultu...
"%PY%" webapp\store.py
echo Spustam appku na http://localhost:5000
start "" http://localhost:5000
"%PY%" webapp\app.py
