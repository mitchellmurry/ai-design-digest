"""Daily artifact writer for source health and ingestion snapshots."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.feed_fetcher import Article


def article_to_dict(article: Article) -> dict[str, Any]:
    return asdict(article)


def write_daily_artifact(
    *,
    artifact_path: str | Path,
    run_date: str,
    window_start: str,
    window_end: str,
    sources_checked: list[dict[str, Any]],
    source_errors: list[dict[str, Any]],
    fetched_items: list[Article],
    ingested_items: list[Article],
    selected_items: list[Article],
) -> dict[str, Any]:
    payload = {
        "run_date": run_date,
        "window": {"start": window_start, "end": window_end},
        "sources_checked": sources_checked,
        "source_errors": source_errors,
        "counts": {
            "fetched": len(fetched_items),
            "ingested": len(ingested_items),
            "selected": len(selected_items),
        },
        "fetched_items": [article_to_dict(a) for a in fetched_items],
        "ingested_items": [article_to_dict(a) for a in ingested_items],
    }

    path = Path(artifact_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
