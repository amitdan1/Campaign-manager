import { chat, isOpenAIAvailable } from "@/lib/openai";
import { config } from "@/lib/config";
import { getPerformanceContext } from "@/lib/services/agent-memory";

export async function generateAdCopy(opts: {
  platform: string;
  campaignType?: string;
  segment?: string;
}) {
  if (!isOpenAIAvailable()) {
    return {
      success: true,
      method: "template",
      content: getDefaultAdCopy(opts.platform),
    };
  }

  const perfContext = await getPerformanceContext("content");

  const systemPrompt = `You are a Hebrew copywriter for ${config.business.name}, a luxury interior design firm.
Write compelling ad copy for ${opts.platform}.
Target: ${config.targets.locations.join(", ")}, ages ${config.targets.ageMin}-${config.targets.ageMax}.
Tone: Professional, warm, aspirational. All text in Hebrew.
${perfContext}`;

  const userMessage = `Create ad copy for a ${opts.campaignType || "general"} campaign on ${opts.platform}.
${opts.segment ? `Target segment: ${opts.segment}` : ""}
Include: headline, description, and CTA.`;

  const result = await chat(systemPrompt, userMessage, { maxTokens: 800, endpoint: "ad_copy" });
  return {
    success: true,
    method: result ? "ai" : "template",
    content: result ?? getDefaultAdCopy(opts.platform),
  };
}

function getDefaultAdCopy(platform: string) {
  return {
    headline: `עיצוב פנים מותאם אישית — ${config.business.name}`,
    description: "הגשימו את בית החלומות שלכם עם ליווי מקצועי מא' ועד ת'. התקשרו לייעוץ חינם.",
    cta: platform === "google" ? "התקשרו עכשיו" : "קבעו ייעוץ חינם",
  };
}

export async function generateEmailContent(opts: {
  type: string;
  leadName?: string;
}) {
  if (!isOpenAIAvailable()) {
    return {
      success: true,
      method: "template",
      subject: `${config.business.name} — ברוכים הבאים`,
      body: `שלום ${opts.leadName ?? ""},\nתודה על פנייתך. נחזור אליך בהקדם.\n${config.business.name}`,
    };
  }

  const systemPrompt = `You are writing marketing emails for ${config.business.name}, a luxury interior design firm in Israel.
All emails must be in Hebrew, professional, warm, and include the business contact info.
Phone: ${config.business.phone}, Email: ${config.business.email}`;

  const result = await chat(systemPrompt, `Write a ${opts.type} email for lead "${opts.leadName ?? ""}".`, {
    maxTokens: 600,
    endpoint: "email_content",
  });

  return {
    success: true,
    method: result ? "ai" : "template",
    subject: `${config.business.name} — ברוכים הבאים`,
    body: result ?? `שלום,\nתודה על פנייתך ל${config.business.name}. נחזור אליך בהקדם.`,
  };
}
