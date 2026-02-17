"""
Content Agent (LLM-powered).
Generates Hebrew ad copy, email templates, landing page content,
and social media posts. Understands Ofir's brand voice and target audience.
Falls back to pre-written templates when OpenAI is not available.
"""

from typing import Any, Dict

from agents.base_agent import BaseAgent
from services.openai_service import OpenAIService
from prompts import load_prompt


class ContentAgent(BaseAgent):
    """Generates marketing content in Hebrew for various channels."""

    def __init__(self):
        super().__init__(name="Content")
        self.ai = OpenAIService()

    def _get_brand_prompt(self) -> str:
        from services.agent_memory import memory_service
        memory_ctx = memory_service.get_prompt_context("Content")
        perf_ctx = memory_service.get_performance_context("Content")
        combined = "\n\n".join(filter(None, [memory_ctx, perf_ctx]))
        return load_prompt("content", "system").format(memory_context=combined)

    def _get_segment_context(self, segment_id: str = "") -> str:
        """Build a prompt context string for a specific audience segment."""
        if not segment_id:
            return ""
        from config import Config
        for seg in Config.SERVICE_SEGMENTS:
            if seg["id"] == segment_id:
                return (
                    f"\n## Target Segment: {seg['name']} ({seg['name_en']})\n"
                    f"Pain points: {', '.join(seg['pain_points'])}\n"
                    f"Key message: {seg['key_message']}\n"
                    f"Keywords: {', '.join(seg['keywords'])}\n"
                    f"Tailor ALL content specifically to this segment's needs and pain points."
                )
        return ""

    def run(self, content_type: str = "ad_copy", **kwargs) -> Dict[str, Any]:
        """
        Generate content.
        content_type: 'ad_copy', 'email', 'landing_page', 'social_post', 'sms'
        kwargs: Additional context like campaign_name, target_audience, segment, etc.
        """
        generators = {
            "ad_copy": self._generate_ad_copy,
            "email": self._generate_email,
            "landing_page": self._generate_landing_page,
            "social_post": self._generate_social_post,
        }

        generator = generators.get(content_type)
        if not generator:
            return {
                "success": False,
                "errors": [f"Unknown content type: {content_type}. Available: {list(generators.keys())}"],
            }

        return generator(**kwargs)

    # --- Ad Copy ---

    def _generate_ad_copy(self, platform: str = "google", campaign_theme: str = "", num_variations: int = 3, segment: str = "", **kwargs) -> Dict[str, Any]:
        """Generate ad copy variations for Google or Facebook, optionally targeted to a segment."""
        if self.ai.is_available():
            segment_ctx = self._get_segment_context(segment)
            prompt = load_prompt("content", "user_ad_copy").format(
                num_variations=num_variations,
                platform=platform,
                campaign_theme=campaign_theme or "high-end interior design in central Israel",
            )
            if segment_ctx:
                prompt += f"\n{segment_ctx}"

            result = self.ai.chat_json(
                system_prompt=self._get_brand_prompt(),
                user_message=prompt,
                temperature=0.7,
                max_tokens=2000,
            )

            if result:
                return {
                    "success": True,
                    "method": "ai",
                    "platform": platform,
                    "segment": segment,
                    "variations": result.get("variations", []),
                }

        # Fallback
        return {
            "success": True,
            "method": "template",
            "platform": platform,
            "segment": segment,
            "variations": self._get_template_ad_copy(platform),
        }

    def _get_template_ad_copy(self, platform: str) -> list:
        """Pre-written ad copy templates."""
        if platform == "google":
            return [
                {
                    "headline1": "עיצוב פנים יוקרתי",
                    "headline2": "אופיר אסולין | מעצבת פנים",
                    "headline3": "ייעוץ חינם | הרצליה ות\"א",
                    "description1": "מתמחה בעיצוב וילות ובתים פרטיים באזור המרכז. ליווי מקצועי מהתכנון ועד ההלבשה.",
                    "description2": "10+ שנות ניסיון בעיצוב בתים יוקרתיים. קבעו שיחת ייעוץ חינמית עכשיו.",
                },
                {
                    "headline1": "בונים בית חדש?",
                    "headline2": "עיצוב פנים מותאם אישית",
                    "headline3": "מעצבת פנים | מרכז הארץ",
                    "description1": "אל תתחילו שיפוץ בלי תכנון מקצועי. אופיר אסולין - עיצוב פנים שמשנה חיים.",
                    "description2": "הורידו מדריך חינמי: 5 שאלות שחייבים לשאול לפני שיפוץ. קבעו פגישה.",
                },
            ]
        else:
            return [
                {
                    "primary_text": "בונים בית חדש? תהליך העיצוב יכול להיות מבלבל ומתיש. אני אופיר אסולין, מעצבת פנים עם ניסיון של שנים, מלווה פרויקטים משלב התכנון ועד ההלבשה הסופית.",
                    "headline": "ייעוץ עיצוב פנים חינמי",
                    "description": "קבעו שיחת ייעוץ חינמית עכשיו",
                    "cta": "Learn More",
                },
                {
                    "primary_text": "הבית שלכם מגיע עיצוב שמשקף את מי שאתם. בסטודיו של אופיר אסולין אנחנו יוצרים מרחבים אישיים ומותאמים בדיוק לצרכים שלכם.",
                    "headline": "עיצוב פנים יוקרתי | מרכז",
                    "description": "ליווי מקצועי מהתכנון ועד ההלבשה",
                    "cta": "Sign Up",
                },
            ]

    # --- Email Templates ---

    def _generate_email(self, email_type: str = "welcome", context: str = "", **kwargs) -> Dict[str, Any]:
        """Generate email template."""
        if self.ai.is_available():
            prompt = load_prompt("content", "user_email").format(
                email_type=email_type,
                context=context or "Standard email for new lead",
            )

            result = self.ai.chat_json(
                system_prompt=self._get_brand_prompt(),
                user_message=prompt,
                temperature=0.5,
            )

            if result:
                return {"success": True, "method": "ai", "email": result}

        # Fallback
        return {
            "success": True,
            "method": "template",
            "email": {
                "subject": "תודה על פנייתך - אופיר אסולין עיצוב פנים",
                "body": (
                    "שלום,\n\n"
                    "תודה על פנייתך לסטודיו של אופיר אסולין עיצוב פנים ואמנות.\n\n"
                    "אני שמחה להכיר אותך ולהבין את החזון שלך לבית שלך.\n\n"
                    "בברכה,\nאופיר אסולין\n052-626-9261"
                ),
            },
        }

    # --- Landing Page ---

    def _generate_landing_page(self, campaign_name: str = "", headline: str = "", segment: str = "", **kwargs) -> Dict[str, Any]:
        """Generate landing page content, optionally targeted to a segment."""
        if self.ai.is_available():
            segment_ctx = self._get_segment_context(segment)
            prompt = load_prompt("content", "user_landing_page").format(
                campaign_name=campaign_name or "Interior Design Lead Gen",
            )
            if segment_ctx:
                prompt += f"\n{segment_ctx}"

            result = self.ai.chat_json(
                system_prompt=self._get_brand_prompt(),
                user_message=prompt,
                temperature=0.6,
            )

            if result:
                return {"success": True, "method": "ai", "segment": segment, "content": result}

        # Fallback
        return {
            "success": True,
            "method": "template",
            "content": {
                "headline": headline or "עיצוב פנים שמשנה חיים",
                "subheadline": "אופיר אסולין - מעצבת פנים מובילה באזור המרכז",
                "bullet_points": [
                    "ליווי מקצועי מהתכנון ועד ההלבשה הסופית",
                    "בניית קונספט עיצובי מותאם אישית",
                    "ניהול פרויקט מלא כולל בקרת איכות",
                    "10+ שנות ניסיון בעיצוב בתים יוקרתיים",
                ],
                "cta_text": "קבעו שיחת ייעוץ חינמית",
                "testimonial": "\"אופיר הפכה את החזון שלנו למציאות. התוצאה עלתה על כל הציפיות.\" - משפחת כהן, הרצליה",
            },
        }

    # --- Social Media ---

    def _generate_social_post(self, post_type: str = "portfolio", topic: str = "", segment: str = "", **kwargs) -> Dict[str, Any]:
        """Generate social media post content, optionally targeted to a segment."""
        if self.ai.is_available():
            segment_ctx = self._get_segment_context(segment)
            prompt = load_prompt("content", "user_social_post").format(
                post_type=post_type,
                topic=topic or "Showcase interior design work",
            )
            if segment_ctx:
                prompt += f"\n{segment_ctx}"

            result = self.ai.chat_json(
                system_prompt=self._get_brand_prompt(),
                user_message=prompt,
                temperature=0.7,
            )

            if result:
                return {"success": True, "method": "ai", "post": result}

        # Fallback
        return {
            "success": True,
            "method": "template",
            "post": {
                "caption": (
                    "✨ עוד פרויקט שהושלם בהצלחה!\n\n"
                    "כל פרויקט מתחיל בחזון ומסתיים בבית חלומות.\n"
                    "רוצים לדעת איך זה מרגיש? קבעו שיחת ייעוץ חינמית.\n\n"
                    "#עיצובפנים #interiordesign #אופיראסולין #עיצובבתים #הרצליה #תלאביב #עיצוביוקרתי"
                ),
                "image_suggestion": "Before/after photo of a living room transformation",
            },
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            "healthy": True,
            "ai_available": self.ai.is_available(),
            "content_method": "ai" if self.ai.is_available() else "templates",
        }
