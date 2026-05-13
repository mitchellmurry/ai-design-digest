"""Tests for the Feed Fetcher module."""
import pytest
from types import SimpleNamespace
from src.feed_fetcher import FeedFetcher, Article


class TestFeedFetcher:
    """Test that FeedFetcher returns normalized articles from RSS sources."""

    def test_fetch_returns_list_of_articles(self):
        """FeedFetcher.fetch() returns a list of Article objects."""
        fetcher = FeedFetcher()
        articles = fetcher.fetch()
        assert isinstance(articles, list)
        assert len(articles) > 0

    def test_articles_have_required_fields(self):
        """Each article has title, summary, url, source, date, category."""
        fetcher = FeedFetcher()
        articles = fetcher.fetch()
        for article in articles:
            assert isinstance(article, Article)
            assert article.title, "Article must have a title"
            assert article.url, "Article must have a URL"
            assert article.source, "Article must have a source"
            assert article.date, "Article must have a date"
            assert article.category, "Article must have a category"

    def test_articles_are_from_tldr_ai(self):
        """Articles fetched from default config have category 'ai'."""
        fetcher = FeedFetcher()
        articles = fetcher.fetch()
        ai_articles = [a for a in articles if a.category == "ai"]
        assert len(ai_articles) > 0, "Should have AI articles"

    def test_skips_invalid_rss_entries_missing_title_or_url(self, monkeypatch):
        """Invalid RSS entries should be skipped during normalization."""
        def fake_parse(_url):
            return SimpleNamespace(entries=[
                {"title": "", "link": "https://example.com/no-title", "published": "Wed, 13 May 2026 00:00:00 GMT"},
                {"title": "No URL", "link": "", "published": "Wed, 13 May 2026 00:00:00 GMT"},
                {"title": "Valid", "link": "https://example.com/ok", "published": "Wed, 13 May 2026 00:00:00 GMT"},
            ])

        monkeypatch.setattr("src.feed_fetcher.feedparser.parse", fake_parse)

        fetcher = FeedFetcher(sources=[{"name": "Test", "url": "https://example.com/feed", "category": "ai", "type": "rss"}])
        articles = fetcher.fetch()

        assert len(articles) == 1
        assert articles[0].title == "Valid"
        assert articles[0].url == "https://example.com/ok"
