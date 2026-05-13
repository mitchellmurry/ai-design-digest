"""Tests for error handling in FeedFetcher and Pipeline."""
import pytest
import tempfile
import os
from types import SimpleNamespace
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

    def test_logs_source_error_and_continues_with_good_source(self, monkeypatch):
        """Broken source should be logged while good source still yields articles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "errors.log")
            logger = ErrorLogger(log_path)

            sources = [
                {"name": "Bad Source", "url": "https://bad.example.com/rss", "category": "ai", "type": "rss"},
                {"name": "Good Source", "url": "https://good.example.com/rss", "category": "ai", "type": "rss"},
            ]

            def fake_parse(url):
                if "bad.example.com" in url:
                    raise RuntimeError("boom")
                return SimpleNamespace(entries=[
                    {
                        "title": "Good article",
                        "link": "https://good.example.com/post",
                        "description": "ok",
                        "published": "Wed, 13 May 2026 00:00:00 GMT",
                    }
                ])

            monkeypatch.setattr("src.feed_fetcher.feedparser.parse", fake_parse)

            fetcher = FeedFetcher(sources=sources, error_logger=logger)
            articles = fetcher.fetch()

            assert len(articles) == 1
            assert articles[0].source == "Good Source"

            errors = logger.read()
            assert len(errors) == 1
            assert errors[0]["source"] == "Bad Source"
            assert errors[0]["error_type"] == "RuntimeError"
            assert "boom" in errors[0]["message"]


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
