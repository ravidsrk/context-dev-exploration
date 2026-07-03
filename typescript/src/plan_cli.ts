/**
 * Bridge to Python plan_cli.py — single planner for scout + MCP loops.
 */
import { execFileSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

function pythonBin(): string {
  const venv = path.join(ROOT, ".venv", "bin", "python");
  return venv;
}

function runPlanCli(args: string[]): Record<string, unknown> {
  const out = execFileSync(pythonBin(), ["-m", "context_dev.planning.cli", ...args], {
    encoding: "utf8",
    env: process.env,
  });
  return JSON.parse(out.trim()) as Record<string, unknown>;
}

export type ScoutPlan = {
  plan_steps: string[];
  policy_source: string;
  goal?: string;
};

export type McpPlan = {
  execute_plan: Array<{ op: string; args: Record<string, string> }>;
  policy_source: string;
  domain?: string;
  raw_plan?: Array<{ op: string; args: Record<string, string> }>;
};

export function runScoutPlan(
  domain: string,
  brand: { title?: string | null; logo_url?: string | null }
): ScoutPlan {
  const brandJson = JSON.stringify(brand);
  const result = runPlanCli(["scout", domain, brandJson]);
  return {
    plan_steps: result.plan_steps as string[],
    policy_source: result.policy_source as string,
    goal: result.goal as string | undefined,
  };
}

export function runMcpPlan(
  goal: string,
  hits: Array<Record<string, string>>
): McpPlan {
  const hitsJson = JSON.stringify(hits);
  const result = runPlanCli(["mcp", goal, hitsJson]);
  return {
    execute_plan: result.execute_plan as McpPlan["execute_plan"],
    policy_source: result.policy_source as string,
    domain: result.domain as string | undefined,
    raw_plan: result.raw_plan as McpPlan["raw_plan"],
  };
}