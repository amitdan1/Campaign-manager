import { NextRequest, NextResponse } from "next/server";
import { getAssets } from "@/lib/agents/brand-scraper";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const source = searchParams.get("source") || undefined;
  const assetType = searchParams.get("type") || undefined;

  const assets = await getAssets({ source, assetType });
  return NextResponse.json({ success: true, assets });
}
