from datetime import datetime, timedelta, timezone

import instaloader

from .config import DOWNLOADS
from .models import Reel

# Pripnuté posty vedia byť na vrchu feedu mimo chronológie — starý post preto
# nezastaví iteráciu hneď, až séria po sebe idúcich starých postov.
STOP_AFTER_OLD = 5


def make_loader(ig_login: str) -> instaloader.Instaloader:
    L = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_video_thumbnails=False,
        save_metadata=False,
        download_comments=False,
        post_metadata_txt_pattern="",
        dirname_pattern=str(DOWNLOADS / "{target}"),
        filename_pattern="{shortcode}",
    )
    if ig_login:
        try:
            L.load_session_from_file(ig_login)
        except FileNotFoundError:
            raise SystemExit(
                f"Chýba Instaloader session pre '{ig_login}'. "
                f"Spusti raz: instaloader --login={ig_login}"
            )
    return L


def parse_handle(s: str) -> str:
    s = s.strip().rstrip("/")
    if "instagram.com" in s:
        s = s.split("instagram.com/")[-1]
        s = s.split("/")[0].split("?")[0]
    return s.lstrip("@")


def fetch_reels(L: instaloader.Instaloader, handle: str, days: int) -> tuple[str, list[Reel]]:
    profile = instaloader.Profile.from_username(L.context, handle)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    reels: list[Reel] = []
    old_streak = 0
    for post in profile.get_posts():
        post_date = post.date_utc.replace(tzinfo=timezone.utc)
        if post_date < cutoff:
            old_streak += 1
            if old_streak >= STOP_AFTER_OLD:
                break
            continue
        old_streak = 0
        if not post.is_video:
            continue
        reels.append(Reel(
            shortcode=post.shortcode,
            url=f"https://www.instagram.com/reel/{post.shortcode}/",
            date=post_date,
            # reels mávajú počet prehratí niekedy v inom poli než bežné videá
            views=post.video_view_count or getattr(post, "video_play_count", 0) or 0,
            likes=post.likes or 0,
            comments=post.comments or 0,
            duration=post.video_duration or 0.0,
            caption=(post.caption or "")[:500],
            post=post,
        ))
    return profile.biography or "", reels


def select_top(reels: list[Reel], top_n: int) -> list[Reel]:
    return sorted(reels, key=lambda r: r.views, reverse=True)[:top_n]
