"""Tests for end-to-end pipeline with curation."""
import pytest
import os
from src.pipeline import Pipeline


class TestPipelineWithCuration:
    """Test full pipeline including golden nugget extraction."""

    def test_pipeline_output_contains_golden_nuggets(self):
        """Running pipeline produces HTML with golden nuggets section."""
        pipeline = Pipeline()
        output_path = "output/test_curated.html"
        pipeline.run(output_path)
        content = open(output_path).read()
        assert "Golden Nuggets" in content

    def test_pipeline_output_has_category_grouping(self):
        """Running pipeline produces HTML with category sections."""
        pipeline = Pipeline()
        output_path = "output/test_curated.html"
        pipeline.run(output_path)
        content = open(output_path).read()
        assert 'class="category"' in content

    def test_pipeline_file_is_written(self):
        """Pipeline creates the output file."""
        pipeline = Pipeline()
        output_path = "output/test_curated.html"
        pipeline.run(output_path)
        assert os.path.exists(output_path)
