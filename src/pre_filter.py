"""Pre-Filter — filters articles by age, topic, and deduplication."""
from datetime import date, datetime, time, timedelta, timezone
from typing import List
from difflib import SequenceMatcher
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit
from zoneinfo import ZoneInfo
from src.feed_fetcher import Article


class PreFilter:
    """Filters articles based on age and relevance criteria."""

    CENTRAL_TZ = ZoneInfo("America/Chicago")

    def __init__(self, max_age_hours: int = 24):
        self.max_age_hours = max_age_hours

    def filter(self, articles: List[Article], run_date: str | date | datetime | None = None) -> List[Article]:
        """Filter articles to prior 5:00 AM CT -> current 5:00 AM CT window."""
        if not articles:
            return []

        start_utc, end_utc = self._compute_5am_ct_window(run_date)
        filtered = []

        for article in articles:
            if self._is_in_window(article, start_utc, end_utc):
                filtered.append(article)

        return filtered

    def _compute_5am_ct_window(self, run_date: str | date | datetime | None) -> tuple[datetime, datetime]:
        if run_date is None:
            run_day = datetime.now(self.CENTRAL_TZ).date()
        elif isinstance(run_date, datetime):
            run_day = run_date.date()
        elif isinstance(run_date, date):
            run_day = run_date
        elif isinstance(run_date, str):
            run_day = datetime.strptime(run_date, "%Y-%m-%d").date()
        else:
            raise TypeError("run_date must be None, str, date, or datetime")

        end_ct = datetime.combine(run_day, time(hour=5), tzinfo=self.CENTRAL_TZ)
        start_ct = end_ct - timedelta(days=1)
        return start_ct.astimezone(timezone.utc), end_ct.astimezone(timezone.utc)

    def _is_in_window(self, article: Article, start_utc: datetime, end_utc: datetime) -> bool:
        """Check [start, end) with normalized published timestamp preferred."""
        raw_ts = article.published_ts or article.date
        try:
            article_dt = self._parse_article_timestamp(raw_ts)
            return start_utc <= article_dt < end_utc
        except (ValueError, TypeError):
            # If date parsing fails, include the article (safe default)
            return True

    def _parse_article_timestamp(self, raw_date: str) -> datetime:
        """Parse common RSS/Atom/ISO date formats into UTC-aware datetime."""
        if not raw_date:
            raise ValueError("Missing date")

        try:
            parsed = parsedate_to_datetime(raw_date)
            if parsed is not None:
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc)
        except (TypeError, ValueError):
            pass

        normalized = raw_date.replace("Z", "+00:00")
        parsed_iso = datetime.fromisoformat(normalized)
        if parsed_iso.tzinfo is None:
            parsed_iso = parsed_iso.replace(tzinfo=timezone.utc)
        return parsed_iso.astimezone(timezone.utc)

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
