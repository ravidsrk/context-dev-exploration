from types import SimpleNamespace

from context_dev import capabilities as cap


class R:
    def __init__(self, d):
        self.d = d

    def model_dump(self, exclude_none=True):
        return self.d


def test_competitors_summary_keeps_only_public_fields():
    resp = R({"target": {"field": "issue tracking"}, "competitors": [
        {"name": "Jira", "domain": "atlassian.com", "confidence": "high", "description": "x"}],
        "key_metadata": {"credits_consumed": 10}})
    client = SimpleNamespace(web=SimpleNamespace(extract_competitors=lambda **k: resp))
    out = cap.competitors(client, "linear.app")
    assert out == {"domain": "linear.app", "field": "issue tracking", "credits": 10,
                   "competitors": [{"name": "Jira", "domain": "atlassian.com", "confidence": "high"}]}


def test_product_summary():
    resp = R({"product": {"data": {"is_product_page": True, "product": {"name": "Shoe", "price": 100.0, "variants": [1, 2]}}},
              "key_metadata": {"credits_consumed": 2}})
    client = SimpleNamespace(web=SimpleNamespace(scrape=lambda **k: resp))
    out = cap.scrape_product(client, "u")
    assert out["product"]["price"] == 100.0 and out["variant_count"] == 2 and out["credits"] == 2
