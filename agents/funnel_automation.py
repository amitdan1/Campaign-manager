"""
Funnel Automation Agent (hybrid: automation + LLM personalization).
Manages email sequences and WhatsApp follow-ups.
Uses LLM to personalize messages in Hebrew based on lead profile.
Falls back to templates when OpenAI is not configured.
"""

from datetime import datetime
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from models.lead import Lead
from models.interaction import Interaction
from services.database import get_session
from services.email_service import EmailService
from services.whatsapp_service import WhatsAppService
from services.openai_service import OpenAIService


PERSONALIZATION_PROMPT = """You are a marketing assistant for Ofir Assulin Interior Design,
a high-end interior designer in central Israel.

Write a personalized follow-up message in Hebrew for the lead described below.
The message should:
- Be warm but professional
- Reference the lead's specific project type and location if available
- If the lead has a high quality score (7+), write as if addressing a VIP prospect
- If their location matches a known project area, mention relevant project experience there
- Emphasize Ofir's expertise in high-end residential projects
- Include a clear call to action (schedule a free consultation)
- Be 3-5 sentences long
- Use the lead's first name

Respond with ONLY the message text in Hebrew, no JSON or other formatting."""


class FunnelAutomationAgent(BaseAgent):
    """Manages automated follow-up sequences across email and WhatsApp."""

    def __init__(self):
        super().__init__(name="FunnelAutomation")
        self.email_service = EmailService()
        self.whatsapp_service = WhatsAppService()
        self.ai = OpenAIService()

    def run(self, lead_id: str = None, action: str = "process_new", **kwargs) -> Dict[str, Any]:
        """
        Execute funnel automation.
        Actions:
            - 'process_new': Send welcome sequence for a new lead
            - 'followup':    Send follow-up for leads that need it
            - 'process_all': Process all leads needing follow-ups
        """
        if action == "process_new" and lead_id:
            return self._process_new_lead(lead_id)
        elif action == "followup" and lead_id:
            return self._send_followup(lead_id)
        elif action == "process_all":
            return self._process_all_pending()
        else:
            return {"success": False, "errors": ["Invalid action or missing lead_id"]}

    def _process_new_lead(self, lead_id: str) -> Dict[str, Any]:
        """Send welcome email + WhatsApp for a newly captured lead."""
        session = get_session()
        try:
            lead = session.query(Lead).filter_by(id=lead_id).first()
            if not lead:
                return {"success": False, "errors": [f"Lead {lead_id} not found"]}

            results = {"email": None, "whatsapp": None}

            # 1. Welcome email
            if self.config.AUTO_FOLLOWUP:
                email_body = self._get_welcome_email(lead)
                email_result = self.email_service.send(
                    to_email=lead.email,
                    subject="תודה על פנייתך - אופיר אסולין עיצוב פנים",
                    body_html=email_body,
                    body_text=email_body,
                )
                results["email"] = email_result

                # Log interaction
                session.add(Interaction(
                    lead_id=lead.id,
                    channel="email",
                    interaction_type="welcome_email",
                    content=email_body[:500],
                    status="sent" if email_result.get("success") else "failed",
                ))

            # 2. WhatsApp message
            if self.config.AUTO_FOLLOWUP:
                wa_message = self._get_whatsapp_message(lead)
                wa_result = self.whatsapp_service.send(
                    to_phone=lead.phone,
                    message=wa_message,
                )
                results["whatsapp"] = wa_result

                session.add(Interaction(
                    lead_id=lead.id,
                    channel="whatsapp",
                    interaction_type="welcome_whatsapp",
                    content=wa_message[:500],
                    status="sent" if wa_result.get("success") else "failed",
                ))

            session.commit()
            self.logger.info(f"Welcome sequence sent for lead {lead_id}")
            return {"success": True, "lead_id": lead_id, "results": results}

        except Exception as e:
            session.rollback()
            self.logger.error(f"Error processing new lead {lead_id}: {e}")
            return {"success": False, "errors": [str(e)]}
        finally:
            session.close()

    def _send_followup(self, lead_id: str) -> Dict[str, Any]:
        """Send a follow-up message to a lead."""
        session = get_session()
        try:
            lead = session.query(Lead).filter_by(id=lead_id).first()
            if not lead:
                return {"success": False, "errors": [f"Lead {lead_id} not found"]}

            # Count previous follow-ups
            followup_count = (
                session.query(Interaction)
                .filter_by(lead_id=lead_id)
                .filter(Interaction.interaction_type.like("followup_%"))
                .count()
            )

            # Score-based cadence: hot leads (score 7+) get up to 4 follow-ups
            is_hot = (lead.quality_score or 0) >= 7
            max_followups = 4 if is_hot else 3

            if followup_count >= max_followups:
                self.logger.info(f"Lead {lead_id} has received max follow-ups ({followup_count}/{max_followups})")
                return {"success": True, "message": "Max follow-ups reached", "count": followup_count}

            # Generate personalized follow-up
            message = self._get_followup_message(lead, followup_count + 1)

            # Send via email
            email_result = self.email_service.send(
                to_email=lead.email,
                subject=self._get_followup_subject(followup_count + 1),
                body_html=message,
                body_text=message,
            )

            session.add(Interaction(
                lead_id=lead.id,
                channel="email",
                interaction_type=f"followup_{followup_count + 1}",
                content=message[:500],
                status="sent" if email_result.get("success") else "failed",
            ))

            session.commit()
            self.logger.info(f"Follow-up {followup_count + 1} sent for lead {lead_id}")
            return {
                "success": True,
                "lead_id": lead_id,
                "followup_number": followup_count + 1,
                "email_result": email_result,
            }

        except Exception as e:
            session.rollback()
            self.logger.error(f"Error sending follow-up for {lead_id}: {e}")
            return {"success": False, "errors": [str(e)]}
        finally:
            session.close()

    def _process_all_pending(self) -> Dict[str, Any]:
        """Find and process all leads that need follow-ups."""
        session = get_session()
        try:
            # Get leads in 'new' or 'contacted' status (still in pipeline)
            pending_leads = (
                session.query(Lead)
                .filter(Lead.status.in_(["new", "contacted"]))
                .all()
            )
            lead_ids = [l.id for l in pending_leads]
        finally:
            session.close()

        results = []
        for lid in lead_ids:
            result = self._send_followup(lid)
            results.append(result)

        sent = sum(1 for r in results if r.get("success"))
        return {
            "success": True,
            "total_pending": len(lead_ids),
            "followups_sent": sent,
            "results": results,
        }

    # --- Message Generation ---

    def _build_lead_context(self, lead: Lead) -> str:
        """Build rich lead context for AI personalization, including segment match."""
        from config import Config
        segment = Config.get_segment_for_project_type(lead.project_type)
        segment_info = ""
        if segment:
            segment_info = (
                f"- Segment: {segment['name']} ({segment['name_en']})\n"
                f"- Segment pain points: {', '.join(segment['pain_points'])}\n"
                f"- Segment key message: {segment['key_message']}\n"
            )

        score_info = ""
        if lead.quality_score:
            priority = "VIP/high-priority" if lead.quality_score >= 7 else ("medium" if lead.quality_score >= 5 else "nurture")
            score_info = f"- Quality Score: {lead.quality_score}/10 ({priority})\n"
            if lead.score_reasoning:
                score_info += f"- Score Reasoning: {lead.score_reasoning}\n"

        return (
            f"- Name: {lead.name}\n"
            f"- Location: {lead.location or 'Not specified'}\n"
            f"- Project Type: {lead.project_type or 'Not specified'}\n"
            f"- Budget: {lead.budget or 'Not specified'}\n"
            f"- Source: {lead.source}\n"
            f"- Campaign: {lead.campaign or 'Not specified'}\n"
            f"{score_info}"
            f"{segment_info}"
        )

    def _get_welcome_email(self, lead: Lead) -> str:
        """Generate welcome email, personalized with AI if available."""
        if self.ai.is_available():
            lead_context = self._build_lead_context(lead)
            personalized = self.ai.chat(
                system_prompt=PERSONALIZATION_PROMPT,
                user_message=f"Write a welcome email for:\n{lead_context}",
            )
            if personalized:
                return personalized

        # Fallback template
        first_name = lead.name.split()[0] if lead.name else ""
        return f"""שלום {first_name},

תודה על פנייתך לסטודיו של אופיר אסולין עיצוב פנים ואמנות.

אני שמחה להכיר אותך ולהבין את החזון שלך לבית שלך.

כמעצבת פנים עם ניסיון של שנים, אני מתמחה ביצירת מרחבים אישיים ומותאמים בדיוק לצרכים שלך.

בהמשך אשלח לך:
📥 מדריך חינמי: "5 שאלות שחייבים לשאול לפני תחילת שיפוץ"
📅 אפשרות לקביעת שיחת ייעוץ חינמית

בינתיים, אני מזמינה אותך להכיר את העבודות שלנו:
{self.config.BUSINESS_WEBSITE}

בברכה,
אופיר אסולין
מעצבת פנים ואמנית
{self.config.BUSINESS_PHONE}
{self.config.BUSINESS_EMAIL}"""

    def _get_whatsapp_message(self, lead: Lead) -> str:
        """Generate WhatsApp welcome message with full lead context."""
        first_name = lead.name.split()[0] if lead.name else ""

        if self.ai.is_available():
            lead_context = self._build_lead_context(lead)
            personalized = self.ai.chat(
                system_prompt=(
                    "Write a short WhatsApp welcome message in Hebrew (2-3 sentences) "
                    "for Ofir Assulin Interior Design. Be warm and professional. "
                    "Reference their specific project/location if available. "
                    "Include a call to schedule a phone call. Respond with ONLY the message text."
                ),
                user_message=f"Lead details:\n{lead_context}",
            )
            if personalized:
                return personalized

        return f"""שלום {first_name} 👋

תודה על פנייתך לסטודיו של אופיר אסולין עיצוב פנים!

אני רוצה לספר לך קצת על התהליך שלנו:
✨ ליווי מקצועי משלב התכנון ועד ההלבשה הסופית
✨ בניית קונספט עיצובי מותאם אישית
✨ ניהול פרויקט מלא כולל בקרת איכות

האם תרצה לקבוע שיחה טלפונית קצרה כדי להבין טוב יותר את הצרכים שלך?

אופיר אסולין
{self.config.BUSINESS_PHONE}"""

    def _get_followup_message(self, lead: Lead, followup_number: int) -> str:
        """Generate follow-up message based on sequence number and lead quality."""
        first_name = lead.name.split()[0] if lead.name else ""
        is_hot = (lead.quality_score or 0) >= 7

        if self.ai.is_available():
            lead_context = self._build_lead_context(lead)
            tone_guide = ""
            if followup_number == 1:
                tone_guide = "Be gentle and offer value — share a relevant case study or tip."
            elif followup_number == 2:
                tone_guide = "Add urgency — limited consultation slots this month."
            elif followup_number == 3:
                tone_guide = "Final follow-up — respectful last chance before closing."

            if is_hot:
                tone_guide += " This is a HIGH-PRIORITY lead — treat them as a VIP. Be more personal and specific."

            personalized = self.ai.chat(
                system_prompt=PERSONALIZATION_PROMPT,
                user_message=(
                    f"Write follow-up #{followup_number} for:\n{lead_context}\n"
                    f"This is follow-up #{followup_number} of 3. {tone_guide}"
                ),
            )
            if personalized:
                return personalized

        # Fallback templates by sequence number
        templates = {
            1: f"""שלום {first_name},

רציתי לוודא שקיבלת את המדריך ששלחנו.

יש לך שאלות לגבי התהליך? אשמח לעזור.

ניתן לקבוע שיחת ייעוץ חינמית כאן: {self.config.BUSINESS_WEBSITE}

אופיר אסולין
{self.config.BUSINESS_PHONE}""",
            2: f"""שלום {first_name},

רציתי לשתף אותך שיש לנו מספר מוגבל של פגישות ייעוץ חינמיות החודש.

אם את/ה מתכננים שיפוץ או בנייה - זה הזמן המושלם להתחיל לתכנן.

אשמח לשמוע על הפרויקט שלך: {self.config.BUSINESS_PHONE}

אופיר אסולין""",
            3: f"""שלום {first_name},

זו ההודעה האחרונה שלי - לא רציתי להפריע יותר מדי.

אם בעתיד תצטרכו עזרה בעיצוב פנים, אני תמיד כאן.

בהצלחה עם הפרויקט! 🏠

אופיר אסולין
{self.config.BUSINESS_PHONE}
{self.config.BUSINESS_WEBSITE}""",
            4: f"""שלום {first_name},

חשבתי עליכם ורציתי לשתף פרויקט שהשלמנו לאחרונה באזור שלכם — אולי יתן לכם השראה.

אני עדיין כאן אם תרצו לדבר על הפרויקט שלכם. שיחת ייעוץ חינמית תמיד פתוחה.

אופיר אסולין
{self.config.BUSINESS_PHONE}
{self.config.BUSINESS_WEBSITE}""",
        }
        return templates.get(followup_number, templates[1])

    def _get_followup_subject(self, followup_number: int) -> str:
        """Get email subject for follow-up number."""
        subjects = {
            1: "קיבלת את המדריך? - אופיר אסולין עיצוב פנים",
            2: "מספר מוגבל של פגישות ייעוץ חינמיות - אופיר אסולין",
            3: "תודה על ההתעניינות - אופיר אסולין עיצוב פנים",
            4: "פרויקט שיכול לתת לכם השראה - אופיר אסולין",
        }
        return subjects.get(followup_number, subjects[1])

    def get_lead_interactions(self, lead_id: str) -> List[dict]:
        """Get all interactions for a specific lead."""
        session = get_session()
        try:
            interactions = (
                session.query(Interaction)
                .filter_by(lead_id=lead_id)
                .order_by(Interaction.created_at.desc())
                .all()
            )
            return [i.to_dict() for i in interactions]
        finally:
            session.close()

    def health_check(self) -> Dict[str, Any]:
        return {
            "healthy": True,
            "email_configured": self.email_service.is_available(),
            "whatsapp_configured": self.whatsapp_service.is_available(),
            "ai_personalization": self.ai.is_available(),
        }
