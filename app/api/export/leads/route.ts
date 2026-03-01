import { NextRequest, NextResponse } from "next/server";
import { getLeads } from "@/lib/agents/lead-capture";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const format = searchParams.get("format") ?? "json";

  const leads = await getLeads();

  if (format === "csv") {
    const headers = ["id", "name", "phone", "email", "source", "status", "qualityScore", "location", "budget", "projectType", "createdAt"];
    const rows = leads.map((l) =>
      headers.map((h) => {
        const val = (l as Record<string, unknown>)[h];
        return val instanceof Date ? val.toISOString() : String(val ?? "");
      }).join(",")
    );
    const csv = [headers.join(","), ...rows].join("\n");

    return new NextResponse(csv, {
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": "attachment; filename=leads.csv",
      },
    });
  }

  return NextResponse.json({ success: true, leads });
}
