"""Mocked tests for context_dev.latest (features shipped after July 2026)."""

from __future__ import annotations

from types import SimpleNamespace

from context_dev import latest
from tests.test_context_client import sdk_mock

META = SimpleNamespace(credits_consumed=2, credits_remaining=998)


def test_scrape_highlights_requests_both_formats():
    c = sdk_mock()
    c.web.scrape.return_value = SimpleNamespace(
        markdown=SimpleNamespace(data="# Pricing\n2.9% + 30c"),
        highlights=SimpleNamespace(data=["2.9% + 30c per successful card charge"], error_code=None),
        cache_metadata=SimpleNamespace(status="miss"),
        key_metadata=META,
    )
    out = latest.scrape_highlights(c, "https://stripe.com/pricing", "card fees?")
    kw = c.web.scrape.call_args.kwargs
    assert kw["formats"] == {"markdown": True, "highlights": True}
    assert kw["highlights_params"]["query"] == "card fees?"
    assert out["highlights"][0].startswith("2.9%")
    assert out["cache_status"] == "miss" and out["credits"] == 2


def test_map_search_passes_search_phrase():
    c = sdk_mock()
    c.web.map_urls.return_value = SimpleNamespace(
        urls=[SimpleNamespace(url="https://stripe.com/pricing", title="Pricing")], key_metadata=META)
    out = latest.map_search(c, "stripe.com", "pricing and fees")
    assert c.web.map_urls.call_args.kwargs["search"] == "pricing and fees"
    assert out["urls"][0]["url"].endswith("/pricing")


def test_answers_fast_mode():
    c = sdk_mock()
    c.web.answers.return_value = SimpleNamespace(
        json_content={"plans": []}, sources=["https://www.context.dev/pricing"], partial=None,
        key_metadata=SimpleNamespace(credits_consumed=10, credits_remaining=0))
    out = latest.answers_fast(c, "plans?", {"type": "object"})
    assert c.web.answers.call_args.kwargs["mode"] == "fast"
    assert out["credits"] == 10 and out["sources"]


def test_brand_by_transaction_uses_unified_retrieve():
    c = sdk_mock()
    c.brand.retrieve.return_value = SimpleNamespace(
        brand=SimpleNamespace(title="Starbucks", domain="starbucks.com"), key_metadata=None)
    out = latest.brand_by_transaction(c, "STARBUCKS STORE 12345", mcc=5814)
    assert c.brand.retrieve.call_args.kwargs["type"] == "by_transaction"
    assert out["domain"] == "starbucks.com"


def test_company_search_calls_raw_route():
    c = sdk_mock()
    c.post.return_value = {"results": [{"name": "Acme", "domain": "acme.com"}],
                           "key_metadata": {"credits_consumed": 2, "credits_remaining": 1}}
    out = latest.company_search(c, "scraping APIs")
    assert c.post.call_args.args[0] == "/company/search"
    assert out["results"][0]["domain"] == "acme.com" and out["credits"] == 2


def test_people_search_drops_personal_fields():
    c = sdk_mock()
    person = SimpleNamespace(
        name="Jane Doe", profiles=["https://linkedin.com/in/x"],
        role=SimpleNamespace(title="Head of DevRel", seniority="head",
                             company=SimpleNamespace(name="Acme")))
    c.people.search.return_value = SimpleNamespace(results=[person], key_metadata=META)
    out = latest.people_search(c, "devrel heads")
    assert out["results"][0] == {"title": "Head of DevRel", "company": "Acme", "seniority": "head"}
    assert "Jane" not in str(out)


def test_news_search_natural_language():
    c = sdk_mock()
    c.news.search.return_value = SimpleNamespace(
        data=[SimpleNamespace(title="T", url="https://n", published_at="2026-10-20")], key_metadata=META)
    out = latest.news_search(c, "scraping funding")
    assert c.news.search.call_args.kwargs["search_by"]["type"] == "natural_language"
    assert out["articles"][0]["title"] == "T"


def test_semantic_monitor_create_and_delete():
    c = sdk_mock()
    c.monitors.create.return_value = SimpleNamespace(id="mon_1", status="active", initial_run_id="run_1")
    out = latest.create_semantic_monitor(c, "https://stripe.com/pricing", "price changes only")
    kw = c.monitors.create.call_args.kwargs
    assert kw["target"]["instructions"] == "price changes only"
    assert kw["change_detection"] == {"type": "semantic"}
    assert out["monitor_id"] == "mon_1"
    assert latest.delete_monitor(c, "mon_1")["deleted"] is True


def test_submit_batch_shape():
    c = sdk_mock()
    c.batch.submit.return_value = SimpleNamespace(id="b_1", status="queued", invalid_urls=[], key_metadata=None)
    out = latest.submit_batch(c, ["https://a.com", "https://b.com"])
    inp = c.batch.submit.call_args.kwargs["input"]
    assert inp["mode"] == "scrape" and len(inp["data"]["urls"]) == 2
    assert out["batch_id"] == "b_1"
