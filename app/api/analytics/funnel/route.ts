import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET() {
  const statuses = ["new", "contacted", "qualified", "consultation_booked", "converted", "lost"];

  const groups = await prisma.lead.groupBy({
    by: ["status"],
    _count: true,
  });

  const funnel: Record<string, number> = {};
  for (const s of statuses) {
    funnel[s] = groups.find((g) => g.status === s)?._count ?? 0;
  }

  return NextResponse.json({ success: true, funnel });
}
