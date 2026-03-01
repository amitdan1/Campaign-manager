import { NextRequest, NextResponse } from "next/server";
import { getTestResults } from "@/lib/services/ab-testing";

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  const result = await getTestResults(parseInt(params.id, 10));
  if (!result) {
    return NextResponse.json({ success: false, error: "Test not found" }, { status: 404 });
  }
  return NextResponse.json({ success: true, test: result });
}
