import { config } from "@/lib/config";
import { prisma } from "@/lib/db";

const MAX_RETRIES = 3;
const RETRY_BASE_DELAY = 1000;

async function recordTokenUsage(model: string, prompt: number, completion: number, endpoint?: string) {
  try {
    await prisma.tokenUsage.create({
      data: {
        model,
        prompt,
        completion,
        total: prompt + completion,
        endpoint,
      },
    });
  } catch {
    // non-critical
  }
}

export async function getTokenStats() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const agg = await prisma.tokenUsage.aggregate({
    where: { date: { gte: today } },
    _sum: { total: true, prompt: true, completion: true },
  });

  const used = agg._sum.total ?? 0;
  return {
    tokensUsedToday: used,
    tokensRemaining: Math.max(0, config.openai.dailyTokenLimit - used),
    dailyLimit: config.openai.dailyTokenLimit,
  };
}

async function isWithinBudget(): Promise<boolean> {
  const stats = await getTokenStats();
  return stats.tokensUsedToday < config.openai.dailyTokenLimit;
}

function getClient() {
  if (!config.openai.isConfigured) return null;
  // Lazy import to avoid issues when key not set
  const { default: OpenAI } = require("openai");
  return new OpenAI({ apiKey: config.openai.apiKey });
}

export async function chat(
  systemPrompt: string,
  userMessage: string,
  options: { temperature?: number; maxTokens?: number; endpoint?: string } = {}
): Promise<string | null> {
  const client = getClient();
  if (!client) return null;

  const withinBudget = await isWithinBudget();
  if (!withinBudget) {
    console.warn("Daily token budget exhausted");
    return null;
  }

  const { temperature = 0.3, maxTokens = 1000, endpoint } = options;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const response = await client.chat.completions.create({
        model: config.openai.model,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userMessage },
        ],
        temperature,
        max_tokens: maxTokens,
      });

      const usage = response.usage;
      if (usage) {
        await recordTokenUsage(
          config.openai.model,
          usage.prompt_tokens,
          usage.completion_tokens,
          endpoint
        );
      }

      return response.choices[0]?.message?.content ?? null;
    } catch (err: unknown) {
      const errStr = String(err).toLowerCase();
      const isTransient = ["429", "rate", "500", "502", "503"].some((s) => errStr.includes(s));
      if (isTransient && attempt < MAX_RETRIES - 1) {
        const delay = RETRY_BASE_DELAY * Math.pow(2, attempt);
        await new Promise((r) => setTimeout(r, delay));
        continue;
      }
      console.error("OpenAI API error:", err);
      return null;
    }
  }

  return null;
}

export async function chatJson<T = Record<string, unknown>>(
  systemPrompt: string,
  userMessage: string,
  options: { temperature?: number; maxTokens?: number; endpoint?: string } = {}
): Promise<T | null> {
  const raw = await chat(systemPrompt, userMessage, {
    ...options,
    temperature: options.temperature ?? 0.2,
  });
  if (!raw) return null;

  try {
    let cleaned = raw.trim();
    if (cleaned.startsWith("```")) {
      const lines = cleaned.split("\n").filter((l) => !l.trim().startsWith("```"));
      cleaned = lines.join("\n");
    }
    const start = cleaned.indexOf("{");
    const end = cleaned.lastIndexOf("}") + 1;
    if (start >= 0 && end > start) {
      cleaned = cleaned.substring(start, end);
    }
    return JSON.parse(cleaned) as T;
  } catch (e) {
    console.error("Failed to parse OpenAI JSON response:", e);
    return null;
  }
}

export function isOpenAIAvailable(): boolean {
  return config.openai.isConfigured;
}
