"""Deterministic tests for source registry v1 content and schema shape."""

from pathlib import Path


REGISTRY_PATH = Path(__file__).resolve().parents[1] / "registry" / "sources.v1.txt"
REQUIRED_FIELDS = {
    "id",
    "name",
    "url",
    "tier",
    "type",
    "trust_weight",
    "topics",
    "fetch_method",
    "cadence",
    "notes",
}


def _parse_registry(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = [ln.rstrip() for ln in text.splitlines()]

    assert lines[0] == "version: 1"
    assert lines[1] == "schema: ai-design-digest.source-registry"

    records = []
    current = {}

    for line in lines[2:]:
        if not line.strip():
            continue
        if line.strip() == "---":
            if current:
                records.append(current)
                current = {}
            continue

        key, sep, value = line.partition(":")
        assert sep == ":", f"Invalid registry line: {line}"
        current[key.strip()] = value.strip()

    if current:
        records.append(current)

    return records


def test_registry_file_exists_and_is_versioned():
    assert REGISTRY_PATH.exists(), "Expected registry/sources.v1.txt to exist"
    records = _parse_registry(REGISTRY_PATH)
    assert records, "Registry must contain source records"


def test_registry_records_have_required_schema_and_value_ranges():
    records = _parse_registry(REGISTRY_PATH)
    valid_tiers = {"authority", "trusted interpretation", "selective longform"}
    valid_fetch_methods = {"rss", "web_listing"}

    seen_ids = set()
    for record in records:
        assert REQUIRED_FIELDS.issubset(record.keys())
        assert record["id"] not in seen_ids
        seen_ids.add(record["id"])

        assert record["tier"] in valid_tiers
        assert record["fetch_method"] in valid_fetch_methods
        assert record["url"].startswith("https://")

        weight = float(record["trust_weight"])
        assert 0.0 <= weight <= 1.0


def test_registry_includes_required_rss_and_web_listing_sources():
    records = _parse_registry(REGISTRY_PATH)
    by_id = {record["id"]: record for record in records}

    expected_rss = {
        "openai",
        "lennys-newsletter",
        "lennys-podcast",
        "bens-bites",
        "diary-of-a-ceo",
    }
    expected_web_listing = {
        "anthropic",
        "figma-blog",
        "every-to",
        "the-batch",
        "knowentry",
    }

    assert expected_rss.issubset(by_id.keys())
    assert expected_web_listing.issubset(by_id.keys())

    for source_id in expected_rss:
        assert by_id[source_id]["fetch_method"] == "rss"

    for source_id in expected_web_listing:
        assert by_id[source_id]["fetch_method"] == "web_listing"
