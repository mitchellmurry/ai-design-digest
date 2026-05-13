"""Tests for the Pre-Filter module."""
import pytest
from datetime import datetime, timedelta
from src.pre_filter import PreFilter
from src.feed_fetcher import Article


class TestPreFilter:
    """Test that PreFilter correctly filters articles."""

    def _make_article(self, days_ago=0, title="Test Article", category="ai"):
        """Helper to create an article with a specific age."""
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        return Article(
            title=title,
            summary="Test summary",
            url="https://example.com/article",
            source="Test Source",
            date=date,
            category=category,
        )

    def test_removes_old_articles(self):
        """Articles older than 24h are removed."""
        fresh = self._make_article(days_ago=0)
        old = self._make_article(days_ago=2)
        pre_filter = PreFilter(max_age_hours=24)
        result = pre_filter.filter([fresh, old])
        assert len(result) == 1
        assert result[0].title == "Test Article"

    def test_keeps_recent_articles(self):
        """Articles within age window are kept."""
        articles = [self._make_article(days_ago=0) for _ in range(5)]
        pre_filter = PreFilter(max_age_hours=24)
        result = pre_filter.filter(articles)
        assert len(result) == 5

    def test_empty_input_returns_empty(self):
        """Empty article list returns empty."""
        pre_filter = PreFilter(max_age_hours=24)
        result = pre_filter.filter([])
        assert result == []

    def test_filters_old_articles_with_iso8601_dates(self):
        """Old ISO-8601 timestamps should be filtered out, not auto-included."""
        old_iso_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        old_article = Article(
            title="Old ISO Article",
            summary="Test summary",
            url="https://example.com/old-iso",
            source="Test Source",
            date=old_iso_date,
            category="ai",
        )

        pre_filter = PreFilter(max_age_hours=24)
        result = pre_filter.filter([old_article])

        assert result == []
