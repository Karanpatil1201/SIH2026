import csv
import os
from functools import lru_cache
from typing import Any, Dict

DATASET_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "data",
        "external",
        "fisheries",
        "capture_quantity_joined.csv",
    )
)


@lru_cache(maxsize=1)
def get_summary() -> Dict[str, Any]:
    """Read lightweight fisheries dataset metadata without loading the full million-row table."""
    if not os.path.exists(DATASET_PATH):
        return {"dataset": "capture_quantity_joined.csv", "status": "UNAVAILABLE", "records": 0}

    records = 0
    total_value = 0.0
    countries = set()
    species = set()
    periods = set()
    with open(DATASET_PATH, "r", encoding="utf-8-sig", newline="") as dataset_file:
        for row in csv.DictReader(dataset_file):
            records += 1
            countries.add(row.get("Country", ""))
            species.add(row.get("Common name", ""))
            periods.add(row.get("PERIOD", ""))
            try:
                total_value += float(row.get("VALUE", 0) or 0)
            except ValueError:
                continue

    return {
        "dataset": "capture_quantity_joined.csv",
        "status": "AVAILABLE",
        "records": records,
        "countries": len(countries),
        "species": len(species),
        "period_start": min(periods) if periods else None,
        "period_end": max(periods) if periods else None,
        "total_quantity": round(total_value, 2),
        "target": "VALUE (reported catch quantity)",
    }
