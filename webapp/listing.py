"""Získanie zoznamu reel URL profilu. Instaloader (primárne) + ručný fallback."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def urls_from_text(text: str) -> list[str]:
    """Vytiahni reel URL z vloženého textu (linky alebo holé shortcode na riadok)."""
    text = text or ""
    found = re.findall(r"https?://[^\s\"']+/reel/[\w-]+", text)
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "http")) and re.fullmatch(r"[\w-]{5,}", line):
            found.append(f"https://www.instagram.com/reel/{line}/")
    seen, out = set(), []
    for u in found:
        u = u.rstrip("/") + "/"
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def list_reel_urls(handle: str, limit: int = 40) -> list[str]:
    """Zoznam reel URL cez Instaloader. Vyhodí výnimku ak IG blokuje (app to zachytí)."""
    import instaloader

    from reels_brain.config import IG_LOGIN
    from reels_brain.scraper import make_loader, parse_handle

    handle = parse_handle(handle)
    L = make_loader(IG_LOGIN)
    prof = instaloader.Profile.from_username(L.context, handle)
    urls = []
    for post in prof.get_posts():
        if post.is_video:
            urls.append(f"https://www.instagram.com/reel/{post.shortcode}/")
            if limit and len(urls) >= limit:
                break
    return urls
