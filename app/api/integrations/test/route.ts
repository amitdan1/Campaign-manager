import { NextRequest, NextResponse } from "next/server";
import { testConnection } from "@/lib/services/integration-manager";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { integration } = body;
  if (!integration) {
    return NextResponse.json({ success: false, error: "Integration key required" }, { status: 400 });
  }
  const result = await testConnection(integration);
  return NextResponse.json(result);
}
