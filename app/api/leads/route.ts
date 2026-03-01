import { NextRequest, NextResponse } from "next/server";
import { getLeads } from "@/lib/agents/lead-capture";
import { captureAndScoreLead } from "@/lib/agents/orchestrator";
import { leadInputSchema } from "@/lib/validation";
import { sendLeadEvent } from "@/lib/services/conversion-tracking";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const status = searchParams.get("status") || undefined;
  const source = searchParams.get("source") || undefined;
  const minScore = searchParams.get("min_score")
    ? parseInt(searchParams.get("min_score")!, 10)
    : undefined;

  const leads = await getLeads({ status, source, minScore });
  return NextResponse.json({ success: true, leads });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const parsed = leadInputSchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json(
        { success: false, errors: parsed.error.flatten().fieldErrors },
        { status: 400 }
      );
    }

    const result = await captureAndScoreLead(parsed.data);

    if (result.success) {
      await sendLeadEvent({
        email: parsed.data.email,
        phone: parsed.data.phone,
        source: parsed.data.source,
        name: parsed.data.name,
      }).catch(() => {});
    }

    return NextResponse.json(result, { status: result.success ? 201 : 400 });
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
