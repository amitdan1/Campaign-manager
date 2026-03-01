import { prisma } from "@/lib/db";

export async function storeMemory(
  agentName: string,
  memoryType: string,
  key: string,
  value: unknown,
  context = ""
): Promise<number | null> {
  try {
    const mem = await prisma.agentMemory.create({
      data: { agentName, memoryType, key, value: value as never, context },
    });
    return mem.id;
  } catch (e) {
    console.error("Failed to store memory:", e);
    return null;
  }
}

export async function recallMemories(
  agentName: string,
  opts: { memoryType?: string; key?: string; limit?: number } = {}
) {
  const { memoryType, key, limit = 10 } = opts;
  try {
    return await prisma.agentMemory.findMany({
      where: {
        agentName,
        ...(memoryType ? { memoryType } : {}),
        ...(key ? { key } : {}),
      },
      orderBy: { createdAt: "desc" },
      take: limit,
    });
  } catch (e) {
    console.error("Failed to recall memories:", e);
    return [];
  }
}

export async function getPromptContext(agentName: string, maxMemories = 5): Promise<string> {
  const memories = await recallMemories(agentName, { limit: maxMemories });
  if (memories.length === 0) return "";

  const lines = ["## Past Experience (from your memory)"];
  for (const m of memories) {
    const val = m.value as Record<string, unknown>;
    if (m.memoryType === "feedback") {
      lines.push(`- User feedback on ${m.key}: ${JSON.stringify(val)}`);
    } else if (m.memoryType === "episodic") {
      lines.push(`- Previous action (${m.key}): ${JSON.stringify(val)}`);
    } else if (m.memoryType === "semantic") {
      lines.push(`- Learned: ${m.key} = ${JSON.stringify(val)}`);
    }
  }
  return lines.join("\n");
}

export async function recordProposalOutcome(
  agentName: string,
  proposalTitle: string,
  status: string,
  feedback = ""
) {
  const value = { title: proposalTitle, outcome: status, ...(feedback ? { feedback } : {}) };
  await storeMemory(agentName, "episodic", `proposal_${status}`, value, feedback);

  if (status === "rejected" && feedback) {
    await storeMemory(
      agentName,
      "feedback",
      "rejection_reason",
      { title: proposalTitle, reason: feedback },
      `User rejected '${proposalTitle}': ${feedback}`
    );
  }
}

export async function recordCampaignPerformance(
  agentName: string,
  campaignName: string,
  platform: string,
  metrics: Record<string, number>
) {
  const value = { campaign: campaignName, platform, ...metrics };
  await storeMemory(
    agentName,
    "episodic",
    `campaign_performance_${platform}`,
    value,
    `Campaign '${campaignName}' on ${platform}: CTR=${(metrics.ctr ?? 0).toFixed(1)}%, CPL=₪${(metrics.cpl ?? 0).toFixed(0)}`
  );
}

export async function getPerformanceContext(agentName: string, maxRecords = 5): Promise<string> {
  const memories = await recallMemories(agentName, { memoryType: "episodic", limit: maxRecords * 2 });
  const perfMemories = memories.filter((m) => m.key.startsWith("campaign_performance_"));
  if (perfMemories.length === 0) return "";

  const lines = ["## Campaign Performance Data (learn from these results)"];

  const sorted = [...perfMemories].sort((a, b) => {
    const aVal = (a.value as Record<string, number>)?.ctr ?? 0;
    const bVal = (b.value as Record<string, number>)?.ctr ?? 0;
    return bVal - aVal;
  });

  const top = sorted.slice(0, 3);
  if (top.length > 0) {
    lines.push("### Top Performing:");
    for (const m of top) {
      const v = m.value as Record<string, unknown>;
      lines.push(
        `- ${v.campaign ?? "Unknown"} (${v.platform ?? ""}): CTR=${Number(v.ctr ?? 0).toFixed(1)}%, CPL=₪${Number(v.cpl ?? 0).toFixed(0)}`
      );
    }
  }

  lines.push("", "Use these insights: build on what worked, avoid what didn't.");
  return lines.join("\n");
}
