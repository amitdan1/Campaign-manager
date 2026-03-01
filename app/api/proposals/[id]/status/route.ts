import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/db";
import { validateStatusTransition } from "@/lib/validation";
import { recordProposalOutcome } from "@/lib/services/agent-memory";

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const { status, feedback } = body;

    const proposal = await prisma.proposal.findUnique({
      where: { id: parseInt(params.id, 10) },
    });

    if (!proposal) {
      return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    }

    const transition = validateStatusTransition(proposal.status, status);
    if (!transition.valid) {
      return NextResponse.json({ success: false, error: transition.error }, { status: 400 });
    }

    const updated = await prisma.proposal.update({
      where: { id: proposal.id },
      data: {
        status,
        feedback: feedback || proposal.feedback,
        ...(status === "approved" ? { approvedAt: new Date() } : {}),
        ...(status === "executing" ? { executedAt: new Date() } : {}),
      },
    });

    await recordProposalOutcome(proposal.agentName, proposal.title, status, feedback).catch(() => {});

    return NextResponse.json({ success: true, proposal: updated });
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
