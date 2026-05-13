"""Tests for the Curation module."""
import pytest
from src.feed_fetcher import Article
from src.curation import CuratedPipeline


class TestArticleGoldenNugget:
    """Test that Article supports golden_nugget field."""

    def test_article_has_golden_nugget_field(self):
        """Article can be created with a golden_nugget."""
        article = Article(
            title="Test",
            summary="This is a summary.",
            url="https://example.com",
            source="Test",
            date="Wed, 13 May 2026 00:00:00 GMT",
            category="ai",
            golden_nugget="This is the golden nugget.",
        )
        assert article.golden_nugget == "This is the golden nugget."

    def test_article_golden_nugget_defaults_to_empty(self):
        """Article golden_nugget defaults to empty string."""
        article = Article(
            title="Test",
            summary="Summary",
            url="https://example.com",
            source="Test",
            date="Wed, 13 May 2026 00:00:00 GMT",
            category="ai",
        )
        assert article.golden_nugget == ""


class TestCuratedPipeline:
    """Test that CuratedPipeline adds golden nuggets to articles."""

    def test_curated_pipeline_sets_golden_nuggets(self):
        """Pipeline extracts golden nuggets from summaries."""
        articles = [
            Article(
                title="Test Article",
                summary="First sentence is the nugget. Second sentence is extra.",
                url="https://example.com",
                source="Test",
                date="Wed, 13 May 2026 00:00:00 GMT",
                category="ai",
            ),
        ]
        pipeline = CuratedPipeline()
        curated = pipeline.curate(articles)
        assert len(curated) == 1
        assert curated[0].golden_nugget == "First sentence is the nugget."

    def test_curated_pipeline_handles_single_sentence(self):
        """Pipeline handles articles with only one sentence."""
        articles = [
            Article(
                title="Short Article",
                summary="Just one sentence here.",
                url="https://example.com",
                source="Test",
                date="Wed, 13 May 2026 00:00:00 GMT",
                category="ai",
            ),
        ]
        pipeline = CuratedPipeline()
        curated = pipeline.curate(articles)
        assert curated[0].golden_nugget == "Just one sentence here."

    def test_curated_pipeline_preserves_original_fields(self):
        """Pipeline preserves all original article fields."""
        articles = [
            Article(
                title="Original Title",
                summary="Original summary.",
                url="https://example.com",
                source="Test Source",
                date="Wed, 13 May 2026 00:00:00 GMT",
                category="design",
            ),
        ]
        pipeline = CuratedPipeline()
        curated = pipeline.curate(articles)
        assert curated[0].title == "Original Title"
        assert curated[0].url == "https://example.com"
        assert curated[0].source == "Test Source"
        assert curated[0].category == "design"
