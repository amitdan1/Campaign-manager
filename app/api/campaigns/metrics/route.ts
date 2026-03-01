import { NextRequest, NextResponse } from "next/server";
import { addCampaignMetrics } from "@/lib/agents/campaign-tracking";
import { campaignMetricsSchema } from "@/lib/validation";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const parsed = campaignMetricsSchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json(
        { success: false, errors: parsed.error.flatten().fieldErrors },
        { status: 400 }
      );
    }

    const result = await addCampaignMetrics(parsed.data);
    return NextResponse.json(result, { status: 201 });
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
