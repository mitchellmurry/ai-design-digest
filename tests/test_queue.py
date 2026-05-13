"""Tests for the Queue Manager module."""
import pytest
import os
import tempfile
from src.queue_manager import QueueManager


class TestQueueManager:
    """Test that QueueManager reads and writes queue.md."""

    def test_add_url_to_queue(self):
        """Adding a URL appends it to queue.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_path = os.path.join(tmpdir, "queue.md")
            manager = QueueManager(queue_path)
            manager.add("https://example.com/article")
            content = open(queue_path).read()
            assert "https://example.com/article" in content

    def test_add_url_includes_timestamp(self):
        """Added URL includes timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_path = os.path.join(tmpdir, "queue.md")
            manager = QueueManager(queue_path)
            manager.add("https://example.com/article")
            content = open(queue_path).read()
            assert "2026" in content  # timestamp contains year

    def test_read_urls_from_queue(self):
        """Reading queue returns list of URLs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_path = os.path.join(tmpdir, "queue.md")
            manager = QueueManager(queue_path)
            manager.add("https://example.com/article1")
            manager.add("https://example.com/article2")
            urls = manager.read()
            assert len(urls) == 2
            assert "https://example.com/article1" in urls
            assert "https://example.com/article2" in urls

    def test_empty_queue_returns_empty(self):
        """Empty queue returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_path = os.path.join(tmpdir, "queue.md")
            manager = QueueManager(queue_path)
            urls = manager.read()
            assert urls == []

    def test_creates_queue_file_if_missing(self):
        """Queue manager creates queue.md if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_path = os.path.join(tmpdir, "queue.md")
            assert not os.path.exists(queue_path)
            manager = QueueManager(queue_path)
            manager.add("https://example.com/article")
            assert os.path.exists(queue_path)
