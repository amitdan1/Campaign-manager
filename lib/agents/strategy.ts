import { prisma } from "@/lib/db";
import { chatJson, isOpenAIAvailable } from "@/lib/openai";
import { config } from "@/lib/config";
import { getPromptContext } from "@/lib/services/agent-memory";

interface StrategyPlan {
  summary: string;
  channelBreakdown: Array<{
    channel: string;
    budget: number;
    actions: string[];
  }>;
  kpiTargets: Record<string, number>;
  recommendations: string[];
}

export async function generateWeeklyStrategy(): Promise<{
  success: boolean;
  plan?: StrategyPlan;
  method: string;
}> {
  const performanceSummary = await getPerformanceSummary();

  if (!isOpenAIAvailable()) {
    return { success: true, plan: getDefaultPlan(), method: "template" };
  }

  const memoryContext = await getPromptContext("strategy");

  const systemPrompt = `You are a performance marketing strategist for ${config.business.name}.
Budget: ₪${config.budget.total}/month (Google: ₪${config.budget.googleAds}, Facebook: ₪${config.budget.facebook}).
Target: CPL ≤ ₪${config.targets.cpl}, CAC ≤ ₪${config.targets.cac}.
${memoryContext}
Respond in JSON with: summary, channelBreakdown (array of {channel, budget, actions[]}), kpiTargets, recommendations[].`;

  const result = await chatJson<StrategyPlan>(
    systemPrompt,
    `Create a weekly marketing strategy based on this performance data:\n${JSON.stringify(performanceSummary)}`,
    { maxTokens: 1500, endpoint: "strategy" }
  );

  if (result) {
    return { success: true, plan: result, method: "ai" };
  }

  return { success: true, plan: getDefaultPlan(), method: "template" };
}

async function getPerformanceSummary() {
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

  const [leadCount, campaignData] = await Promise.all([
    prisma.lead.count({ where: { createdAt: { gte: sevenDaysAgo } } }),
    prisma.campaign.aggregate({
      where: { date: { gte: sevenDaysAgo } },
      _sum: { cost: true, clicks: true, conversions: true, impressions: true },
    }),
  ]);

  return {
    leadsLast7Days: leadCount,
    spend: campaignData._sum.cost ?? 0,
    clicks: campaignData._sum.clicks ?? 0,
    conversions: campaignData._sum.conversions ?? 0,
    impressions: campaignData._sum.impressions ?? 0,
  };
}

function getDefaultPlan(): StrategyPlan {
  return {
    summary: "תוכנית שיווק שבועית סטנדרטית",
    channelBreakdown: [
      { channel: "Google Ads", budget: config.budget.googleAds, actions: ["הפעלת קמפיין חיפוש", "מעקב המרות"] },
      { channel: "Facebook/Instagram", budget: config.budget.facebook, actions: ["קמפיין לידים", "רימרקטינג"] },
    ],
    kpiTargets: {
      cpl: config.targets.cpl,
      consultationRate: config.targets.consultationRate * 100,
      conversionRate: config.targets.conversionRate * 100,
    },
    recommendations: [
      "לבדוק ביצועי מודעות קיימות ולעדכן קריאייטיב",
      "להגדיר קהלי יעד מפורטים יותר",
      "לבדוק דפי נחיתה ולשפר שיעור המרה",
    ],
  };
}
