import shutil
import subprocess

from .config import CLAUDE_FAST, CLAUDE_SMART, CLAUDE_TIMEOUT
from .models import Reel

NICHE_PROMPT = """Urč niche tohto Instagram profilu podľa bio a popisov videí.

BIO: {bio}

POPISY VIDEÍ:
{captions}

Odpovedz IBA názvom niche po slovensky, 1-4 slová, bez úvodzoviek a bez bodky.
Príklady dobrých odpovedí: Finančný poradca / Fitness tréner / Realitný maklér / Osobný rozvoj"""

ANATOMY_PROMPT = """Si expert na virálny copywriting Reels videí. Dostaneš transcript virálneho videa a metadáta.

METADÁTA:
- Profil: @{handle} (niche: {niche})
- Pozretia: {views:,} | Lajky: {likes:,} | Komentáre: {comments:,}
- Dĺžka: {duration:.0f} s
- Popis pod videom: {caption}

TRANSCRIPT:
{transcript}

Rozober scenár tohto videa. Odpovedz PRESNE v tomto formáte (markdown, po slovensky):

NÁZOV: <3-6 slov vystihujúcich video>

## Hook (prvé 1-3 sekundy)
<citácia hooku + typ hooku (otázka/šok/kontrarián/číslo/príbeh...) + prečo zastaví scroll>

## Stavba a retention
<ako je video vystavané, open loops, tempo, čo drží diváka do konca>

## CTA
<aká je výzva na akciu a kde je umiestnená; ak nie je, napíš že chýba>

## Formula na reuse
<zovšeobecnená šablóna scenára s [placeholdermi], použiteľná na inú tému v tej istej niche>

## Prečo malo {views:,} pozretí
<2-4 vety, hlavné dôvody virality>"""

PLAYBOOK_PROMPT = """Si tréner virálneho copywritingu. Nižšie sú rozbory {count} najvirálnejších Reels z niche „{niche}".
{existing_section}
ROZBORY:
{anatomies}

Vytvor {update_or_new} PLAYBOOK tejto niche — destilát toho, čo v nej virálne funguje.
Odpovedz IBA markdownom playbooku, po slovensky, presne v tejto štruktúre:

# Playbook: {niche}

## Hooky ktoré fungujú
<typy hookov + konkrétne príklady z rozborov>

## Štruktúry videí
<opakujúce sa formuly, každá ako šablóna s [placeholdermi]>

## CTA vzorce

## Časté chyby / čo virálne videá nerobia

## Checklist pred natočením
<7-10 bodov>"""


def ask_claude(prompt: str, model: str) -> str:
    exe = shutil.which("claude")
    if not exe:
        raise RuntimeError("claude CLI nie je v PATH")
    r = subprocess.run(
        [exe, "-p", "--model", model],
        input=prompt, capture_output=True, text=True,
        encoding="utf-8", timeout=CLAUDE_TIMEOUT,
    )
    if r.returncode != 0:
        raise RuntimeError(f"claude -p zlyhalo ({model}): {(r.stderr or '')[:500]}")
    out = (r.stdout or "").strip()
    if not out:
        raise RuntimeError(f"claude -p ({model}) vrátilo prázdnu odpoveď")
    return out


def classify_niche(bio: str, reels: list[Reel]) -> str:
    captions = "\n".join(f"- {r.caption[:150]}" for r in reels if r.caption) or "—"
    prompt = NICHE_PROMPT.format(bio=bio or "—", captions=captions)
    try:
        out = ask_claude(prompt, CLAUDE_FAST)
    except RuntimeError:
        return "Nezaradené"
    lines = [line.strip().strip('"') for line in out.splitlines() if line.strip()]
    return lines[-1][:60] if lines else "Nezaradené"


def analyze_reel(reel: Reel, handle: str, niche: str) -> str:
    prompt = ANATOMY_PROMPT.format(
        handle=handle, niche=niche, views=reel.views, likes=reel.likes,
        comments=reel.comments, duration=reel.duration,
        caption=reel.caption or "—", transcript=reel.transcript,
    )
    return ask_claude(prompt, CLAUDE_SMART)


def parse_title(anatomy: str, fallback: str) -> tuple[str, str]:
    lines = anatomy.strip().splitlines()
    if lines:
        first = lines[0].strip()
        low = first.lower()
        if low.startswith("názov:") or low.startswith("nazov:"):
            title = first.split(":", 1)[1].strip().strip('"')
            body = "\n".join(lines[1:]).lstrip("\n")
            if title:
                return title, body
    return fallback, anatomy


def build_playbook(niche: str, reels: list[Reel], existing: str | None) -> str:
    anatomies = "\n\n---\n\n".join(
        f"### {r.title} ({r.views:,} pozretí)\n{r.anatomy}" for r in reels
    )
    existing_section = (
        f"\nEXISTUJÚCI PLAYBOOK (aktualizuj ho, staré poznatky nezahadzuj):\n{existing}\n"
        if existing else ""
    )
    prompt = PLAYBOOK_PROMPT.format(
        count=len(reels), niche=niche, existing_section=existing_section,
        anatomies=anatomies, update_or_new="AKTUALIZOVANÝ" if existing else "NOVÝ",
    )
    return ask_claude(prompt, CLAUDE_SMART)
