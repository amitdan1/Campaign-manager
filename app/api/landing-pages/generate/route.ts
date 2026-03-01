import { NextRequest, NextResponse } from "next/server";
import { generateLandingPage } from "@/lib/agents/landing-page";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { campaignName, variant, segment } = body;
    if (!campaignName) {
      return NextResponse.json({ success: false, error: "Campaign name required" }, { status: 400 });
    }

    const result = await generateLandingPage({ campaignName, variant, segment });
    return NextResponse.json(result);
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
