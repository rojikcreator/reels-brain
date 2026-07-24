"""Spracovanie jedného reelu: yt-dlp audio -> whisper prepis -> DB + .md vo vaulte.
Čistý prepis, žiadna AI analýza."""
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import store  # noqa: E402
from reels_brain.config import BRAIN_SUBDIR, DOWNLOADS, VAULT  # noqa: E402
from reels_brain.transcriber import transcribe  # noqa: E402
from reels_brain.vault import sanitize, slug  # noqa: E402

YTDLP = [sys.executable, "-m", "yt_dlp"]


def _shortcode(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def _meta(url: str) -> dict:
    r = subprocess.run(
        YTDLP + ["--dump-json", "--skip-download", "--no-warnings", url],
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0 or not r.stdout.strip():
        return {}
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {}


def _download_audio(url: str, handle: str, shortcode: str) -> Path:
    folder = DOWNLOADS / handle
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / f"{shortcode}.%(ext)s"
    r = subprocess.run(
        YTDLP + ["-f", "ba/b", "-x", "--audio-format", "m4a", "--no-warnings", "-o", str(out), url],
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        raise RuntimeError(f"yt-dlp: {(r.stderr or '')[:180]}")
    cand = sorted(folder.glob(f"{shortcode}.m4a")) or sorted(folder.glob(f"{shortcode}.*"))
    if not cand:
        raise FileNotFoundError("audio sa nestiahlo")
    return cand[0]


def _note_md(rec: dict) -> str:
    return f"""---
vytvorené: {date.today():%Y-%m-%d}
tagy: [reels, {slug(rec['niche'])}]
profil: "{rec['profile']}"
niche: "{rec['niche']}"
zdroj: {rec['url']}
publikované: {rec['date']}
lajky: {rec['likes']}
komentáre: {rec['comments']}
---

{rec['transcript']}

## Popis pod videom

{rec['caption'] or '—'}
"""


def _write_note(rec: dict) -> None:
    folder = VAULT / BRAIN_SUBDIR / sanitize(rec["niche"]) / rec["profile"]
    folder.mkdir(parents=True, exist_ok=True)
    words = rec["transcript"].split()
    title = sanitize(" ".join(words[:6])) if words else rec["shortcode"]
    (folder / f"{rec['date']} {title}.md").write_text(_note_md(rec), encoding="utf-8")


def ingest_one(url: str, handle: str, niche: str, keep_media: bool = False) -> dict:
    sc = _shortcode(url)
    m = _meta(url)
    up = m.get("upload_date")
    d = datetime.strptime(up, "%Y%m%d").strftime("%Y-%m-%d") if up else date.today().isoformat()
    audio = _download_audio(url, handle, sc)
    transcript = transcribe(audio)
    if not keep_media:
        try:
            audio.unlink()
        except OSError:
            pass
    rec = {
        "shortcode": sc, "profile": handle, "niche": niche, "url": url, "date": d,
        "likes": m.get("like_count") or 0, "comments": m.get("comment_count") or 0,
        "caption": (m.get("description") or "")[:1000], "transcript": transcript,
        "added": date.today().isoformat(),
    }
    store.upsert_reel(rec)
    _write_note(rec)
    return rec
