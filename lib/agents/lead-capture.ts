import { prisma } from "@/lib/db";

interface LeadInput {
  name: string;
  phone: string;
  email?: string;
  source?: string;
  campaign?: string;
  location?: string;
  budget?: string;
  projectType?: string;
  notes?: string;
}

function normalize(data: LeadInput) {
  return {
    name: data.name.trim(),
    phone: data.phone.replace(/[^\d+\-]/g, ""),
    email: (data.email ?? "").trim().toLowerCase(),
    source: (data.source ?? "manual").trim().toLowerCase(),
    campaign: (data.campaign ?? "").trim(),
    location: data.location?.trim() || null,
    budget: data.budget?.trim() || null,
    projectType: data.projectType?.trim() || null,
    notes: data.notes?.trim() || null,
  };
}

export async function captureLead(input: LeadInput) {
  const data = normalize(input);

  // Check for duplicates
  const existing = await prisma.lead.findFirst({
    where: {
      OR: [
        ...(data.phone ? [{ phone: data.phone }] : []),
        ...(data.email ? [{ email: data.email }] : []),
      ],
    },
  });

  if (existing) {
    return {
      success: false,
      duplicate: true,
      existingLeadId: existing.id,
      message: "Lead already exists",
    };
  }

  const lead = await prisma.lead.create({
    data: {
      name: data.name,
      phone: data.phone,
      email: data.email,
      source: data.source,
      campaign: data.campaign,
      location: data.location,
      budget: data.budget,
      projectType: data.projectType,
      notes: data.notes,
    },
  });

  await prisma.interaction.create({
    data: {
      leadId: lead.id,
      channel: data.source,
      interactionType: "lead_captured",
      content: `Lead captured from ${data.source} via ${data.campaign || "direct"}`,
      status: "completed",
    },
  });

  return { success: true, leadId: lead.id, lead };
}

export async function updateLeadStatus(leadId: string, status: string, notes?: string) {
  const validStatuses = ["new", "contacted", "qualified", "consultation_booked", "converted", "lost"];
  if (!validStatuses.includes(status)) {
    return { success: false, errors: [`Invalid status. Must be one of: ${validStatuses.join(", ")}`] };
  }

  const lead = await prisma.lead.findUnique({ where: { id: leadId } });
  if (!lead) {
    return { success: false, errors: [`Lead ${leadId} not found`] };
  }

  const oldStatus = lead.status;
  const updated = await prisma.lead.update({
    where: { id: leadId },
    data: { status, ...(notes ? { notes } : {}) },
  });

  await prisma.interaction.create({
    data: {
      leadId,
      channel: "system",
      interactionType: "status_change",
      content: `Status changed from '${oldStatus}' to '${status}'${notes ? `. Notes: ${notes}` : ""}`,
      status: "completed",
    },
  });

  return { success: true, lead: updated };
}

export async function getLeads(filters: { status?: string; source?: string; minScore?: number } = {}) {
  return prisma.lead.findMany({
    where: {
      ...(filters.status ? { status: filters.status } : {}),
      ...(filters.source ? { source: filters.source } : {}),
      ...(filters.minScore != null ? { qualityScore: { gte: filters.minScore } } : {}),
    },
    orderBy: { createdAt: "desc" },
  });
}

export async function getLead(leadId: string) {
  return prisma.lead.findUnique({ where: { id: leadId } });
}
