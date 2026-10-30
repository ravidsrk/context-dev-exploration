/**
 * TypeScript Research Scout loop: perceive → plan (plan_cli.py) → act → observe.
 */
import ContextDev from "context.dev";
import { runScoutPlan } from "./plan_cli.js";

const DOMAIN = process.argv[2] ?? "stripe.com";

function getClient(): ContextDev {
  const key = process.env.CONTEXT_DEV_API_KEY ?? process.env.CONTEXT_API_KEY;
  if (!key) throw new Error("CONTEXT_DEV_API_KEY is required");
  return new ContextDev({ apiKey: key });
}

async function withRetry<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e: unknown) {
      const status = (e as { status?: number }).status;
      if ((status === 408 || status === 429) && i < 2) {
        await new Promise((r) => setTimeout(r, 1000 * 2 ** i));
        continue;
      }
      throw e;
    }
  }
  throw new Error("retry exhausted");
}

async function main(): Promise<void> {
  const client = getClient();
  const perceiveLog: string[] = [];
  let credits = 0;

  const brandRes = await withRetry(() => client.brand.retrieve({ type: "by_domain", domain: DOMAIN }));
  perceiveLog.push("brand.retrieve");
  credits += 10;
  const brand = brandRes.brand;

  const brandForPlan = {
    title: brand?.title ?? null,
    logo_url: brand?.logos?.[0]?.url ?? null,
  };
  const { plan_steps: steps, policy_source: policySource, goal } = runScoutPlan(
    DOMAIN,
    brandForPlan
  );

  let naicsRes: Awaited<ReturnType<ContextDev["industry"]["retrieveNaics"]>> | null = null;
  let smRes: Awaited<ReturnType<ContextDev["web"]["mapUrls"]>> | null = null;
  // July bug: has_pricing_content was markdown.length > 100, which nav-only Markdown passed.
  // Now: ask Scrape for passages relevant to prices (highlights) and require at least one.
  let pricingHighlights: string[] = [];

  for (const step of steps) {
    if (step === "naics") {
      naicsRes = await withRetry(() => client.industry.retrieveNaics({ input: DOMAIN }));
      perceiveLog.push("retrieveNaics");
      credits += 10;
    } else if (step === "sitemap") {
      smRes = await withRetry(() => client.web.mapUrls({ domain: DOMAIN }));
      perceiveLog.push("mapUrls");
      credits += 1;
    } else if (step === "pricing_scrape") {
      const pricingRes = await withRetry(() =>
        client.web.scrape({
          url: `https://${DOMAIN}/pricing`,
          formats: { highlights: true },
          highlightsParams: { query: "prices, fees and plan costs", maxCharacters: 1500 },
        })
      );
      perceiveLog.push("scrape_highlights:pricing");
      credits += 2; // scrape 1 + highlights 1 (pricing page); Sep 23 changelog said +3
      pricingHighlights = pricingRes.highlights?.data ?? [];
    }
  }

  const topCode = naicsRes?.codes?.[0];
  const brief = {
    domain: DOMAIN,
    goal: goal ?? null,
    company: brand?.title ?? null,
    logo_url: brand?.logos?.[0]?.url ?? null,
    industry: topCode
      ? { code: topCode.code, name: topCode.name, confidence: topCode.confidence }
      : null,
    sitemap_urls: (smRes?.urls ?? []).length,
    has_pricing_content: pricingHighlights.length > 0,
    pricing_preview: pricingHighlights.join(" | ").slice(0, 200) || null,
    credits_estimated: credits,
    policy_source: policySource,
    plan_steps: steps,
    perceive_log: perceiveLog,
    observation: {
      confidence: brand?.title ? 0.95 : 0.5,
      recommend_revisit_days: (smRes?.urls ?? []).length > 1000 ? 7 : 30,
      policy_source: policySource,
    },
  };

  console.log(JSON.stringify(brief, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});