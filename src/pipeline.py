"""Pipeline — orchestrates fetch -> filter -> curate -> generate."""
from datetime import datetime
from src.feed_fetcher import FeedFetcher
from src.pre_filter import PreFilter
from src.curation import CuratedPipeline
from src.html_generator import HtmlGenerator


class Pipeline:
    """Chains feed fetching, filtering, curation, and HTML generation."""

    def __init__(self, sources=None, max_age_hours=24):
        self.fetcher = FeedFetcher(sources=sources)
        self.pre_filter = PreFilter(max_age_hours=max_age_hours)
        self.curator = CuratedPipeline()
        self.generator = HtmlGenerator()

    def run(self, output_path: str, date: str = None) -> str:
        """Run the full pipeline and write HTML to output_path."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Fetch
        articles = self.fetcher.fetch()

        # Filter
        articles = self.pre_filter.filter(articles)

        # Curate (add golden nuggets)
        articles = self.curator.curate(articles)

        # Generate HTML
        html = self.generator.generate(articles, date)

        # Save
        self.generator.save(html, output_path)

        return html
