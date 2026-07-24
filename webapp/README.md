# Reels Brain — web app

Vlož Instagram username → stiahne všetky reels → prepíše (whisper) → uloží do priečinka podľa niche → **vyhľadávač** naprieč všetkými prepismi.

Čisté prepisy, žiadna AI. Databáza rastie s každým profilom.

## Spustenie

**Windows:** dvojklik na `start-web.bat` (v koreni projektu).

**Mac:** `bash start-web.sh`

Otvorí sa `http://localhost:5000`.

## Ako to funguje

- **Pridať profil:** username + niche + počet videí → *Spracovať*. Ak Instagram práve nedovolí načítať zoznam, klikni „vlož linky ručne" a vlož reel URL (jeden na riadok).
- **Hľadať:** píš do vyhľadávača — nájde prepisy naprieč všetkými profilmi/niche, s filtrom podľa niche. „celý prepis" rozbalí text, `@profil` otvorí video.

## Dáta

- **Zdroj pravdy:** `.md` prepisy vo vaulte `3-Zdroje/Reels Brain/<niche>/<profil>/` — syncujú sa gitom, čitateľné v Obsidiane.
- **Index:** `reels.db` (SQLite FTS5) — lokálny, rebuildovateľný. `python webapp/store.py` ho postaví nanovo z vaultu (spúšťa sa aj pri štarte appky).

## Sync medzi PC a Mac

Po pridaní profilov: vo vaulte `git add -A && git commit && git push`. Na druhom stroji `git pull` a spusti appku — index sa prestaví sám.
