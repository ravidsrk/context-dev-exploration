/**
 * TypeScript MCP Code Mode loop: hosted search_docs + hosted execute (TS sandbox).
 */
import {
  buildExecuteTypescript,
  extractDomain,
  hostedExecute,
  hostedSearchDocs,
} from "./mcp_client.js";

const goal =
  process.argv.slice(2).join(" ") ||
  "Get stripe.com brand identity, design tokens, and site scale";

async function main(): Promise<void> {
  const domain = extractDomain(goal);
  const hits = await hostedSearchDocs(goal);
  const code = buildExecuteTypescript(domain);
  const raw = await hostedExecute(code, goal);

  if (typeof raw.raw === "string" && raw.raw.includes("TS Diagnostics")) {
    throw new Error(`hosted execute failed: ${raw.raw}`);
  }

  const payload =
    typeof raw.result === "object" && raw.result !== null
      ? (raw.result as Record<string, unknown>)
      : raw;

  const identity = (payload as { identity?: { title?: string } }).identity;
  if (!identity?.title) {
    throw new Error(`hosted execute empty identity: ${JSON.stringify(payload).slice(0, 200)}`);
  }

  const out = {
    goal,
    search_docs: { query: goal, source: "hosted_mcp", hits },
    execute_source: "hosted_mcp_execute",
    execute_typescript: code,
    policy_source: "typescript_direct",
    result: payload,
    ops_run: [
      "hosted:execute(brand.retrieve)",
      "hosted:execute(web.extractStyleguide)",
      "hosted:execute(web.scrape_sitemap)",
    ],
    credits_estimated: 21,
  };

  console.log(JSON.stringify(out, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});