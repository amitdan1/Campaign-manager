import { NextResponse } from "next/server";
import { scrapeAssets } from "@/lib/agents/brand-scraper";

export async function POST() {
  const result = await scrapeAssets();
  return NextResponse.json(result);
}
