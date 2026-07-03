/**
 * Canonical op mapping for MCP search_docs / LLM execute plan IDs.
 * Mirrors context_dev.mcp.op_map.py.
 */

export type DocHit = {
  id: string;
  signature: string;
  returns: string;
  credits: string;
  description: string;
};

export type ExecuteStep = { op: string; args: Record<string, string> };

export const CANONICAL_OPS = new Set([
  "brand.retrieve",
  "web.extract_styleguide",
  "web.scrape_sitemap",
]);

export const OP_CREDITS: Record<string, number> = {
  "brand.retrieve": 10,
  "web.extract_styleguide": 10,
  "web.scrape_sitemap": 1,
};

const OP_ALIASES: Record<string, string> = {
  "brand.retrieve": "brand.retrieve",
  "client.brand.retrieve": "brand.retrieve",
  "client.brand.retrievesimplified": "brand.retrieve",
  "client.brand.retrieveSimplified": "brand.retrieve",
  "web.extract_styleguide": "web.extract_styleguide",
  "client.web.extract_styleguide": "web.extract_styleguide",
  "client.web.extractStyleguide": "web.extract_styleguide",
  "web.scrape_sitemap": "web.scrape_sitemap",
  "client.brand.webscrapesitemap": "web.scrape_sitemap",
  "client.brand.webScrapeSitemap": "web.scrape_sitemap",
  "client.web.webScrapeSitemap": "web.scrape_sitemap",
};

export function canonicalizeOp(opId: string): string | null {
  if (!opId) return null;
  const stripped = opId.trim();
  if (CANONICAL_OPS.has(stripped)) return stripped;
  if (OP_ALIASES[stripped]) return OP_ALIASES[stripped];
  const lowered = stripped.toLowerCase();
  if (OP_ALIASES[lowered]) return OP_ALIASES[lowered];
  return null;
}

export function normalizeExecutePlan(
  goal: string,
  rawPlan: ExecuteStep[],
  hits: DocHit[],
  domain: string
): ExecuteStep[] {
  const candidates: ExecuteStep[] = rawPlan.length
    ? [...rawPlan]
    : hits.map((h) => ({ op: h.id, args: {} }));

  const seen = new Set<string>();
  const normalized: ExecuteStep[] = [];

  for (const step of candidates) {
    const canonical = canonicalizeOp(step.op);
    if (!canonical || seen.has(canonical)) continue;
    const args = { ...(step.args ?? {}) };
    if (!args.domain) args.domain = domain;
    normalized.push({ op: canonical, args });
    seen.add(canonical);
  }

  if (
    !seen.has("web.scrape_sitemap") &&
    (goal.toLowerCase().includes("scale") ||
      hits.some((h) => (h.id ?? "").toLowerCase().includes("sitemap")))
  ) {
    normalized.push({ op: "web.scrape_sitemap", args: { domain } });
  }

  if (!normalized.length) {
    return [
      { op: "brand.retrieve", args: { domain } },
      { op: "web.extract_styleguide", args: { domain } },
      { op: "web.scrape_sitemap", args: { domain } },
    ];
  }
  return normalized;
}