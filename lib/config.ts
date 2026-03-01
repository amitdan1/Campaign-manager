export const config = {
  business: {
    name: process.env.BUSINESS_NAME ?? "Ofir Assulin Interior Design",
    phone: process.env.BUSINESS_PHONE ?? "052-626-9261",
    email: process.env.BUSINESS_EMAIL ?? "ofirassulin.design@gmail.com",
    website: process.env.BUSINESS_WEBSITE ?? "https://www.ofirassulin.design/",
  },

  budget: {
    total: parseInt(process.env.BUDGET_TOTAL ?? "500", 10),
    googleAds: parseInt(process.env.BUDGET_GOOGLE_ADS ?? "300", 10),
    facebook: parseInt(process.env.BUDGET_FACEBOOK ?? "200", 10),
  },

  targets: {
    cpl: parseInt(process.env.TARGET_CPL ?? "200", 10),
    consultationRate: parseFloat(process.env.TARGET_CONSULTATION_RATE ?? "0.40"),
    conversionRate: parseFloat(process.env.TARGET_CONVERSION_RATE ?? "0.50"),
    cac: parseInt(process.env.TARGET_CAC ?? "300", 10),
    roas: parseInt(process.env.TARGET_ROAS ?? "200", 10),
    ageMin: parseInt(process.env.TARGET_AGE_MIN ?? "35", 10),
    ageMax: parseInt(process.env.TARGET_AGE_MAX ?? "55", 10),
    locations: (process.env.TARGET_LOCATIONS ?? "תל אביב,הרצליה,רמת השרון,כפר שמריהו,סביון").split(","),
    minProjectBudget: parseInt(process.env.TARGET_MIN_PROJECT_BUDGET ?? "500000", 10),
  },

  openai: {
    apiKey: process.env.OPENAI_API_KEY ?? "",
    model: process.env.OPENAI_MODEL ?? "gpt-4o-mini",
    dailyTokenLimit: parseInt(process.env.DAILY_TOKEN_LIMIT ?? "500000", 10),
    get isConfigured() {
      return Boolean(this.apiKey);
    },
  },

  sendgrid: {
    apiKey: process.env.SENDGRID_API_KEY ?? "",
    fromEmail: process.env.SENDGRID_FROM_EMAIL ?? process.env.BUSINESS_EMAIL ?? "ofirassulin.design@gmail.com",
    get isConfigured() {
      return Boolean(this.apiKey);
    },
  },

  twilio: {
    accountSid: process.env.TWILIO_ACCOUNT_SID ?? "",
    authToken: process.env.TWILIO_AUTH_TOKEN ?? "",
    whatsappFrom: process.env.TWILIO_WHATSAPP_FROM ?? "",
    get isConfigured() {
      return Boolean(this.accountSid && this.authToken);
    },
  },

  googleAds: {
    developerToken: process.env.GOOGLE_ADS_DEVELOPER_TOKEN ?? "",
    clientId: process.env.GOOGLE_ADS_CLIENT_ID ?? "",
    clientSecret: process.env.GOOGLE_ADS_CLIENT_SECRET ?? "",
    refreshToken: process.env.GOOGLE_ADS_REFRESH_TOKEN ?? "",
    customerId: process.env.GOOGLE_ADS_CUSTOMER_ID ?? "",
    conversionId: process.env.GOOGLE_ADS_CONVERSION_ID ?? "",
    conversionLabel: process.env.GOOGLE_ADS_CONVERSION_LABEL ?? "",
    get isConfigured() {
      return Boolean(this.developerToken && this.customerId);
    },
  },

  facebook: {
    accessToken: process.env.FACEBOOK_ACCESS_TOKEN ?? "",
    adAccountId: process.env.FACEBOOK_AD_ACCOUNT_ID ?? "",
    pixelId: process.env.FACEBOOK_PIXEL_ID ?? "",
    get isConfigured() {
      return Boolean(this.accessToken && this.adAccountId);
    },
    get isPixelConfigured() {
      return Boolean(this.pixelId);
    },
  },

  flask: {
    secretKey: process.env.FLASK_SECRET_KEY ?? "change-me-in-production",
    debug: process.env.NODE_ENV !== "production",
    allowedOrigins: (process.env.ALLOWED_ORIGINS ?? "http://localhost:3000").split(","),
    maxContentLength: parseInt(process.env.MAX_CONTENT_LENGTH ?? String(2 * 1024 * 1024), 10),
  },

  automation: {
    autoFollowup: (process.env.AUTO_FOLLOWUP ?? "true") === "true",
    followupDelayHours: parseInt(process.env.FOLLOWUP_DELAY_HOURS ?? "2", 10),
    leadScoringEnabled: (process.env.LEAD_SCORING_ENABLED ?? "true") === "true",
  },

  serviceSegments: [
    {
      id: "villa_new_build",
      name: "בוני וילות חדשות",
      nameEn: "New Villa Builders",
      painPoints: ["מוצפים מהחלטות עיצוב", "פחד מטעויות יקרות", "צריכים ליווי מקצועי מא' ועד ת'"],
      keyMessage: "בונים בית חדש? נלווה אתכם מהתכנון ועד ההלבשה — בדיוק כמו שדמיינתם",
      keywords: ["עיצוב פנים וילה", "מעצבת פנים בתים פרטיים", "עיצוב פנים בית חדש"],
      projectTypes: ["villa", "new_build"],
    },
    {
      id: "renovation",
      name: "משפצים",
      nameEn: "Renovators",
      painPoints: ["לא יודעים מאיפה להתחיל", "חוששים מחריגות תקציב", "רוצים שמישהו ינהל הכל"],
      keyMessage: "שיפוץ לא חייב להיות כאב ראש — ליווי מקצועי שמבטיח שקט נפשי ותוצאה מושלמת",
      keywords: ["שיפוץ דירה יוקרתית", "מעצבת פנים שיפוצים", "שיפוץ מקיף"],
      projectTypes: ["renovation"],
    },
    {
      id: "luxury_apartment",
      name: "דירות יוקרה ופנטהאוזים",
      nameEn: "Luxury Apartments",
      painPoints: ["רוצים עיצוב שמרגיש ייחודי ולא 'עוד דירה'", "חשוב להם סטטוס ואסתטיקה", "מחפשים מעצבת עם טעם מוכח"],
      keyMessage: "עיצוב פנים שמשקף את מי שאתם — יוקרה שקטה, פרטים מדויקים, תחושת בית",
      keywords: ["עיצוב פנטהאוז", "עיצוב דירת יוקרה", "מעצבת פנים תל אביב"],
      projectTypes: ["penthouse", "luxury_apt"],
    },
  ],
} as const;

export type Config = typeof config;
