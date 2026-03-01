import { prisma } from "@/lib/db";
import { chatJson, isOpenAIAvailable } from "@/lib/openai";
import { config } from "@/lib/config";

interface Recommendation {
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
  category: string;
}

export async function getRecommendations(): Promise<{
  success: boolean;
  recommendations: Recommendation[];
  method: string;
}> {
  const perfData = await gatherPerformance();

  if (!isOpenAIAvailable()) {
    return { success: true, recommendations: getDefaultRecommendations(), method: "rule_based" };
  }

  const systemPrompt = `You are a performance marketing optimization expert for ${config.business.name}.
Budget: ₪${config.budget.total}/month. Targets: CPL ≤ ₪${config.targets.cpl}, CAC ≤ ₪${config.targets.cac}.
Analyze the data and provide 3-5 actionable recommendations.
Respond in JSON: { "recommendations": [{"title": "...", "description": "...", "priority": "high|medium|low", "category": "budget|creative|targeting|conversion"}] }`;

  const result = await chatJson<{ recommendations: Recommendation[] }>(
    systemPrompt,
    `Current performance:\n${JSON.stringify(perfData)}`,
    { maxTokens: 1000, endpoint: "optimization" }
  );

  if (result?.recommendations) {
    return { success: true, recommendations: result.recommendations, method: "ai" };
  }

  return { success: true, recommendations: getDefaultRecommendations(), method: "rule_based" };
}

async function gatherPerformance() {
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

  const [leads, campaigns] = await Promise.all([
    prisma.lead.count({ where: { createdAt: { gte: thirtyDaysAgo } } }),
    prisma.campaign.aggregate({
      where: { date: { gte: thirtyDaysAgo } },
      _sum: { cost: true, clicks: true, conversions: true, impressions: true },
    }),
  ]);

  const totalCost = campaigns._sum.cost ?? 0;
  const totalConv = campaigns._sum.conversions ?? 0;

  return {
    leads,
    totalSpend: totalCost,
    conversions: totalConv,
    cpl: totalConv > 0 ? totalCost / totalConv : 0,
    budgetUsed: (totalCost / config.budget.total) * 100,
  };
}

function getDefaultRecommendations(): Recommendation[] {
  return [
    {
      title: "בדקו ביצועי קמפיינים",
      description: "סקרו את כל הקמפיינים הפעילים ועצרו קמפיינים עם CPL גבוה מ-₪" + config.targets.cpl,
      priority: "high",
      category: "budget",
    },
    {
      title: "שפרו דפי נחיתה",
      description: "בדקו שיעור המרה בדפי נחיתה ושקלו A/B טסט לכותרות וקריאה לפעולה",
      priority: "medium",
      category: "conversion",
    },
    {
      title: "עדכנו קריאייטיב",
      description: "רעננו תמונות ומודעות שרצות יותר מ-14 יום למניעת עייפות מודעות",
      priority: "medium",
      category: "creative",
    },
  ];
}
