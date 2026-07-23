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
