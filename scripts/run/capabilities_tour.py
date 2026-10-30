"""Run the capability tour and write evidence/runs/capabilities-<date>.json."""
import datetime as dt, json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from context.dev import ContextDev  # noqa: E402
from context_dev import capabilities as cap  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
c = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
steps = {
    "web_search": lambda: cap.web_search(c, "open source web scraping API for AI agents"),
    "crawl": lambda: cap.crawl(c, "https://docs.context.dev/scrape/overview", 3),
    "scrape_json": lambda: cap.scrape_json(c, "https://www.context.dev/pricing"),
    "scrape_product": lambda: cap.scrape_product(c, "https://www.allbirds.com/products/mens-tree-runners"),
    "prebuilt_parser": lambda: cap.prebuilt_parser(c, "https://play.google.com/store/apps/details?id=com.duolingo", "google-play"),
    "screenshot": lambda: cap.screenshot(c, "stripe.com"),
    "styleguide": lambda: cap.styleguide(c, "linear.app"),
    "brand_by_domain": lambda: cap.brand_by_domain(c, "linear.app"),
    "competitors": lambda: cap.competitors(c, "linear.app", 5),
    "images": lambda: cap.images(c, "https://linear.app"),
    "parse_file": lambda: cap.parse_file(c, ROOT / "tests/fixtures/files/invoice-sample.pdf"),
}
out = {"run_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "sdk": "context.dev 2.41.1", "results": {}}
for name, fn in steps.items():
    if len(sys.argv) > 1 and name not in sys.argv[1:]:
        continue
    try:
        out["results"][name] = {"ok": True, **fn()}
    except Exception as e:  # record, never echo headers/keys
        out["results"][name] = {"ok": False, "error": type(e).__name__, "detail": str(e)[:300]}
    print(name, "ok" if out["results"][name]["ok"] else "ERR", out["results"][name].get("credits"))
p = ROOT / f"evidence/runs/capabilities-{dt.date.today()}.json"
p.write_text(json.dumps(out, indent=2, default=str))
print("wrote", p.relative_to(ROOT))
