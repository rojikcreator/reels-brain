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
