"""Tests for cross-source deduplication."""
import pytest
from src.pre_filter import PreFilter
from src.feed_fetcher import Article


class TestDeduplication:
    """Test that PreFilter deduplicates across sources."""

    def _make_article(self, url="https://example.com/article", title="Test Article", source="Source A"):
        return Article(
            title=title,
            summary="Summary",
            url=url,
            source=source,
            date="Wed, 13 May 2026 00:00:00 GMT",
            category="ai",
        )

    def test_deduplicates_same_url(self):
        """Articles with same URL are deduplicated."""
        a1 = self._make_article(url="https://example.com/article", source="Source A")
        a2 = self._make_article(url="https://example.com/article", source="Source B")
        pre_filter = PreFilter()
        result = pre_filter.deduplicate([a1, a2])
        assert len(result) == 1

    def test_keeps_different_urls(self):
        """Articles with different URLs and titles are kept."""
        a1 = self._make_article(url="https://example.com/article1", title="First Unique Article")
        a2 = self._make_article(url="https://example.com/article2", title="Second Unique Article")
        pre_filter = PreFilter()
        result = pre_filter.deduplicate([a1, a2])
        assert len(result) == 2

    def test_deduplicates_similar_titles(self):
        """Articles with very similar titles are deduplicated."""
        a1 = self._make_article(url="https://example.com/a", title="AI is changing everything")
        a2 = self._make_article(url="https://example.com/b", title="AI is changing everything!")
        pre_filter = PreFilter()
        result = pre_filter.deduplicate([a1, a2])
        assert len(result) == 1

    def test_empty_input_returns_empty(self):
        """Empty list returns empty."""
        pre_filter = PreFilter()
        result = pre_filter.deduplicate([])
        assert result == []

    def test_deduplicates_canonical_urls_with_tracking_params(self):
        """Same URL with tracking query params should be treated as duplicates."""
        a1 = self._make_article(url="https://example.com/article?utm_source=newsletter", title="AI launch")
        a2 = self._make_article(url="https://example.com/article", title="AI launch mirrored", source="Source B")
        pre_filter = PreFilter()
        result = pre_filter.deduplicate([a1, a2])
        assert len(result) == 1
