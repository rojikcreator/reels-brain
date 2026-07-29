"""Davkove spracovanie reel URL zo suboru (cisty prepis, bez AI).
Pouzitie: python webapp/batch.py <handle> <subor_url> <niche>"""
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

handle = sys.argv[1]
urls = [x.strip() for x in Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()
        if x.strip() and not x.strip().startswith("#")]
niche = sys.argv[3]

print(f"@{handle} -> {niche}: {len(urls)} reels", flush=True)
ok = 0
for i, u in enumerate(urls, 1):
    sc = u.rstrip("/").split("/")[-1]
    if store.exists(sc):  # dobehnutie po padu — nespracuvavaj znova
        ok += 1
        print(f"{i}/{len(urls)} SKIP (uz mame) {sc}", flush=True)
        continue
    try:
        r = ingest.ingest_one(u, handle, niche)
        ok += 1
        print(f"{i}/{len(urls)} OK {r['transcript'][:60]}", flush=True)
    except Exception as e:
        print(f"{i}/{len(urls)} FAIL {sc}: {e}", flush=True)
print(f"HOTOVO: {ok}/{len(urls)} prepisov", flush=True)
