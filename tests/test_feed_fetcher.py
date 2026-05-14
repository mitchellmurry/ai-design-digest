"""Deterministic tests for feed fetching and RSS normalization."""

from types import SimpleNamespace

from src.feed_fetcher import FeedFetcher
from src.source_registry import SourceDefinition, SourceRegistry


class DummyLogger:
    def __init__(self):
        self.calls = []

    def log(self, source, error_type, message):
        self.calls.append((source, error_type, message))


def test_default_fetcher_loads_only_registry_rss_sources(monkeypatch):
    registry = SourceRegistry(
        version=1,
        schema="ai-design-digest.source-registry",
        sources=[
            SourceDefinition(
                id="rss-a",
                name="RSS A",
                url="https://example.com/a.xml",
                tier="authority",
                type="publisher",
                trust_weight=0.9,
                topics=["ai"],
                fetch_method="rss",
                cadence="daily",
                notes="",
                raw={},
            ),
            SourceDefinition(
                id="web-b",
                name="Web B",
                url="https://example.com/b",
                tier="authority",
                type="publisher",
                trust_weight=0.9,
                topics=["ai"],
                fetch_method="web_listing",
                cadence="daily",
                notes="",
                raw={},
            ),
        ],
    )

    monkeypatch.setattr("src.feed_fetcher.load_source_registry", lambda *_args, **_kwargs: registry)

    seen_urls = []

    def fake_parse(url):
        seen_urls.append(url)
        return SimpleNamespace(entries=[{"title": "t", "link": "https://item", "published": "Wed, 13 May 2026 00:00:00 GMT"}], bozo=0)

    monkeypatch.setattr("src.feed_fetcher.feedparser.parse", fake_parse)

    fetcher = FeedFetcher()
    articles = fetcher.fetch()

    assert len(fetcher.sources) == 1
    assert fetcher.sources[0]["id"] == "rss-a"
    assert seen_urls == ["https://example.com/a.xml"]
    assert len(articles) == 1


def test_rss_entries_are_normalized_with_registry_metadata(monkeypatch):
    def fake_parse(_url):
        return SimpleNamespace(
            entries=[
                {
                    "title": "Model update",
                    "link": "https://example.com/post",
                    "guid": "urn:example:model-update",
                    "published": "Wed, 13 May 2026 00:00:00 GMT",
                    "description": "Raw summary",
                }
            ],
            bozo=0,
        )

    monkeypatch.setattr("src.feed_fetcher.feedparser.parse", fake_parse)

    source = {
        "id": "openai",
        "name": "OpenAI",
        "url": "https://example.com/rss.xml",
        "category": "ai",
        "type": "rss",
        "tier": "authority",
        "trust_weight": 1.0,
        "topics": ["ai-research", "policy"],
    }

    article = FeedFetcher(sources=[source]).fetch()[0]

    assert article.title == "Model update"
    assert article.url == "https://example.com/post"
    assert article.canonical_url == "https://example.com/post"
    assert article.dedup_key == "https://example.com/post"
    assert article.source_id == "openai"
    assert article.source_name == "OpenAI"
    assert article.source_tier == "authority"
    assert article.trust_weight == 1.0
    assert article.published_ts == "Wed, 13 May 2026 00:00:00 GMT"
    assert article.fetched_ts
    assert article.raw_summary == "Raw summary"
    assert article.topic_hints == ["ai-research", "policy"]


def test_invalid_rss_entries_missing_title_or_url_are_skipped(monkeypatch):
    def fake_parse(_url):
        return SimpleNamespace(
            entries=[
                {"title": "", "link": "https://example.com/no-title", "published": "Wed, 13 May 2026 00:00:00 GMT"},
                {"title": "No URL", "link": "", "published": "Wed, 13 May 2026 00:00:00 GMT"},
                {"title": "Valid", "link": "https://example.com/ok", "published": "Wed, 13 May 2026 00:00:00 GMT"},
            ],
            bozo=0,
        )

    monkeypatch.setattr("src.feed_fetcher.feedparser.parse", fake_parse)

    fetcher = FeedFetcher(sources=[{"id": "test", "name": "Test", "url": "https://example.com/feed", "category": "ai", "type": "rss"}])
    articles = fetcher.fetch()

    assert len(articles) == 1
    assert articles[0].title == "Valid"


def test_source_fetch_failures_are_logged_and_do_not_stop_other_sources(monkeypatch):
    logger = DummyLogger()

    def fake_parse(url):
        if "bad" in url:
            return SimpleNamespace(entries=[], bozo=1, bozo_exception=RuntimeError("bad feed"))
        return SimpleNamespace(entries=[{"title": "ok", "link": "https://example.com/ok", "published": "Wed, 13 May 2026 00:00:00 GMT"}], bozo=0)

    monkeypatch.setattr("src.feed_fetcher.feedparser.parse", fake_parse)

    sources = [
        {"id": "bad", "name": "Bad Source", "url": "https://example.com/bad.xml", "category": "ai", "type": "rss"},
        {"id": "good", "name": "Good Source", "url": "https://example.com/good.xml", "category": "ai", "type": "rss"},
    ]

    articles = FeedFetcher(sources=sources, error_logger=logger).fetch()

    assert len(articles) == 1
    assert articles[0].source_id == "good"
    assert len(logger.calls) == 1
    assert logger.calls[0][0] == "bad"
