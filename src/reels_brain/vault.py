import re
from datetime import date
from pathlib import Path

from .config import BRAIN_SUBDIR, VAULT
from .models import Reel

_FORBIDDEN = '<>:"/\\|?*#[]^'


def sanitize(name: str) -> str:
    out = "".join(c for c in name if c not in _FORBIDDEN)
    out = " ".join(out.split())
    return out[:80].strip() or "bez nazvu"


def slug(name: str) -> str:
    trans = str.maketrans("áäčďéíĺľňóôŕšťúýž", "aacdeillnoorstuyz")
    s = name.lower().translate(trans)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "nezaradene"


def reel_note(reel: Reel, handle: str, niche: str) -> str:
    return f"""---
vytvorené: {date.today():%Y-%m-%d}
tagy: [reels, {slug(niche)}]
profil: "{handle}"
zdroj: {reel.url}
pozretia: {reel.views}
lajky: {reel.likes}
komentáre: {reel.comments}
dĺžka: {reel.duration:.0f}s
publikované: {reel.date:%Y-%m-%d}
---

{reel.anatomy}

## Transcript

{reel.transcript}

## Popis pod videom

{reel.caption or "—"}

---
Playbook niche: [[_PLAYBOOK {sanitize(niche)}]]
"""


def playbook_note(niche: str, playbook_md: str) -> str:
    return f"""---
vytvorené: {date.today():%Y-%m-%d}
aktualizované: {date.today():%Y-%m-%d}
tagy: [reels, playbook, {slug(niche)}]
---

{playbook_md}
"""


def _playbook_path(niche: str) -> Path:
    return VAULT / BRAIN_SUBDIR / sanitize(niche) / f"_PLAYBOOK {sanitize(niche)}.md"


def read_playbook(niche: str) -> str | None:
    p = _playbook_path(niche)
    return p.read_text(encoding="utf-8") if p.exists() else None


def _append_log(niche: str, handle: str, filenames: list[str]) -> None:
    log = VAULT / BRAIN_SUBDIR / "_LOG.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    if not log.exists():
        log.write_text("# Reels Brain — log importov\n", encoding="utf-8")
    entry = f"\n## {date.today():%Y-%m-%d} — @{handle} → {niche}\n"
    entry += "".join(f"- [[{name[:-3]}]]\n" for name in filenames)
    with log.open("a", encoding="utf-8") as fh:
        fh.write(entry)


def write_run(niche: str, handle: str, reels: list[Reel], playbook_md: str) -> Path:
    folder = VAULT / BRAIN_SUBDIR / sanitize(niche) / handle
    folder.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for r in reels:
        fname = f"{r.date:%Y-%m-%d} {sanitize(r.title or r.shortcode)}.md"
        (folder / fname).write_text(reel_note(r, handle, niche), encoding="utf-8")
        written.append(fname)
    _playbook_path(niche).write_text(playbook_note(niche, playbook_md), encoding="utf-8")
    _append_log(niche, handle, written)
    return folder
