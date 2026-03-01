import { chat, isOpenAIAvailable } from "@/lib/openai";
import { config } from "@/lib/config";

type Variant = "hero_gallery" | "split_layout" | "story_flow";

export async function generateLandingPage(opts: {
  campaignName: string;
  variant?: Variant;
  segment?: string;
}) {
  const variant = opts.variant ?? "hero_gallery";

  if (!isOpenAIAvailable()) {
    return {
      success: true,
      method: "template",
      html: buildTemplatePage(variant, opts.campaignName),
    };
  }

  const systemPrompt = `You are an expert landing page designer for ${config.business.name}, a luxury interior design firm in Israel.
Create a complete, self-contained HTML landing page. The page must be RTL Hebrew, mobile-responsive, with modern design.
Business: ${config.business.name}, Phone: ${config.business.phone}, Email: ${config.business.email}
Include: hero section, benefits, portfolio gallery placeholders, testimonials, lead capture form, footer.
Style: Warm luxury aesthetic, gold accent (#c9a96e), clean typography.
Layout variant: ${variant}`;

  const result = await chat(
    systemPrompt,
    `Create a landing page for campaign "${opts.campaignName}". ${opts.segment ? `Target segment: ${opts.segment}` : ""}`,
    { maxTokens: 4000, endpoint: "landing_page" }
  );

  return {
    success: true,
    method: result ? "ai" : "template",
    html: result ?? buildTemplatePage(variant, opts.campaignName),
  };
}

function buildTemplatePage(variant: Variant, campaignName: string): string {
  return `<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${config.business.name} — ${campaignName}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Inter,sans-serif;background:#faf9f7;color:#2d2d2d;direction:rtl}
.hero{background:#1a1a2e;color:#fff;padding:4rem 2rem;text-align:center}
.hero h1{font-size:2.5rem;margin-bottom:1rem;color:#c9a96e}
.hero p{font-size:1.2rem;opacity:.8;max-width:600px;margin:0 auto}
.cta-btn{display:inline-block;background:#c9a96e;color:#fff;padding:1rem 2.5rem;border-radius:8px;font-size:1.1rem;margin-top:2rem;text-decoration:none}
.section{padding:3rem 2rem;max-width:900px;margin:0 auto}
.footer{background:#1a1a2e;color:#e0ddd8;padding:2rem;text-align:center;font-size:.85rem}
</style>
</head>
<body>
<section class="hero">
<h1>${config.business.name}</h1>
<p>עיצוב פנים שמשקף את מי שאתם — יוקרה שקטה, פרטים מדויקים, תחושת בית</p>
<a href="tel:${config.business.phone}" class="cta-btn">קבעו ייעוץ חינם — ${config.business.phone}</a>
</section>
<section class="section">
<h2>למה ${config.business.name}?</h2>
<p>ליווי מקצועי מא' ועד ת', עיצוב מותאם אישית, ותוצאות שמדברות בעד עצמן.</p>
</section>
<footer class="footer">
<p>${config.business.name} | ${config.business.phone} | ${config.business.email}</p>
</footer>
</body>
</html>`;
}
