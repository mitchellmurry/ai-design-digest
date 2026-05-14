"""Tests for source registry loader and validator."""

from pathlib import Path

from src.source_registry import (
    SourceRegistryValidationError,
    load_source_registry,
    validate_source_registry,
)


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "registry"


def test_load_source_registry_returns_structured_definitions():
    registry = load_source_registry(FIXTURE_DIR / "valid_sources.v1.txt")

    assert registry.version == 1
    assert registry.schema == "ai-design-digest.source-registry"
    assert len(registry.sources) == 2

    first = registry.sources[0]
    assert first.id == "openai"
    assert first.fetch_method == "rss"
    assert first.trust_weight == 1.0
    assert first.topics == ["ai-research", "model-releases", "policy"]


def test_validation_catches_missing_required_fields_with_source_and_field():
    with_errors = load_source_registry(FIXTURE_DIR / "missing_required_field.v1.txt")

    errors = validate_source_registry(with_errors)

    assert len(errors) == 1
    err = errors[0]
    assert err.source_id == "missing-url"
    assert err.field == "url"
    assert "required" in err.message.lower()


def test_validation_catches_invalid_tier_fetch_method_and_weight_ranges():
    with_errors = load_source_registry(FIXTURE_DIR / "invalid_values.v1.txt")

    errors = validate_source_registry(with_errors)
    keyset = {(e.source_id, e.field) for e in errors}

    assert ("bad-tier", "tier") in keyset
    assert ("bad-fetch", "fetch_method") in keyset
    assert ("bad-weight", "trust_weight") in keyset


def test_loader_raises_with_specific_errors_when_validation_requested():
    path = FIXTURE_DIR / "invalid_values.v1.txt"

    try:
        load_source_registry(path, validate=True)
        assert False, "Expected SourceRegistryValidationError"
    except SourceRegistryValidationError as exc:
        details = {(e.source_id, e.field) for e in exc.errors}
        assert ("bad-tier", "tier") in details
        assert ("bad-fetch", "fetch_method") in details
        assert ("bad-weight", "trust_weight") in details
