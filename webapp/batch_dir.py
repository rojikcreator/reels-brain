"""Spracuj vsetky docs/skating/*.txt do jednej niche (cisty prepis, skip uz spracovanych).
Pouzitie: python webapp/batch_dir.py "Korčuľovanie" """
import glob
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
folder = Path(__file__).resolve().parents[1] / "docs" / "skating"
files = sorted(glob.glob(str(folder / "*.txt")))
print(f"NICHE {niche}: {len(files)} profilov", flush=True)

grand_ok = grand_total = 0
for f in files:
    handle = Path(f).stem
    urls = [x.strip() for x in Path(f).read_text(encoding="utf-8").splitlines()
            if x.strip() and not x.strip().startswith("#")]
    grand_total += len(urls)
    print(f"### @{handle}: {len(urls)} reels", flush=True)
    for i, u in enumerate(urls, 1):
        sc = u.rstrip("/").split("/")[-1]
        if store.exists(sc):
            grand_ok += 1
            print(f"  {i}/{len(urls)} SKIP {sc}", flush=True)
            continue
        try:
            r = ingest.ingest_one(u, handle, niche)
            grand_ok += 1
            print(f"  {i}/{len(urls)} OK {r['transcript'][:50]}", flush=True)
        except Exception as e:
            print(f"  {i}/{len(urls)} FAIL {sc}: {e}", flush=True)
print(f"HOTOVO CELE: {grand_ok}/{grand_total}", flush=True)
