import { NextResponse } from "next/server";
import { getTokenStats } from "@/lib/openai";

export const dynamic = "force-dynamic";

export async function GET() {
  const stats = await getTokenStats();
  return NextResponse.json({ success: true, ...stats });
}
