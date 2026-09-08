"""Parsing, granularity detection and row validation for population imports.

Pure and synchronous - no DB, no Celery. The import task feeds a file object
in and inserts the batches this module yields. Kept chunk-based so NISR-scale
files (>1M rows) never fully materialise in memory.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import IO, Iterator

import pandas as pd

from app.models.population import (
    AreaType,
    Granularity,
    MaritalStatus,
    RelationshipToHead,
    Sex,
)

CHUNK_SIZE = 50_000
MAX_REJECTION_SAMPLES = 25

MIN_AGE, MAX_AGE = 0, 122

_RELATIONSHIP_ALIASES = {
    "head": RelationshipToHead.head,
    "household head": RelationshipToHead.head,
    "spouse": RelationshipToHead.spouse,
    "wife": RelationshipToHead.spouse,
    "husband": RelationshipToHead.spouse,
    "child": RelationshipToHead.child,
    "son": RelationshipToHead.child,
    "daughter": RelationshipToHead.child,
    "parent": RelationshipToHead.parent,
    "father": RelationshipToHead.parent,
    "mother": RelationshipToHead.parent,
    "other relative": RelationshipToHead.other_relative,
    "other_relative": RelationshipToHead.other_relative,
    "non-relative": RelationshipToHead.non_relative,
    "non_relative": RelationshipToHead.non_relative,
    "not related": RelationshipToHead.non_relative,
}

_MARITAL_ALIASES = {
    "never married": MaritalStatus.never_married,
    "never_married": MaritalStatus.never_married,
    "single": MaritalStatus.never_married,
    "married": MaritalStatus.married,
    "divorced": MaritalStatus.divorced,
    "widowed": MaritalStatus.widowed,
    "separated": MaritalStatus.separated,
}


class GranularityDetectionError(ValueError):
    """Raised when the file's columns match neither storage tier."""


@dataclass
class ImportReport:
    granularity: str = ""
    imported: int = 0
    rejected: int = 0
    rejection_samples: list[str] = field(default_factory=list)

    def reject(self, row_number: int, reason: str) -> None:
        self.rejected += 1
        if len(self.rejection_samples) < MAX_REJECTION_SAMPLES:
            self.rejection_samples.append(f"row {row_number}: {reason}")

    def as_dict(self) -> dict:
        return {
            "granularity": self.granularity,
            "imported": self.imported,
            "rejected": self.rejected,
            "rejection_samples": self.rejection_samples,
        }


@dataclass
class Batch:
    tier: str  # "microdata" | "records"
    rows: list[dict]


def _norm_columns(columns) -> set[str]:
    return {str(c).strip().lower() for c in columns}


def detect_granularity(columns) -> Granularity:
    """Detect the storage tier from column headers.

    Aggregate markers (`age_band` + `population_count`) win over microdata
    markers, since an aggregate export never carries per-person columns.
    """
    cols = _norm_columns(columns)
    if {"age_band", "population_count"} <= cols:
        return Granularity.aggregate
    if cols & {"household_id", "person_id"} or {"age", "sex"} <= cols:
        return Granularity.microdata
    raise GranularityDetectionError(
        "Could not detect dataset format from columns: "
        f"{sorted(cols)}. Expected microdata columns (household_id/person_id/age) "
        "or aggregate columns (age_band/population_count)."
    )


def _clean(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def _parse_int(value, label: str) -> int:
    text = _clean(value)
    if text is None:
        raise ValueError(f"{label} is required")
    try:
        return int(float(text))
    except ValueError:
        raise ValueError(f"{label} is not an integer ({value!r})")


def _validate_microdata_row(raw: dict) -> dict:
    household_id = _clean(raw.get("household_id")) or _clean(raw.get("hhid"))
    if not household_id:
        raise ValueError("household_id is required")

    person_id = _parse_int(raw.get("person_id") or raw.get("pid") or raw.get("line_no"), "person_id")

    province_code = _parse_int(raw.get("province_code") or raw.get("province"), "province_code")
    district_code = _parse_int(raw.get("district_code") or raw.get("district"), "district_code")
    sector_code = _parse_int(raw.get("sector_code") or raw.get("sector"), "sector_code")

    if not 1 <= province_code <= 5:
        raise ValueError(f"province_code out of range 1-5 ({province_code})")
    # District: 2-digit, leading digit = province. Sector: 4-digit, leading digit
    # = province. NISR's district/sector codes don't strictly nest digit-for-digit
    # (docs give district 12 but sector 1101), so only the province digit is checked.
    if not 10 <= district_code <= 59 or district_code // 10 != province_code:
        raise ValueError(f"district_code {district_code} malformed for province {province_code}")
    if not 1000 <= sector_code <= 5999 or sector_code // 1000 != province_code:
        raise ValueError(f"sector_code {sector_code} malformed for province {province_code}")

    area_raw = (_clean(raw.get("area_type")) or _clean(raw.get("urban_rural")) or "").lower()
    try:
        area_type = AreaType(area_raw)
    except ValueError:
        raise ValueError(f"area_type must be urban/rural ({area_raw!r})")

    sex_raw = (_clean(raw.get("sex")) or "").lower()
    sex_raw = {"m": "male", "f": "female"}.get(sex_raw, sex_raw)
    try:
        sex = Sex(sex_raw)
    except ValueError:
        raise ValueError(f"sex must be male/female ({sex_raw!r})")

    age = _parse_int(raw.get("age"), "age")
    if not MIN_AGE <= age <= MAX_AGE:
        raise ValueError(f"age out of range {MIN_AGE}-{MAX_AGE} ({age})")

    rel_raw = (_clean(raw.get("relationship_to_head")) or _clean(raw.get("relationship")) or "").lower()
    relationship = _RELATIONSHIP_ALIASES.get(rel_raw, RelationshipToHead.other_relative)

    mar_raw = (_clean(raw.get("marital_status")) or "").lower()
    marital_status = _MARITAL_ALIASES.get(mar_raw)

    return {
        "household_id": household_id,
        "person_id": person_id,
        "province_code": province_code,
        "district_code": district_code,
        "sector_code": sector_code,
        "area_type": area_type,
        "sex": sex,
        "age": age,
        "relationship_to_head": relationship,
        "marital_status": marital_status,
    }


def _validate_record_row(raw: dict) -> dict:
    sub_region_id = _clean(raw.get("sub_region_id")) or _clean(raw.get("sector_code")) or _clean(raw.get("district_code"))
    if not sub_region_id:
        raise ValueError("sub_region_id (or sector_code/district_code) is required")

    age_band = _clean(raw.get("age_band"))
    if not age_band:
        raise ValueError("age_band is required")

    population_count = _parse_int(raw.get("population_count"), "population_count")
    if population_count < 0:
        raise ValueError(f"population_count must be >= 0 ({population_count})")

    density_raw = _clean(raw.get("density_per_km2"))
    density = float(density_raw) if density_raw is not None else None

    ur_raw = (_clean(raw.get("urban_rural")) or _clean(raw.get("area_type")) or "").lower()
    try:
        urban_rural = AreaType(ur_raw)
    except ValueError:
        raise ValueError(f"urban_rural must be urban/rural ({ur_raw!r})")

    return {
        "sub_region_id": sub_region_id,
        "age_band": age_band,
        "population_count": population_count,
        "density_per_km2": density,
        "urban_rural": urban_rural,
    }


def iter_import_batches(
    file_obj: IO,
    stated_granularity: Granularity | None = None,
    *,
    chunk_size: int = CHUNK_SIZE,
    report: ImportReport | None = None,
) -> Iterator[Batch]:
    """Yield validated insert-ready batches, one per CSV chunk.

    `report` is mutated in place with running counts and a sample of rejection
    reasons. Invalid rows are counted and skipped, never fatal.
    """
    report = report if report is not None else ImportReport()
    reader = pd.read_csv(file_obj, dtype=str, chunksize=chunk_size, skipinitialspace=True)

    detected: Granularity | None = None
    validator = None
    tier = ""
    row_number = 1  # header is row 1

    for chunk in reader:
        chunk.columns = [str(c).strip().lower() for c in chunk.columns]
        if detected is None:
            detected = detect_granularity(chunk.columns)
            report.granularity = detected.value
            if detected is Granularity.microdata:
                validator, tier = _validate_microdata_row, "microdata"
            else:
                validator, tier = _validate_record_row, "records"

        valid: list[dict] = []
        for raw in chunk.to_dict(orient="records"):
            row_number += 1
            try:
                valid.append(validator(raw))
            except ValueError as exc:
                report.reject(row_number, str(exc))

        report.imported += len(valid)
        if valid:
            yield Batch(tier=tier, rows=valid)

    if detected is None:
        raise GranularityDetectionError("File is empty - no header row found")
