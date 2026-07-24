"""Spracuj konkretne reel URL bez Instaloaderu (obchadza IG API blok).

Pouzitie:
    py tools\\run_from_urls.py <handle> <subor_s_url> [bio_text]

Kazdy reel: yt-dlp metadata + audio -> whisper transcript -> claude rozbor -> vault.
yt-dlp funguje anonymne aj ked Instaloader API cestu IG blokuje.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# aby sa importoval balik z src/ aj ked skript spustis z korena projektu
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reels_brain import vault  # noqa: E402
from reels_brain.analyzer import (  # noqa: E402
    analyze_reel, build_playbook, classify_niche, parse_title,
)
from reels_brain.config import DOWNLOADS  # noqa: E402
from reels_brain.models import Reel  # noqa: E402
from reels_brain.transcriber import transcribe  # noqa: E402

YTDLP = [sys.executable, "-m", "yt_dlp"]


def read_urls(path: Path) -> list[str]:
    urls = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def fetch_meta(url: str) -> dict:
    r = subprocess.run(
        YTDLP + ["--dump-json", "--skip-download", "--no-warnings", url],
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"yt-dlp metadata zlyhalo: {(r.stderr or '')[:200]}")
    return json.loads(r.stdout)


def download_audio(url: str, handle: str, shortcode: str) -> Path:
    folder = DOWNLOADS / handle
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / f"{shortcode}.%(ext)s"
    r = subprocess.run(
        YTDLP + ["-f", "ba/b", "-x", "--audio-format", "m4a",
                 "--no-warnings", "-o", str(out), url],
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        raise RuntimeError(f"yt-dlp download zlyhalo: {(r.stderr or '')[:200]}")
    cand = sorted(folder.glob(f"{shortcode}.m4a")) or sorted(folder.glob(f"{shortcode}.*"))
    if not cand:
        raise FileNotFoundError(f"audio pre {shortcode} sa nestiahlo")
    return cand[0]


def meta_to_reel(url: str, m: dict) -> Reel:
    up = m.get("upload_date")  # "YYYYMMDD"
    if up:
        d = datetime.strptime(up, "%Y%m%d").replace(tzinfo=timezone.utc)
    else:
        d = datetime.now(timezone.utc)
    return Reel(
        shortcode=m.get("id") or url.rstrip("/").split("/")[-1],
        url=url,
        date=d,
        views=m.get("view_count") or m.get("like_count") or 0,
        likes=m.get("like_count") or 0,
        comments=m.get("comment_count") or 0,
        duration=float(m.get("duration") or 0),
        caption=(m.get("description") or "")[:500],
    )


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")

    handle = sys.argv[1]
    urls = read_urls(Path(sys.argv[2]))
    bio = sys.argv[3] if len(sys.argv) > 3 else ""
    print(f"📡 @{handle}: {len(urls)} reels na spracovanie (yt-dlp cesta, bez Instaloaderu)")

    # 1) metadata pre vsetky, zorad podla views (alebo lajkov ako nahrada)
    reels = []
    for u in urls:
        try:
            reels.append(meta_to_reel(u, fetch_meta(u)))
        except Exception as e:
            print(f"   ⚠️  metadata {u}: {e}")
    reels.sort(key=lambda r: r.views, reverse=True)
    print("   rebríček:")
    for i, r in enumerate(reels, 1):
        print(f"   {i:2}. {r.views:>8,} 👁/❤  {r.date:%d.%m.}  {r.shortcode}")

    print("🧠 niche (haiku)...")
    niche = classify_niche(bio, reels)
    print(f"   → {niche}")

    done = []
    for i, r in enumerate(reels, 1):
        try:
            print(f"🎬 [{i}/{len(reels)}] {r.shortcode}: audio...")
            audio = download_audio(r.url, handle, r.shortcode)
            r.audio_path = audio
            print("   ✍️  whisper...")
            r.transcript = transcribe(audio)
            print("   🔬 rozbor (sonnet)...")
            raw = analyze_reel(r, handle, niche)
            r.title, r.anatomy = parse_title(raw, r.shortcode)
            done.append(r)
        except Exception as e:
            print(f"   ❌ preskakujem {r.shortcode}: {e}")

    if not done:
        print("❌ ani jeden reel — vault nedotknutý")
        return

    print("📓 playbook (sonnet)...")
    playbook = build_playbook(niche, done, vault.read_playbook(niche))
    folder = vault.write_run(niche, handle, done, playbook)
    print(f"✅ Hotovo: {len(done)}/{len(reels)} poznámok → {folder}")


if __name__ == "__main__":
    main()
