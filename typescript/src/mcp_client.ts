/**
 * HTTP client for Context.dev hosted MCP (search_docs + execute).
 */

const MCP_URL = process.env.CONTEXT_DEV_MCP_URL ?? "https://context-dev.stlmcp.com";

function apiKey(): string {
  const key = process.env.CONTEXT_DEV_API_KEY ?? process.env.CONTEXT_API_KEY;
  if (!key) throw new Error("CONTEXT_DEV_API_KEY is required");
  return key;
}

function parseSse(raw: string): Record<string, unknown> {
  for (const line of raw.split("\n")) {
    if (line.startsWith("data: ")) {
      return JSON.parse(line.slice(6)) as Record<string, unknown>;
    }
  }
  throw new Error(`No SSE data in MCP response: ${raw.slice(0, 200)}`);
}

async function mcpRequest(
  method: string,
  params?: Record<string, unknown>,
  id = 1
): Promise<Record<string, unknown>> {
  const res = await fetch(MCP_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
      "User-Agent": "context-dev-exploration-ts/1.0",
      "x-context-dev-api-key": apiKey(),
    },
    body: JSON.stringify({ jsonrpc: "2.0", id, method, params }),
  });
  if (!res.ok) {
    throw new Error(`MCP HTTP ${res.status}: ${(await res.text()).slice(0, 300)}`);
  }
  const payload = parseSse(await res.text());
  if (payload.error) throw new Error(JSON.stringify(payload.error));
  return (payload.result as Record<string, unknown>) ?? payload;
}

export type DocHit = {
  id: string;
  signature: string;
  returns: string;
  credits: string;
  description: string;
};

export async function hostedSearchDocs(
  query: string,
  language = "typescript"
): Promise<DocHit[]> {
  const result = await mcpRequest("tools/call", {
    name: "search_docs",
    arguments: { query, language, detail: "default" },
  }, 42);
  const content = (result.content as Array<{ type: string; text?: string }>) ?? [];
  const text = content.find((b) => b.type === "text")?.text ?? "";
  if (!text) throw new Error("search_docs returned empty content");
  const methods = JSON.parse(text) as Array<Record<string, unknown>>;
  return methods.slice(0, 5).map((m) => ({
    id: String(m.method ?? ""),
    signature: String((m.params as string[])?.[0] ?? ""),
    returns: String(m.summary ?? ""),
    credits: "",
    description: String(m.description ?? ""),
  }));
}

export async function hostedExecute(
  code: string,
  intent = ""
): Promise<Record<string, unknown>> {
  const args: Record<string, string> = { code };
  if (intent) args.intent = intent;
  const result = await mcpRequest("tools/call", {
    name: "execute",
    arguments: args,
  }, 43);
  const content = (result.content as Array<{ type: string; text?: string }>) ?? [];
  const text = content.find((b) => b.type === "text")?.text ?? "";
  if (!text) return { content };
  try {
    return JSON.parse(text) as Record<string, unknown>;
  } catch {
    return { raw: text };
  }
}

export function extractDomain(goal: string): string {
  const m = goal.toLowerCase().match(/[\w-]+\.[\w]{2,}/);
  return m?.[0] ?? "stripe.com";
}

export function buildExecuteTypescript(domain: string): string {
  return `
async function run(client) {
  const domain = "${domain}";
  const brand = await client.brand.retrieve({ domain });
  const style = await client.web.extractStyleguide({ domain });
  const sm = await client.web.webScrapeSitemap({ domain });
  const sg = style.styleguide;
  const c = sg?.colors as { accent?: string; background?: string; text?: string } | undefined;
  const colorCount = [c?.accent, c?.background, c?.text].filter(Boolean).length;
  return {
    identity: { title: brand.brand?.title, logo_url: brand.brand?.logos?.[0]?.url },
    design_tokens: { color_count: colorCount, has_typography: !!sg?.typography },
    site_scale: { url_count: (sm.urls || []).length, sample_paths: (sm.urls || []).slice(0, 3) },
  };
}
`.trim();
}