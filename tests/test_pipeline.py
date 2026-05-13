"""Tests for the Pipeline orchestrator."""
import pytest
import os
from src.pipeline import Pipeline


class TestPipeline:
    """Test that Pipeline chains fetch -> filter -> generate."""

    def test_pipeline_produces_html_file(self):
        """Running the pipeline creates an HTML file."""
        pipeline = Pipeline()
        output_path = "output/test_digest.html"
        pipeline.run(output_path)
        assert os.path.exists(output_path)

    def test_pipeline_html_is_valid(self):
        """Generated HTML has proper structure."""
        pipeline = Pipeline()
        output_path = "output/test_digest.html"
        pipeline.run(output_path)
        content = open(output_path).read()
        assert "<!DOCTYPE html>" in content
        assert "</html>" in content

    def test_pipeline_with_custom_date(self):
        """Pipeline accepts a custom date string."""
        pipeline = Pipeline()
        output_path = "output/test_custom_date.html"
        pipeline.run(output_path, date="2026-01-01")
        content = open(output_path).read()
        assert "2026-01-01" in content
