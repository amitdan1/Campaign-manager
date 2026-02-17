"""
Lead Capture Agent (pure automation).
Receives leads from webhooks, forms, and API integrations.
Validates data, deduplicates, and stores in the database.
"""

import re
from datetime import datetime
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent
from models.lead import Lead
from models.interaction import Interaction
from services.database import get_session


class LeadCaptureAgent(BaseAgent):
    """Handles all lead intake from any source."""

    def __init__(self):
        super().__init__(name="LeadCapture")

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Capture a new lead.
        Expected kwargs: name, phone, email, source, campaign,
                         location (opt), budget (opt), project_type (opt)
        """
        # Validate required fields
        errors = self._validate(kwargs)
        if errors:
            return {"success": False, "errors": errors}

        # Normalize data
        data = self._normalize(kwargs)

        # Check for duplicates
        session = get_session()
        try:
            duplicate = self._find_duplicate(session, data["phone"], data["email"])
            if duplicate:
                self.logger.info(
                    f"Duplicate lead detected: {duplicate.id} "
                    f"(phone={data['phone']}, email={data['email']})"
                )
                return {
                    "success": False,
                    "duplicate": True,
                    "existing_lead_id": duplicate.id,
                    "message": "Lead already exists",
                }

            # Create lead
            lead = Lead(
                id=self._generate_id(),
                name=data["name"],
                phone=data["phone"],
                email=data["email"],
                source=data["source"],
                campaign=data.get("campaign", ""),
                status="new",
                location=data.get("location"),
                budget=data.get("budget"),
                project_type=data.get("project_type"),
                notes=data.get("notes"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            session.add(lead)

            # Log the capture interaction
            interaction = Interaction(
                lead_id=lead.id,
                channel=data["source"],
                interaction_type="lead_captured",
                content=f"Lead captured from {data['source']} via {data.get('campaign', 'direct')}",
                status="completed",
            )
            session.add(interaction)
            session.commit()

            self.logger.info(f"New lead captured: {lead.id} - {lead.name} from {lead.source}")
            return {
                "success": True,
                "lead_id": lead.id,
                "lead": lead.to_dict(),
            }

        except Exception as e:
            session.rollback()
            self.logger.error(f"Error capturing lead: {e}")
            return {"success": False, "errors": [str(e)]}
        finally:
            session.close()

    def update_status(self, lead_id: str, status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Update a lead's status."""
        valid_statuses = ["new", "contacted", "qualified", "consultation_booked", "converted", "lost"]
        if status not in valid_statuses:
            return {"success": False, "errors": [f"Invalid status. Must be one of: {valid_statuses}"]}

        session = get_session()
        try:
            lead = session.query(Lead).filter_by(id=lead_id).first()
            if not lead:
                return {"success": False, "errors": [f"Lead {lead_id} not found"]}

            old_status = lead.status
            lead.status = status
            if notes:
                lead.notes = notes
            lead.updated_at = datetime.utcnow()

            # Log status change
            interaction = Interaction(
                lead_id=lead_id,
                channel="system",
                interaction_type="status_change",
                content=f"Status changed from '{old_status}' to '{status}'" + (f". Notes: {notes}" if notes else ""),
                status="completed",
            )
            session.add(interaction)
            session.commit()

            self.logger.info(f"Lead {lead_id} status: {old_status} -> {status}")
            return {"success": True, "lead": lead.to_dict()}

        except Exception as e:
            session.rollback()
            self.logger.error(f"Error updating lead status: {e}")
            return {"success": False, "errors": [str(e)]}
        finally:
            session.close()

    def get_leads(
        self,
        status: Optional[str] = None,
        source: Optional[str] = None,
        min_score: Optional[int] = None,
    ) -> list:
        """Retrieve leads with optional filters."""
        session = get_session()
        try:
            query = session.query(Lead)
            if status:
                query = query.filter(Lead.status == status)
            if source:
                query = query.filter(Lead.source == source)
            if min_score is not None:
                query = query.filter(Lead.quality_score >= min_score)
            query = query.order_by(Lead.created_at.desc())
            return [lead.to_dict() for lead in query.all()]
        finally:
            session.close()

    def get_lead(self, lead_id: str) -> Optional[dict]:
        """Get a single lead by ID."""
        session = get_session()
        try:
            lead = session.query(Lead).filter_by(id=lead_id).first()
            return lead.to_dict() if lead else None
        finally:
            session.close()

    def health_check(self) -> Dict[str, Any]:
        """Check database connectivity."""
        session = get_session()
        try:
            count = session.query(Lead).count()
            return {"healthy": True, "total_leads": count}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
        finally:
            session.close()

    # --- Private helpers ---

    def _validate(self, data: dict) -> list:
        """Validate lead data. Returns list of error messages."""
        errors = []
        if not data.get("name") or not data["name"].strip():
            errors.append("Name is required")
        if not data.get("phone") or not data["phone"].strip():
            errors.append("Phone is required")
        if not data.get("email") or not data["email"].strip():
            errors.append("Email is required")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
            errors.append("Invalid email format")
        if not data.get("source"):
            errors.append("Source is required")
        return errors

    def _normalize(self, data: dict) -> dict:
        """Clean and normalize lead data."""
        normalized = {}
        normalized["name"] = data["name"].strip()
        normalized["phone"] = re.sub(r"[^\d+\-]", "", data["phone"])
        normalized["email"] = data["email"].strip().lower()
        normalized["source"] = data.get("source", "organic").strip().lower()
        normalized["campaign"] = data.get("campaign", "").strip()
        normalized["location"] = data.get("location", "").strip() if data.get("location") else None
        normalized["budget"] = data.get("budget", "").strip() if data.get("budget") else None
        normalized["project_type"] = data.get("project_type", "").strip() if data.get("project_type") else None
        normalized["notes"] = data.get("notes", "").strip() if data.get("notes") else None
        return normalized

    def _find_duplicate(self, session, phone: str, email: str) -> Optional[Lead]:
        """Check if a lead with the same phone or email already exists."""
        return (
            session.query(Lead)
            .filter((Lead.phone == phone) | (Lead.email == email))
            .first()
        )

    def _generate_id(self) -> str:
        """Generate a unique lead ID."""
        return f"L{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
