import { prisma } from "@/lib/db";
import { chatJson, isOpenAIAvailable } from "@/lib/openai";
import { config } from "@/lib/config";

interface ScoreResult {
  score: number;
  reasoning: string;
  priority: string;
  recommendedAction: string;
  method: "ai" | "rule_based";
}

function ruleBasedScore(lead: {
  location?: string | null;
  budget?: string | null;
  projectType?: string | null;
  source?: string;
}): ScoreResult {
  let score = 5;
  const reasons: string[] = [];

  if (lead.location && config.targets.locations.some((loc) => lead.location?.includes(loc))) {
    score += 2;
    reasons.push("Located in target area");
  }

  if (lead.budget) {
    const budgetNum = parseInt(lead.budget.replace(/[^\d]/g, ""), 10);
    if (budgetNum >= config.targets.minProjectBudget) {
      score += 2;
      reasons.push("Budget meets minimum threshold");
    }
  }

  if (lead.projectType && ["villa", "new_build", "penthouse"].includes(lead.projectType)) {
    score += 1;
    reasons.push("High-value project type");
  }

  if (lead.source === "google") {
    score += 1;
    reasons.push("Google source (high intent)");
  }

  score = Math.min(10, Math.max(1, score));

  return {
    score,
    reasoning: reasons.join(". ") || "Default scoring",
    priority: score >= 8 ? "high" : score >= 5 ? "medium" : "low",
    recommendedAction:
      score >= 8 ? "Immediate follow-up recommended" : score >= 5 ? "Standard follow-up" : "Low priority, nurture",
    method: "rule_based",
  };
}

export async function scoreLead(leadId: string): Promise<ScoreResult & { success: boolean }> {
  const lead = await prisma.lead.findUnique({ where: { id: leadId } });
  if (!lead) {
    return { success: false, score: 0, reasoning: "Lead not found", priority: "low", recommendedAction: "", method: "rule_based" };
  }

  let result: ScoreResult;

  if (isOpenAIAvailable()) {
    const systemPrompt = `You are a lead scoring expert for an interior design business in Israel.
Score the lead from 1-10 based on: location, budget, project type, and source.
Target audience: ${config.targets.ageMin}-${config.targets.ageMax}, locations: ${config.targets.locations.join(", ")}, min budget: ₪${config.targets.minProjectBudget.toLocaleString()}.
Respond in JSON: {"score": number, "reasoning": "...", "priority": "high|medium|low", "recommended_action": "..."}`;

    const userMessage = `Score this lead:
Name: ${lead.name}
Phone: ${lead.phone}
Email: ${lead.email}
Source: ${lead.source}
Location: ${lead.location || "Unknown"}
Budget: ${lead.budget || "Unknown"}
Project type: ${lead.projectType || "Unknown"}
Notes: ${lead.notes || "None"}`;

    const aiResult = await chatJson<{
      score: number;
      reasoning: string;
      priority: string;
      recommended_action: string;
    }>(systemPrompt, userMessage, { endpoint: "lead_scoring" });

    if (aiResult) {
      result = {
        score: Math.min(10, Math.max(1, aiResult.score)),
        reasoning: aiResult.reasoning,
        priority: aiResult.priority,
        recommendedAction: aiResult.recommended_action,
        method: "ai",
      };
    } else {
      result = ruleBasedScore(lead);
    }
  } else {
    result = ruleBasedScore(lead);
  }

  await prisma.lead.update({
    where: { id: leadId },
    data: {
      qualityScore: result.score,
      scoreReasoning: result.reasoning,
    },
  });

  return { success: true, ...result };
}

export async function rescoreAllLeads(): Promise<{ scored: number; errors: number }> {
  const leads = await prisma.lead.findMany({
    where: { status: { not: "lost" } },
    select: { id: true },
  });

  let scored = 0;
  let errors = 0;

  for (const lead of leads) {
    try {
      await scoreLead(lead.id);
      scored++;
    } catch {
      errors++;
    }
  }

  return { scored, errors };
}
