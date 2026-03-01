import { NextResponse } from "next/server";
import { getAllStatuses } from "@/lib/services/integration-manager";

export async function GET() {
  return NextResponse.json({ success: true, integrations: getAllStatuses() });
}
