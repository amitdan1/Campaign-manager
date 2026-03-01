import { config } from "@/lib/config";

export async function sendLeadEvent(lead: {
  email?: string;
  phone?: string;
  source?: string;
  name?: string;
}) {
  const results: Record<string, boolean> = {};

  if (config.facebook.isPixelConfigured) {
    results.facebookCapi = await sendFacebookEvent(lead);
  }

  if (config.googleAds.conversionId) {
    results.googleEnhanced = await sendGoogleConversion(lead);
  }

  return results;
}

export async function sendStatusEvent(leadId: string, status: string) {
  // Track conversion events when lead reaches key milestones
  if (!["consultation_booked", "converted"].includes(status)) return {};

  // In production, this would send server-side conversion events
  // to Facebook CAPI and Google Ads Enhanced Conversions
  return { tracked: true, status };
}

async function sendFacebookEvent(lead: Record<string, unknown>): Promise<boolean> {
  if (!config.facebook.accessToken || !config.facebook.pixelId) return false;

  try {
    const url = `https://graph.facebook.com/v19.0/${config.facebook.pixelId}/events`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        data: [
          {
            event_name: "Lead",
            event_time: Math.floor(Date.now() / 1000),
            action_source: "website",
            user_data: {
              em: lead.email ? [lead.email] : [],
              ph: lead.phone ? [lead.phone] : [],
            },
          },
        ],
        access_token: config.facebook.accessToken,
      }),
    });
    return response.ok;
  } catch {
    return false;
  }
}

async function sendGoogleConversion(lead: Record<string, unknown>): Promise<boolean> {
  // Google Ads Enhanced Conversions would go here
  // Requires Google Ads API setup
  void lead;
  return false;
}
