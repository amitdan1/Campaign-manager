import { NextRequest, NextResponse } from "next/server";
import { generateWeeklyStrategy } from "@/lib/agents/strategy";
import { prisma } from "@/lib/db";

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get("authorization");
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const result = await generateWeeklyStrategy();
  if (result.success && result.plan) {
    await prisma.proposal.create({
      data: {
        agentName: "strategy",
        proposalType: "strategy",
        title: `תוכנית שבועית — ${new Date().toLocaleDateString("he-IL")}`,
        summary: result.plan.summary,
        content: result.plan as never,
        status: "pending_review",
      },
    });
  }

  return NextResponse.json(result);
}
