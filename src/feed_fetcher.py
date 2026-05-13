"""Feed Fetcher — fetches articles from RSS, HN, GitHub, and personal queue."""
from dataclasses import dataclass
from typing import List
import feedparser
import requests
from datetime import datetime
from src.queue_manager import QueueManager


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


# Default RSS sources
DEFAULT_SOURCES = [
    {
        "name": "TLDR AI",
        "url": "https://bullrich.github.io/tldr-rss/ai.rss",
        "category": "ai",
    },
]


class FeedFetcher:
    """Fetches and normalizes articles from configured sources."""

    def __init__(self, sources=None, queue_path=None):
        self.sources = sources or DEFAULT_SOURCES
        self.queue_manager = QueueManager(queue_path) if queue_path else None

    def fetch(self) -> List[Article]:
        """Fetch articles from all configured sources and queue."""
        articles = []

        # Fetch from configured sources
        for source in self.sources:
            try:
                source_type = source.get("type", "rss")
                if source_type == "rss":
                    articles.extend(self._fetch_rss(source))
                elif source_type == "hn_algolia":
                    articles.extend(self._fetch_hn(source))
                elif source_type == "github_releases":
                    articles.extend(self._fetch_github_releases(source))
            except Exception:
                # Silent skip on error
                pass

        # Fetch from personal queue
        if self.queue_manager:
            articles.extend(self._fetch_queue())

        return articles

    def _fetch_queue(self) -> List[Article]:
        """Fetch articles from the personal queue."""
        urls = self.queue_manager.read()
        articles = []
        for url in urls:
            try:
                # Try fetching as RSS first
                feed = feedparser.parse(url)
                if feed.entries:
                    for entry in feed.entries:
                        article = Article(
                            title=entry.get("title", ""),
                            summary=entry.get("description", ""),
                            url=entry.get("guid") or entry.get("link", url),
                            source="Personal Queue",
                            date=entry.get("published", ""),
                            category="ai",  # default category
                        )
                        articles.append(article)
                else:
                    # If not RSS, create a placeholder article
                    article = Article(
                        title=url.split("/")[-1] or url,
                        summary="Queued article",
                        url=url,
                        source="Personal Queue",
                        date=datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                        category="ai",
                    )
                    articles.append(article)
            except Exception:
                pass
        return articles

    def _fetch_rss(self, source: dict) -> List[Article]:
        """Fetch articles from an RSS source."""
        feed = feedparser.parse(source["url"])
        articles = []
        for entry in feed.entries:
            article = Article(
                title=entry.get("title", ""),
                summary=entry.get("description", ""),
                url=entry.get("guid") or entry.get("link", ""),
                source=source["name"],
                date=entry.get("published", ""),
                category=source["category"],
            )
            articles.append(article)
        return articles

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
        for release in releases[:10]:  # Last 10 releases
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
