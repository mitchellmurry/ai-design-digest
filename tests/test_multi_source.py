"""Tests for multi-source feed fetching."""
import pytest
from src.feed_fetcher import FeedFetcher, Article


class TestConfigDrivenSources:
    """Test that FeedFetcher loads sources from config list."""

    def test_fetcher_with_multiple_rss_sources(self):
        """FeedFetcher fetches from multiple RSS sources via config."""
        sources = [
            {"name": "TLDR AI", "url": "https://bullrich.github.io/tldr-rss/ai.rss", "category": "ai", "type": "rss"},
            {"name": "TLDR Design", "url": "https://bullrich.github.io/tldr-rss/design.rss", "category": "design", "type": "rss"},
        ]
        fetcher = FeedFetcher(sources=sources)
        articles = fetcher.fetch()
        assert len(articles) > 0
        categories = set(a.category for a in articles)
        assert "ai" in categories
        assert "design" in categories

    def test_fetcher_with_custom_source(self):
        """FeedFetcher accepts a custom source config."""
        sources = [
            {"name": "Lenny's Newsletter", "url": "https://lennysnewsletter.com/feed", "category": "product", "type": "rss"},
        ]
        fetcher = FeedFetcher(sources=sources)
        articles = fetcher.fetch()
        assert len(articles) > 0
        assert articles[0].source == "Lenny's Newsletter"
        assert articles[0].category == "product"
