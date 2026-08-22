"""Spracuj manifest 'handle|shortcode' do jednej niche (cisty prepis, skip uz spracovanych).
Pouzitie: python webapp/batch_manifest.py "Korčuľovanie" docs/skating-manifest.txt"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

import ingest  # noqa: E402
import store  # noqa: E402

niche = sys.argv[1]
lines = [l.strip() for l in Path(sys.argv[2]).read_text(encoding="utf-8").splitlines() if "|" in l]
total = len(lines)
print(f"NICHE {niche}: {total} videi z {len({l.split('|',1)[0] for l in lines})} profilov", flush=True)

ok = 0
for i, l in enumerate(lines, 1):
    handle, sc = l.split("|", 1)
    if store.exists(sc):
        ok += 1
        print(f"{i}/{total} SKIP {sc}", flush=True)
        continue
    url = f"https://www.instagram.com/reel/{sc}/"
    try:
        r = ingest.ingest_one(url, handle, niche)
        ok += 1
        print(f"{i}/{total} OK @{handle} {r['transcript'][:40]}", flush=True)
    except Exception as e:
        print(f"{i}/{total} FAIL @{handle} {sc}: {e}", flush=True)
print(f"HOTOVO: {ok}/{total}", flush=True)
