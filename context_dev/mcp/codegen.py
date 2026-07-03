"""Generate TypeScript for hosted MCP execute sandbox."""

from __future__ import annotations

from typing import Any


def build_execute_typescript(domain: str, plan: list[dict[str, Any]] | None = None) -> str:
    """
    Build async run(client) TypeScript matching hosted MCP SDK shape (client.web.*).
    """
    ops = {step.get("op") for step in (plan or [])}
    if not ops:
        ops = {"brand.retrieve", "web.extract_styleguide", "web.scrape_sitemap"}

    lines = [
        "async function run(client) {",
        f'  const domain = "{domain}";',
    ]

    if "brand.retrieve" in ops:
        lines.append("  const brand = await client.brand.retrieve({ domain });")
    # Hosted sandbox SDK: web.* only — client.brand.styleguide triggers TS2339 on Brand.
    if "web.extract_styleguide" in ops:
        lines.append("  const style = await client.web.extractStyleguide({ domain });")
    if "web.scrape_sitemap" in ops:
        lines.append("  const sm = await client.web.webScrapeSitemap({ domain });")

    lines.append("  return {")
    if "brand.retrieve" in ops:
        lines.extend(
            [
                "    identity: {",
                "      title: brand.brand?.title,",
                "      logo_url: brand.brand?.logos?.[0]?.url,",
                "    },",
            ]
        )
    if "web.extract_styleguide" in ops:
        lines.extend(
            [
                "    design_tokens: {",
                "      color_count: [style.styleguide?.colors?.accent, style.styleguide?.colors?.background, style.styleguide?.colors?.text].filter(Boolean).length,",
                "      has_typography: !!style.styleguide?.typography,",
                "    },",
            ]
        )
    if "web.scrape_sitemap" in ops:
        lines.extend(
            [
                "    site_scale: {",
                "      url_count: (sm.urls || []).length,",
                "      sample_paths: (sm.urls || []).slice(0, 3),",
                "    },",
            ]
        )
    lines.append("  };")
    lines.append("}")

    return "\n".join(lines)