"""Tests for the Pre-Filter module."""
from src.pre_filter import PreFilter
from src.feed_fetcher import Article


class TestPreFilter:
    """Test that PreFilter correctly filters articles."""

    def _make_article(self, *, title: str, published_ts: str = "", date: str = "") -> Article:
        return Article(
            title=title,
            summary="Test summary",
            url=f"https://example.com/{title.lower().replace(' ', '-')}",
            source="Test Source",
            date=date,
            category="ai",
            published_ts=published_ts,
        )

    def test_empty_input_returns_empty(self):
        pre_filter = PreFilter()
        assert pre_filter.filter([], run_date="2026-05-13") == []

    def test_daily_window_5am_ct_boundaries(self):
        """[start, end) window: include at start; exclude before start and at/after end."""
        pre_filter = PreFilter()

        # run_date=2026-05-13 => window is [2026-05-12 05:00 CT, 2026-05-13 05:00 CT)
        # In May (CDT, UTC-5): start=2026-05-12T10:00:00Z, end=2026-05-13T10:00:00Z
        articles = [
            self._make_article(title="before-start", published_ts="2026-05-12T09:59:59Z"),
            self._make_article(title="at-start", published_ts="2026-05-12T10:00:00Z"),
            self._make_article(title="inside", published_ts="2026-05-13T09:59:59Z"),
            self._make_article(title="at-end", published_ts="2026-05-13T10:00:00Z"),
            self._make_article(title="after-end", published_ts="2026-05-13T10:00:01Z"),
        ]

        result = pre_filter.filter(articles, run_date="2026-05-13")
        assert [a.title for a in result] == ["at-start", "inside"]

    def test_filter_uses_published_ts_preferred_over_legacy_date(self):
        pre_filter = PreFilter()

        # published_ts is inside window, legacy date is outside; article should be included.
        article = self._make_article(
            title="use-published-ts",
            published_ts="2026-05-12T10:00:00Z",
            date="Wed, 11 May 2026 00:00:00 GMT",
        )

        result = pre_filter.filter([article], run_date="2026-05-13")
        assert [a.title for a in result] == ["use-published-ts"]

    def test_dst_spring_forward_window_is_deterministic(self):
        """DST start day (US/Central) should still use local 5 AM boundaries."""
        pre_filter = PreFilter()

        # run_date=2026-03-08: end boundary 2026-03-08 05:00 CDT = 10:00Z
        # prior boundary 2026-03-07 05:00 CST = 11:00Z
        articles = [
            self._make_article(title="before", published_ts="2026-03-07T10:59:59Z"),
            self._make_article(title="at-start", published_ts="2026-03-07T11:00:00Z"),
            self._make_article(title="inside", published_ts="2026-03-08T09:59:59Z"),
            self._make_article(title="at-end", published_ts="2026-03-08T10:00:00Z"),
        ]

        result = pre_filter.filter(articles, run_date="2026-03-08")
        assert [a.title for a in result] == ["at-start", "inside"]

    def test_dst_fall_back_window_is_deterministic(self):
        """DST end day (US/Central) should still use local 5 AM boundaries."""
        pre_filter = PreFilter()

        # run_date=2026-11-01: end boundary 2026-11-01 05:00 CST = 11:00Z
        # prior boundary 2026-10-31 05:00 CDT = 10:00Z
        articles = [
            self._make_article(title="before", published_ts="2026-10-31T09:59:59Z"),
            self._make_article(title="at-start", published_ts="2026-10-31T10:00:00Z"),
            self._make_article(title="inside", published_ts="2026-11-01T10:59:59Z"),
            self._make_article(title="at-end", published_ts="2026-11-01T11:00:00Z"),
        ]

        result = pre_filter.filter(articles, run_date="2026-11-01")
        assert [a.title for a in result] == ["at-start", "inside"]
