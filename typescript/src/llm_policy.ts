/**
 * OpenRouter LLM policy for agent plan steps (mirrors agents/llm_policy.py).
 */

export type DocHit = {
  id: string;
  signature: string;
  returns: string;
  credits: string;
  description: string;
};

export type ExecuteStep = { op: string; args: Record<string, string> };

const ALLOWED_SCOUT_STEPS = new Set(["naics", "sitemap", "pricing_scrape"]);

async function openrouterChat(prompt: string, maxTokens = 200): Promise<string> {
  const apiKey = process.env.OPEN_ROUTER_KEY;
  if (!apiKey) throw new Error("OPEN_ROUTER_KEY not set");

  const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "openai/gpt-4o-mini",
      messages: [{ role: "user", content: prompt }],
      max_tokens: maxTokens,
      temperature: 0,
    }),
  });
  if (!res.ok) throw new Error(`OpenRouter HTTP ${res.status}`);
  const data = (await res.json()) as { choices: Array<{ message: { content: string } }> };
  return data.choices[0].message.content;
}

function parseJsonArray(text: string): string[] {
  const match = text.match(/\[[\s\S]*?\]/);
  if (!match) return [];
  try {
    const parsed = JSON.parse(match[0]) as unknown;
    if (Array.isArray(parsed)) return parsed.map(String);
  } catch {
    /* fallback below */
  }
  return [];
}

export async function planScoutPerception(
  domain: string,
  brand: { title?: string | null; logo_url?: string | null },
  goal = "Build a sales intelligence dossier with industry, site scale, and pricing signals."
): Promise<{ steps: string[]; policySource: string }> {
  const title = brand.title ?? domain;
  const prompt = `You are an agent planner with a credit budget.

Goal: ${goal}
Domain: ${domain}
Brand resolved: title=${JSON.stringify(title)}, logo=${Boolean(brand.logo_url)}

Available perceive tools (pick subset, ordered):
- "naics" — industry classification (10 credits)
- "sitemap" — URL count / site scale (1 credit)
- "pricing_scrape" — scrape /pricing markdown (1 credit)

Reply with ONLY a JSON array of tool names to call, e.g. ["naics","sitemap","pricing_scrape"].
Skip tools that don't help the goal. Always include naics for sales dossiers.`;

  try {
    const raw = await openrouterChat(prompt);
    const steps = parseJsonArray(raw).filter((s) => ALLOWED_SCOUT_STEPS.has(s));
    if (steps.length) return { steps, policySource: "llm" };
  } catch {
    /* fallback */
  }

  const fallback = ["naics", "sitemap"];
  if (brand.title) fallback.push("pricing_scrape");
  return { steps: fallback, policySource: "fallback" };
}

export async function planMcpExecute(
  goal: string,
  docHits: DocHit[]
): Promise<{ plan: ExecuteStep[]; policySource: string }> {
  const docsText = JSON.stringify(docHits, null, 2);
  const prompt = `You simulate Context.dev MCP Code Mode \`execute\`.

User goal: ${goal}

SDK docs from search_docs:
${docsText}

Write a JSON array of operations to run. Each item: {"op": "<name>", "args": {...}}.
Allowed ops: brand.retrieve, web.extract_styleguide, web.scrape_sitemap
Example: [{"op":"brand.retrieve","args":{"domain":"stripe.com"}},{"op":"web.extract_styleguide","args":{"domain":"stripe.com"}}]

Reply ONLY with the JSON array.`;

  try {
    const raw = await openrouterChat(prompt, 300);
    const match = raw.match(/\[[\s\S]*\]/);
    if (match) {
      const plan = JSON.parse(match[0]) as ExecuteStep[];
      if (Array.isArray(plan) && plan.length) return { plan, policySource: "llm" };
    }
  } catch {
    /* fallback */
  }

  const domainMatch = goal.toLowerCase().match(/[\w.-]+\.[a-z]{2,}/);
  const domain = domainMatch?.[0] ?? "stripe.com";
  return {
    plan: [
      { op: "brand.retrieve", args: { domain } },
      { op: "web.extract_styleguide", args: { domain } },
      { op: "web.scrape_sitemap", args: { domain } },
    ],
    policySource: "fallback",
  };
}