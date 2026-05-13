"""Tests for Feed Fetcher queue integration."""
import pytest
import tempfile
import os
from src.feed_fetcher import FeedFetcher, Article
from src.queue_manager import QueueManager


class TestFeedFetcherWithQueue:
    """Test that FeedFetcher reads and fetches queued URLs."""

    def test_fetcher_includes_queued_urls(self):
        """FeedFetcher fetches URLs from queue.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_path = os.path.join(tmpdir, "queue.md")
            manager = QueueManager(queue_path)
            manager.add("https://bullrich.github.io/tldr-rss/design.rss")

            fetcher = FeedFetcher(queue_path=queue_path)
            articles = fetcher.fetch()
            # Should have articles from the queued RSS feed
            assert len(articles) > 0

    def test_fetcher_without_queue(self):
        """FeedFetcher works without queue file."""
        fetcher = FeedFetcher()
        articles = fetcher.fetch()
        assert len(articles) > 0

    def test_fetcher_merges_queue_and_sources(self):
        """FeedFetcher combines queue articles with configured sources."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_path = os.path.join(tmpdir, "queue.md")
            manager = QueueManager(queue_path)
            manager.add("https://bullrich.github.io/tldr-rss/design.rss")

            sources = [
                {"name": "TLDR AI", "url": "https://bullrich.github.io/tldr-rss/ai.rss", "category": "ai", "type": "rss"},
            ]
            fetcher = FeedFetcher(sources=sources, queue_path=queue_path)
            articles = fetcher.fetch()
            # Should have articles from both sources
            sources_found = set(a.source for a in articles)
            assert "TLDR AI" in sources_found
            assert "Personal Queue" in sources_found
