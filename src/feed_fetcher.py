"""Feed Fetcher — fetches and normalizes articles from configured sources."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import struct_time
from typing import List

import feedparser
import requests

from src.queue_manager import QueueManager
from src.source_registry import SourceDefinition, load_source_registry


@dataclass
class Article:
    """Normalized article from any source."""

    title: str
    summary: str
    url: str
    source: str
    date: str
    category: str
    golden_nugget: str = ""

    # Registry-driven normalized fields
    canonical_url: str = ""
    dedup_key: str = ""
    source_id: str = ""
    source_name: str = ""
    source_tier: str = ""
    trust_weight: float = 0.0
    published_ts: str = ""
    fetched_ts: str = ""
    raw_summary: str = ""
    topic_hints: list[str] = field(default_factory=list)


# Backward compatible fallback source when registry loading fails
DEFAULT_SOURCES = [
    {
        "id": "tldr-ai",
        "name": "TLDR AI",
        "url": "https://bullrich.github.io/tldr-rss/ai.rss",
        "category": "ai",
        "type": "rss",
        "tier": "trusted interpretation",
        "trust_weight": 0.75,
        "topics": ["ai"],
    },
]


class FeedFetcher:
    """Fetches and normalizes articles from configured sources."""

    def __init__(self, sources=None, queue_path=None, error_logger=None, registry_path: str | Path | None = None):
        self.error_logger = error_logger
        self.registry_path = Path(registry_path) if registry_path else Path(__file__).resolve().parents[1] / "registry" / "sources.v1.txt"
        self.sources = sources if sources is not None else self._load_default_sources()
        self.queue_manager = QueueManager(queue_path) if queue_path else None
        self.last_source_reports: list[dict] = []
        self.last_source_errors: list[dict] = []

    def _load_default_sources(self) -> list[dict]:
        try:
            registry = load_source_registry(self.registry_path)
            return [self._source_definition_to_config(s) for s in registry.sources if s.fetch_method == "rss"]
        except Exception:
            return list(DEFAULT_SOURCES)

    @staticmethod
    def _source_definition_to_config(source: SourceDefinition) -> dict:
        category = source.topics[0] if source.topics else "ai"
        return {
            "id": source.id,
            "name": source.name,
            "url": source.url,
            "category": category,
            "type": "rss",
            "tier": source.tier,
            "trust_weight": source.trust_weight,
            "topics": list(source.topics),
        }

    def fetch(self) -> List[Article]:
        """Fetch articles from all configured sources and queue."""
        articles = []
        self.last_source_reports = []
        self.last_source_errors = []

        for source in self.sources:
            checked_ts = datetime.now(timezone.utc).isoformat()
            source_id = source.get("id") or source.get("name", "unknown")
            source_name = source.get("name", "")
            fetch_method = source.get("fetch_method") or source.get("type", "rss")
            try:
                source_type = source.get("type", "rss")
                if source_type == "rss":
                    source_articles = self._fetch_rss(source)
                elif source_type == "hn_algolia":
                    source_articles = self._fetch_hn(source)
                elif source_type == "github_releases":
                    source_articles = self._fetch_github_releases(source)
                else:
                    source_articles = []

                articles.extend(source_articles)
                self.last_source_reports.append({
                    "source_id": source_id,
                    "source_name": source_name,
                    "fetch_method": fetch_method,
                    "status": "ok",
                    "item_count": len(source_articles),
                    "checked_ts": checked_ts,
                })
            except Exception as exc:
                if self.error_logger:
                    self.error_logger.log(source_id, type(exc).__name__, str(exc))
                err = {
                    "source_id": source_id,
                    "source_name": source_name,
                    "fetch_method": fetch_method,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                    "checked_ts": checked_ts,
                }
                self.last_source_errors.append(err)
                self.last_source_reports.append({
                    "source_id": source_id,
                    "source_name": source_name,
                    "fetch_method": fetch_method,
                    "status": "error",
                    "item_count": 0,
                    "checked_ts": checked_ts,
                })

        if self.queue_manager:
            articles.extend(self._fetch_queue())

        return articles

    def _fetch_queue(self) -> List[Article]:
        """Fetch articles from the personal queue."""
        urls = self.queue_manager.read()
        articles = []
        for url in urls:
            try:
                feed = feedparser.parse(url)
                if feed.entries:
                    for entry in feed.entries:
                        article = Article(
                            title=entry.get("title", ""),
                            summary=entry.get("description", ""),
                            url=entry.get("guid") or entry.get("link", url),
                            source="Personal Queue",
                            date=entry.get("published", ""),
                            category="ai",
                        )
                        articles.append(article)
                else:
                    article = Article(
                        title=url.split("/")[-1] or url,
                        summary="Queued article",
                        url=url,
                        source="Personal Queue",
                        date=datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                        category="ai",
                    )
                    articles.append(article)
            except Exception:
                pass
        return articles

    def _fetch_rss(self, source: dict) -> List[Article]:
        """Fetch articles from an RSS source."""
        feed = feedparser.parse(source["url"])
        if getattr(feed, "bozo", 0):
            raise ValueError(f"Invalid RSS feed: {getattr(feed, 'bozo_exception', 'unknown parser error')}")

        fetched_ts = datetime.now(timezone.utc).isoformat()
        articles = []
        for entry in feed.entries:
            article = self._normalize_rss_entry(entry, source, fetched_ts)
            if article:
                articles.append(article)
        return articles

    def _normalize_rss_entry(self, entry: dict, source: dict, fetched_ts: str) -> Article | None:
        title = str(entry.get("title") or "").strip()
        raw_url = str(entry.get("link") or entry.get("guid") or "").strip()
        if not title or not raw_url:
            return None

        canonical_url = str(entry.get("link") or raw_url).strip()
        dedup_key = canonical_url.lower() if canonical_url else f"{source.get('id', source.get('name', 'unknown'))}:{raw_url.lower()}"
        published_ts = self._extract_published_timestamp(entry)
        raw_summary = str(entry.get("description") or entry.get("summary") or "")

        topic_hints = source.get("topics") or []
        if isinstance(topic_hints, str):
            topic_hints = [t.strip() for t in topic_hints.split(",") if t.strip()]

        return Article(
            title=title,
            summary=raw_summary,
            url=raw_url,
            source=source.get("name", ""),
            date=published_ts,
            category=source.get("category") or (topic_hints[0] if topic_hints else "ai"),
            canonical_url=canonical_url,
            dedup_key=dedup_key,
            source_id=source.get("id", ""),
            source_name=source.get("name", ""),
            source_tier=source.get("tier", ""),
            trust_weight=float(source.get("trust_weight", 0.0) or 0.0),
            published_ts=published_ts,
            fetched_ts=fetched_ts,
            raw_summary=raw_summary,
            topic_hints=topic_hints,
        )

    @staticmethod
    def _extract_published_timestamp(entry: dict) -> str:
        parsed = entry.get("published_parsed")
        if isinstance(parsed, struct_time):
            return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()
        return str(entry.get("published") or "")

    def _fetch_hn(self, source: dict) -> List[Article]:
        """Fetch articles from Hacker News via Algolia API."""
        keywords = source.get("keywords", ["AI"])
        query = " OR ".join(keywords)
        params = {
            "query": query,
            "tags": "story",
            "hitsPerPage": 20,
        }
        resp = requests.get(source["url"], params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        articles = []
        for hit in data.get("hits", []):
            created_at = hit.get("created_at", "")
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                date_str = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
            except (ValueError, TypeError):
                date_str = created_at

            article = Article(
                title=hit.get("title", ""),
                summary=hit.get("title", ""),
                url=hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                source=source["name"],
                date=date_str,
                category=source["category"],
            )
            articles.append(article)
        return articles

    def _fetch_github_releases(self, source: dict) -> List[Article]:
        """Fetch articles from GitHub Releases API."""
        resp = requests.get(source["url"], timeout=15)
        resp.raise_for_status()
        releases = resp.json()

        articles = []
        for release in releases[:10]:
            article = Article(
                title=release.get("name") or release.get("tag_name", ""),
                summary=(release.get("body") or "")[:200],
                url=release.get("html_url", ""),
                source=source["name"],
                date=release.get("published_at", ""),
                category=source["category"],
            )
            articles.append(article)
        return articles
