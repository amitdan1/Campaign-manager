import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/db";
import { proposalInputSchema } from "@/lib/validation";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const status = searchParams.get("status") || undefined;
  const proposalType = searchParams.get("proposal_type") || undefined;
  const limit = parseInt(searchParams.get("limit") ?? "50", 10);
  const offset = parseInt(searchParams.get("offset") ?? "0", 10);

  const proposals = await prisma.proposal.findMany({
    where: {
      ...(status ? { status } : {}),
      ...(proposalType ? { proposalType } : {}),
    },
    orderBy: { createdAt: "desc" },
    take: limit,
    skip: offset,
  });

  return NextResponse.json({ success: true, proposals });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const parsed = proposalInputSchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json(
        { success: false, errors: parsed.error.flatten().fieldErrors },
        { status: 400 }
      );
    }

    const proposal = await prisma.proposal.create({
      data: {
        agentName: parsed.data.agentName ?? "user",
        proposalType: parsed.data.proposalType ?? "general",
        title: parsed.data.title,
        summary: parsed.data.summary,
        content: JSON.stringify(parsed.data.content ?? {}),
        status: "pending_review",
      },
    });

    return NextResponse.json({ success: true, proposal }, { status: 201 });
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
