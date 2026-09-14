"""Basic tests for the enrich stage (Stage 2 tracker matching)."""
import enrich


def test_is_tracker_matches_parent_domain():
    trackers = {"doubleclick.net"}
    assert enrich.is_tracker("stats.g.doubleclick.net", trackers) is True


def test_is_tracker_matches_exact_domain():
    trackers = {"google-analytics.com"}
    assert enrich.is_tracker("google-analytics.com", trackers) is True


def test_is_tracker_rejects_unlisted():
    trackers = {"doubleclick.net"}
    assert enrich.is_tracker("github.com", trackers) is False
