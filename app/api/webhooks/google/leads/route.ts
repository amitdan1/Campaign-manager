import { NextRequest, NextResponse } from "next/server";
import { captureAndScoreLead } from "@/lib/agents/orchestrator";
import { sendLeadEvent } from "@/lib/services/conversion-tracking";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const leadData = body.user_column_data ?? body;

    const result = await captureAndScoreLead({
      name: leadData.full_name || leadData.name || "Google Lead",
      phone: leadData.phone_number || leadData.phone || "",
      email: leadData.email || "",
      source: "google",
      campaign: body.campaign_id ?? "",
    });

    if (result.success) {
      await sendLeadEvent({ email: leadData.email, phone: leadData.phone, source: "google" }).catch(() => {});
    }

    return NextResponse.json(result);
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
