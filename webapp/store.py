"""SQLite full-text databaza prepisov (FTS5, diakritika-insensitive).

DB je lokalny index (rebuildovatelny) — zdroj pravdy su .md prepisy vo vaulte,
ktore sa syncuju gitom. `rebuild_from_vault()` postavi index na hociktorom stroji.
"""
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from reels_brain.config import BRAIN_SUBDIR, VAULT  # noqa: E402

DB_PATH = Path(__file__).resolve().parents[1] / "reels.db"
REELS_DIR = VAULT / BRAIN_SUBDIR


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS reels(
            shortcode TEXT PRIMARY KEY,
            profile   TEXT,
            niche     TEXT,
            url       TEXT,
            date      TEXT,
            likes     INTEGER,
            comments  INTEGER,
            caption   TEXT,
            transcript TEXT,
            added     TEXT
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS reels_fts USING fts5(
            shortcode UNINDEXED,
            profile, niche, caption, transcript,
            tokenize='unicode61 remove_diacritics 2'
        );
        """)


def upsert_reel(r: dict) -> None:
    """r: shortcode, profile, niche, url, date, likes, comments, caption, transcript."""
    with _conn() as c:
        c.execute("""
            INSERT INTO reels(shortcode,profile,niche,url,date,likes,comments,caption,transcript,added)
            VALUES(:shortcode,:profile,:niche,:url,:date,:likes,:comments,:caption,:transcript,:added)
            ON CONFLICT(shortcode) DO UPDATE SET
              profile=excluded.profile, niche=excluded.niche, url=excluded.url,
              date=excluded.date, likes=excluded.likes, comments=excluded.comments,
              caption=excluded.caption, transcript=excluded.transcript
        """, {**r, "added": r.get("added") or date.today().isoformat()})
        c.execute("DELETE FROM reels_fts WHERE shortcode=?", (r["shortcode"],))
        c.execute("""
            INSERT INTO reels_fts(shortcode,profile,niche,caption,transcript)
            VALUES(?,?,?,?,?)
        """, (r["shortcode"], r["profile"], r["niche"], r.get("caption", ""), r.get("transcript", "")))


def _fts_query(q: str) -> str:
    # kazde slovo ako prefix, implicitne AND; uvodzovky = presna fraza
    q = q.strip()
    if not q:
        return ""
    if '"' in q:
        return q
    words = re.findall(r"\w+", q, flags=re.UNICODE)
    return " ".join(f'"{w}"*' for w in words)


def search(q: str, niche: str | None = None, limit: int = 100) -> list[dict]:
    fts = _fts_query(q)
    with _conn() as c:
        if fts:
            sql = """
                SELECT r.*, snippet(reels_fts,4,'[[',']]','…',12) AS snippet
                FROM reels_fts f JOIN reels r ON r.shortcode=f.shortcode
                WHERE reels_fts MATCH ?
            """
            params: list = [fts]
        else:
            sql = "SELECT r.*, substr(r.transcript,1,160) AS snippet FROM reels r WHERE 1=1"
            params = []
        if niche:
            sql += " AND r.niche = ?"
            params.append(niche)
        sql += " ORDER BY " + ("rank" if fts else "r.date DESC") + " LIMIT ?"
        params.append(limit)
        return [dict(row) for row in c.execute(sql, params)]


def niches() -> list[dict]:
    with _conn() as c:
        return [dict(row) for row in c.execute(
            "SELECT niche, COUNT(*) AS n FROM reels GROUP BY niche ORDER BY n DESC")]


def stats() -> dict:
    with _conn() as c:
        row = c.execute("SELECT COUNT(*) n, COUNT(DISTINCT profile) p, COUNT(DISTINCT niche) k FROM reels").fetchone()
        return {"reels": row["n"], "profily": row["p"], "niche": row["k"]}


# ---------- rebuild indexu z .md prepisov vo vaulte ----------

def _frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
    return fm


def _section(text: str, header: str) -> str:
    m = re.search(rf"^##\s*{re.escape(header)}\s*\n(.*?)(?=\n##\s|\n---\s*\nPlaybook|\Z)",
                  text, re.DOTALL | re.MULTILINE)
    return m.group(1).strip() if m else ""


def _parse_note(path: Path, niche: str, handle: str) -> dict | None:
    text = path.read_text(encoding="utf-8")
    fm = _frontmatter(text)
    url = fm.get("zdroj", "")
    shortcode = url.rstrip("/").split("/")[-1] if url else path.stem
    transcript = _section(text, "Transcript")
    if not transcript:
        # novy format: telo je rovno prepis (medzi frontmatterom a "## Popis")
        body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
        transcript = re.split(r"\n##\s", body)[0].strip()
    caption = _section(text, "Popis pod videom")
    return {
        "shortcode": shortcode,
        "profile": fm.get("profil", handle),
        "niche": fm.get("niche", niche),
        "url": url,
        "date": fm.get("publikované", fm.get("vytvorené", "")),
        "likes": int(re.sub(r"\D", "", fm.get("lajky", "0")) or 0),
        "comments": int(re.sub(r"\D", "", fm.get("komentáre", "0")) or 0),
        "caption": caption,
        "transcript": transcript,
        "added": fm.get("vytvorené", ""),
    }


def rebuild_from_vault() -> int:
    init_db()
    with _conn() as c:
        c.execute("DELETE FROM reels")
        c.execute("DELETE FROM reels_fts")
    n = 0
    if not REELS_DIR.exists():
        return 0
    for niche_dir in REELS_DIR.iterdir():
        if not niche_dir.is_dir():
            continue
        niche = niche_dir.name
        for md in niche_dir.rglob("*.md"):
            if md.name.startswith("_PLAYBOOK") or md.name == "_LOG.md":
                continue
            handle = md.parent.name
            rec = _parse_note(md, niche, handle)
            if rec and rec["transcript"]:
                upsert_reel(rec)
                n += 1
    return n


if __name__ == "__main__":
    count = rebuild_from_vault()
    print(f"Index postaveny: {count} prepisov")
    print("Stats:", stats())
    print("Niche:", niches())
