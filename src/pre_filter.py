"""Pre-Filter — filters articles by age, topic, and deduplication."""
from datetime import datetime, timedelta
from typing import List
from difflib import SequenceMatcher
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit
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
            article_date = self._parse_article_date(article.date)
            return article_date >= cutoff
        except (ValueError, TypeError):
            # If date parsing fails, include the article (safe default)
            return True

    def _parse_article_date(self, raw_date: str) -> datetime:
        """Parse common RSS/Atom/ISO date formats into a naive local datetime."""
        if not raw_date:
            raise ValueError("Missing date")

        # RFC-822/RSS style, e.g. "Wed, 13 May 2026 00:00:00 GMT"
        try:
            parsed = parsedate_to_datetime(raw_date)
            if parsed is not None:
                if parsed.tzinfo is not None:
                    return parsed.astimezone().replace(tzinfo=None)
                return parsed
        except (TypeError, ValueError):
            pass

        # ISO-8601 style, e.g. "2026-05-13T00:00:00Z"
        normalized = raw_date.replace("Z", "+00:00")
        parsed_iso = datetime.fromisoformat(normalized)
        if parsed_iso.tzinfo is not None:
            return parsed_iso.astimezone().replace(tzinfo=None)
        return parsed_iso

    def deduplicate(self, articles: List[Article]) -> List[Article]:
        """Remove duplicate articles by URL and similar titles."""
        if not articles:
            return []

        seen_urls = set()
        seen_titles = []
        unique = []

        for article in articles:
            canonical_url = self._canonicalize_url(article.url)

            # Check URL dedup
            if canonical_url in seen_urls:
                continue

            # Check title similarity
            is_dup = False
            for seen_title in seen_titles:
                similarity = SequenceMatcher(None, article.title.lower(), seen_title.lower()).ratio()
                if similarity > 0.85:
                    is_dup = True
                    break

            if not is_dup:
                seen_urls.add(canonical_url)
                seen_titles.append(article.title)
                unique.append(article)

        return unique

    def _canonicalize_url(self, url: str) -> str:
        """Normalize URL for deduplication (strip common tracking params)."""
        if not url:
            return ""

        parts = urlsplit(url)
        filtered_query = []
        for key, value in parse_qsl(parts.query, keep_blank_values=True):
            lower = key.lower()
            if lower.startswith("utm_") or lower in {"fbclid", "gclid", "mc_cid", "mc_eid"}:
                continue
            filtered_query.append((key, value))

        normalized_query = urlencode(filtered_query, doseq=True)
        normalized_path = parts.path.rstrip("/") or "/"
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), normalized_path, normalized_query, ""))
