import { z } from "zod";

export const VALID_LEAD_STATUSES = [
  "new",
  "contacted",
  "qualified",
  "consultation_booked",
  "converted",
  "lost",
] as const;

export const VALID_PROPOSAL_TYPES = [
  "campaign",
  "landing_page",
  "ad_copy",
  "budget",
  "strategy",
  "content",
  "general",
] as const;

export const VALID_PROPOSAL_STATUSES = [
  "draft",
  "pending_review",
  "approved",
  "revision_requested",
  "rejected",
  "executing",
  "completed",
  "failed",
] as const;

const VALID_TRANSITIONS: Record<string, Set<string>> = {
  draft: new Set(["pending_review"]),
  pending_review: new Set(["approved", "revision_requested", "rejected"]),
  revision_requested: new Set(["pending_review", "rejected"]),
  approved: new Set(["executing"]),
  executing: new Set(["completed", "failed"]),
  completed: new Set(),
  failed: new Set(["pending_review"]),
  rejected: new Set(),
};

export function validateStatusTransition(
  current: string,
  next: string
): { valid: boolean; error: string } {
  const allowed = VALID_TRANSITIONS[current] ?? new Set();
  if (allowed.has(next)) return { valid: true, error: "" };
  const allowedStr = Array.from(allowed).join(", ") || "none";
  return {
    valid: false,
    error: `Invalid transition: ${current} -> ${next}. Allowed: ${allowedStr}`,
  };
}

export const leadInputSchema = z.object({
  name: z.string().min(2, "שם חייב להכיל לפחות 2 תווים"),
  phone: z
    .string()
    .min(1, "טלפון הוא שדה חובה")
    .regex(/^[\d\-+\s()]{7,20}$/, "מספר טלפון לא תקין"),
  email: z
    .string()
    .email("כתובת אימייל לא תקינה")
    .optional()
    .or(z.literal("")),
  source: z.string().default("manual"),
  campaign: z.string().optional().default(""),
  location: z.string().optional(),
  budget: z.string().optional(),
  projectType: z.string().optional(),
  notes: z.string().optional(),
});

export const proposalInputSchema = z.object({
  title: z.string().min(1, "Title is required"),
  proposalType: z.enum(VALID_PROPOSAL_TYPES).optional().default("general"),
  summary: z.string().optional(),
  content: z.any().optional(),
  agentName: z.string().optional().default("user"),
});

export const campaignMetricsSchema = z.object({
  campaignId: z.string().min(1),
  campaignName: z.string().min(1),
  platform: z.string().min(1),
  impressions: z.number().int().min(0).default(0),
  clicks: z.number().int().min(0).default(0),
  conversions: z.number().int().min(0).default(0),
  cost: z.number().min(0).default(0),
});

export const chatMessageSchema = z.object({
  message: z.string().min(1).max(2000),
});

export type LeadInput = z.infer<typeof leadInputSchema>;
export type ProposalInput = z.infer<typeof proposalInputSchema>;
export type CampaignMetricsInput = z.infer<typeof campaignMetricsSchema>;
