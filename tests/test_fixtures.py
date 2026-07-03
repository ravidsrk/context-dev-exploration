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


def test_sic_fixture_has_codes():
    data = json.loads((FIXTURES / "sic-stripe-sample.json").read_text())
    assert data["codes"][0]["code"] == "6199"


def test_styleguide_fixture():
    data = json.loads((FIXTURES / "styleguide-stripe-sample.json").read_text())
    assert data["color_count"] >= 1
    assert data["has_typography"] is True


def test_screenshot_fixture():
    data = json.loads((FIXTURES / "screenshot-stripe-sample.json").read_text())
    assert data["has_screenshot"] is True
    assert data["screenshot_url"].startswith("https://")


def test_crawl_fixture():
    data = json.loads((FIXTURES / "crawl-stripe-sample.json").read_text())
    assert data["num_succeeded"] >= 1


def test_prefetch_fixture():
    data = json.loads((FIXTURES / "prefetch-stripe-sample.json").read_text())
    assert data["status"] == "ok"