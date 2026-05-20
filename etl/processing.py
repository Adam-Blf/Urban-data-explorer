from __future__ import annotations

import csv
import io
import json
import re
from datetime import date, datetime
from typing import Iterable

import polars as pl
import requests

from .catalog import SourceSpec


def _detect_delimiter(sample: str) -> str:
    """Guess the delimiter of a flat file payload."""

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t,")
        return dialect.delimiter
    except csv.Error:
        return ";"


def resolve_payload(spec: SourceSpec) -> bytes:
    """Fetch the raw payload for a downloadable source."""

    if not spec.download_url:
        raise ValueError(f"Source not downloadable: {spec.source_id}")
    response = requests.get(spec.download_url, timeout=120)
    response.raise_for_status()
    return response.content


def read_source_frame(spec: SourceSpec) -> pl.DataFrame:
    """Read one source into a Polars dataframe regardless of format."""

    payload = resolve_payload(spec)
    text = payload.decode("utf-8", errors="ignore")
    if text.lstrip().startswith("{") or text.lstrip().startswith("["):
        return pl.read_json(io.BytesIO(payload))
    delimiter = _detect_delimiter(text[:4096])
    return pl.read_csv(
        io.BytesIO(payload),
        separator=delimiter,
        infer_schema_length=200,
        ignore_errors=True,
        try_parse_dates=True,
        null_values=["", "null", "NULL", "NaN"],
    )


def _first_value(row: dict[str, object], candidates: Iterable[str]) -> object | None:
    for name in candidates:
        value = row.get(name)
        if value is not None and str(value).strip() not in {"", "null", "NULL", "nan", "None"}:
            return value
    return None


def _normalize_code(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    digits = re.sub(r"\D", "", text)
    if len(digits) >= 5 and digits.startswith("75"):
        return f"75{int(digits[-2:]):03d}"
    if digits.isdigit():
        number = int(digits)
        if 1 <= number <= 20:
            return f"75{number:03d}"
        if 75001 <= number <= 75999:
            return f"75{number % 100:03d}"
    lowered = text.lower()
    match = re.search(r"(\d{1,2})", lowered)
    if match:
        number = int(match.group(1))
        if 1 <= number <= 20:
            return f"75{number:03d}"
    return None


def _to_float(value: object | None) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return None


def build_bronze_records(spec: SourceSpec, frame: pl.DataFrame, snapshot_date: str) -> list[dict[str, object]]:
    """Wrap raw rows with ingestion metadata for the Bronze layer."""

    records: list[dict[str, object]] = []
    for row in frame.to_dicts():
        raw_payload = json.dumps(row, ensure_ascii=False, default=str)
        records.append(
            {
                "source_id": spec.source_id,
                "source_title": spec.title,
                "family": spec.family,
                "snapshot_date": snapshot_date,
                "raw_payload": raw_payload,
                "load_ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }
        )
    return records


def build_silver_records(spec: SourceSpec, bronze_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Normalize Bronze rows into a shared Silver schema."""

    records: list[dict[str, object]] = []
    for row in bronze_rows:
        payload = json.loads(str(row["raw_payload"]))
        arrondissement_code = _normalize_code(
            _first_value(payload, spec.arrondissement_candidates)
            or _first_value(payload, spec.postal_candidates)
        )
        postal_code = _first_value(payload, spec.postal_candidates)
        records.append(
            {
                **row,
                "arrondissement_code": arrondissement_code,
                "postal_code": _normalize_code(postal_code) if postal_code else None,
                "status": _first_value(payload, spec.status_candidates),
                "category": _first_value(payload, spec.category_candidates),
                "latitude": _to_float(_first_value(payload, spec.latitude_candidates)),
                "longitude": _to_float(_first_value(payload, spec.longitude_candidates)),
                "quality_flag": "ok" if arrondissement_code else "needs_review",
            }
        )
    return records


def _family_counts(frame: pl.DataFrame) -> pl.DataFrame:
    if frame.is_empty():
        return pl.DataFrame(
            {
                "arrondissement_code": [],
                "green_space_count": [],
                "mobility_count": [],
                "public_service_count": [],
                "education_count": [],
                "culture_count": [],
                "health_count": [],
                "housing_count": [],
                "pressure_count": [],
            }
        )
    pivot = (
        frame.filter(pl.col("arrondissement_code").is_not_null())
        .group_by(["arrondissement_code", "family"])
        .len()
        .pivot(
            index="arrondissement_code",
            columns="family",
            values="len",
            aggregate_function="first",
        )
        .fill_null(0)
    )
    rename_map = {
        "green_space": "green_space_count",
        "mobility": "mobility_count",
        "public_service": "public_service_count",
        "education": "education_count",
        "culture": "culture_count",
        "health": "health_count",
        "housing": "housing_count",
        "pressure": "pressure_count",
    }
    for src, dst in rename_map.items():
        if src not in pivot.columns:
            pivot = pivot.with_columns(pl.lit(0).alias(src))
        pivot = pivot.rename({src: dst})
    return pivot


def _scale_series(values: list[int | float]) -> list[float]:
    if not values:
        return []
    minimum = min(values)
    maximum = max(values)
    if minimum == maximum:
        return [50.0 for _ in values]
    return [round((value - minimum) / (maximum - minimum) * 100, 2) for value in values]


def build_gold_dashboard(silver_frame: pl.DataFrame) -> pl.DataFrame:
    """Aggregate Silver rows into an arrondissement KPI dashboard."""

    counts = _family_counts(silver_frame)
    if counts.is_empty():
        return counts
    counts = counts.with_columns(
        (
            pl.col("mobility_count") * 0.25
            + pl.col("public_service_count") * 0.15
            + pl.col("education_count") * 0.15
            + pl.col("health_count") * 0.15
            + pl.col("green_space_count") * 0.15
            + pl.col("culture_count") * 0.15
        ).alias("accessibility_raw"),
        (
            pl.col("pressure_count") * 0.65 + pl.col("housing_count") * 0.35
        ).alias("pressure_raw"),
        (
            pl.col("green_space_count") * 0.22
            + pl.col("mobility_count") * 0.22
            + pl.col("public_service_count") * 0.18
            + pl.col("culture_count") * 0.18
            + pl.col("health_count") * 0.10
            + pl.col("education_count") * 0.10
        ).alias("attractiveness_raw"),
    )
    counts = counts.with_columns(
        pl.Series("accessibility_index", _scale_series(counts["accessibility_raw"].to_list())),
        pl.Series("pressure_index", _scale_series(counts["pressure_raw"].to_list())),
        pl.Series("attractiveness_index", _scale_series(counts["attractiveness_raw"].to_list())),
    )
    return counts.select(
        [
            "arrondissement_code",
            "green_space_count",
            "mobility_count",
            "public_service_count",
            "education_count",
            "culture_count",
            "health_count",
            "housing_count",
            "pressure_count",
            "accessibility_index",
            "pressure_index",
            "attractiveness_index",
        ]
    ).sort("arrondissement_code")


def build_gold_timeline(silver_frame: pl.DataFrame) -> pl.DataFrame:
    """Build a monthly trend table for the Gold mart."""

    if silver_frame.is_empty():
        return pl.DataFrame(
            {
                "arrondissement_code": [],
                "year": [],
                "month": [],
                "record_count": [],
                "accessibility_index": [],
                "pressure_index": [],
                "attractiveness_index": [],
            }
        )
    with_dates = silver_frame.with_columns(
        pl.col("snapshot_date").str.strptime(pl.Date, strict=False).alias("snapshot_dt")
    )
    grouped = (
        with_dates.filter(pl.col("arrondissement_code").is_not_null())
        .with_columns(
            pl.col("snapshot_dt").dt.year().alias("year"),
            pl.col("snapshot_dt").dt.month().alias("month"),
        )
        .group_by(["arrondissement_code", "year", "month"])
        .agg(
            pl.len().alias("record_count"),
            pl.col("family").n_unique().alias("family_count"),
            pl.col("family").count().alias("event_volume"),
        )
        .sort(["arrondissement_code", "year", "month"])
    )
    grouped = grouped.with_columns(
        pl.Series("accessibility_index", _scale_series(grouped["record_count"].to_list())),
        pl.Series("pressure_index", _scale_series(grouped["event_volume"].to_list())),
        pl.Series("attractiveness_index", _scale_series(grouped["family_count"].to_list())),
    )
    return grouped.select(
        [
            "arrondissement_code",
            "year",
            "month",
            "record_count",
            "accessibility_index",
            "pressure_index",
            "attractiveness_index",
        ]
    )
