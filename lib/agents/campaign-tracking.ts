import { prisma } from "@/lib/db";
import { recordCampaignPerformance } from "@/lib/services/agent-memory";

export async function pullMetrics() {
  // In the full implementation this would call Google Ads and Facebook APIs.
  // For now, it aggregates existing data and records performance memories.
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

  const campaigns = await prisma.campaign.findMany({
    where: { date: { gte: sevenDaysAgo } },
    orderBy: { date: "desc" },
  });

  for (const c of campaigns) {
    await recordCampaignPerformance("campaign_tracking", c.campaignName, c.platform, {
      impressions: c.impressions,
      clicks: c.clicks,
      conversions: c.conversions,
      cost: c.cost,
      cpl: c.cpl,
      ctr: c.ctr,
      conversionRate: c.conversionRate,
    });
  }

  return { success: true, campaignsProcessed: campaigns.length };
}

export async function addCampaignMetrics(data: {
  campaignId: string;
  campaignName: string;
  platform: string;
  impressions?: number;
  clicks?: number;
  conversions?: number;
  cost?: number;
}) {
  const impressions = data.impressions ?? 0;
  const clicks = data.clicks ?? 0;
  const conversions = data.conversions ?? 0;
  const cost = data.cost ?? 0;

  const ctr = impressions > 0 ? (clicks / impressions) * 100 : 0;
  const cpl = conversions > 0 ? cost / conversions : 0;
  const conversionRate = clicks > 0 ? (conversions / clicks) * 100 : 0;

  const campaign = await prisma.campaign.create({
    data: {
      campaignId: data.campaignId,
      campaignName: data.campaignName,
      platform: data.platform,
      impressions,
      clicks,
      conversions,
      cost,
      ctr,
      cpl,
      conversionRate,
    },
  });

  return { success: true, campaign };
}
