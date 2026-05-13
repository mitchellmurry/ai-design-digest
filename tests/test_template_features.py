"""Tests for HTML template golden nuggets and category grouping."""
import pytest
from src.feed_fetcher import Article
from src.html_generator import HtmlGenerator


class TestGoldenNuggetsInHtml:
    """Test that golden nuggets appear at top of digest."""

    def _sample_articles(self):
        return [
            Article(
                title="AI Article 1",
                summary="Summary of AI article.",
                url="https://example.com/ai1",
                source="Source A",
                date="Wed, 13 May 2026 00:00:00 GMT",
                category="ai",
                golden_nugget="This is the AI golden nugget.",
            ),
            Article(
                title="Design Article 1",
                summary="Summary of design article.",
                url="https://example.com/design1",
                source="Source B",
                date="Wed, 13 May 2026 00:00:00 GMT",
                category="design",
                golden_nugget="This is the design golden nugget.",
            ),
        ]

    def test_golden_nuggets_section_appears(self):
        """HTML contains a golden nuggets section."""
        generator = HtmlGenerator()
        html = generator.generate(self._sample_articles(), "2026-05-13")
        assert "Golden Nuggets" in html

    def test_golden_nuggets_before_categories(self):
        """Golden nuggets section appears before category sections."""
        generator = HtmlGenerator()
        html = generator.generate(self._sample_articles(), "2026-05-13")
        nuggets_pos = html.find("Golden Nuggets")
        ai_pos = html.find('class="category"')
        assert nuggets_pos < ai_pos, "Golden nuggets should appear before categories"

    def test_golden_nugget_text_appears(self):
        """Individual golden nugget text is in the HTML."""
        generator = HtmlGenerator()
        html = generator.generate(self._sample_articles(), "2026-05-13")
        assert "This is the AI golden nugget." in html
        assert "This is the design golden nugget." in html

    def test_articles_grouped_by_category(self):
        """Articles are grouped under category headings."""
        generator = HtmlGenerator()
        html = generator.generate(self._sample_articles(), "2026-05-13")
        assert 'class="category"' in html
        assert "AI" in html
        assert "Design" in html
