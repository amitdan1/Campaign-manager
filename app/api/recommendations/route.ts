import { NextResponse } from "next/server";
import { getRecommendations } from "@/lib/agents/budget-optimizer";

export const dynamic = "force-dynamic";

export async function GET() {
  const result = await getRecommendations();
  return NextResponse.json(result);
}
