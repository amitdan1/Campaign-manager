import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const days = parseInt(searchParams.get("days") ?? "30", 10);
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);

  const [leads, campaigns] = await Promise.all([
    prisma.lead.findMany({
      where: { createdAt: { gte: cutoff } },
      select: { createdAt: true, source: true },
      orderBy: { createdAt: "asc" },
    }),
    prisma.campaign.findMany({
      where: { date: { gte: cutoff } },
      select: { date: true, cost: true, conversions: true, platform: true },
      orderBy: { date: "asc" },
    }),
  ]);

  // Group leads by day
  const leadsByDay: Record<string, number> = {};
  for (const lead of leads) {
    const day = lead.createdAt.toISOString().slice(0, 10);
    leadsByDay[day] = (leadsByDay[day] ?? 0) + 1;
  }

  // Group spend by day
  const spendByDay: Record<string, number> = {};
  for (const c of campaigns) {
    const day = c.date.toISOString().slice(0, 10);
    spendByDay[day] = (spendByDay[day] ?? 0) + c.cost;
  }

  return NextResponse.json({ success: true, leadsByDay, spendByDay });
}
