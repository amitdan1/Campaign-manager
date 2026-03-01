import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";
import { config } from "@/lib/config";

export const dynamic = "force-dynamic";

export async function GET() {
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

  const platformSpend = await prisma.campaign.groupBy({
    by: ["platform"],
    where: { date: { gte: thirtyDaysAgo } },
    _sum: { cost: true },
  });

  const allocated: Record<string, number> = {
    google: config.budget.googleAds,
    facebook: config.budget.facebook,
  };

  const spent: Record<string, number> = {};
  for (const row of platformSpend) {
    spent[row.platform] = row._sum.cost ?? 0;
  }

  return NextResponse.json({
    success: true,
    budget: {
      total: config.budget.total,
      allocated,
      spent,
    },
  });
}
