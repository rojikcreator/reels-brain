from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Reel:
    shortcode: str
    url: str
    date: datetime          # UTC, aware
    views: int
    likes: int
    comments: int
    duration: float         # sekundy
    caption: str
    audio_path: Optional[Path] = None
    transcript: str = ""
    anatomy: str = ""       # markdown rozbor scenára (analyzer)
    title: str = ""         # krátky názov poznámky (analyzer)
    post: object = field(default=None, repr=False)  # instaloader.Post, aby sa nemusel fetchovať 2x
