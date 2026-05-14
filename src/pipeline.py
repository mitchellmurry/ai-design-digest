"""Pipeline — orchestrates fetch -> filter -> curate -> generate."""
from datetime import datetime
from pathlib import Path

from src.daily_artifact import write_daily_artifact
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

    def run(self, output_path: str, date: str = None, artifact_dir: str = "digest/artifacts") -> str:
        """Run the full pipeline and write artifact + HTML output."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Fetch
        fetched_articles = self.fetcher.fetch()

        # Filter / ingestion stage
        ingested_articles = self.pre_filter.filter(fetched_articles, run_date=date)
        window_start, window_end = self.pre_filter._compute_5am_ct_window(date)

        # Curate (selected items for current pipeline)
        selected_articles = self.curator.curate(ingested_articles)

        # Write daily artifact before render/delivery
        artifact_path = Path(artifact_dir) / f"{date}.json"
        write_daily_artifact(
            artifact_path=artifact_path,
            run_date=date,
            window_start=window_start.isoformat(),
            window_end=window_end.isoformat(),
            sources_checked=list(self.fetcher.last_source_reports),
            source_errors=list(self.fetcher.last_source_errors),
            fetched_items=fetched_articles,
            ingested_items=ingested_articles,
            selected_items=selected_articles,
        )

        # Generate HTML
        html = self.generator.generate(selected_articles, date)

        # Save
        self.generator.save(html, output_path)

        return html
