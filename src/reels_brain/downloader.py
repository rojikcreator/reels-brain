import subprocess
import sys
from pathlib import Path
from typing import Optional

import instaloader

from .config import DOWNLOADS
from .models import Reel


def _download_via_ytdlp(reel: Reel, handle: str) -> Optional[Path]:
    folder = DOWNLOADS / handle
    folder.mkdir(parents=True, exist_ok=True)

    out_template = str(folder / f"{reel.shortcode}.%(ext)s")
    result = subprocess.run(
        [
            sys.executable, "-m", "yt_dlp",
            "-f", "ba/b",
            "--no-playlist",
            "--quiet",
            "--no-warnings",
            "-o", out_template,
            reel.url,
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None

    candidates = sorted(folder.glob(f"{reel.shortcode}.*"))
    if not candidates:
        return None

    audio_path = candidates[0]
    reel.audio_path = audio_path
    return audio_path


def _download_via_instaloader(L: instaloader.Instaloader, reel: Reel, handle: str) -> Path:
    post = reel.post or instaloader.Post.from_shortcode(L.context, reel.shortcode)
    L.download_post(post, target=handle)

    folder = DOWNLOADS / handle
    mp4 = folder / f"{reel.shortcode}.mp4"
    if not mp4.exists():
        candidates = sorted(folder.glob(f"*{reel.shortcode}*.mp4"))
        if not candidates:
            raise FileNotFoundError(f"Video pre {reel.shortcode} sa nestiahlo do {folder}")
        mp4 = candidates[0]

    m4a = mp4.with_suffix(".m4a")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(mp4), "-vn", "-acodec", "copy", str(m4a)],
        check=True, capture_output=True,
    )
    mp4.unlink()
    reel.audio_path = m4a
    return m4a


def download_audio(L: instaloader.Instaloader, reel: Reel, handle: str) -> Path:
    folder = DOWNLOADS / handle
    folder.mkdir(parents=True, exist_ok=True)

    audio_path = _download_via_ytdlp(reel, handle)
    if audio_path is not None:
        return audio_path

    return _download_via_instaloader(L, reel, handle)
