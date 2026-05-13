"""Tests for deployment features: robots.txt, homepage, output structure."""
import pytest
import os
from src.deployment import DeploymentManager


class TestRobotsTxt:
    """Test that robots.txt blocks search engines."""

    def test_robots_txt_blocks_all(self):
        """robots.txt contains Disallow: /."""
        manager = DeploymentManager()
        content = manager.get_robots_txt()
        assert "Disallow: /" in content

    def test_robots_txt_is_valid(self):
        """robots.txt has proper format."""
        manager = DeploymentManager()
        content = manager.get_robots_txt()
        assert "User-agent: *" in content


class TestHomepage:
    """Test that homepage shows latest digest + archive links."""

    def test_homepage_generation(self):
        """Homepage can be generated."""
        manager = DeploymentManager()
        html = manager.generate_homepage("2026-05-13", ["2026-05-12", "2026-05-11"])
        assert "<!DOCTYPE html>" in html
        assert "2026-05-13" in html

    def test_homepage_includes_archive_links(self):
        """Homepage includes links to past digests."""
        manager = DeploymentManager()
        html = manager.generate_homepage("2026-05-13", ["2026-05-12", "2026-05-11"])
        assert "2026-05-12" in html
        assert "2026-05-11" in html

    def test_homepage_links_to_digest(self):
        """Homepage links to the digest HTML file."""
        manager = DeploymentManager()
        html = manager.generate_homepage("2026-05-13", [])
        assert "2026-05-13.html" in html


class TestOutputStructure:
    """Test that output follows /digest/ structure."""

    def test_output_path_format(self):
        """Digest output path follows date-based format."""
        manager = DeploymentManager()
        path = manager.get_digest_path("2026-05-13")
        assert "2026-05-13" in path
        assert path.endswith(".html")
