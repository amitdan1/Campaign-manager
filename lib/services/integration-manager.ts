import { config } from "@/lib/config";

interface IntegrationStatus {
  name: string;
  key: string;
  connected: boolean;
  icon: string;
  description: string;
  fields: Array<{ key: string; label: string; required: boolean }>;
}

export function getAllStatuses(): IntegrationStatus[] {
  return [
    {
      name: "OpenAI",
      key: "openai",
      connected: config.openai.isConfigured,
      icon: "brain",
      description: "AI-powered content generation, lead scoring, and strategy",
      fields: [
        { key: "OPENAI_API_KEY", label: "API Key", required: true },
        { key: "OPENAI_MODEL", label: "Model", required: false },
      ],
    },
    {
      name: "Google Ads",
      key: "google_ads",
      connected: config.googleAds.isConfigured,
      icon: "google",
      description: "Campaign management and conversion tracking",
      fields: [
        { key: "GOOGLE_ADS_DEVELOPER_TOKEN", label: "Developer Token", required: true },
        { key: "GOOGLE_ADS_CUSTOMER_ID", label: "Customer ID", required: true },
        { key: "GOOGLE_ADS_CLIENT_ID", label: "Client ID", required: false },
        { key: "GOOGLE_ADS_CLIENT_SECRET", label: "Client Secret", required: false },
        { key: "GOOGLE_ADS_REFRESH_TOKEN", label: "Refresh Token", required: false },
      ],
    },
    {
      name: "Facebook Marketing",
      key: "facebook",
      connected: config.facebook.isConfigured,
      icon: "facebook",
      description: "Ad campaigns, lead ads, and pixel tracking",
      fields: [
        { key: "FACEBOOK_ACCESS_TOKEN", label: "Access Token", required: true },
        { key: "FACEBOOK_AD_ACCOUNT_ID", label: "Ad Account ID", required: true },
        { key: "FACEBOOK_PIXEL_ID", label: "Pixel ID", required: false },
      ],
    },
    {
      name: "SendGrid",
      key: "sendgrid",
      connected: config.sendgrid.isConfigured,
      icon: "envelope",
      description: "Email automation for lead nurturing",
      fields: [
        { key: "SENDGRID_API_KEY", label: "API Key", required: true },
        { key: "SENDGRID_FROM_EMAIL", label: "From Email", required: false },
      ],
    },
    {
      name: "Twilio WhatsApp",
      key: "twilio",
      connected: config.twilio.isConfigured,
      icon: "whatsapp",
      description: "WhatsApp messaging for lead follow-up",
      fields: [
        { key: "TWILIO_ACCOUNT_SID", label: "Account SID", required: true },
        { key: "TWILIO_AUTH_TOKEN", label: "Auth Token", required: true },
        { key: "TWILIO_WHATSAPP_FROM", label: "WhatsApp From Number", required: true },
      ],
    },
  ];
}

export async function testConnection(integrationKey: string): Promise<{ success: boolean; message: string }> {
  switch (integrationKey) {
    case "openai":
      return config.openai.isConfigured
        ? { success: true, message: "OpenAI API key configured" }
        : { success: false, message: "API key not set" };
    case "google_ads":
      return config.googleAds.isConfigured
        ? { success: true, message: "Google Ads credentials configured" }
        : { success: false, message: "Credentials not set" };
    case "facebook":
      return config.facebook.isConfigured
        ? { success: true, message: "Facebook credentials configured" }
        : { success: false, message: "Credentials not set" };
    case "sendgrid":
      return config.sendgrid.isConfigured
        ? { success: true, message: "SendGrid API key configured" }
        : { success: false, message: "API key not set" };
    case "twilio":
      return config.twilio.isConfigured
        ? { success: true, message: "Twilio credentials configured" }
        : { success: false, message: "Credentials not set" };
    default:
      return { success: false, message: `Unknown integration: ${integrationKey}` };
  }
}
