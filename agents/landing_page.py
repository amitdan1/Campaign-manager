"""
Landing Page Agent (LLM-powered).
Generates high-end, brand-aligned landing pages inspired by Ofir Assulin's
website aesthetic: fullscreen photography, warm minimalism, quiet luxury.
Produces 3 template variants and saves each as a proposal with live preview.

Target audience: wealthy clients (35-60) in central Israel seeking luxury
interior design for villas, penthouses, and high-end apartments.
"""

import random
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from models.proposal import Proposal
from models.brand_asset import BrandAsset
from services.database import get_session
from services.openai_service import OpenAIService
from prompts import load_prompt


# ---------------------------------------------------------------------------
# Brand constants -- sourced directly from ofirassulin.design
# ---------------------------------------------------------------------------
BRAND = {
    "logo_url": "https://static.wixstatic.com/media/23a2ee_b11a3356168a424bb5dc7bf607c7b85f~mv2.png/v1/fill/w_236,h_57,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/%D7%9C%D7%95%D7%92%D7%95%20%D7%9E%D7%9C%D7%90%20%D7%A2%D7%9D%20%D7%A8%D7%A7%D7%A2%20%D7%A9%D7%A7%D7%95%D7%A3.png",
    "tagline_en": "Giving Soul To Spaces",
    "tagline_he": "נותנת נשמה לחללים",
    "quote": "עיצוב פנים משפיע על רגשות, זיכרונות, חוויות ורגשות",
    "whatsapp": "972526269261",
    "instagram": "ofirassulin.design",
    "colors": {"bg": "#faf9f7", "accent": "#c9a96e", "text": "#2d2d2d", "light": "#f5f0e8", "dark": "#1a1a2e"},
    "fonts": {"heading": "Playfair Display", "body": "Inter"},
    # Default hero images from the real site (fallback if scraper hasn't run)
    "default_images": [
        "https://static.wixstatic.com/media/0b41c3_6f333c7d19bf44ecb22bc003a8a0d551~mv2.jpg/v1/fill/w_1920,h_1020,fp_0.46_0.56,q_90,enc_avif,quality_auto/0b41c3_6f333c7d19bf44ecb22bc003a8a0d551~mv2.jpg",
        "https://static.wixstatic.com/media/0b41c3_91f2262ed307435eb2ab93392b48f365~mv2.jpg/v1/fill/w_1920,h_1020,fp_0.56_0.51,q_90,enc_avif,quality_auto/0b41c3_91f2262ed307435eb2ab93392b48f365~mv2.jpg",
        "https://static.wixstatic.com/media/0b41c3_5fda7b7222fd49d8b75992af680f9901~mv2.jpg/v1/fill/w_1920,h_1020,fp_0.48_0.65,q_90,enc_avif,quality_auto/0b41c3_5fda7b7222fd49d8b75992af680f9901~mv2.jpg",
        "https://static.wixstatic.com/media/0b41c3_602a3ddc65874da6a63b434ef9975072~mv2.jpg/v1/fill/w_1920,h_1020,fp_0.35_0.59,q_90,enc_avif,quality_auto/0b41c3_602a3ddc65874da6a63b434ef9975072~mv2.jpg",
        "https://static.wixstatic.com/media/0b41c3_ba5903479b0e4af1a1fa76f5b804e016~mv2.jpg/v1/fill/w_1920,h_1020,fp_0.48_0.63,q_90,enc_avif,quality_auto/0b41c3_ba5903479b0e4af1a1fa76f5b804e016~mv2.jpg",
        "https://static.wixstatic.com/media/0b41c3_b197a45c26474c179699f89d9f94346c~mv2.jpg/v1/fill/w_1920,h_1020,q_90,enc_avif,quality_auto/0b41c3_b197a45c26474c179699f89d9f94346c~mv2.jpg",
        "https://static.wixstatic.com/media/0b41c3_61594ff8965d406290bd3bcdf9d1f867~mv2.jpg/v1/fill/w_1920,h_1020,q_90,enc_avif,quality_auto/0b41c3_61594ff8965d406290bd3bcdf9d1f867~mv2.jpg",
    ],
}

# ---------------------------------------------------------------------------
# Shared CSS foundation for all templates -- luxury-optimized
# ---------------------------------------------------------------------------
_SHARED_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:'Inter',system-ui,-apple-system,sans-serif;background:%(bg)s;color:%(text)s;direction:rtl;line-height:1.7;-webkit-font-smoothing:antialiased}
h1,h2,h3{font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-weight:700;line-height:1.25}
.container{max-width:1100px;margin:0 auto;padding:0 2rem}
img{max-width:100%%;height:auto}
a{color:%(accent)s;text-decoration:none}

/* --- Header / Nav --- */
.lp-nav{position:fixed;top:0;right:0;left:0;z-index:50;display:flex;justify-content:space-between;align-items:center;padding:1.2rem 2.5rem;background:transparent;transition:background .3s}
.lp-nav.scrolled{background:rgba(26,26,46,.92);backdrop-filter:blur(8px)}
.lp-nav img{height:36px}
.lp-nav-links{display:flex;gap:1.5rem;align-items:center}
.lp-nav-links a{color:#fff;font-size:.85rem;letter-spacing:.03em;transition:color .2s}
.lp-nav-links a:hover{color:%(accent)s}

/* --- CTA Button --- */
.cta-btn{display:inline-flex;align-items:center;gap:.5rem;padding:.9rem 2.4rem;background:%(accent)s;color:#fff;border:none;border-radius:4px;font-size:1rem;font-weight:600;cursor:pointer;transition:all .25s;text-decoration:none;font-family:'Inter',sans-serif;letter-spacing:.02em}
.cta-btn:hover{background:#b8993f;transform:translateY(-1px);box-shadow:0 8px 24px rgba(201,169,110,.4)}
.cta-btn i{font-size:1.1rem}
.cta-btn-outline{background:transparent;border:1.5px solid %(accent)s;color:%(accent)s}
.cta-btn-outline:hover{background:%(accent)s;color:#fff}
.cta-btn-whatsapp{background:#25D366;color:#fff}
.cta-btn-whatsapp:hover{background:#1da851}

/* --- Section spacing --- */
.section{padding:6.5rem 0}
.section-dark{background:%(dark)s;color:#e8e6e1}
.section-light{background:%(light)s}
.section-title{font-size:2.4rem;text-align:center;margin-bottom:.6rem;color:%(text)s}
.section-dark .section-title{color:#fff}
.section-subtitle{text-align:center;color:#8a8a8a;font-size:1rem;margin-bottom:3.5rem;max-width:600px;margin-left:auto;margin-right:auto;line-height:1.7}
.section-dark .section-subtitle{color:#b0aca5}
.section-label{font-family:'Playfair Display',serif;color:%(accent)s;font-size:.85rem;letter-spacing:.15em;text-align:center;display:block;margin-bottom:.4rem}

/* --- Social Proof Bar --- */
.social-proof-bar{display:flex;justify-content:center;align-items:center;gap:2rem;padding:1.5rem 2rem;background:%(dark)s;color:#e0ddd8;font-size:.9rem;letter-spacing:.02em}
.social-proof-bar .sp-divider{width:1px;height:1.2rem;background:%(accent)s;opacity:.6}
.social-proof-bar .sp-item{display:flex;align-items:center;gap:.4rem}
.social-proof-bar .sp-item i{color:%(accent)s;font-size:.8rem}
.social-proof-bar .sp-number{font-weight:700;color:%(accent)s}

/* --- Value Props --- */
.values-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:3rem}
.value-card{text-align:center;padding:2.5rem 1.5rem;border-top:2px solid %(accent)s}
.value-card i{font-size:1.8rem;color:%(accent)s;margin-bottom:1.2rem;display:block}
.value-card h3{font-size:1.15rem;margin-bottom:.7rem}
.value-card p{font-size:.9rem;color:#8a8a8a;line-height:1.7}

/* --- Gallery --- */
.gallery-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:.75rem}
.gallery-grid img{width:100%%;height:280px;object-fit:cover;border-radius:4px;transition:transform .4s,filter .4s}
.gallery-grid img:hover{transform:scale(1.03);filter:brightness(1.05)}

/* --- Testimonial --- */
.testimonial-section{max-width:700px;margin:0 auto;text-align:center;padding:3rem 2rem}
.testimonial-section blockquote{font-family:'Playfair Display',serif;font-size:1.3rem;font-style:italic;line-height:1.8;color:%(text)s;position:relative;padding:2rem 0;border-top:2px solid rgba(201,169,110,.3);border-bottom:2px solid rgba(201,169,110,.3)}
.testimonial-section .tq-source{font-family:'Inter',sans-serif;font-size:.82rem;color:#8a8a8a;margin-top:1rem;font-style:normal;letter-spacing:.02em}

/* --- Form --- */
.form-card{background:#fff;border-radius:8px;padding:3rem 2.5rem;box-shadow:0 12px 40px rgba(0,0,0,.06);max-width:520px;margin:0 auto}
.form-card h2{font-size:1.6rem;text-align:center;margin-bottom:.5rem}
.form-card .form-sub{text-align:center;color:#8a8a8a;font-size:.88rem;margin-bottom:2rem}
.form-card label{display:block;font-size:.82rem;font-weight:600;margin-bottom:.35rem;color:%(text)s}
.form-card input,.form-card select{width:100%%;padding:.75rem 1rem;margin-bottom:1.2rem;border:1px solid #e0ddd8;border-radius:4px;font-size:.92rem;background:%(bg)s;transition:border-color .2s,box-shadow .2s;font-family:'Inter',sans-serif}
.form-card input:focus,.form-card select:focus{outline:none;border-color:%(accent)s;box-shadow:0 0 0 3px rgba(201,169,110,.15)}
.form-card .cta-btn{width:100%%;justify-content:center;padding:1rem;font-size:1.05rem;margin-top:.75rem}

/* --- Footer --- */
.lp-footer{text-align:center;padding:2.5rem;font-size:.8rem;color:#b0aca5;background:%(dark)s}
.lp-footer a{color:%(accent)s}

/* --- Responsive --- */
@media(max-width:768px){
  .hero-content h1{font-size:2rem !important}
  .split-layout{grid-template-columns:1fr !important}
  .lp-nav{padding:1rem 1.2rem}
  .lp-nav-links{display:none}
  .section{padding:4rem 0}
  .form-card{margin:0 1rem;padding:2rem 1.5rem}
  .social-proof-bar{flex-direction:column;gap:.75rem;padding:1.2rem 1rem}
  .social-proof-bar .sp-divider{display:none}
  .testimonial-section blockquote{font-size:1.1rem}
  .gallery-grid img{height:200px}
}
""" % BRAND["colors"]


class LandingPageAgent(BaseAgent):
    """Generates luxury landing pages as proposals with 3 template variants."""

    def __init__(self):
        super().__init__(name="LandingPage")
        self.ai = OpenAIService()

    def run(self, campaign_name: str = "", campaign_details: str = "",
            variant: str = "", **kwargs) -> Dict[str, Any]:
        """Generate a landing page and save as proposal."""
        images = self._get_brand_images()

        if self.ai.is_available():
            result = self._ai_generate(campaign_name, campaign_details, images)
        else:
            v = variant or random.choice(["hero_gallery", "split_layout", "story_flow"])
            result = self._template_generate(campaign_name, v, images)

        # Save as proposal
        session = get_session()
        try:
            proposal = Proposal(
                agent_name="LandingPage",
                proposal_type="landing_page",
                title=f"דף נחיתה: {result.get('title', campaign_name or 'כללי')}",
                summary=result.get("headline", ""),
                content=result,
                status="pending_review",
            )
            session.add(proposal)
            session.commit()
            self.logger.info(f"Landing page proposal created: {proposal.id} (variant: {result.get('variant')})")
            return {"success": True, "proposal_id": proposal.id, "page": result}
        except Exception as e:
            session.rollback()
            return {"success": False, "errors": [str(e)]}
        finally:
            session.close()

    # ------------------------------------------------------------------
    # AI generation
    # ------------------------------------------------------------------

    def _ai_generate(self, name: str, details: str, images: list) -> dict:
        from services.agent_memory import memory_service
        perf_ctx = memory_service.get_performance_context("LandingPage")

        c = BRAND["colors"]
        prompt = load_prompt("landing_page", "system").format(
            logo_url=BRAND["logo_url"],
            bg=c["bg"], accent=c["accent"], text=c["text"], dark=c["dark"],
            whatsapp=BRAND["whatsapp"],
            instagram=BRAND["instagram"],
            brand_images="\n".join(f"- {url}" for url in images[:8]) if images else "No images available -- use placeholder backgrounds with overlays",
            campaign_details=details or f"Campaign: {name or 'General luxury interior design lead generation'}",
        )
        if perf_ctx:
            prompt += f"\n\n{perf_ctx}"
        result = self.ai.chat_json(
            system_prompt=prompt,
            user_message="Generate the landing page now. Make it world-class.",
            temperature=0.5, max_tokens=4000,
        )
        if result and result.get("html"):
            return result
        return self._template_generate(name, "hero_gallery", images)

    # ------------------------------------------------------------------
    # Template variants (fallback when no OpenAI key)
    # ------------------------------------------------------------------

    def _template_generate(self, campaign_name: str, variant: str, images: list) -> dict:
        generators = {
            "hero_gallery": self._build_hero_gallery,
            "split_layout": self._build_split_layout,
            "story_flow": self._build_story_flow,
        }
        gen = generators.get(variant, self._build_hero_gallery)
        return gen(campaign_name or "עיצוב פנים יוקרתי", images)

    # ------------------------------------------------------------------
    # Shared HTML blocks
    # ------------------------------------------------------------------

    def _build_social_proof_bar(self) -> str:
        return """
<div class="social-proof-bar">
  <div class="sp-item"><i class="fas fa-check-circle"></i> <span class="sp-number">100+</span> פרויקטים שהושלמו</div>
  <div class="sp-divider"></div>
  <div class="sp-item"><i class="fas fa-map-marker-alt"></i> הרצליה, כפר שמריהו, סביון, תל אביב</div>
  <div class="sp-divider"></div>
  <div class="sp-item"><i class="fas fa-award"></i> <span class="sp-number">15+</span> שנות ניסיון</div>
</div>"""

    def _build_testimonial(self, variant: str = "default") -> str:
        testimonials = {
            "default": {
                "quote": "אופיר הצליחה לתרגם את החזון שלנו לחלל שמרגיש בדיוק כמו שדמיינו — ואפילו יותר. כל פרט, כל חומר, כל פינה — הכל נבחר בקפידה ובטעם מושלם.",
                "source": "בעלי וילה, הרצליה פיתוח",
            },
            "renovation": {
                "quote": "השיפוץ הפך את הדירה שלנו למשהו שלא חשבנו שאפשרי. הליווי המקצועי מהרגע הראשון נתן לנו שקט מוחלט לאורך כל הדרך.",
                "source": "בעלי פנטהאוז, תל אביב",
            },
            "new_build": {
                "quote": "מהתכנון הראשוני ועד ההלבשה הסופית — תהליך חלק, מקצועי ומדויק. הבית שלנו הוא בדיוק מה שרצינו ויותר.",
                "source": "בעלי וילה, כפר שמריהו",
            },
        }
        t = testimonials.get(variant, testimonials["default"])
        return f"""
<section class="section">
  <div class="testimonial-section">
    <span class="section-label">TESTIMONIAL</span>
    <blockquote>"{t['quote']}"</blockquote>
    <p class="tq-source">— {t['source']}</p>
  </div>
</section>"""

    # --- Variant 1: Hero Gallery ---
    def _build_hero_gallery(self, title: str, images: list) -> dict:
        hero_img = images[0] if images else BRAND["default_images"][0]
        gallery = images[1:7] if len(images) > 1 else BRAND["default_images"][1:7]
        return {
            "title": title,
            "headline": "Giving Soul To Spaces",
            "variant": "hero_gallery",
            "html": self._wrap_page(title, f"""
<!-- HERO -->
<section style="position:relative;height:100vh;overflow:hidden">
  <div style="position:absolute;inset:0;background:url('{hero_img}') center/cover no-repeat"></div>
  <div style="position:absolute;inset:0;background:linear-gradient(to top,rgba(26,26,46,.7) 0%,rgba(26,26,46,.2) 50%,transparent 100%)"></div>
  <div style="position:relative;z-index:2;height:100%;display:flex;flex-direction:column;justify-content:flex-end;padding:0 2.5rem 6rem">
    <h1 style="font-family:'Playfair Display',serif;font-size:4rem;color:#fff;margin-bottom:.5rem;letter-spacing:-.02em">Giving Soul To Spaces</h1>
    <p style="font-size:1.2rem;color:#e0ddd8;max-width:560px;margin-bottom:2.5rem;line-height:1.7">{BRAND['quote']}</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap">
      <a href="#contact" class="cta-btn"><i class="fas fa-calendar-check"></i> קבעו פגישת היכרות</a>
      <a href="https://api.whatsapp.com/send/?phone={BRAND['whatsapp']}" target="_blank" class="cta-btn cta-btn-whatsapp"><i class="fab fa-whatsapp"></i> דברו איתנו</a>
    </div>
  </div>
</section>

<!-- SOCIAL PROOF -->
{self._build_social_proof_bar()}

<!-- EXPERIENCE -->
<section class="section">
  <div class="container">
    <span class="section-label">THE EXPERIENCE</span>
    <h2 class="section-title">חוויית העיצוב</h2>
    <p class="section-subtitle">ליווי מקצועי מהתכנון ועד ההלבשה הסופית — כל פרט נבחר בקפידה</p>
    <div class="values-grid">
      <div class="value-card"><i class="fas fa-pencil-ruler"></i><h3>קונספט מותאם אישית</h3><p>תכנון שמשקף את מי שאתם — עיצוב שמותאם בדיוק לאורח החיים ולשפה העיצובית שאתם אוהבים</p></div>
      <div class="value-card"><i class="fas fa-hard-hat"></i><h3>ניהול פרויקט מלא</h3><p>מסט תכניות מלא ועד הלבשה סופית. ביקורות באתר, ניהול ספקים ובקרת איכות</p></div>
      <div class="value-card"><i class="fas fa-gem"></i><h3>תשומת לב לפרטים</h3><p>פונקציונלי, פרקטי, נוח — ובאותה נשימה מדויק ויוקרתי. כל אלמנט נבחר בקפידה</p></div>
    </div>
  </div>
</section>

<!-- GALLERY -->
<section class="section section-light">
  <div class="container">
    <span class="section-label">PROJECTS</span>
    <h2 class="section-title">מהפרויקטים שלנו</h2>
    <p class="section-subtitle">הצצה לעולם העיצוב של אופיר אסולין</p>
    <div class="gallery-grid">
      {''.join(f'<img src="{img}" alt="פרויקט עיצוב פנים יוקרתי" loading="lazy">' for img in gallery)}
    </div>
  </div>
</section>

<!-- TESTIMONIAL -->
{self._build_testimonial("default")}

<!-- FORM -->
<section class="section section-light" id="contact">
  <div class="container">
    <div class="form-card">
      <h2>קבעו פגישת היכרות</h2>
      <p class="form-sub">השאירו פרטים ונתאם פגישה אישית</p>
      {self._build_form(title)}
    </div>
  </div>
</section>

<!-- WHATSAPP CTA -->
<section class="section-dark" style="padding:4rem 0;text-align:center">
  <h2 style="font-family:'Playfair Display',serif;font-size:1.8rem;color:#fff;margin-bottom:.5rem">מעדיפים לדבר ישירות?</h2>
  <p style="color:#b0aca5;margin-bottom:1.5rem;font-size:.95rem">נשמח לשמוע על הפרויקט שלכם</p>
  <a href="https://api.whatsapp.com/send/?phone={BRAND['whatsapp']}" target="_blank" class="cta-btn cta-btn-whatsapp" style="font-size:1.1rem;padding:1rem 2.5rem"><i class="fab fa-whatsapp"></i> שלחו הודעה</a>
</section>
"""),
        }

    # --- Variant 2: Split Layout ---
    def _build_split_layout(self, title: str, images: list) -> dict:
        hero_img = images[0] if images else BRAND["default_images"][0]
        gallery = images[1:5] if len(images) > 1 else BRAND["default_images"][1:5]
        return {
            "title": title,
            "headline": "נותנת נשמה לחללים",
            "variant": "split_layout",
            "html": self._wrap_page(title, f"""
<!-- HERO SPLIT -->
<section style="display:grid;grid-template-columns:1fr 1fr;min-height:100vh" class="split-layout">
  <div style="background:url('{hero_img}') center/cover no-repeat"></div>
  <div style="display:flex;flex-direction:column;justify-content:center;padding:4rem 3.5rem;background:{BRAND['colors']['bg']}">
    <img src="{BRAND['logo_url']}" alt="אופיר אסולין" style="height:40px;margin-bottom:2.5rem;align-self:flex-start">
    <p style="font-family:'Playfair Display',serif;color:{BRAND['colors']['accent']};font-size:.95rem;letter-spacing:.1em;margin-bottom:.5rem">INTERIOR DESIGN & ART</p>
    <h1 style="font-family:'Playfair Display',serif;font-size:3rem;margin-bottom:1rem;line-height:1.15">נותנת נשמה<br>לחללים</h1>
    <p style="color:#8a8a8a;font-size:1.05rem;margin-bottom:2.5rem;max-width:420px;line-height:1.7">{BRAND['quote']}</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap">
      <a href="#contact" class="cta-btn"><i class="fas fa-calendar-check"></i> קבעו פגישת היכרות</a>
      <a href="https://api.whatsapp.com/send/?phone={BRAND['whatsapp']}" target="_blank" class="cta-btn cta-btn-outline"><i class="fab fa-whatsapp"></i> דברו איתנו</a>
    </div>
  </div>
</section>

<!-- SOCIAL PROOF -->
{self._build_social_proof_bar()}

<!-- SERVICES -->
<section class="section">
  <div class="container">
    <span class="section-label">OUR SERVICES</span>
    <h2 class="section-title">השירותים שלנו</h2>
    <p class="section-subtitle">ליווי מקצועי מהתכנון ועד ההלבשה הסופית</p>
    <div class="values-grid">
      <div class="value-card"><i class="fas fa-drafting-compass"></i><h3>עיצוב קונספט</h3><p>בניית סט תכניות מלא, הדמיות תלת-ממד, ובניית קונספט עיצובי שמותאם בדיוק לחזון שלכם</p></div>
      <div class="value-card"><i class="fas fa-building"></i><h3>ליווי שיפוץ ובנייה</h3><p>ביקורים באתר, בקרת איכות, ניהול ספקים ותקציב — שקט נפשי לאורך כל התהליך</p></div>
      <div class="value-card"><i class="fas fa-couch"></i><h3>הלבשה סופית</h3><p>בחירת ריהוט, טקסטיל, תאורה ואביזרים — עד הפרט האחרון</p></div>
    </div>
  </div>
</section>

<!-- GALLERY -->
<section class="section section-light">
  <div class="container">
    <span class="section-label">PORTFOLIO</span>
    <h2 class="section-title">פרויקטים נבחרים</h2>
    <p class="section-subtitle">&nbsp;</p>
    <div class="gallery-grid">
      {''.join(f'<img src="{img}" alt="פרויקט עיצוב יוקרתי" loading="lazy">' for img in gallery)}
    </div>
  </div>
</section>

<!-- TESTIMONIAL -->
{self._build_testimonial("renovation")}

<!-- FORM -->
<section class="section section-light" id="contact">
  <div class="container">
    <div class="form-card">
      <h2>התחילו את המסע</h2>
      <p class="form-sub">השאירו פרטים ונתאם פגישה אישית</p>
      {self._build_form(title)}
    </div>
  </div>
</section>

<!-- WHATSAPP CTA -->
<section class="section-dark" style="padding:4rem 0;text-align:center">
  <p style="color:#b0aca5;margin-bottom:1rem;font-size:.95rem">מעדיפים שיחה אישית?</p>
  <a href="https://api.whatsapp.com/send/?phone={BRAND['whatsapp']}" target="_blank" class="cta-btn cta-btn-whatsapp"><i class="fab fa-whatsapp"></i> דברו איתנו</a>
</section>
"""),
        }

    # --- Variant 3: Story Flow ---
    def _build_story_flow(self, title: str, images: list) -> dict:
        imgs = images[:6] if images else BRAND["default_images"][:6]
        return {
            "title": title,
            "headline": "הבית הוא הנשמה שלכם בעולם החומר",
            "variant": "story_flow",
            "html": self._wrap_page(title, f"""
<!-- HERO -->
<section style="position:relative;height:100vh;overflow:hidden">
  <div style="position:absolute;inset:0;background:url('{imgs[0]}') center/cover"></div>
  <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(26,26,46,.15) 0%,rgba(26,26,46,.75) 100%)"></div>
  <div style="position:relative;z-index:2;height:100%;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:2rem">
    <img src="{BRAND['logo_url']}" alt="אופיר אסולין" style="height:44px;margin-bottom:2.5rem">
    <h1 style="font-family:'Playfair Display',serif;font-size:3.5rem;color:#fff;max-width:700px;margin-bottom:1rem">הבית הוא הנשמה שלכם<br>בעולם החומר</h1>
    <p style="color:#e0ddd8;font-size:1.1rem;max-width:500px;margin-bottom:2.5rem;line-height:1.7">הופכת מבנה לבית עם נשמה — ליווי מקצועי מהתכנון ועד ההלבשה הסופית</p>
    <a href="#contact" class="cta-btn"><i class="fas fa-arrow-down"></i> גלו עוד</a>
  </div>
</section>

<!-- SOCIAL PROOF -->
{self._build_social_proof_bar()}

<!-- STORY SECTION 1 -->
<section class="section">
  <div class="container" style="display:grid;grid-template-columns:1fr 1fr;gap:3.5rem;align-items:center">
    <div>
      <span class="section-label" style="text-align:right">THE STUDIO</span>
      <h2 style="font-family:'Playfair Display',serif;font-size:2.2rem;margin-bottom:1.2rem">הסטודיו של אופיר</h2>
      <p style="color:#8a8a8a;line-height:1.8;margin-bottom:1rem">הסטודיו הוקם מתוך תשוקה עמוקה ליצירת שינוי מהותי באיכות חייהם של אנשים. בתהליך תכנון ועיצוב הבית שלכם, אני יוצרת עבורכם מקום שמותאם בדיוק לצרכים שלכם — מקום שמעניק את התחושות הנכונות.</p>
      <p style="color:#8a8a8a;line-height:1.8;margin-bottom:2rem">פונקציונלי, פרקטי, נוח — ובאותה נשימה מדויק לשפה העיצובית שאתם אוהבים.</p>
      <a href="#contact" class="cta-btn cta-btn-outline"><i class="fas fa-calendar-check"></i> קבעו פגישת היכרות</a>
    </div>
    <img src="{imgs[1] if len(imgs) > 1 else imgs[0]}" alt="סטודיו אופיר אסולין" style="border-radius:6px;height:440px;width:100%;object-fit:cover">
  </div>
</section>

<!-- GALLERY -->
<section class="section section-light">
  <div class="container">
    <span class="section-label">PROJECTS</span>
    <h2 class="section-title">מהפרויקטים שלנו</h2>
    <p class="section-subtitle">&nbsp;</p>
    <div class="gallery-grid">
      {''.join(f'<img src="{img}" alt="פרויקט עיצוב יוקרתי" loading="lazy">' for img in imgs[2:])}
    </div>
  </div>
</section>

<!-- VALUES -->
<section class="section">
  <div class="container">
    <span class="section-label">OUR APPROACH</span>
    <h2 class="section-title">הגישה שלנו</h2>
    <p class="section-subtitle">כל פרויקט מתחיל בהקשבה — ומסתיים בבית שמרגיש בדיוק נכון</p>
    <div class="values-grid">
      <div class="value-card"><i class="fas fa-lightbulb"></i><h3>קונספט עיצובי</h3><p>תכנון שמשקף את מי שאתם ומותאם לאורח חייכם — מהדמיות תלת-ממד ועד סט תכניות מלא</p></div>
      <div class="value-card"><i class="fas fa-tools"></i><h3>ליווי מלא</h3><p>ניהול פרויקט מקצועי — ספקים, לוחות זמנים, תקציב ובקרת איכות</p></div>
      <div class="value-card"><i class="fas fa-heart"></i><h3>תשומת לב לפרטים</h3><p>כל אלמנט נבחר בקפידה — ריהוט, טקסטיל, תאורה ואביזרים. עד הפרט האחרון</p></div>
    </div>
  </div>
</section>

<!-- TESTIMONIAL -->
{self._build_testimonial("new_build")}

<!-- FORM -->
<section class="section section-light" id="contact">
  <div class="container">
    <div class="form-card">
      <h2>גלו את הפרויקט הבא שלכם</h2>
      <p class="form-sub">השאירו פרטים ונתאם פגישה אישית</p>
      {self._build_form(title)}
    </div>
  </div>
</section>

<!-- WHATSAPP CTA -->
<section class="section-dark" style="padding:4rem 0;text-align:center">
  <h2 style="font-family:'Playfair Display',serif;font-size:1.6rem;color:#fff;margin-bottom:1.2rem">נשמח לשמוע על החזון שלכם</h2>
  <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
    <a href="https://api.whatsapp.com/send/?phone={BRAND['whatsapp']}" target="_blank" class="cta-btn cta-btn-whatsapp"><i class="fab fa-whatsapp"></i> דברו איתנו</a>
    <a href="https://www.instagram.com/{BRAND['instagram']}" target="_blank" class="cta-btn cta-btn-outline" style="border-color:#fff;color:#fff"><i class="fab fa-instagram"></i> Instagram</a>
  </div>
</section>
"""),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_form(self, campaign: str) -> str:
        return f"""<form id="leadForm" action="#">
        <label>שם מלא</label><input type="text" name="name" placeholder="השם שלכם" required>
        <label>טלפון</label><input type="tel" name="phone" placeholder="050-0000000" required>
        <label>אימייל</label><input type="email" name="email" placeholder="your@email.com">
        <label>מיקום הנכס</label>
        <select name="location"><option value="">בחרו אזור</option><option value="שרונה / נווה צדק">שרונה / נווה צדק</option><option value="הרצליה פיתוח">הרצליה פיתוח</option><option value="כפר שמריהו / סביון">כפר שמריהו / סביון</option><option value="רמת השרון">רמת השרון</option><option value="קיסריה">קיסריה</option><option value="אחר">אחר</option></select>
        <label>סוג פרויקט</label>
        <select name="project_type"><option value="">בחרו סוג</option><option value="villa">וילה פרטית</option><option value="penthouse">פנטהאוז</option><option value="luxury_apt">דירת יוקרה</option><option value="renovation">שיפוץ מקיף</option><option value="commercial">עיצוב מסחרי</option></select>
        <label>טווח תקציב משוער</label>
        <select name="budget_range"><option value="">בחרו טווח</option><option value="up_to_500k">עד ₪500,000</option><option value="500k_1m">₪500,000 - ₪1,000,000</option><option value="1m_3m">₪1,000,000 - ₪3,000,000</option><option value="3m_plus">מעל ₪3,000,000</option></select>
        <input type="hidden" name="source" value="landing_page">
        <input type="hidden" name="campaign" value="{campaign}">
        <button type="submit" class="cta-btn"><i class="fas fa-calendar-check"></i> קבעו פגישה</button>
      </form>"""

    def _build_tracking_scripts(self) -> str:
        """Generate Facebook Pixel and Google gtag scripts using configured IDs."""
        from config import Config
        scripts = []

        fb_pixel_id = Config.FACEBOOK_PIXEL_ID
        if fb_pixel_id:
            scripts.append(f"""<!-- Facebook Pixel -->
<script>
!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','{fb_pixel_id}');
fbq('track','PageView');
</script>
<noscript><img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id={fb_pixel_id}&ev=PageView&noscript=1"/></noscript>""")

        google_conversion_id = Config.GOOGLE_ADS_CONVERSION_ID
        if google_conversion_id:
            scripts.append(f"""<!-- Google Ads gtag -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-{google_conversion_id}"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}
gtag('js',new Date());gtag('config','AW-{google_conversion_id}');
</script>""")

        return "\n".join(scripts)

    def _build_conversion_js(self) -> str:
        """Generate JS that fires conversion events on form submit."""
        from config import Config
        parts = []

        if Config.FACEBOOK_PIXEL_ID:
            parts.append("if(typeof fbq==='function'){fbq('track','Lead');}")

        google_id = Config.GOOGLE_ADS_CONVERSION_ID
        google_label = Config.GOOGLE_ADS_CONVERSION_LABEL
        if google_id and google_label:
            parts.append(
                f"if(typeof gtag==='function'){{gtag('event','conversion',{{'send_to':'AW-{google_id}/{google_label}'}});}}"
            )

        return "\n      ".join(parts)

    def _wrap_page(self, title: str, body_html: str) -> str:
        tracking_head = self._build_tracking_scripts()
        conversion_js = self._build_conversion_js()

        return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} | אופיר אסולין עיצוב פנים</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
{tracking_head}
<style>{_SHARED_CSS}</style>
</head>
<body>

<!-- NAV -->
<nav class="lp-nav" id="lpNav">
  <img src="{BRAND['logo_url']}" alt="אופיר אסולין">
  <div class="lp-nav-links">
    <a href="#contact">צרו קשר</a>
    <a href="https://api.whatsapp.com/send/?phone={BRAND['whatsapp']}" target="_blank" class="cta-btn cta-btn-whatsapp" style="padding:.5rem 1.2rem;font-size:.85rem"><i class="fab fa-whatsapp"></i> דברו איתנו</a>
  </div>
</nav>

{body_html}

<!-- FOOTER -->
<footer class="lp-footer">
  <p>&copy; 2026 אופיר אסולין עיצוב פנים &middot; <a href="https://www.instagram.com/{BRAND['instagram']}" target="_blank">@{BRAND['instagram']}</a></p>
</footer>

<script>
// Sticky nav background on scroll
window.addEventListener('scroll',function(){{document.getElementById('lpNav').classList.toggle('scrolled',window.scrollY>80)}});
// Form submission with conversion tracking
document.getElementById('leadForm').addEventListener('submit',function(e){{
  e.preventDefault();
  var d=Object.fromEntries(new FormData(this));
  fetch('/api/leads',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d)}})
    .then(r=>r.json()).then(function(r){{
      if(r.success){{
        // Fire conversion events to ad networks
        {conversion_js}
        alert('תודה! ניצור איתכם קשר בהקדם לתיאום פגישה.');
      }}else{{alert(r.error||'שגיאה');}}
    }});
}});
</script>
</body>
</html>"""

    def _get_brand_images(self) -> List[str]:
        session = get_session()
        try:
            assets = session.query(BrandAsset).filter_by(
                asset_type="image", source="website"
            ).limit(10).all()
            urls = [a.url for a in assets]
            return urls if urls else BRAND["default_images"]
        except Exception:
            return BRAND["default_images"]
        finally:
            session.close()

    def health_check(self) -> Dict[str, Any]:
        return {"healthy": True, "ai_available": self.ai.is_available()}
