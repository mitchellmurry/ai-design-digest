"""Tests for the HTML Generator module."""
import pytest
import os
from src.html_generator import HtmlGenerator
from src.feed_fetcher import Article


class TestHtmlGenerator:
    """Test that HtmlGenerator produces valid HTML from articles."""

    def _sample_articles(self):
        """Create sample articles for testing."""
        return [
            Article(
                title="Test AI Article",
                summary="This is a test AI article summary.",
                url="https://example.com/ai",
                source="Test Source",
                date="Wed, 13 May 2026 00:00:00 GMT",
                category="ai",
            ),
            Article(
                title="Test Design Article",
                summary="This is a test design article summary.",
                url="https://example.com/design",
                source="Test Source",
                date="Wed, 13 May 2026 00:00:00 GMT",
                category="design",
            ),
        ]

    def test_generates_html_string(self):
        """Generator returns a non-empty HTML string."""
        generator = HtmlGenerator()
        html = generator.generate(self._sample_articles(), "2026-05-13")
        assert isinstance(html, str)
        assert len(html) > 0

    def test_html_contains_articles(self):
        """Generated HTML includes article titles and links."""
        generator = HtmlGenerator()
        html = generator.generate(self._sample_articles(), "2026-05-13")
        assert "Test AI Article" in html
        assert "Test Design Article" in html
        assert "https://example.com/ai" in html

    def test_html_is_valid_structure(self):
        """Generated HTML has proper document structure."""
        generator = HtmlGenerator()
        html = generator.generate(self._sample_articles(), "2026-05-13")
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert "<head>" in html
        assert "<body>" in html

    def test_html_contains_date(self):
        """Generated HTML includes the digest date."""
        generator = HtmlGenerator()
        html = generator.generate(self._sample_articles(), "2026-05-13")
        assert "2026-05-13" in html

    def test_html_contains_source_attribution(self):
        """Generated HTML includes source name for each article."""
        generator = HtmlGenerator()
        html = generator.generate(self._sample_articles(), "2026-05-13")
        assert "Test Source" in html
