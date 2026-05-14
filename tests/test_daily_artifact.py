"""Tests for daily artifact writing and pipeline integration."""

import json
from types import SimpleNamespace

from src.pipeline import Pipeline


def test_daily_artifact_captures_partial_source_failure(monkeypatch, tmp_path):
    def fake_parse(url):
        if "bad" in url:
            return SimpleNamespace(entries=[], bozo=1, bozo_exception=RuntimeError("bad feed"))
        return SimpleNamespace(
            entries=[
                {
                    "title": "Good item",
                    "link": "https://example.com/good-item",
                    "published": "2026-05-12T12:00:00Z",
                    "description": "Summary",
                }
            ],
            bozo=0,
        )

    monkeypatch.setattr("src.feed_fetcher.feedparser.parse", fake_parse)

    out_html = tmp_path / "digest.html"
    artifact_dir = tmp_path / "artifacts"
    pipeline = Pipeline(
        sources=[
            {"id": "bad", "name": "Bad", "url": "https://example.com/bad.xml", "category": "ai", "type": "rss"},
            {"id": "good", "name": "Good", "url": "https://example.com/good.xml", "category": "ai", "type": "rss"},
        ]
    )

    pipeline.run(str(out_html), date="2026-05-13", artifact_dir=str(artifact_dir))

    artifact_path = artifact_dir / "2026-05-13.json"
    assert artifact_path.exists()
    data = json.loads(artifact_path.read_text())

    assert data["window"]["start"] == "2026-05-12T10:00:00+00:00"
    assert data["window"]["end"] == "2026-05-13T10:00:00+00:00"
    assert len(data["sources_checked"]) == 2
    assert any(s["status"] == "error" and s["source_id"] == "bad" for s in data["sources_checked"])
    assert any(s["status"] == "ok" and s["source_id"] == "good" and s["item_count"] == 1 for s in data["sources_checked"])
    assert len(data["source_errors"]) == 1
    assert data["source_errors"][0]["source_id"] == "bad"
    assert len(data["ingested_items"]) == 1


def test_daily_artifact_written_when_all_quiet_or_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "src.feed_fetcher.feedparser.parse",
        lambda _url: SimpleNamespace(entries=[], bozo=0),
    )

    out_html = tmp_path / "digest.html"
    artifact_dir = tmp_path / "artifacts"
    pipeline = Pipeline(
        sources=[
            {"id": "quiet", "name": "Quiet", "url": "https://example.com/quiet.xml", "category": "ai", "type": "rss"}
        ]
    )
    pipeline.run(str(out_html), date="2026-05-13", artifact_dir=str(artifact_dir))

    artifact_path = artifact_dir / "2026-05-13.json"
    assert artifact_path.exists()
    data = json.loads(artifact_path.read_text())

    assert data["counts"]["fetched"] == 0
    assert data["counts"]["ingested"] == 0
    assert data["counts"]["selected"] == 0
    assert data["ingested_items"] == []
    assert data["source_errors"] == []
    assert data["sources_checked"][0]["status"] == "ok"
    assert data["sources_checked"][0]["item_count"] == 0
