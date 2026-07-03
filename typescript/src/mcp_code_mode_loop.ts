/**
 * TypeScript MCP Code Mode loop: hosted search_docs → LLM plan → hosted execute.
 * Mirrors agents/mcp_code_mode_loop.py with local SDK fallback.
 */
import ContextDev from "context.dev";
import { planMcpExecute } from "./llm_policy.js";
import { buildExecuteTypescript } from "./mcp_execute_codegen.js";
import { OP_CREDITS, normalizeExecutePlan } from "./mcp_op_map.js";
import {
  extractDomain,
  hostedExecute,
  hostedSearchDocs,
} from "./mcp_client.js";
import type { ExecuteStep } from "./llm_policy.js";

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

function isHostedExecuteFailure(raw: Record<string, unknown>): boolean {
  if (typeof raw.raw === "string") {
    const t = raw.raw;
    return t.includes("TS Diagnostics") || t.toLowerCase().includes("error");
  }
  const result = raw.result as Record<string, unknown> | undefined;
  const identity = result?.identity as { title?: string } | undefined;
  return !identity?.title;
}

async function executePlanLocal(
  plan: ExecuteStep[]
): Promise<{ result: Record<string, unknown>; opsRun: string[]; credits: number }> {
  const client = getClient();
  const out: Record<string, unknown> = {};
  const opsRun: string[] = [];
  let credits = 0;

  for (const step of plan) {
    const domain = step.args.domain;
    if (!domain) continue;

    if (step.op === "brand.retrieve") {
      const brandRes = await withRetry(() => client.brand.retrieve({ domain }));
      out.identity = {
        title: brandRes.brand?.title ?? null,
        logo_url: brandRes.brand?.logos?.[0]?.url ?? null,
      };
      credits += OP_CREDITS["brand.retrieve"];
      opsRun.push(`local:brand.retrieve(${domain})`);
    } else if (step.op === "web.extract_styleguide") {
      const styleRes = await withRetry(() => client.brand.styleguide({ domain }));
      const colors = styleRes.styleguide?.colors;
      out.design_tokens = {
        color_count: [colors?.accent, colors?.background, colors?.text].filter(Boolean).length,
        has_typography: !!styleRes.styleguide?.typography,
      };
      credits += OP_CREDITS["web.extract_styleguide"];
      opsRun.push(`local:brand.styleguide(${domain})`);
    } else if (step.op === "web.scrape_sitemap") {
      const smRes = await withRetry(() => client.brand.webScrapeSitemap({ domain }));
      out.site_scale = {
        url_count: (smRes.urls ?? []).length,
        sample_paths: (smRes.urls ?? []).slice(0, 3),
      };
      credits += OP_CREDITS["web.scrape_sitemap"];
      opsRun.push(`local:brand.webScrapeSitemap(${domain})`);
    }
  }

  return { result: { ...out, credits_estimated: credits }, opsRun, credits };
}

export async function runCodeModeLoop(goal: string): Promise<Record<string, unknown>> {
  const domain = extractDomain(goal);
  const hits = await hostedSearchDocs(goal);
  const { plan: rawPlan, policySource } = await planMcpExecute(goal, hits);
  const planSteps = normalizeExecutePlan(goal, rawPlan, hits, domain);
  const code = buildExecuteTypescript(domain, planSteps);

  let executeSource = "hosted_mcp_execute";
  let result: Record<string, unknown>;
  let opsRun: string[];
  let credits = planSteps.reduce((sum, s) => sum + (OP_CREDITS[s.op] ?? 0), 0);

  try {
    const raw = await hostedExecute(code, goal);
    if (isHostedExecuteFailure(raw)) {
      throw new Error(
        typeof raw.raw === "string" ? raw.raw.slice(0, 200) : "hosted execute empty identity"
      );
    }
    const payload =
      typeof raw.result === "object" && raw.result !== null
        ? (raw.result as Record<string, unknown>)
        : raw;
    result = { ...payload, credits_estimated: credits };
    opsRun = planSteps.map((s) => `hosted:execute(${s.op})`);
  } catch (exc) {
    const local = await executePlanLocal(planSteps);
    result = local.result;
    opsRun = local.opsRun;
    credits = local.credits;
    executeSource = `local_sdk_fallback:${exc instanceof Error ? exc.constructor.name : "Error"}`;
  }

  return {
    goal,
    search_docs: { query: goal, source: "hosted_mcp", hits },
    execute_plan: planSteps,
    policy_source: policySource,
    execute_source: executeSource,
    execute_typescript: code,
    result,
    ops_run: opsRun,
    credits_estimated: credits,
  };
}

async function main(): Promise<void> {
  const goal =
    process.argv.slice(2).join(" ") ||
    "Get stripe.com brand identity, design tokens, and site scale";
  console.log(JSON.stringify(await runCodeModeLoop(goal), null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});