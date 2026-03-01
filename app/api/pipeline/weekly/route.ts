import { NextResponse } from "next/server";
import { generateWeeklyStrategy } from "@/lib/agents/strategy";
import { prisma } from "@/lib/db";

export async function POST() {
  try {
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
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
