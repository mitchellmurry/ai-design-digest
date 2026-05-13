"""Curation — adds golden nuggets to articles."""
from typing import List
from src.feed_fetcher import Article


class CuratedPipeline:
    """Extracts golden nuggets from article summaries."""

    def curate(self, articles: List[Article]) -> List[Article]:
        """Add golden nuggets to each article."""
        curated = []
        for article in articles:
            golden_nugget = self._extract_golden_nugget(article.summary)
            curated.append(Article(
                title=article.title,
                summary=article.summary,
                url=article.url,
                source=article.source,
                date=article.date,
                category=article.category,
                golden_nugget=golden_nugget,
            ))
        return curated

    def _extract_golden_nugget(self, summary: str) -> str:
        """Extract first sentence as golden nugget placeholder."""
        if not summary:
            return ""
        # Split on sentence-ending punctuation
        for delimiter in [". ", ". "]:
            parts = summary.split(delimiter, 1)
            if len(parts) > 1:
                return parts[0].strip() + "."
        # If no sentence break found, use full summary
        return summary.strip()
