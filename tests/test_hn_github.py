"""Tests for Hacker News and GitHub Releases fetchers."""
import pytest
from src.feed_fetcher import FeedFetcher, Article


class TestHackerNewsFetcher:
    """Test Hacker News fetcher via Algolia API."""

    def test_hn_fetcher_returns_articles(self):
        """HN source type returns articles from Algolia API."""
        sources = [
            {"name": "Hacker News", "url": "https://hn.algolia.com/api/v1/search", "category": "ai", "type": "hn_algolia", "keywords": ["AI", "LLM"]},
        ]
        fetcher = FeedFetcher(sources=sources)
        articles = fetcher.fetch()
        assert len(articles) > 0
        assert all(a.source == "Hacker News" for a in articles)

    def test_hn_articles_have_required_fields(self):
        """HN articles have title, url, date, category."""
        sources = [
            {"name": "Hacker News", "url": "https://hn.algolia.com/api/v1/search", "category": "ai", "type": "hn_algolia", "keywords": ["AI"]},
        ]
        fetcher = FeedFetcher(sources=sources)
        articles = fetcher.fetch()
        for article in articles[:5]:
            assert article.title, "HN article must have title"
            assert article.url, "HN article must have URL"
            assert article.date, "HN article must have date"


class TestGitHubReleasesFetcher:
    """Test GitHub Releases fetcher."""

    def test_github_releases_returns_articles(self):
        """GitHub Releases source returns articles."""
        sources = [
            {"name": "Hermes Agent", "url": "https://api.github.com/repos/NousResearch/hermes-agent/releases", "category": "community", "type": "github_releases"},
        ]
        fetcher = FeedFetcher(sources=sources)
        articles = fetcher.fetch()
        assert len(articles) > 0
        assert all(a.source == "Hermes Agent" for a in articles)

    def test_github_releases_have_required_fields(self):
        """GitHub Release articles have title, url, date."""
        sources = [
            {"name": "Hermes Agent", "url": "https://api.github.com/repos/NousResearch/hermes-agent/releases", "category": "community", "type": "github_releases"},
        ]
        fetcher = FeedFetcher(sources=sources)
        articles = fetcher.fetch()
        for article in articles[:3]:
            assert article.title, "Release must have title"
            assert article.url, "Release must have URL"
            assert article.date, "Release must have date"
