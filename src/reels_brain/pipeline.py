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
