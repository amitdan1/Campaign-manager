import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const days = parseInt(searchParams.get("days") ?? "30", 10);
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);

  const campaigns = await prisma.campaign.findMany({
    where: { date: { gte: cutoff } },
    orderBy: { date: "desc" },
  });

  return NextResponse.json({ success: true, campaigns });
}
