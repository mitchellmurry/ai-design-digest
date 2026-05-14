"""Source registry loader and validation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


VALID_TIERS = {"authority", "trusted interpretation", "selective longform"}
VALID_FETCH_METHODS = {"rss", "web_listing"}
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


@dataclass(frozen=True)
class SourceDefinition:
    id: str
    name: str
    url: str
    tier: str
    type: str
    trust_weight: float
    topics: list[str]
    fetch_method: str
    cadence: str
    notes: str
    raw: dict[str, Any]


@dataclass(frozen=True)
class SourceRegistry:
    version: int
    schema: str
    sources: list[SourceDefinition]


@dataclass(frozen=True)
class ValidationError:
    source_id: str
    field: str
    message: str


class SourceRegistryValidationError(ValueError):
    def __init__(self, errors: list[ValidationError]):
        self.errors = errors
        detail = "; ".join(f"{e.source_id}.{e.field}: {e.message}" for e in errors)
        super().__init__(f"Source registry validation failed ({len(errors)} errors): {detail}")


def _parse_registry_text(text: str) -> tuple[int, str, list[dict[str, str]]]:
    lines = [ln.rstrip() for ln in text.splitlines()]
    if len(lines) < 2:
        raise ValueError("Registry file must start with version and schema headers")

    version_line = lines[0]
    schema_line = lines[1]
    if not version_line.startswith("version:"):
        raise ValueError("First line must be 'version: <int>'")
    if not schema_line.startswith("schema:"):
        raise ValueError("Second line must be 'schema: <value>'")

    version = int(version_line.split(":", 1)[1].strip())
    schema = schema_line.split(":", 1)[1].strip()

    records: list[dict[str, str]] = []
    current: dict[str, str] = {}

    for line in lines[2:]:
        if not line.strip():
            continue
        if line.strip() == "---":
            if current:
                records.append(current)
                current = {}
            continue
        key, sep, value = line.partition(":")
        if sep != ":":
            raise ValueError(f"Invalid registry line: {line}")
        current[key.strip()] = value.strip()

    if current:
        records.append(current)

    return version, schema, records


def _to_source_definition(record: dict[str, str]) -> SourceDefinition:
    topics = [part.strip() for part in record.get("topics", "").split(",") if part.strip()]
    try:
        trust_weight = float(record.get("trust_weight", "nan"))
    except ValueError:
        trust_weight = float("nan")

    return SourceDefinition(
        id=record.get("id", ""),
        name=record.get("name", ""),
        url=record.get("url", ""),
        tier=record.get("tier", ""),
        type=record.get("type", ""),
        trust_weight=trust_weight,
        topics=topics,
        fetch_method=record.get("fetch_method", ""),
        cadence=record.get("cadence", ""),
        notes=record.get("notes", ""),
        raw=dict(record),
    )


def load_source_registry(path: str | Path, validate: bool = False) -> SourceRegistry:
    file_path = Path(path)
    version, schema, records = _parse_registry_text(file_path.read_text(encoding="utf-8"))
    registry = SourceRegistry(
        version=version,
        schema=schema,
        sources=[_to_source_definition(record) for record in records],
    )

    if validate:
        errors = validate_source_registry(registry)
        if errors:
            raise SourceRegistryValidationError(errors)

    return registry


def validate_source_registry(registry: SourceRegistry) -> list[ValidationError]:
    errors: list[ValidationError] = []

    for source in registry.sources:
        source_id = source.id or "<missing-id>"
        for field in REQUIRED_FIELDS:
            value = source.raw.get(field, "")
            if not str(value).strip():
                errors.append(ValidationError(source_id=source_id, field=field, message="Field is required"))

        if source.tier and source.tier not in VALID_TIERS:
            errors.append(
                ValidationError(
                    source_id=source_id,
                    field="tier",
                    message=f"Invalid tier '{source.tier}'",
                )
            )

        if source.fetch_method and source.fetch_method not in VALID_FETCH_METHODS:
            errors.append(
                ValidationError(
                    source_id=source_id,
                    field="fetch_method",
                    message=f"Invalid fetch_method '{source.fetch_method}'",
                )
            )

        if source.raw.get("trust_weight", ""):
            if not (0.0 <= source.trust_weight <= 1.0):
                errors.append(
                    ValidationError(
                        source_id=source_id,
                        field="trust_weight",
                        message="trust_weight must be between 0.0 and 1.0",
                    )
                )

    return errors
