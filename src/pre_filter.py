"""Pre-Filter — filters articles by age, topic, and deduplication."""
from datetime import datetime, timedelta
from typing import List
from difflib import SequenceMatcher
from src.feed_fetcher import Article


class PreFilter:
    """Filters articles based on age and relevance criteria."""

    def __init__(self, max_age_hours: int = 24):
        self.max_age_hours = max_age_hours

    def filter(self, articles: List[Article]) -> List[Article]:
        """Filter articles by age window."""
        if not articles:
            return []

        cutoff = datetime.now() - timedelta(hours=self.max_age_hours)
        filtered = []

        for article in articles:
            if self._is_recent(article, cutoff):
                filtered.append(article)

        return filtered

    def _is_recent(self, article: Article, cutoff: datetime) -> bool:
        """Check if article date is after cutoff."""
        try:
            # RSS date format: "Wed, 13 May 2026 00:00:00 GMT"
            article_date = datetime.strptime(article.date, "%a, %d %b %Y %H:%M:%S %Z")
            return article_date >= cutoff
        except (ValueError, TypeError):
            # If date parsing fails, include the article (safe default)
            return True

    def deduplicate(self, articles: List[Article]) -> List[Article]:
        """Remove duplicate articles by URL and similar titles."""
        if not articles:
            return []

        seen_urls = set()
        seen_titles = []
        unique = []

        for article in articles:
            # Check URL dedup
            if article.url in seen_urls:
                continue

            # Check title similarity
            is_dup = False
            for seen_title in seen_titles:
                similarity = SequenceMatcher(None, article.title.lower(), seen_title.lower()).ratio()
                if similarity > 0.85:
                    is_dup = True
                    break

            if not is_dup:
                seen_urls.add(article.url)
                seen_titles.append(article.title)
                unique.append(article)

        return unique
