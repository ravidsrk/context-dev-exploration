/**
 * TypeScript Research Scout loop: perceive → plan → act → observe.
 * Uses Context.dev npm SDK directly (mirrors Python scout_loop).
 */
import ContextDev from "context.dev";

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

  const naicsRes = await withRetry(() =>
    client.brand.retrieveNaics({ input: DOMAIN })
  );
  perceiveLog.push("retrieveNaics");
  credits += 10;

  const smRes = await withRetry(() =>
    client.brand.webScrapeSitemap({ domain: DOMAIN })
  );
  perceiveLog.push("webScrapeSitemap");
  credits += 1;

  const pricingRes = await withRetry(() =>
    client.brand.webScrapeMd({ url: `https://${DOMAIN}/pricing` })
  );
  perceiveLog.push("webScrapeMd:pricing");
  credits += 1;

  const topCode = naicsRes.codes?.[0];
  const brief = {
    domain: DOMAIN,
    company: brand?.title ?? null,
    logo_url: brand?.logos?.[0]?.url ?? null,
    industry: topCode
      ? { code: topCode.code, name: topCode.name, confidence: topCode.confidence }
      : null,
    sitemap_urls: (smRes.urls ?? []).length,
    has_pricing_content: (pricingRes.markdown ?? "").length > 100,
    credits_estimated: credits,
    policy_source: "typescript_heuristic",
    plan_steps: ["naics", "sitemap", "pricing_scrape"],
    perceive_log: perceiveLog,
    observation: {
      confidence: brand?.title ? 0.95 : 0.5,
      recommend_revisit_days: (smRes.urls ?? []).length > 1000 ? 7 : 30,
    },
  };

  console.log(JSON.stringify(brief, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});