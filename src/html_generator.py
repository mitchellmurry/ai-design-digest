"""HTML Generator — renders articles into a static HTML digest page."""
from typing import List
from collections import defaultdict
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from src.feed_fetcher import Article


# Category display order
CATEGORY_ORDER = ["ai", "design", "product", "community"]

CATEGORY_LABELS = {
    "ai": "AI",
    "design": "Design",
    "product": "Product",
    "community": "Community",
}


class HtmlGenerator:
    """Generates static HTML digest pages from articles."""

    def __init__(self, template_dir=None):
        if template_dir is None:
            template_dir = str(Path(__file__).parent)
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
        )

    def generate(self, articles: List[Article], date: str) -> str:
        """Generate HTML digest page from articles."""
        template = self.env.get_template("template.html")

        # Group articles by category
        categories = defaultdict(list)
        for article in articles:
            categories[article.category].append(article)

        # Sort categories by defined order
        sorted_categories = {}
        for cat in CATEGORY_ORDER:
            if cat in categories:
                sorted_categories[CATEGORY_LABELS.get(cat, cat)] = categories[cat]

        # Add any categories not in the predefined order
        for cat, cat_articles in categories.items():
            if cat not in CATEGORY_ORDER:
                sorted_categories[CATEGORY_LABELS.get(cat, cat)] = cat_articles

        return template.render(date=date, categories=sorted_categories)

    def save(self, html: str, output_path: str) -> None:
        """Write HTML to file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(html, encoding="utf-8")
