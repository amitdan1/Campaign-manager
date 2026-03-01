import { prisma } from "@/lib/db";
import { captureLead } from "@/lib/agents/lead-capture";
import { scoreLead } from "@/lib/agents/lead-scoring";

export async function captureAndScoreLead(data: {
  name: string;
  phone: string;
  email?: string;
  source?: string;
  campaign?: string;
  location?: string;
  budget?: string;
  projectType?: string;
  notes?: string;
}) {
  const captureResult = await captureLead(data);
  if (!captureResult.success) return captureResult;

  const leadId = captureResult.leadId!;
  const scoreResult = await scoreLead(leadId);

  return {
    success: true,
    leadId,
    lead: captureResult.lead,
    scoring: {
      score: scoreResult.score,
      reasoning: scoreResult.reasoning,
      priority: scoreResult.priority,
      recommendedAction: scoreResult.recommendedAction,
      method: scoreResult.method,
    },
  };
}

export async function getDashboardStats(days = 30) {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);

  const cutoff7d = new Date();
  cutoff7d.setDate(cutoff7d.getDate() - 7);

  const cutoff14d = new Date();
  cutoff14d.setDate(cutoff14d.getDate() - 14);

  try {
    const [
      totalLeads,
      qualifiedLeads,
      consultations,
      conversions,
      campaignAgg,
      sourceGroups,
      statusGroups,
      last7Count,
      prev7Count,
      pendingProposals,
    ] = await Promise.all([
      prisma.lead.count({ where: { createdAt: { gte: cutoff } } }),
      prisma.lead.count({ where: { createdAt: { gte: cutoff }, qualityScore: { gte: 7 } } }),
      prisma.lead.count({ where: { createdAt: { gte: cutoff }, status: "consultation_booked" } }),
      prisma.lead.count({ where: { createdAt: { gte: cutoff }, status: "converted" } }),
      prisma.campaign.aggregate({
        where: { date: { gte: cutoff } },
        _sum: { cost: true, conversions: true },
      }),
      prisma.lead.groupBy({
        by: ["source"],
        where: { createdAt: { gte: cutoff } },
        _count: true,
      }),
      prisma.lead.groupBy({
        by: ["status"],
        where: { createdAt: { gte: cutoff } },
        _count: true,
      }),
      prisma.lead.count({ where: { createdAt: { gte: cutoff7d } } }),
      prisma.lead.count({ where: { createdAt: { gte: cutoff14d, lt: cutoff7d } } }),
      prisma.proposal.count({ where: { status: "pending_review" } }),
    ]);

    const totalSpend = campaignAgg._sum.cost ?? 0;
    const totalConv = campaignAgg._sum.conversions ?? 0;
    const avgCpl = totalConv > 0 ? totalSpend / totalConv : 0;
    const consultationRate = totalLeads > 0 ? (consultations / totalLeads) * 100 : 0;
    const conversionRate = consultations > 0 ? (conversions / consultations) * 100 : 0;
    const cac = conversions > 0 ? totalSpend / conversions : 0;

    const leadsBySource: Record<string, number> = {};
    for (const row of sourceGroups) {
      leadsBySource[row.source] = row._count;
    }

    const statusMap: Record<string, number> = {};
    for (const row of statusGroups) {
      statusMap[row.status] = row._count;
    }
    const statusBreakdown: Record<string, number> = {};
    for (const s of ["new", "contacted", "qualified", "consultation_booked", "converted", "lost"]) {
      statusBreakdown[s] = statusMap[s] ?? 0;
    }

    const trendPct = prev7Count > 0 ? ((last7Count - prev7Count) / prev7Count) * 100 : 0;

    return {
      success: true,
      stats: {
        totalLeads,
        qualifiedLeads,
        consultations,
        conversions,
        totalSpend,
        avgCpl,
        consultationRate,
        conversionRate,
        cac,
        recentLeadsCount: last7Count,
        leadsBySource,
        statusBreakdown,
        trend: { leads: last7Count - prev7Count, percentage: trendPct },
        pendingProposals,
      },
    };
  } catch (e) {
    console.error("Error getting dashboard stats:", e);
    return { success: false, error: String(e) };
  }
}

export async function healthCheck() {
  try {
    const leadCount = await prisma.lead.count();
    return {
      healthy: true,
      agents: {
        leadCapture: { healthy: true, totalLeads: leadCount },
        leadScoring: { healthy: true },
      },
    };
  } catch (e) {
    return { healthy: false, error: String(e) };
  }
}
