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

  const brandRes = await withRetry(() => client.brand.retrieve({ domain: DOMAIN }));
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

  let naicsRes: Awaited<ReturnType<ContextDev["brand"]["retrieveNaics"]>> | null = null;
  let smRes: Awaited<ReturnType<ContextDev["brand"]["webScrapeSitemap"]>> | null = null;
  let pricingMarkdown = "";

  for (const step of steps) {
    if (step === "naics") {
      naicsRes = await withRetry(() => client.brand.retrieveNaics({ input: DOMAIN }));
      perceiveLog.push("retrieveNaics");
      credits += 10;
    } else if (step === "sitemap") {
      smRes = await withRetry(() => client.brand.webScrapeSitemap({ domain: DOMAIN }));
      perceiveLog.push("webScrapeSitemap");
      credits += 1;
    } else if (step === "pricing_scrape") {
      const pricingRes = await withRetry(() =>
        client.brand.webScrapeMd({ url: `https://${DOMAIN}/pricing` })
      );
      perceiveLog.push("webScrapeMd:pricing");
      credits += 1;
      pricingMarkdown = pricingRes.markdown ?? "";
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
    has_pricing_content: pricingMarkdown.length > 100,
    pricing_preview: pricingMarkdown.slice(0, 200) || null,
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