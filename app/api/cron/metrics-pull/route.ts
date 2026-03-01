import { NextRequest, NextResponse } from "next/server";
import { pullMetrics } from "@/lib/agents/campaign-tracking";

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get("authorization");
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const result = await pullMetrics();
  return NextResponse.json(result);
}
