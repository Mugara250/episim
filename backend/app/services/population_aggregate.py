"""Derive `population_records` from `population_microdata`.

Grouping key: sector_code + 5-year age band + area_type. `density_per_km2` is
left null - it needs sector land area from Module 9's geographic boundary data,
which isn't built yet (known gap, do not fabricate).
"""
from __future__ import annotations

from collections import Counter

from sqlalchemy import String, case, cast, func, literal, select

from app.models.population import PopulationMicrodata

AGE_BAND_WIDTH = 5
TOP_BAND_FLOOR = 85


def age_to_band(age: int) -> str:
    if age >= TOP_BAND_FLOOR:
        return f"{TOP_BAND_FLOOR}+"
    low = (age // AGE_BAND_WIDTH) * AGE_BAND_WIDTH
    return f"{low}-{low + AGE_BAND_WIDTH - 1}"


def _age_band_sql(age_col):
    low = cast(func.floor(age_col / AGE_BAND_WIDTH) * AGE_BAND_WIDTH, String)
    high = cast(func.floor(age_col / AGE_BAND_WIDTH) * AGE_BAND_WIDTH + (AGE_BAND_WIDTH - 1), String)
    return case(
        (age_col >= TOP_BAND_FLOOR, literal(f"{TOP_BAND_FLOOR}+")),
        else_=low.concat(literal("-")).concat(high),
    )


def aggregation_query(dataset_id):
    """A GROUP BY select that computes the aggregate tier entirely in the DB,
    so a >1M-row microdata set is never pulled into the worker.
    """
    band = _age_band_sql(PopulationMicrodata.age).label("age_band")
    return (
        select(
            cast(PopulationMicrodata.sector_code, String).label("sub_region_id"),
            band,
            PopulationMicrodata.area_type.label("urban_rural"),
            func.count().label("population_count"),
        )
        .where(PopulationMicrodata.dataset_id == dataset_id)
        .group_by(PopulationMicrodata.sector_code, band, PopulationMicrodata.area_type)
    )


def aggregate_rows(rows: list[dict]) -> list[dict]:
    """Pure-Python equivalent of `aggregation_query`, for unit tests."""
    counter: Counter[tuple[str, str, str]] = Counter()
    for row in rows:
        key = (
            str(row["sector_code"]),
            age_to_band(int(row["age"])),
            row["area_type"].value if hasattr(row["area_type"], "value") else str(row["area_type"]),
        )
        counter[key] += 1
    return [
        {
            "sub_region_id": sub_region_id,
            "age_band": age_band,
            "urban_rural": urban_rural,
            "population_count": count,
            "density_per_km2": None,
        }
        for (sub_region_id, age_band, urban_rural), count in sorted(counter.items())
    ]
