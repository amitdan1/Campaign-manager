import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  const proposal = await prisma.proposal.findUnique({
    where: { id: parseInt(params.id, 10) },
  });

  if (!proposal) {
    return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
  }

  return NextResponse.json({ success: true, proposal });
}
