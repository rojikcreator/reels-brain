"""Prehľadové poznámky Reels Brain: hub -> odvetvie -> prepisy (aby bol vault v Obsidiane poprepájaný).

Poznámky ležia v koreni Reels Brain (nie v priečinkoch odvetví), takže ich webapp index neberie ako prepisy.
Spustenie ručne: py -m reels_brain.index
"""
from datetime import date
from pathlib import Path

from .config import BRAIN_SUBDIR, VAULT

HUB = "Reels Brain"
PREFIX = f"{HUB} — "


def _link(md: Path, label: str) -> str:
    rel = md.relative_to(VAULT).with_suffix("").as_posix()
    return f"[[{rel}|{label}]]"


def _niche_note(niche_dir: Path) -> tuple[str, int]:
    niche = niche_dir.name
    extra = sorted(p for p in niche_dir.glob("*.md"))  # _PLAYBOOK, _ANALÝZA
    profiles = sorted(p for p in niche_dir.iterdir() if p.is_dir())
    lines = [
        "---",
        f"aktualizované: {date.today():%Y-%m-%d}",
        "tagy: [reels, prehlad]",
        "---",
        f"# {PREFIX}{niche}",
        "",
        f"Súčasť [[{HUB}]]. Generuje sa automaticky (`py -m reels_brain.index`), ručne neupravuj.",
        "",
    ]
    if extra:
        lines += ["## Rozbory", *[f"- {_link(p, p.stem)}" for p in extra], ""]
    total = 0
    for prof in profiles:
        notes = sorted(prof.glob("*.md"), reverse=True)
        if not notes:
            continue
        total += len(notes)
        lines += [f"## @{prof.name} ({len(notes)})", *[f"- {_link(n, n.stem)}" for n in notes], ""]
    return "\n".join(lines), total


def rebuild_index() -> int:
    root = VAULT / BRAIN_SUBDIR
    if not root.exists():
        return 0
    rows = []
    for niche_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        text, total = _niche_note(niche_dir)
        (root / f"{PREFIX}{niche_dir.name}.md").write_text(text, encoding="utf-8")
        rows.append((niche_dir.name, total))
    hub = [
        "---",
        f"aktualizované: {date.today():%Y-%m-%d}",
        "tagy: [reels, hub]",
        "---",
        f"# {HUB}",
        "",
        "Súčasť [[RojikCreator]]. Databáza prepisov IG reels podľa odvetví. Plní ju pipeline "
        "`C:\\Users\\jakub\\CODE CHAT\\reels-brain`, scenáre z nej píše skill `/scenar`.",
        "Generuje sa automaticky, ručne neupravuj.",
        "",
        "## Odvetvia",
        *[f"- [[{PREFIX}{n}|{n}]] — {t} prepisov" for n, t in rows],
        "",
        f"Spolu: **{sum(t for _, t in rows)} prepisov**. Log importov: [[_LOG]]",
        "",
    ]
    (root / f"{HUB}.md").write_text("\n".join(hub), encoding="utf-8")
    return sum(t for _, t in rows)


if __name__ == "__main__":
    print(f"Prehľady Reels Brain obnovené: {rebuild_index()} prepisov")
