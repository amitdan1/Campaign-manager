import { NextRequest, NextResponse } from "next/server";
import { updateLeadStatus } from "@/lib/agents/lead-capture";
import { sendStatusEvent } from "@/lib/services/conversion-tracking";

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const { status, notes } = body;

    if (!status) {
      return NextResponse.json(
        { success: false, error: "Status is required" },
        { status: 400 }
      );
    }

    const result = await updateLeadStatus(params.id, status, notes);

    if (result.success) {
      await sendStatusEvent(params.id, status).catch(() => {});
    }

    return NextResponse.json(result, { status: result.success ? 200 : 400 });
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
