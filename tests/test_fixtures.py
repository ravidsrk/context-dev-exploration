"""Structural checks on committed API fixtures."""

import json
from pathlib import Path

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_brand_fixture_has_required_fields():
    data = json.loads((FIXTURES / "brand-stripe-sample.json").read_text())
    assert data["title"]
    assert data["domain"]
    assert data["logo_url"].startswith("https://")


def test_naics_fixture_has_codes():
    data = json.loads((FIXTURES / "naics-stripe-sample.json").read_text())
    assert len(data["codes"]) >= 1
    assert data["codes"][0]["code"]
    assert data["codes"][0]["confidence"] in ("high", "medium", "low")