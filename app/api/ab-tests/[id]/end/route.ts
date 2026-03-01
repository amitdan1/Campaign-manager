import { NextRequest, NextResponse } from "next/server";
import { endTest } from "@/lib/services/ab-testing";

export async function POST(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const test = await endTest(parseInt(params.id, 10));
    return NextResponse.json({ success: true, test });
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
