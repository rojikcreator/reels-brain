import argparse
import sys

from .config import DAYS, TOP_N
from .pipeline import run


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(
        prog="reels-brain",
        description="IG profil → top reels → transcripty → Obsidian brain",
    )
    ap.add_argument("profile", help="URL alebo @handle Instagram profilu")
    ap.add_argument("--days", type=int, default=DAYS, help=f"okno v dňoch (default {DAYS})")
    ap.add_argument("--top", type=int, default=TOP_N, help=f"koľko top reels (default {TOP_N})")
    ap.add_argument("--dry-run", action="store_true", help="len rebríček, nič nesťahuje")
    ap.add_argument("--keep-media", action="store_true", help="nemazať stiahnuté audio")
    a = ap.parse_args()
    run(a.profile, days=a.days, top_n=a.top, dry_run=a.dry_run, keep_media=a.keep_media)


if __name__ == "__main__":
    main()
