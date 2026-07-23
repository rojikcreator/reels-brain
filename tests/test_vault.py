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
