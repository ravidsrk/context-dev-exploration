/**
 * TypeScript probe — mirrors Python demos across 3+ API categories.
 * Auth: CONTEXT_DEV_API_KEY env (never hardcode).
 */
import ContextDev from "context.dev";
// TS SDK namespaces web + industry helpers under client.brand

const DOMAIN = "stripe.com";
const URL = "https://stripe.com";

function getClient(): ContextDev {
  const key = process.env.CONTEXT_DEV_API_KEY ?? process.env.CONTEXT_API_KEY;
  if (!key) {
    throw new Error("CONTEXT_DEV_API_KEY is required");
  }
  return new ContextDev({ apiKey: key });
}

async function withRetry<T>(fn: () => Promise<T>, retries = 3): Promise<T> {
  let last: unknown;
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (e: unknown) {
      last = e;
      const status = (e as { status?: number }).status;
      if (status === 408 || status === 429) {
        await new Promise((r) => setTimeout(r, 1000 * 2 ** i));
        continue;
      }
      throw e;
    }
  }
  throw last;
}

async function main(): Promise<void> {
  const client = getClient();
  const started = Date.now();

  console.log("=== TS Brand Retrieve ===");
  const brandRes = await withRetry(() => client.brand.retrieve({ domain: DOMAIN }));
  const brand = brandRes.brand;
  console.log(`  title: ${brand?.title ?? "n/a"}`);
  console.log(`  domain: ${brand?.domain ?? DOMAIN}`);
  const logoUrl = brand?.logos?.[0]?.url ?? "n/a";
  console.log(`  logo_url: ${logoUrl}`);

  console.log("\n=== TS Scrape Markdown ===");
  const scrapeRes = await withRetry(() => client.brand.webScrapeMd({ url: URL }));
  const md = scrapeRes.markdown ?? "";
  console.log(`  url: ${scrapeRes.url ?? URL}`);
  console.log(`  markdown_length: ${md.length}`);

  console.log("\n=== TS NAICS Classification ===");
  const naicsRes = await withRetry(() =>
    client.brand.retrieveNaics({ input: DOMAIN })
  );
  const codes = naicsRes.codes ?? [];
  console.log(`  domain: ${naicsRes.domain ?? DOMAIN}`);
  console.log(
    `  top_code: ${codes[0] ? `${codes[0].code} ${codes[0].name}` : "n/a"}`
  );

  console.log("\n=== TS Sitemap ===");
  const sitemapRes = await withRetry(() =>
    client.brand.webScrapeSitemap({ domain: DOMAIN })
  );
  const urls = sitemapRes.urls ?? [];
  console.log(`  url_count: ${urls.length}`);
  console.log(`  sample: ${urls.slice(0, 2).join(", ") || "n/a"}`);

  console.log(`\n=== Done in ${Date.now() - started}ms ===`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});