import { NextResponse } from "next/server";
import { healthCheck } from "@/lib/agents/orchestrator";

export async function GET() {
  const result = await healthCheck();
  return NextResponse.json({ ...result, timestamp: new Date().toISOString() });
}
