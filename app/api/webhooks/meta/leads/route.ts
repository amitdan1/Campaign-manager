import { NextRequest, NextResponse } from "next/server";
import { captureAndScoreLead } from "@/lib/agents/orchestrator";
import { sendLeadEvent } from "@/lib/services/conversion-tracking";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const mode = searchParams.get("hub.mode");
  const token = searchParams.get("hub.verify_token");
  const challenge = searchParams.get("hub.challenge");

  if (mode === "subscribe" && token === process.env.META_WEBHOOK_VERIFY_TOKEN) {
    return new NextResponse(challenge, { status: 200 });
  }
  return NextResponse.json({ error: "Forbidden" }, { status: 403 });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const entry = body?.entry?.[0]?.changes?.[0]?.value;
    if (!entry) {
      return NextResponse.json({ success: false, error: "No lead data" }, { status: 400 });
    }

    const fieldData = entry.field_data ?? [];
    const fields: Record<string, string> = {};
    for (const f of fieldData) {
      fields[f.name?.toLowerCase()] = f.values?.[0] ?? "";
    }

    const result = await captureAndScoreLead({
      name: fields.full_name || fields.name || "Meta Lead",
      phone: fields.phone_number || fields.phone || "",
      email: fields.email || "",
      source: "facebook",
      campaign: entry.form_id ?? "",
    });

    if (result.success) {
      await sendLeadEvent({ email: fields.email, phone: fields.phone, source: "facebook" }).catch(() => {});
    }

    return NextResponse.json(result);
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
