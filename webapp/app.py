"""Reels Brain — web app. Vlož IG username -> stiahne, prepíše, uloží. + vyhľadávač."""
import sys
import threading
from pathlib import Path

# Flask server má na Windowse cp1252 stdout — whisper/yt-dlp tlačia slovenčinu, tak prepneme na UTF-8
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ingest  # noqa: E402
import listing  # noqa: E402
import store  # noqa: E402
from reels_brain.scraper import parse_handle  # noqa: E402

app = Flask(__name__)
store.init_db()

JOB = {"running": False, "profile": "", "niche": "", "done": 0, "total": 0, "log": [], "error": ""}


def _run_job(handle: str, niche: str, urls: list[str]) -> None:
    JOB.update(running=True, profile=handle, niche=niche, done=0, total=len(urls), log=[], error="")
    for i, u in enumerate(urls, 1):
        try:
            rec = ingest.ingest_one(u, handle, niche)
            JOB["done"] = i
            JOB["log"].insert(0, f"{i}/{len(urls)} ✓ {rec['transcript'][:70]}…")
        except Exception as e:  # jeden pokazený reel nezhodí beh
            JOB["done"] = i
            JOB["log"].insert(0, f"{i}/{len(urls)} ✗ {u.split('/reel/')[-1].strip('/')}: {e}")
    JOB["running"] = False


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/stats")
def api_stats():
    return jsonify({"stats": store.stats(), "niches": store.niches()})


@app.get("/api/search")
def api_search():
    q = request.args.get("q", "")
    niche = request.args.get("niche") or None
    return jsonify(store.search(q, niche))


@app.post("/api/process")
def api_process():
    if JOB["running"]:
        return jsonify({"ok": False, "error": "Už beží spracovanie, počkaj kým dobehne."}), 409
    data = request.get_json(force=True)
    handle = parse_handle((data.get("username") or "").strip())
    niche = (data.get("niche") or "Nezaradené").strip() or "Nezaradené"
    pasted = (data.get("urls") or "").strip()

    if pasted:
        urls = listing.urls_from_text(pasted)
    elif handle:
        try:
            urls = listing.list_reel_urls(handle, limit=int(data.get("limit") or 40))
        except Exception as e:
            return jsonify({"ok": False, "needUrls": True,
                            "error": f"Instagram teraz nedovolí načítať zoznam ({str(e)[:120]}). "
                                     f"Vlož linky na reely ručne do poľa nižšie."})
    else:
        return jsonify({"ok": False, "error": "Zadaj username alebo vlož linky."})

    if not urls:
        return jsonify({"ok": False, "error": "Nenašiel som žiadne reely."})
    if not handle:
        handle = "manual"
    threading.Thread(target=_run_job, args=(handle, niche, urls), daemon=True).start()
    return jsonify({"ok": True, "total": len(urls)})


@app.get("/api/progress")
def api_progress():
    return jsonify(JOB)


@app.route("/api/upload_meta", methods=["POST", "OPTIONS"])
def api_upload_meta():
    """Prijme JSON s metadátami (zber z prehliadača) a uloží do docs/. CORS + PNA povolené."""
    resp_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Private-Network": "true",
    }
    if request.method == "OPTIONS":
        return ("", 204, resp_headers)
    name = request.args.get("name", "upload")
    safe = "".join(c for c in name if c.isalnum() or c in "-_")[:60] or "upload"
    path = Path(__file__).resolve().parents[1] / "docs" / f"{safe}.json"
    path.write_bytes(request.get_data())
    return (jsonify({"ok": True, "bytes": path.stat().st_size, "file": str(path)}), 200, resp_headers)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
