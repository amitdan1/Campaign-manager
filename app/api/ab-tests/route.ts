import { NextRequest, NextResponse } from "next/server";
import { getAllTests, createTest } from "@/lib/services/ab-testing";

export async function GET() {
  const tests = await getAllTests();
  return NextResponse.json({ success: true, tests });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, variants } = body;
    if (!name || !variants?.length) {
      return NextResponse.json({ success: false, error: "Name and variants required" }, { status: 400 });
    }
    const test = await createTest(name, variants);
    return NextResponse.json({ success: true, test }, { status: 201 });
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
