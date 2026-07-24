#!/usr/bin/env bash
# Reels Brain — spustenie web appky (Mac/Linux). Spusti: bash start-web.sh
cd "$(dirname "$0")"
source .venv/bin/activate 2>/dev/null || true
echo "Stavam vyhladavaci index z vaultu..."
python webapp/store.py
echo "Spustam appku na http://127.0.0.1:5000"
( sleep 2; open http://127.0.0.1:5000 2>/dev/null || xdg-open http://127.0.0.1:5000 2>/dev/null ) &
python webapp/app.py
