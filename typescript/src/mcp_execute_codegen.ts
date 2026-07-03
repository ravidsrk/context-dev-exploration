/**
 * Generate TypeScript for hosted MCP execute sandbox.
 * Hosted sandbox SDK uses client.web.* — NOT client.brand.styleguide (TS2339 on Brand).
 */

import type { ExecuteStep } from "./mcp_op_map.js";

export function buildExecuteTypescript(domain: string, plan?: ExecuteStep[]): string {
  const ops = new Set((plan ?? []).map((s) => s.op));
  if (!ops.size) {
    ops.add("brand.retrieve");
    ops.add("web.extract_styleguide");
    ops.add("web.scrape_sitemap");
  }

  const lines = [
    "async function run(client) {",
    `  const domain = "${domain}";`,
  ];

  if (ops.has("brand.retrieve")) {
    lines.push("  const brand = await client.brand.retrieve({ domain });");
  }
  if (ops.has("web.extract_styleguide")) {
    lines.push("  const style = await client.web.extractStyleguide({ domain });");
  }
  if (ops.has("web.scrape_sitemap")) {
    lines.push("  const sm = await client.web.webScrapeSitemap({ domain });");
  }

  lines.push("  return {");
  if (ops.has("brand.retrieve")) {
    lines.push("    identity: {");
    lines.push("      title: brand.brand?.title,");
    lines.push("      logo_url: brand.brand?.logos?.[0]?.url,");
    lines.push("    },");
  }
  if (ops.has("web.extract_styleguide")) {
    lines.push("    design_tokens: {");
    lines.push(
      "      color_count: [style.styleguide?.colors?.accent, style.styleguide?.colors?.background, style.styleguide?.colors?.text].filter(Boolean).length,"
    );
    lines.push("      has_typography: !!style.styleguide?.typography,");
    lines.push("    },");
  }
  if (ops.has("web.scrape_sitemap")) {
    lines.push("    site_scale: {");
    lines.push("      url_count: (sm.urls || []).length,");
    lines.push("      sample_paths: (sm.urls || []).slice(0, 3),");
    lines.push("    },");
  }
  lines.push("  };");
  lines.push("}");

  return lines.join("\n");
}