# REELS BRAIN — Implementačný plán (Kniha)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Jeden príkaz `py -m reels_brain <instagram-profil>` stiahne metadáta reels za posledných 30 dní, vyberie 10 s najviac pozretiami, spraví transkripty, rozoberie scenáre a uloží ich ako prepojené poznámky do Obsidian brain vaultu — videá potom zmaže. Nadstavba: skill `/scenar`, ktorý z nazbieraného brainu píše nové virálne scenáre.

**Architecture:** Pipeline so 6 modulmi: scraper (Instaloader, len metadáta) → selector (top 10 podľa pozretí) → downloader (video → ffmpeg vytiahne audio → video sa hneď maže) → transcriber (lokálny faster-whisper) → analyzer (`claude -p`: Haiku klasifikuje niche, Sonnet rozoberá scenáre a skladá playbook) → vault writer (Obsidian poznámky s frontmatterom a wikilinkami). Nula externých API kľúčov — LLM beží cez Claude CLI subscription, whisper lokálne.

**Tech Stack:** Python 3.12 (winget), Instaloader, faster-whisper, ffmpeg (už nainštalovaný, 8.1.1), Claude CLI (`claude -p`), python-dotenv, pytest.

---

## Prečo presne takto (efektivita)

| Rozhodnutie | Prečo je to najefektívnejšie |
|---|---|
| Metadáta najprv, sťahovanie potom | Rebríček top 10 sa spraví **bez stiahnutia jediného videa**. Sťahuje sa len 10 víťazov, nie celý mesiac obsahu. |
| Video → audio → video zmazané hneď | Transcript potrebuje len zvuk. Video žije na disku pár sekúnd, audio (~1 MB/ks) len do konca behu. |
| Lokálny faster-whisper | 0 €. 10 reels ≈ 7 min audia ≈ pár minút prepisu na CPU. Rozumie slovenčine aj češtine. |
| `claude -p` namiesto Anthropic API | Ide cez existujúcu subscription — žiadny API kľúč, žiadne extra kredity. |
| Haiku na klasifikáciu, Sonnet na rozbory | Lacný model na triviálnu úlohu, silný model tam, kde vzniká hodnota (anatómia scenárov, playbook). |
| Playbook per niche | Destilát virálnych formúl sa hromadí naprieč profilmi tej istej niche — to je „tréning" agenta. |

Poznámka k nápadu „vytiahnuť scenár ešte pred stiahnutím": Instagram prepisy videí nevystavuje, takže audio treba mať. Toto je najbližšia možná verzia tej myšlienky — sťahuje sa absolútne minimum a žije to na disku absolútne minimum času.

## Obsah knihy

| Kapitola | Čo vznikne | Kto kóduje |
|---|---|---|
| 1. Základný tábor | Python, projekt, git repo, závislosti, IG login | **Haiku** |
| 2. Dátový model a config | `models.py`, `config.py`, `.env` | **Haiku** |
| 3. Scraper | Metadáta reels za 30 dní + výber top 10 (s testami) | **Sonnet** |
| 4. Downloader | Stiahnutie reelu, extrakcia audia, zmazanie videa | **Sonnet** |
| 5. Transcriber | faster-whisper prepis | **Sonnet** |
| 6. Analyzer | `claude -p` mozog: niche, anatómia scenára, playbook (s testami) | **Sonnet** |
| 7. Vault writer | Zápis do Obsidianu: poznámky, playbook, log (s testami) | **Sonnet** |
| 8. Pipeline a CLI | Orchestrácia, progress výpis, cleanup, `reels-brain` príkaz | **Sonnet** |
| 9. E2E overenie | Ostrý beh na reálnom profile, kontrola vaultu | **Opus + Jakub** |
| 10. Agent `/scenar` | Skill, ktorý píše nové scenáre z brainu | **Sonnet**, review Opus |

## Ako túto knihu použiť (návod pre Opus orchestrátora)

1. Prečítaj tento úvod a Globálne pravidlá. Potom choď kapitolu po kapitole, **v poradí**.
2. Na každú kapitolu dispatchni čerstvého subagenta (skill superpowers:subagent-driven-development) s **modelom podľa tabuľky vyššie** a s kompletným textom kapitoly v prompte. Subagent nevidí zvyšok knihy — kapitoly sú preto sebestačné.
3. Po každej kapitole: spusti testy, prezri diff, commitni. Až potom ďalšia kapitola.
4. Kapitola 9 je tvoja (orchestrátorova) — nedeleguj ju, spolupracuješ v nej s Jakubom.
5. Sám (ako Opus) nekóduj nič okrem review a opráv drobností — kódovanie je práca Sonneta/Haiku, šetríme kredity.

## Globálne pravidlá

Platia pre KAŽDÚ kapitolu; každý subagent ich musí dostať v prompte spolu s kapitolou.

- **Projekt:** `C:\Users\jakub\CODE CHAT\reels-brain` (git repo vznikne v kapitole 1). Windows 11, PowerShell.
- **Python volaj cez `py`** (`py -m pip ...`, `py -m pytest ...`) — alias `python` môže byť Windows Store stub.
- **Každé `open()`/`read_text()`/`write_text()` v Pythone MUSÍ mať `encoding="utf-8"`** — Windows default (cp1250) by rozbil diakritiku.
- **Vault:** `C:\Users\jakub\OneDrive\Počítač\Brain` — Obsidian, PARA. Zapisuje sa VÝHRADNE do `3-Zdroje\Reels Brain\`. Nikdy nie do `0-Inbox\_import\`. Poznámky po slovensky, frontmatter `vytvorené: RRRR-MM-DD` + `tagy:`. Secrety (heslá, kľúče) do vaultu NEPATRIA.
- **LLM volania výhradne cez `claude -p`** (Claude CLI, subscription). Žiadny `anthropic` SDK, žiadny API kľúč.
- **Heslá zadáva výhradne Jakub.** `instaloader --login` je interaktívny krok pre neho — agent ho nikdy nespúšťa s heslom.
- **ffmpeg 8.1.1 je už v PATH.** Python a pip k 2026-07-24 nainštalované NIE SÚ — rieši kapitola 1.
- Commit po každej kapitole (príkazy sú v krokoch). DRY, YAGNI, testy pred implementáciou tam, kde je logika čistá (bez siete).

## Súborová mapa (kde čo žije)

```
reels-brain/
├── pyproject.toml              # závislosti, entry point `reels-brain`, pytest config
├── .env                        # IG_LOGIN, VAULT_PATH (negituje sa)
├── .env.example
├── .gitignore
├── downloads/                  # dočasné médiá (negituje sa, po behu prázdne)
├── src/reels_brain/
│   ├── __init__.py
│   ├── __main__.py             # CLI (argparse) → pipeline.run
│   ├── config.py               # cesty, konštanty, .env
│   ├── models.py               # dataclass Reel
│   ├── scraper.py              # make_loader, parse_handle, fetch_reels, select_top
│   ├── downloader.py           # download_audio (video → m4a → video zmazané)
│   ├── transcriber.py          # transcribe (faster-whisper)
│   ├── analyzer.py             # ask_claude, classify_niche, analyze_reel, parse_title, build_playbook
│   ├── vault.py                # sanitize, slug, reel_note, write_run, _LOG.md
│   └── pipeline.py             # run() — orchestrácia celého behu
└── tests/
    ├── test_scraper.py
    ├── test_analyzer.py
    └── test_vault.py
```

Výstup vo vaulte po behu:

```
Brain/3-Zdroje/Reels Brain/
├── _LOG.md                                  # append-only log importov
└── Finančný poradca/                        # priečinok = niche (určí Haiku)
    ├── _PLAYBOOK Finančný poradca.md        # destilát virálnych formúl niche
    └── nazovprofilu/
        ├── 2026-07-20 Tri chyby s hypotékou.md
        └── ... (10 poznámok, každá: frontmatter + anatómia scenára + transcript)
```

---

### Kapitola 1: Základný tábor — prostredie a skeleton

**Model: Haiku**

**Files:**
- Create: `C:\Users\jakub\CODE CHAT\reels-brain\pyproject.toml`
- Create: `C:\Users\jakub\CODE CHAT\reels-brain\.gitignore`
- Create: `C:\Users\jakub\CODE CHAT\reels-brain\.env.example`
- Create: `C:\Users\jakub\CODE CHAT\reels-brain\src\reels_brain\__init__.py`

**Interfaces:**
- Consumes: nič (prvá kapitola).
- Produces: nainštalovaný Python 3.12 + balíky `instaloader`, `faster-whisper`, `python-dotenv`, `pytest`; git repo; editovateľná inštalácia balíka `reels_brain` (`pip install -e .`), takže ďalšie kapitoly môžu `from reels_brain.x import y`.

- [ ] **Krok 1: Nainštaluj Python 3.12**

```powershell
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
```

Potom **otvor nový terminál** (PATH sa načíta až v novom shelli) a over:

```powershell
py --version
```

Očakávané: `Python 3.12.x`. Ak `py` neexistuje, skús `python --version`; ak sa otvára Windows Store, vypni alias v Nastavenia → Aplikácie → Rozšírené nastavenia aplikácií → Aliasy spúšťania aplikácií, alebo použi plnú cestu `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`.

- [ ] **Krok 2: Vytvor skeleton projektu**

```powershell
New-Item -ItemType Directory -Force "C:\Users\jakub\CODE CHAT\reels-brain\src\reels_brain"
New-Item -ItemType Directory -Force "C:\Users\jakub\CODE CHAT\reels-brain\tests"
New-Item -ItemType Directory -Force "C:\Users\jakub\CODE CHAT\reels-brain\downloads"
```

- [ ] **Krok 3: Zapíš `pyproject.toml`**

```toml
[project]
name = "reels-brain"
version = "0.1.0"
description = "IG profil -> top reels -> transcripty -> Obsidian brain"
requires-python = ">=3.12"
dependencies = [
    "instaloader>=4.13",
    "faster-whisper>=1.1",
    "python-dotenv>=1.0",
]

[project.scripts]
reels-brain = "reels_brain.__main__:main"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Krok 4: Zapíš `.gitignore`**

```gitignore
__pycache__/
*.egg-info/
.pytest_cache/
.env
downloads/
*.mp4
*.m4a
```

- [ ] **Krok 5: Zapíš `.env.example`**

```ini
# Instagram login, ktorym je prihlaseny Instaloader (session vznikne cez `instaloader --login`)
IG_LOGIN=
# Cesta k Obsidian vaultu (default plati pre Jakuba)
VAULT_PATH=C:\Users\jakub\OneDrive\Počítač\Brain
# Whisper model: large-v3-turbo (najlepsi, ~1.6 GB) alebo small (rychly, ~460 MB)
WHISPER_MODEL=large-v3-turbo
```

- [ ] **Krok 6: Zapíš prázdny `src\reels_brain\__init__.py`** (prázdny súbor).

- [ ] **Krok 7: Git repo a prvý commit**

```powershell
cd "C:\Users\jakub\CODE CHAT\reels-brain"
git init
git add -A
git commit -m "chore: skeleton projektu reels-brain"
```

- [ ] **Krok 8: Nainštaluj závislosti**

```powershell
cd "C:\Users\jakub\CODE CHAT\reels-brain"
py -m pip install -e .
py -m pip install pytest
```

Očakávané: `Successfully installed ... reels-brain-0.1.0` (faster-whisper ťahá ctranslate2, ~150 MB — torch NEinštaluje). Over:

```powershell
py -c "import instaloader, faster_whisper, dotenv; print('OK')"
```

Očakávané: `OK`.

- [ ] **Krok 9: Over Claude CLI**

```powershell
claude --version
```

Očakávané: číslo verzie. Claude CLI je LLM engine pipeline — bez neho analyzer (kapitola 6) nebeží.

- [ ] **Krok 10: ⚠️ JEDINÝ MANUÁLNY KROK — Instagram login (robí Jakub, nie agent)**

Povedz Jakubovi, nech v termináli spustí (so SVOJÍM instagram loginom):

```powershell
instaloader --login=TVOJ_IG_LOGIN
```

Zadá heslo (+ 2FA ak má) — session sa uloží lokálne a ďalšie behy už login nepýtajú. Potom nech vytvorí `.env` (kópiou `.env.example`) a doplní `IG_LOGIN=`. **Agent heslo nikdy nezadáva a nevidí.** Bez loginu pipeline pobeží anonymne — funguje to horšie (rate limity, chýbajúce počty pozretí), ale nepadne.

- [ ] **Krok 11: Commit**

```powershell
git add -A
git commit -m "chore: zavislosti nainstalovane, env sablona"
```

---

### Kapitola 2: Dátový model a config

**Model: Haiku**

**Files:**
- Create: `src\reels_brain\models.py`
- Create: `src\reels_brain\config.py`

**Interfaces:**
- Consumes: `.env` z kapitoly 1.
- Produces: `Reel` dataclass (polia presne ako nižšie) a config konštanty `VAULT: Path`, `BRAIN_SUBDIR: str`, `IG_LOGIN: str`, `DAYS: int = 30`, `TOP_N: int = 10`, `WHISPER_MODEL/WHISPER_DEVICE/WHISPER_COMPUTE: str`, `CLAUDE_FAST = "haiku"`, `CLAUDE_SMART = "sonnet"`, `CLAUDE_TIMEOUT: int`, `DOWNLOADS: Path`. Všetky ďalšie kapitoly importujú odtiaľto.

- [ ] **Krok 1: Zapíš `src\reels_brain\models.py`**

```python
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
```

- [ ] **Krok 2: Zapíš `src\reels_brain\config.py`**

```python
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_DIR / ".env")

VAULT = Path(os.environ.get("VAULT_PATH", r"C:\Users\jakub\OneDrive\Počítač\Brain"))
BRAIN_SUBDIR = "3-Zdroje/Reels Brain"

IG_LOGIN = os.environ.get("IG_LOGIN", "")

DAYS = 30
TOP_N = 10

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "large-v3-turbo")
WHISPER_DEVICE = "cpu"      # kto má NVIDIA GPU, prepne na "cuda"
WHISPER_COMPUTE = "int8"    # na CPU najrýchlejšie; na "cuda" daj "float16"

CLAUDE_FAST = "haiku"       # klasifikácia niche
CLAUDE_SMART = "sonnet"     # anatómia scenárov, playbook
CLAUDE_TIMEOUT = 600        # sekúnd na jedno claude -p volanie

DOWNLOADS = PROJECT_DIR / "downloads"
```

- [ ] **Krok 3: Over importy**

```powershell
cd "C:\Users\jakub\CODE CHAT\reels-brain"
py -c "from reels_brain.config import VAULT, TOP_N; from reels_brain.models import Reel; print(VAULT, TOP_N)"
```

Očakávané: `C:\Users\jakub\OneDrive\Počítač\Brain 10`.

- [ ] **Krok 4: Commit**

```powershell
git add -A
git commit -m "feat: datovy model Reel a config"
```

---

### Kapitola 3: Scraper — metadáta a výber top 10

**Model: Sonnet**

**Files:**
- Create: `src\reels_brain\scraper.py`
- Test: `tests\test_scraper.py`

**Interfaces:**
- Consumes: `Reel` z `reels_brain.models`; `IG_LOGIN`, `DOWNLOADS` z `reels_brain.config`.
- Produces:
  - `make_loader(ig_login: str) -> instaloader.Instaloader` — jediná inštancia loadera pre celý beh (metadáta AJ sťahovanie).
  - `parse_handle(s: str) -> str` — z URL/`@handle`/handle spraví čistý handle.
  - `fetch_reels(L, handle: str, days: int) -> tuple[str, list[Reel]]` — (bio profilu, reels za posledných `days` dní, nezoradené).
  - `select_top(reels: list[Reel], top_n: int) -> list[Reel]` — top N podľa `views` zostupne.

- [ ] **Krok 1: Napíš zlyhávajúce testy `tests\test_scraper.py`**

```python
from datetime import datetime, timezone

from reels_brain.models import Reel
from reels_brain.scraper import parse_handle, select_top


def make_reel(shortcode="abc", views=0):
    return Reel(
        shortcode=shortcode, url="u",
        date=datetime(2026, 7, 1, tzinfo=timezone.utc),
        views=views, likes=0, comments=0, duration=30.0, caption="",
    )


def test_parse_handle_from_url():
    assert parse_handle("https://www.instagram.com/finance.guru/") == "finance.guru"


def test_parse_handle_from_url_with_tab_and_query():
    assert parse_handle("https://www.instagram.com/finance.guru/reels/?hl=en") == "finance.guru"


def test_parse_handle_plain_and_at():
    assert parse_handle("@finance.guru") == "finance.guru"
    assert parse_handle("finance.guru") == "finance.guru"


def test_select_top_sorts_by_views_desc():
    reels = [make_reel("a", 100), make_reel("b", 300), make_reel("c", 200)]
    assert [r.shortcode for r in select_top(reels, 10)] == ["b", "c", "a"]


def test_select_top_limits_count():
    reels = [make_reel(str(i), i) for i in range(20)]
    assert len(select_top(reels, 10)) == 10


def test_select_top_empty():
    assert select_top([], 10) == []
```

- [ ] **Krok 2: Spusti testy — musia zlyhať**

```powershell
cd "C:\Users\jakub\CODE CHAT\reels-brain"
py -m pytest tests\test_scraper.py -v
```

Očakávané: FAIL / collection error — `scraper` neexistuje.

- [ ] **Krok 3: Zapíš `src\reels_brain\scraper.py`**

```python
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
```

- [ ] **Krok 4: Spusti testy — musia prejsť**

```powershell
py -m pytest tests\test_scraper.py -v
```

Očakávané: 6 passed.

- [ ] **Krok 5: Commit**

```powershell
git add -A
git commit -m "feat: scraper metadat a vyber top 10"
```

---

### Kapitola 4: Downloader — video → audio

**Model: Sonnet**

**Files:**
- Create: `src\reels_brain\downloader.py`

**Interfaces:**
- Consumes: `Reel` (s vyplneným `post`) z kapitoly 3; loader z `make_loader`; `DOWNLOADS` z configu; ffmpeg v PATH.
- Produces: `download_audio(L, reel: Reel, handle: str) -> Path` — stiahne reel do `downloads\<handle>\<shortcode>.mp4`, ffmpeg-om vytiahne zvukovú stopu do `.m4a` (bez re-enkódovania, `-acodec copy`), `.mp4` hneď zmaže a vráti cestu k `.m4a`.

- [ ] **Krok 1: Zapíš `src\reels_brain\downloader.py`**

```python
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
```

- [ ] **Krok 2: Smoke test importu** (sieťová logika sa ostro overí v kapitole 9)

```powershell
cd "C:\Users\jakub\CODE CHAT\reels-brain"
py -c "from reels_brain.downloader import download_audio; print('OK')"
```

Očakávané: `OK`.

- [ ] **Krok 3: Commit**

```powershell
git add -A
git commit -m "feat: downloader s extrakciou audia"
```

---

### Kapitola 5: Transcriber — whisper

**Model: Sonnet**

**Files:**
- Create: `src\reels_brain\transcriber.py`

**Interfaces:**
- Consumes: `WHISPER_MODEL`, `WHISPER_DEVICE`, `WHISPER_COMPUTE` z configu; `.m4a` súbor z kapitoly 4.
- Produces: `transcribe(audio: Path) -> str` — čistý text prepisu (jedna súvislá reťaz, normalizované medzery). Model sa nahráva lenivo a len raz na proces.

- [ ] **Krok 1: Zapíš `src\reels_brain\transcriber.py`**

```python
from pathlib import Path

from faster_whisper import WhisperModel

from .config import WHISPER_COMPUTE, WHISPER_DEVICE, WHISPER_MODEL

_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        print(f"   (nahrávam whisper model {WHISPER_MODEL} — prvýkrát sa sťahuje, ~1.6 GB)")
        _model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE)
    return _model


def transcribe(audio: Path) -> str:
    segments, _info = _get_model().transcribe(str(audio), vad_filter=True)
    text = " ".join(seg.text.strip() for seg in segments)
    return " ".join(text.split())
```

- [ ] **Krok 2: Smoke test importu** (ostrý prepis reálneho audia je súčasť kapitoly 9; model sa nesťahuje zbytočne vopred)

```powershell
cd "C:\Users\jakub\CODE CHAT\reels-brain"
py -c "from reels_brain.transcriber import transcribe; print('OK')"
```

Očakávané: `OK`.

- [ ] **Krok 3: Commit**

```powershell
git add -A
git commit -m "feat: transcriber faster-whisper"
```

---

### Kapitola 6: Analyzer — Claude mozog

**Model: Sonnet**

**Files:**
- Create: `src\reels_brain\analyzer.py`
- Test: `tests\test_analyzer.py`

**Interfaces:**
- Consumes: `Reel` z models; `CLAUDE_FAST`, `CLAUDE_SMART`, `CLAUDE_TIMEOUT` z configu; `claude` CLI v PATH.
- Produces:
  - `ask_claude(prompt: str, model: str) -> str` — spustí `claude -p --model <model>`, prompt cez stdin, vráti stdout. `RuntimeError` pri zlyhaní.
  - `classify_niche(bio: str, reels: list[Reel]) -> str` — názov niche po slovensky (Haiku), pri chybe `"Nezaradené"`.
  - `analyze_reel(reel: Reel, handle: str, niche: str) -> str` — surový markdown rozbor (Sonnet), prvý riadok `NÁZOV: ...`.
  - `parse_title(anatomy: str, fallback: str) -> tuple[str, str]` — (názov, telo bez riadku NÁZOV); pri chýbajúcom názve (fallback, pôvodný text).
  - `build_playbook(niche: str, reels: list[Reel], existing: str | None) -> str` — nový alebo aktualizovaný playbook niche (Sonnet).

- [ ] **Krok 1: Napíš zlyhávajúce testy `tests\test_analyzer.py`**

```python
from reels_brain.analyzer import parse_title


def test_parse_title_extracts_title_and_body():
    raw = "NÁZOV: Tri chyby s hypotékou\n\n## Hook\ntext"
    title, body = parse_title(raw, "fallback")
    assert title == "Tri chyby s hypotékou"
    assert body.startswith("## Hook")


def test_parse_title_missing_uses_fallback():
    raw = "## Hook\nniečo"
    title, body = parse_title(raw, "fallback")
    assert title == "fallback"
    assert body == raw


def test_parse_title_case_and_diacritics_insensitive():
    title, _ = parse_title("nazov: Test video\ntelo", "f")
    assert title == "Test video"


def test_parse_title_empty_title_uses_fallback():
    title, _ = parse_title("NÁZOV:\ntelo", "f")
    assert title == "f"
```

- [ ] **Krok 2: Spusti testy — musia zlyhať**

```powershell
cd "C:\Users\jakub\CODE CHAT\reels-brain"
py -m pytest tests\test_analyzer.py -v
```

Očakávané: FAIL / collection error — `analyzer` neexistuje.

- [ ] **Krok 3: Zapíš `src\reels_brain\analyzer.py`**

```python
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
```

- [ ] **Krok 4: Spusti testy — musia prejsť**

```powershell
py -m pytest tests\test_analyzer.py -v
```

Očakávané: 4 passed.

- [ ] **Krok 5: Ostrý mini-test `ask_claude`**

```powershell
py -c "from reels_brain.analyzer import ask_claude; print(ask_claude('Odpovedz jednym slovom: ahoj', 'haiku'))"
```

Očakávané: krátka odpoveď (napr. `Ahoj`). Ak zlyhá, over `claude --version` a prihlásenie Claude CLI.

- [ ] **Krok 6: Commit**

```powershell
git add -A
git commit -m "feat: analyzer - niche, anatomia scenara, playbook cez claude -p"
```

---

### Kapitola 7: Vault writer — zápis do brainu

**Model: Sonnet**

**Files:**
- Create: `src\reels_brain\vault.py`
- Test: `tests\test_vault.py`

**Interfaces:**
- Consumes: `Reel` z models; `VAULT`, `BRAIN_SUBDIR` z configu.
- Produces:
  - `sanitize(name: str) -> str` — bezpečný názov súboru (bez `<>:"/\|?*#[]^`, zbalené medzery, max 80 znakov, fallback `"bez nazvu"`).
  - `slug(name: str) -> str` — kebab-case bez diakritiky pre tagy.
  - `reel_note(reel: Reel, handle: str, niche: str) -> str` — markdown poznámky (frontmatter + anatómia + transcript + wikilink na playbook).
  - `playbook_note(niche: str, playbook_md: str) -> str` — playbook s frontmatterom.
  - `read_playbook(niche: str) -> str | None` — existujúci playbook niche, ak je.
  - `write_run(niche: str, handle: str, reels: list[Reel], playbook_md: str) -> Path` — zapíše všetko do vaultu, doplní `_LOG.md`, vráti priečinok profilu.

- [ ] **Krok 1: Napíš zlyhávajúce testy `tests\test_vault.py`**

```python
from datetime import datetime, timezone

from reels_brain.models import Reel
from reels_brain.vault import reel_note, sanitize, slug


def test_sanitize_removes_forbidden_chars():
    assert sanitize('Ako: na "hypo"? <video>') == "Ako na hypo video"


def test_sanitize_empty_falls_back():
    assert sanitize("???") == "bez nazvu"


def test_sanitize_trims_length():
    assert len(sanitize("x" * 300)) <= 80


def test_slug_strips_diacritics():
    assert slug("Finančný poradca") == "financny-poradca"


def test_reel_note_contains_data():
    r = Reel(
        shortcode="x", url="https://www.instagram.com/reel/x/",
        date=datetime(2026, 7, 20, tzinfo=timezone.utc),
        views=12345, likes=10, comments=2, duration=31.2, caption="popis",
    )
    r.transcript = "ahoj svet"
    r.anatomy = "## Hook\nsuper"
    note = reel_note(r, "profil", "Finančný poradca")
    assert note.startswith("---\n")
    assert "pozretia: 12345" in note
    assert "ahoj svet" in note
    assert "[[_PLAYBOOK Finančný poradca]]" in note
```

- [ ] **Krok 2: Spusti testy — musia zlyhať**

```powershell
cd "C:\Users\jakub\CODE CHAT\reels-brain"
py -m pytest tests\test_vault.py -v
```

Očakávané: FAIL / collection error — `vault` neexistuje.

- [ ] **Krok 3: Zapíš `src\reels_brain\vault.py`**

```python
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
```

- [ ] **Krok 4: Spusti testy — musia prejsť**

```powershell
py -m pytest tests\test_vault.py -v
```

Očakávané: 5 passed.

- [ ] **Krok 5: Commit**

```powershell
git add -A
git commit -m "feat: vault writer pre Obsidian brain"
```

---

### Kapitola 8: Pipeline a CLI

**Model: Sonnet**

**Files:**
- Create: `src\reels_brain\pipeline.py`
- Create: `src\reels_brain\__main__.py`

**Interfaces:**
- Consumes: všetko z kapitol 2–7 (presné signatúry: `make_loader(ig_login)`, `parse_handle(s)`, `fetch_reels(L, handle, days)`, `select_top(reels, top_n)`, `download_audio(L, reel, handle)`, `transcribe(audio)`, `classify_niche(bio, reels)`, `analyze_reel(reel, handle, niche)`, `parse_title(anatomy, fallback)`, `build_playbook(niche, reels, existing)`, `vault.read_playbook(niche)`, `vault.write_run(niche, handle, reels, playbook_md)`).
- Produces: `run(profile_input, days, top_n, dry_run, keep_media)` a CLI `py -m reels_brain <profil> [--days N] [--top N] [--dry-run] [--keep-media]` (aj alias `reels-brain` z pyproject entry pointu).

- [ ] **Krok 1: Zapíš `src\reels_brain\pipeline.py`**

```python
import shutil

from . import vault
from .analyzer import analyze_reel, build_playbook, classify_niche, parse_title
from .config import DAYS, DOWNLOADS, IG_LOGIN, TOP_N
from .downloader import download_audio
from .scraper import fetch_reels, make_loader, parse_handle, select_top
from .transcriber import transcribe


def run(profile_input: str, days: int = DAYS, top_n: int = TOP_N,
        dry_run: bool = False, keep_media: bool = False) -> None:
    handle = parse_handle(profile_input)
    print(f"📡 @{handle} — čítam metadáta reels za posledných {days} dní...")
    L = make_loader(IG_LOGIN)
    bio, reels = fetch_reels(L, handle, days)
    print(f"   nájdených {len(reels)} reels")

    top = select_top(reels, top_n)
    for i, r in enumerate(top, 1):
        print(f"   {i:2}. {r.views:>10,} 👁  {r.date:%d.%m.}  {r.caption[:60]!r}")
    if not top:
        print("⚠️  žiadne reels za dané obdobie — končím")
        return
    if dry_run:
        print("(dry-run: končím pred sťahovaním)")
        return

    print("🧠 určujem niche (haiku)...")
    niche = classify_niche(bio, top)
    print(f"   → {niche}")

    done: list = []
    for i, r in enumerate(top, 1):
        try:
            print(f"🎬 [{i}/{len(top)}] {r.shortcode}: sťahujem a vyťahujem audio...")
            audio = download_audio(L, r, handle)
            print("   ✍️  prepisujem (whisper)...")
            r.transcript = transcribe(audio)
            print("   🔬 rozbor scenára (sonnet)...")
            raw = analyze_reel(r, handle, niche)
            r.title, r.anatomy = parse_title(raw, r.shortcode)
            done.append(r)
        except Exception as e:  # jeden pokazený reel nezhodí celý beh
            print(f"   ❌ preskakujem {r.shortcode}: {e}")

    if not done:
        print("❌ nepodarilo sa spracovať ani jeden reel — vault nechávam nedotknutý")
        return

    print("📓 skladám playbook niche (sonnet)...")
    playbook = build_playbook(niche, done, vault.read_playbook(niche))
    folder = vault.write_run(niche, handle, done, playbook)

    if not keep_media:
        shutil.rmtree(DOWNLOADS / handle, ignore_errors=True)
        print("🧹 stiahnuté médiá zmazané")

    print(f"✅ Hotovo: {len(done)}/{len(top)} poznámok → {folder}")
```

- [ ] **Krok 2: Zapíš `src\reels_brain\__main__.py`**

```python
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
```

- [ ] **Krok 3: Over CLI help + celý testovací balík**

```powershell
cd "C:\Users\jakub\CODE CHAT\reels-brain"
py -m reels_brain --help
py -m pytest -v
```

Očakávané: help s argumentmi `profile, --days, --top, --dry-run, --keep-media`; 15 testov passed.

- [ ] **Krok 4: Commit**

```powershell
git add -A
git commit -m "feat: pipeline a CLI"
```

---

### Kapitola 9: E2E overenie na reálnom profile

**Model: Opus (orchestrátor sám, spolu s Jakubom)** — REQUIRED SUB-SKILL: superpowers:verification-before-completion

- [ ] **Krok 1: Vypýtaj si od Jakuba reálny profil** (napr. slovenský finančný poradca, ktorého sleduje). Ak žiadny nedá, použi na test verejný SK/CZ profil s reels, ktorý sám nájde.

- [ ] **Krok 2: Dry-run — over scraper bez sťahovania**

```powershell
cd "C:\Users\jakub\CODE CHAT\reels-brain"
py -m reels_brain @PROFIL --dry-run
```

Očakávané: zoznam reels za 30 dní s počtami pozretí, zoradený zostupne, max 10 riadkov. Ak sú pozretia 0 pri všetkých, session nie je prihlásená — vráť sa ku kapitole 1, krok 10. Ak v zozname chýbajú reels, ktoré na profile v tabe Reels vidno, profil ich nezdieľa do gridu — vtedy v `fetch_reels` vymeň `profile.get_posts()` za `profile.get_reels()` (novšie verzie Instaloaderu tab Reels iterujú priamo; over `hasattr(profile, "get_reels")`).

- [ ] **Krok 3: Ostrý beh**

```powershell
py -m reels_brain @PROFIL
```

Očakávané poradie výpisu: 📡 metadáta → rebríček → 🧠 niche → 10× (🎬 → ✍️ → 🔬) → 📓 playbook → 🧹 → ✅ s cestou do vaultu. Prvý beh sťahuje whisper model (~1.6 GB) — trpezlivosť.

- [ ] **Krok 4: Over vault**

```powershell
Get-ChildItem -Recurse "C:\Users\jakub\OneDrive\Počítač\Brain\3-Zdroje\Reels Brain"
```

Skontroluj: priečinok niche má zmysluplný slovenský názov; v ňom `_PLAYBOOK <niche>.md` + priečinok profilu s ~10 poznámkami; existuje `_LOG.md`. Otvor jednu poznámku (Read) a over: frontmatter s `vytvorené/tagy/pozretia`, diakritika v poriadku (žiadne `Ã¡`), sekcie NÁZOV-less anatómia / Transcript / Popis, wikilink na playbook. Otvor playbook: má sekcie Hooky/Štruktúry/CTA/Chyby/Checklist.

- [ ] **Krok 5: Over cleanup**

```powershell
Get-ChildItem "C:\Users\jakub\CODE CHAT\reels-brain\downloads" -Recurse
```

Očakávané: prázdne (žiadne .mp4/.m4a).

- [ ] **Krok 6: Ukáž Jakubovi jednu poznámku + playbook a commitni**

```powershell
git add -A
git commit -m "test: E2E beh na realnom profile overeny"
```

---

### Kapitola 10: Agent `/scenar` — payoff

**Model: Sonnet, review Opus**

**Files:**
- Create: `C:\Users\jakub\.claude\skills\scenar\SKILL.md`

**Interfaces:**
- Consumes: vault `3-Zdroje\Reels Brain\` naplnený kapitolou 9.
- Produces: globálny skill `/scenar` — píše nové Reels scenáre natrénované na playbookoch a rozboroch z vaultu, a učí sa z Jakubovho feedbacku.

- [ ] **Krok 1: Zapíš `C:\Users\jakub\.claude\skills\scenar\SKILL.md`**

```markdown
---
name: scenar
description: Napíš virálny Reels scenár natrénovaný na Reels Brain vaulte. Použi keď používateľ chce scenár/skript/hook na reels alebo nápady na video („napíš mi scenár na...", „daj hook na...", „nápady na reels o...").
---

# Scenárista

Píšeš scenáre pre krátke videá (Reels) natrénované na reálnych virálnych videách z vaultu.

## Zdroj pravdy

- Priečinok: `C:\Users\jakub\OneDrive\Počítač\Brain\3-Zdroje\Reels Brain\`
- Každá niche má priečinok s `_PLAYBOOK <niche>.md` a podpriečinky profilov s rozbormi jednotlivých videí.

## Postup

1. Zisti tému a niche. Ak niche nie je jasná z požiadavky, vypíš dostupné priečinky
   (`Get-ChildItem`) a spýtaj sa jednou vetou.
2. Načítaj `_PLAYBOOK` danej niche + 3–5 rozborov najrelevantnejších k téme
   (vyberaj podľa názvov poznámok a počtu pozretí vo frontmatteri).
3. Napíš **3 varianty scenára** s rôznymi typmi hookov. Formát každého variantu:
   - **HOOK** (0–3 s) — presný text + čo je v obraze
   - **TELO** — voiceover po strihoch (riadok = strih), open loop minimálne jeden
   - **CTA** (posledné 2–3 s)
   - **B-ROLL** — 3–5 návrhov záberov
4. Drž sa formúl z playbooku; texty konkurencie nikdy nekopíruj doslovne.
5. Pod scenáre napíš, z ktorých poznámok si čerpal ([[wikilinky]]).
6. Keď Jakub povie, že niektorý scenár/hook zabral (video malo výsledky), dopíš ten
   poznatok do `_PLAYBOOK` príslušnej niche (sekcia Hooky alebo Štruktúry) —
   takto sa agent tréningom zlepšuje.

## Pravidlá

- Slovenčina, hovorová, žiadne korporátne frázy ani motivačný balast.
- Hook max 8 slov. Scenár na 30–45 s ≈ 80–110 slov voiceoveru.
- Zápis do vaultu len do `3-Zdroje\Reels Brain\`, vždy `encoding utf-8`.
```

- [ ] **Krok 2: Over, že skill funguje**

Spusti `/scenar` s testovacou požiadavkou, napr.: „napíš mi scenár na reels o tom, prečo si ľudia zle nastavujú hypotéku". Očakávané: skill načíta playbook + rozbory z vaultu a vráti 3 varianty scenára vo formáte HOOK/TELO/CTA/B-ROLL s wikilinkami na zdroje.

- [ ] **Krok 3: Zapíš `README.md` do repa (Write tool, UTF-8) a commitni**

Obsah `C:\Users\jakub\CODE CHAT\reels-brain\README.md`:

```markdown
# Reels Brain

IG profil → top 10 reels za 30 dní → transcripty → Obsidian brain.

Použitie: `py -m reels_brain @profil` (alebo `reels-brain @profil`)

Agent na scenáre: skill `/scenar` (globálny, v `~/.claude/skills/scenar`).
```

```powershell
cd "C:\Users\jakub\CODE CHAT\reels-brain"
git add -A
git commit -m "docs: README + skill /scenar"
```

---

## Záver: prevádzka a ďalšie levely

**Denná prevádzka:** jeden príkaz na profil — `py -m reels_brain @profil`. Každý ďalší profil tej istej niche playbook obohacuje (analyzer ho aktualizuje, nezahadzuje). Scenáre potom píše `/scenar`; keď niečo zaberie, povedz to `/scenar` a zapíše si to do playbooku — to je tréningová slučka.

**Ak niečo padá:** najčastejšie je to Instagram rate-limit (Instaloader sám čaká a opakuje — nechať bežať) alebo odhlásená session (`instaloader --login=...` znova, robí Jakub).

**Ďalšie levely (mimo scope tejto knihy, len nápady):**
- Týždenný automatický beh cez skill `/schedule` na obľúbené profily.
- Rozšírenie na TikTok/YouTube Shorts (yt-dlp vie oboje; selector, transcriber, analyzer a vault sa nemenia).
- `--top 20` a `--days 90` pre hlbší tréning niche.
