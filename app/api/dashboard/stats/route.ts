import { NextResponse } from "next/server";
import { getDashboardStats } from "@/lib/agents/orchestrator";

export async function GET() {
  const result = await getDashboardStats(30);
  return NextResponse.json(result);
}
