import subprocess
from pathlib import Path

import instaloader

from .config import DOWNLOADS
from .models import Reel


def download_audio(L: instaloader.Instaloader, reel: Reel, handle: str) -> Path:
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
