"""Tests for error handling in FeedFetcher and Pipeline."""
import pytest
import tempfile
import os
from src.feed_fetcher import FeedFetcher, Article
from src.pipeline import Pipeline
from src.error_logger import ErrorLogger


class TestFeedFetcherErrorHandling:
    """Test that FeedFetcher handles errors gracefully."""

    def test_bad_source_doesnt_crash(self):
        """FeedFetcher skips bad sources without crashing."""
        sources = [
            {"name": "Bad Source", "url": "https://invalid.example.com/feed", "category": "ai", "type": "rss"},
            {"name": "TLDR AI", "url": "https://bullrich.github.io/tldr-rss/ai.rss", "category": "ai", "type": "rss"},
        ]
        fetcher = FeedFetcher(sources=sources)
        articles = fetcher.fetch()
        # Should still get articles from the good source
        assert len(articles) > 0
        assert all(a.source == "TLDR AI" for a in articles)

    def test_all_bad_sources_returns_empty(self):
        """FeedFetcher returns empty list if all sources fail."""
        sources = [
            {"name": "Bad Source 1", "url": "https://invalid.example.com/feed", "category": "ai", "type": "rss"},
            {"name": "Bad Source 2", "url": "https://another.invalid.example.com/feed", "category": "design", "type": "rss"},
        ]
        fetcher = FeedFetcher(sources=sources)
        articles = fetcher.fetch()
        assert articles == []


class TestPipelineErrorHandling:
    """Test that Pipeline completes even with source failures."""

    def test_pipeline_completes_with_bad_sources(self):
        """Pipeline generates output even if some sources fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sources = [
                {"name": "Bad Source", "url": "https://invalid.example.com/feed", "category": "ai", "type": "rss"},
                {"name": "TLDR AI", "url": "https://bullrich.github.io/tldr-rss/ai.rss", "category": "ai", "type": "rss"},
            ]
            pipeline = Pipeline(sources=sources)
            output_path = os.path.join(tmpdir, "digest.html")
            pipeline.run(output_path)
            assert os.path.exists(output_path)
            content = open(output_path).read()
            assert "<!DOCTYPE html>" in content

    def test_pipeline_with_all_bad_sources(self):
        """Pipeline generates empty digest if all sources fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sources = [
                {"name": "Bad Source", "url": "https://invalid.example.com/feed", "category": "ai", "type": "rss"},
            ]
            pipeline = Pipeline(sources=sources)
            output_path = os.path.join(tmpdir, "digest.html")
            pipeline.run(output_path)
            assert os.path.exists(output_path)
