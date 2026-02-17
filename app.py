"""
Web Application for Performance Marketing System
Flask-based UI backed by the multi-agent architecture.
"""

import csv
import io
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

from config import Config
from agents.orchestrator import AgentOrchestrator
from services.validation import (
    validate_status_transition, validate_lead_input,
    validate_proposal_input, chat_limiter, api_limiter,
)

# --- App Setup ---
app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH

CORS(app, origins=Config.ALLOWED_ORIGINS)

# --- Structured Logging ---
from services.logging_service import init_request_logging, get_logger
init_request_logging(app)
logger = get_logger(__name__)

orchestrator = AgentOrchestrator()

# --- Conversion Tracking ---
from services.conversion_tracking import conversion_tracker


def require_auth(f):
    """No-op auth decorator -- kept as a hook for future auth."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(f):
    """Rate-limit decorator for POST/PUT endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = f"{request.remote_addr or 'global'}:{request.endpoint}"
        if not api_limiter.is_allowed(key):
            return jsonify({"success": False, "error": "Rate limit exceeded. Try again shortly."}), 429
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# Error Handlers
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Not found"}), 404
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Internal server error"}), 500
    return render_template("errors/500.html"), 500


@app.errorhandler(413)
def request_too_large(e):
    return jsonify({"success": False, "error": "Request too large (max 2MB)"}), 413


# =============================================================================
# Pages
# =============================================================================

@app.route("/")
@require_auth
def index():
    return render_template("dashboard.html")


@app.route("/proposals")
@require_auth
def proposals_page():
    return render_template("proposals.html")


@app.route("/leads")
@require_auth
def leads_page():
    return render_template("leads.html")


@app.route("/campaigns")
@require_auth
def campaigns_page():
    return render_template("campaigns.html")


@app.route("/landing-pages")
@require_auth
def landing_pages_page():
    return render_template("landing_pages.html")


@app.route("/assets")
@require_auth
def assets_page():
    return render_template("assets.html")


@app.route("/agents")
@require_auth
def agents_page():
    return render_template("agents.html")


@app.route("/strategy")
@require_auth
def strategy_page():
    return render_template("strategy.html")


@app.route("/integrations")
@require_auth
def integrations_page():
    return render_template("integrations.html")


# =============================================================================
# Dashboard API
# =============================================================================

@app.route("/api/dashboard/stats")
@require_auth
def dashboard_stats():
    return jsonify(orchestrator.get_dashboard_stats(days=30))


# =============================================================================
# Proposals API
# =============================================================================

@app.route("/api/proposals", methods=["GET"])
@require_auth
def get_proposals():
    from services.database import get_session
    from models.proposal import Proposal

    status = request.args.get("status")
    proposal_type = request.args.get("proposal_type")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=50, type=int)
    per_page = min(per_page, 100)  # Cap at 100

    session = get_session()
    try:
        q = session.query(Proposal).order_by(Proposal.created_at.desc())
        if status:
            q = q.filter(Proposal.status == status)
        if proposal_type:
            q = q.filter(Proposal.proposal_type == proposal_type)
        total = q.count()
        proposals = [p.to_dict() for p in q.offset((page - 1) * per_page).limit(per_page).all()]
        return jsonify({
            "success": True, "proposals": proposals,
            "pagination": {"page": page, "per_page": per_page, "total": total, "pages": (total + per_page - 1) // per_page},
        })
    finally:
        session.close()


@app.route("/api/proposals/<int:proposal_id>", methods=["GET"])
@require_auth
def get_proposal(proposal_id):
    from services.database import get_session
    from models.proposal import Proposal

    session = get_session()
    try:
        p = session.query(Proposal).filter_by(id=proposal_id).first()
        if not p:
            return jsonify({"success": False, "error": "Not found"}), 404
        return jsonify({"success": True, "proposal": p.to_dict()})
    finally:
        session.close()


@app.route("/api/proposals", methods=["POST"])
@require_auth
@rate_limit
def create_proposal():
    from services.database import get_session
    from models.proposal import Proposal

    data = request.get_json()
    valid, errors = validate_proposal_input(data)
    if not valid:
        return jsonify({"success": False, "errors": errors}), 400

    session = get_session()
    try:
        p = Proposal(
            agent_name=data.get("agent_name", "manual"),
            proposal_type=data.get("proposal_type", "general"),
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            content=data.get("content", {}),
            status=data.get("status", "pending_review"),
        )
        session.add(p)
        session.commit()
        return jsonify({"success": True, "proposal": p.to_dict()}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
    finally:
        session.close()


@app.route("/api/proposals/<int:proposal_id>/status", methods=["PUT"])
@require_auth
@rate_limit
def update_proposal_status(proposal_id):
    from services.database import get_session
    from models.proposal import Proposal

    data = request.get_json()
    new_status = data.get("status")
    feedback = data.get("feedback")

    session = get_session()
    try:
        p = session.query(Proposal).filter_by(id=proposal_id).first()
        if not p:
            return jsonify({"success": False, "error": "Not found"}), 404

        # C3: Validate state transition
        valid, err_msg = validate_status_transition(p.status, new_status)
        if not valid:
            return jsonify({"success": False, "error": err_msg}), 400

        p.status = new_status
        p.updated_at = datetime.utcnow()

        if feedback:
            p.feedback = feedback
        if new_status == "approved":
            p.approved_at = datetime.utcnow()
        if new_status == "executing":
            p.executed_at = datetime.utcnow()

        session.commit()

        # C1: Record proposal outcome in agent memory
        try:
            from services.agent_memory import memory_service
            memory_service.record_proposal_outcome(
                agent_name=p.agent_name,
                proposal_title=p.title,
                status=new_status,
                feedback=feedback or "",
            )
        except Exception:
            pass

        # Trigger execution pipeline on approval
        pipeline_result = None
        if new_status == "approved":
            try:
                from agents.execution_pipeline import ExecutionPipeline
                pipeline = ExecutionPipeline(orchestrator)
                pipeline_result = pipeline.on_proposal_approved(proposal_id)
            except Exception as ex:
                pipeline_result = {"error": str(ex)}

        result = {"success": True, "proposal": p.to_dict()}
        if pipeline_result:
            result["pipeline"] = pipeline_result
        return jsonify(result)
    except Exception as e:
        session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
    finally:
        session.close()


@app.route("/api/landing-pages/generate", methods=["POST"])
@require_auth
@rate_limit
def generate_landing_page():
    """Generate a new landing page via the LandingPageAgent."""
    data = request.get_json()
    result = orchestrator.landing_page.run(
        campaign_name=data.get("campaign_name", ""),
        campaign_details=data.get("campaign_details", ""),
        variant=data.get("variant", ""),
    )
    return jsonify(result), 201 if result.get("success") else 400


@app.route("/api/proposals/<int:proposal_id>/preview")
@require_auth
def proposal_preview_html(proposal_id):
    """Return raw HTML content for iframe rendering."""
    from services.database import get_session
    from models.proposal import Proposal

    session = get_session()
    try:
        p = session.query(Proposal).filter_by(id=proposal_id).first()
        if not p or not p.content:
            return "Not found", 404
        html = p.content.get("html", "")
        if not html:
            return "No HTML content", 404
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    finally:
        session.close()


@app.route("/landing-pages/<int:proposal_id>/preview")
def landing_page_standalone(proposal_id):
    """Serve landing page as standalone page (for sharing/testing)."""
    from services.database import get_session
    from models.proposal import Proposal

    session = get_session()
    try:
        p = session.query(Proposal).filter_by(id=proposal_id).first()
        if not p or not p.content:
            return "Not found", 404
        html = p.content.get("html", "")
        if not html:
            return "No HTML content", 404
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    finally:
        session.close()


@app.route("/api/pipeline/weekly", methods=["POST"])
@require_auth
@rate_limit
def trigger_weekly_cycle():
    """Trigger the full weekly autonomous cycle."""
    from agents.execution_pipeline import ExecutionPipeline
    pipeline = ExecutionPipeline(orchestrator)
    result = pipeline.run_weekly_cycle()
    return jsonify(result)


# =============================================================================
# Chat API
# =============================================================================

@app.route("/api/chat", methods=["POST"])
@require_auth
@rate_limit
def chat():
    from services.database import get_session
    from models.chat_message import ChatMessage
    from services.openai_service import OpenAIService

    data = request.get_json()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"success": False, "error": "Empty message"}), 400

    if not chat_limiter.is_allowed(request.remote_addr or "global"):
        return jsonify({"success": False, "error": "Rate limit exceeded. Try again in a minute."}), 429

    session = get_session()
    try:
        # Store user message
        user_msg = ChatMessage(role="user", content=message)
        session.add(user_msg)

        # Generate agent response
        ai = OpenAIService()
        if ai.is_available():
            from prompts import load_prompt
            response_text = ai.chat(
                system_prompt=load_prompt("orchestrator", "chat_system"),
                user_message=message,
                temperature=0.5,
            )
        else:
            response_text = (
                "שלום! אני מנהל הסוכנים. כרגע מפתח OpenAI לא מוגדר, "
                "אז אני עובד במצב בסיסי. הגדר OPENAI_API_KEY בקובץ .env "
                "כדי לקבל תשובות חכמות. בינתיים, אפשר להשתמש בלוח ההצעות ובדשבורד."
            )

        # Store agent response
        agent_msg = ChatMessage(role="agent", agent_name="Orchestrator", content=response_text)
        session.add(agent_msg)
        session.commit()

        return jsonify({
            "success": True,
            "response": response_text,
            "agent": "Orchestrator",
        })
    except Exception as e:
        session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        session.close()


@app.route("/api/chat/history", methods=["GET"])
@require_auth
def chat_history():
    from services.database import get_session
    from models.chat_message import ChatMessage

    session = get_session()
    try:
        messages = (
            session.query(ChatMessage)
            .order_by(ChatMessage.created_at.desc())
            .limit(50)
            .all()
        )
        return jsonify({
            "success": True,
            "messages": [m.to_dict() for m in reversed(messages)],
        })
    finally:
        session.close()


# =============================================================================
# Brand Assets API
# =============================================================================

@app.route("/api/assets", methods=["GET"])
@require_auth
def get_assets():
    from services.database import get_session
    from models.brand_asset import BrandAsset

    source = request.args.get("source")
    asset_type = request.args.get("type")

    session = get_session()
    try:
        q = session.query(BrandAsset).order_by(BrandAsset.created_at.desc())
        if source:
            q = q.filter(BrandAsset.source == source)
        if asset_type:
            q = q.filter(BrandAsset.asset_type == asset_type)
        assets = [a.to_dict() for a in q.all()]
        return jsonify({"success": True, "assets": assets, "count": len(assets)})
    finally:
        session.close()


@app.route("/api/assets/scrape", methods=["POST"])
@require_auth
@rate_limit
def scrape_assets():
    try:
        result = orchestrator.brand_scraper.run()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# Agents Status API
# =============================================================================

@app.route("/api/agents/status")
@require_auth
def agents_status():
    agents_info = [
        {"name": "LeadCapture", "description": "קליטת לידים, ולידציה, ומניעת כפילויות", "type": "Automation"},
        {"name": "LeadScoring", "description": "ניקוד לידים מבוסס AI עם נימוק", "type": "LLM"},
        {"name": "FunnelAutomation", "description": "רצפי מיילים ו-WhatsApp אוטומטיים", "type": "Hybrid"},
        {"name": "CampaignTracking", "description": "שליפת מדדים מ-Google Ads ו-Facebook", "type": "Automation"},
        {"name": "ContentCreative", "description": "יצירת קופי, מודעות ותוכן בעברית", "type": "LLM"},
        {"name": "BrandScraper", "description": "איסוף תמונות וסגנון מהנוכחות הדיגיטלית", "type": "Automation"},
        {"name": "Strategy", "description": "תכנון אסטרטגי ויצירת תוכניות שבועיות", "type": "LLM"},
        {"name": "LandingPage", "description": "בניית דפי נחיתה בסגנון המותג", "type": "LLM"},
        {"name": "CampaignManager", "description": "הרכבת קמפיינים מלאים עם טרגוט ותקציב", "type": "LLM"},
        {"name": "BudgetOptimizer", "description": "אופטימיזציית תקציב ומעקב אחר ביצועים", "type": "LLM"},
    ]

    # Get health from available agents
    health_data = {}
    try:
        health_data = orchestrator.health_check().get("agents", {})
    except Exception:
        pass

    for a in agents_info:
        key = a["name"].lower().replace(" ", "_")
        h = health_data.get(key, health_data.get(a["name"].lower(), {}))
        a["healthy"] = h.get("healthy", True)
        a["details"] = {k: v for k, v in h.items() if k != "healthy"}

    return jsonify({"success": True, "agents": agents_info})


# =============================================================================
# Leads API
# =============================================================================

@app.route("/api/leads", methods=["GET"])
@require_auth
def get_leads_api():
    status = request.args.get("status")
    source = request.args.get("source")
    min_score = request.args.get("min_score", type=int)
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=50, type=int)
    per_page = min(per_page, 100)

    leads = orchestrator.lead_capture.get_leads(status=status, source=source, min_score=min_score)
    for lead in leads:
        lead["timestamp"] = lead.get("created_at", "")

    total = len(leads)
    start = (page - 1) * per_page
    paginated = leads[start:start + per_page]
    return jsonify({
        "success": True, "count": total, "leads": paginated,
        "pagination": {"page": page, "per_page": per_page, "total": total, "pages": (total + per_page - 1) // per_page},
    })


@app.route("/api/leads", methods=["POST"])
@require_auth
@rate_limit
def add_lead_api():
    data = request.get_json()
    valid, errors = validate_lead_input(data)
    if not valid:
        return jsonify({"success": False, "errors": errors}), 400

    try:
        result = orchestrator.capture_and_score_lead(
            name=data.get("name"),
            phone=data.get("phone"),
            email=data.get("email"),
            source=data.get("source", "organic"),
            campaign=data.get("campaign", "manual"),
            location=data.get("location"),
            budget=data.get("budget"),
            project_type=data.get("project_type"),
        )
        if result.get("success"):
            # Fire server-side Lead conversion event to ad networks
            try:
                conversion_tracker.send_lead_event(
                    lead_data=data,
                    source_url=request.referrer or "",
                )
            except Exception:
                pass

            return jsonify({
                "success": True,
                "lead": {
                    "id": result["lead_id"],
                    "name": result["lead"].get("name"),
                    "quality_score": result["scoring"].get("score"),
                    "score_reasoning": result["scoring"].get("reasoning"),
                    "status": result["lead"].get("status"),
                },
            }), 201
        else:
            errors = result.get("errors", [])
            msg = result.get("message", "; ".join(errors) if errors else "Unknown error")
            return jsonify({"success": False, "error": msg}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/leads/<lead_id>/status", methods=["PUT"])
@require_auth
@rate_limit
def update_lead_status_api(lead_id):
    data = request.get_json()
    new_status = data.get("status")
    result = orchestrator.lead_capture.update_status(lead_id, new_status, data.get("notes"))
    if result.get("success"):
        # Fire downstream conversion events for milestone statuses
        if new_status in ("consultation_booked", "converted"):
            try:
                from services.database import get_session as _get_session
                from models.lead import Lead as _Lead
                _session = _get_session()
                try:
                    _lead = _session.query(_Lead).filter_by(id=lead_id).first()
                    if _lead:
                        conversion_tracker.send_status_event(
                            status=new_status,
                            lead_data={
                                "name": _lead.name,
                                "email": _lead.email,
                                "phone": _lead.phone,
                            },
                        )
                finally:
                    _session.close()
            except Exception:
                pass

        return jsonify({"success": True}), 200
    return jsonify({"success": False, "error": "; ".join(result.get("errors", []))}), 400


# =============================================================================
# Campaigns API
# =============================================================================

@app.route("/api/campaigns", methods=["GET"])
@require_auth
def get_campaigns_api():
    from services.database import get_session
    from models.campaign import Campaign

    days = request.args.get("days", default=30, type=int)
    cutoff = datetime.utcnow() - timedelta(days=days)
    session = get_session()
    try:
        campaigns = session.query(Campaign).filter(Campaign.date >= cutoff).all()
        return jsonify({"success": True, "count": len(campaigns), "campaigns": [c.to_dict() for c in campaigns]})
    finally:
        session.close()


@app.route("/api/campaigns/metrics", methods=["POST"])
@require_auth
@rate_limit
def add_campaign_metrics_api():
    from services.database import get_session
    from models.campaign import Campaign

    data = request.get_json()
    impressions = data.get("impressions", 0)
    clicks = data.get("clicks", 0)
    conversions = data.get("conversions", 0)
    cost = data.get("cost", 0)

    ctr = (clicks / impressions * 100) if impressions > 0 else 0
    conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
    cpl = (cost / conversions) if conversions > 0 else 0

    session = get_session()
    try:
        campaign = Campaign(
            campaign_id=data.get("campaign_id", ""),
            campaign_name=data.get("campaign_name", ""),
            platform=data.get("platform", ""),
            impressions=impressions, clicks=clicks,
            conversions=conversions, cost=cost,
            cpl=cpl, ctr=ctr, conversion_rate=conversion_rate,
        )
        session.add(campaign)
        session.commit()
        return jsonify({"success": True, "metrics": {"cpl": cpl, "ctr": ctr, "conversion_rate": conversion_rate}}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
    finally:
        session.close()


# =============================================================================
# Recommendations API
# =============================================================================

@app.route("/api/recommendations", methods=["GET"])
@require_auth
def get_recommendations():
    try:
        ai_recs = orchestrator.optimization.run()
        campaign_recs = ai_recs.get("recommendations", [])
    except Exception:
        campaign_recs = []

    strategy_recs = [
        {"action": "focus", "campaign": f"Google Ads (₪{Config.BUDGET_GOOGLE_ADS}/month)", "reason": f"Allocate 60% of ₪{Config.BUDGET_TOTAL} budget to high-intent Google search keywords", "priority": "high"},
        {"action": "optimize", "campaign": f"Facebook/Instagram (₪{Config.BUDGET_FACEBOOK}/month)", "reason": "Use remaining 40% for targeted lead gen with native forms", "priority": "high"},
        {"action": "target", "campaign": "Geographic Targeting", "reason": "Limit ads to central Israel only (Herzliya, Tel Aviv, Ramat Hasharon)", "priority": "medium"},
    ]

    return jsonify({"success": True, "campaign_recommendations": campaign_recs, "strategy_recommendations": strategy_recs})


# =============================================================================
# Export API
# =============================================================================

@app.route("/api/export/leads")
@require_auth
def export_leads():
    format_type = request.args.get("format", "csv")
    status = request.args.get("status")
    leads = orchestrator.lead_capture.get_leads(status=status)

    if format_type == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Name", "Phone", "Email", "Source", "Campaign", "Status", "Quality Score", "Score Reasoning", "Location", "Budget", "Project Type", "Created At", "Notes"])
        for lead in leads:
            writer.writerow([lead.get("id"), lead.get("name"), lead.get("phone"), lead.get("email"), lead.get("source"), lead.get("campaign"), lead.get("status"), lead.get("quality_score", ""), lead.get("score_reasoning", ""), lead.get("location", ""), lead.get("budget", ""), lead.get("project_type", ""), lead.get("created_at", ""), lead.get("notes", "")])
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode("utf-8-sig")), mimetype="text/csv", as_attachment=True, download_name=f'leads_{datetime.now().strftime("%Y%m%d")}.csv')
    elif format_type == "json":
        return jsonify({"success": True, "leads": leads, "count": len(leads)})
    return jsonify({"success": False, "error": "Invalid format"}), 400


# =============================================================================
# Integrations API
# =============================================================================

@app.route("/api/integrations", methods=["GET"])
@require_auth
def get_integrations():
    from services.integration_manager import IntegrationManager
    mgr = IntegrationManager()
    return jsonify({"success": True, "integrations": mgr.get_all_statuses()})


@app.route("/api/integrations/save", methods=["POST"])
@require_auth
@rate_limit
def save_integration_keys():
    from services.integration_manager import IntegrationManager
    data = request.get_json()
    integration_id = data.get("integration_id")
    fields = data.get("fields", {})

    if not integration_id:
        return jsonify({"success": False, "error": "Missing integration_id"}), 400
    if not fields:
        return jsonify({"success": False, "error": "No fields provided"}), 400

    mgr = IntegrationManager()
    result = mgr.save_keys(integration_id, fields)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/api/integrations/test", methods=["POST"])
@require_auth
@rate_limit
def test_integration_connection():
    from services.integration_manager import IntegrationManager
    data = request.get_json()
    integration_id = data.get("integration_id")

    if not integration_id:
        return jsonify({"success": False, "message": "Missing integration_id"}), 400

    mgr = IntegrationManager()
    result = mgr.test_connection(integration_id)
    return jsonify(result)


# =============================================================================
# Analytics API (enhanced charts)
# =============================================================================

@app.route("/api/analytics/trends", methods=["GET"])
@require_auth
def analytics_trends():
    """Return daily lead and spend trend data for the last 30 days."""
    from services.database import get_session
    from models.lead import Lead
    from models.campaign import Campaign
    from sqlalchemy import func

    days = request.args.get("days", default=30, type=int)
    cutoff = datetime.utcnow() - timedelta(days=days)
    session = get_session()
    try:
        # Daily lead counts
        lead_rows = (
            session.query(func.date(Lead.created_at).label("day"), func.count().label("cnt"))
            .filter(Lead.created_at >= cutoff)
            .group_by(func.date(Lead.created_at))
            .order_by(func.date(Lead.created_at))
            .all()
        )
        # Daily spend
        spend_rows = (
            session.query(func.date(Campaign.date).label("day"), func.sum(Campaign.cost).label("spend"))
            .filter(Campaign.date >= cutoff)
            .group_by(func.date(Campaign.date))
            .order_by(func.date(Campaign.date))
            .all()
        )
        return jsonify({
            "success": True,
            "leads_trend": [{"date": str(r.day), "count": r.cnt} for r in lead_rows],
            "spend_trend": [{"date": str(r.day), "spend": float(r.spend or 0)} for r in spend_rows],
        })
    finally:
        session.close()


@app.route("/api/analytics/funnel", methods=["GET"])
@require_auth
def analytics_funnel():
    """Return funnel data: leads -> contacted -> qualified -> consultation -> converted."""
    from services.database import get_session
    from models.lead import Lead
    from sqlalchemy import func

    session = get_session()
    try:
        counts = dict(
            session.query(Lead.status, func.count())
            .group_by(Lead.status)
            .all()
        )
        total = sum(counts.values())
        funnel = [
            {"stage": "לידים", "count": total},
            {"stage": "ליצרנו קשר", "count": counts.get("contacted", 0) + counts.get("qualified", 0) + counts.get("consultation_booked", 0) + counts.get("converted", 0)},
            {"stage": "מתאימים", "count": counts.get("qualified", 0) + counts.get("consultation_booked", 0) + counts.get("converted", 0)},
            {"stage": "פגישות", "count": counts.get("consultation_booked", 0) + counts.get("converted", 0)},
            {"stage": "המרות", "count": counts.get("converted", 0)},
        ]
        return jsonify({"success": True, "funnel": funnel})
    finally:
        session.close()


@app.route("/api/analytics/budget", methods=["GET"])
@require_auth
def analytics_budget():
    """Return budget allocation vs spend data."""
    from services.database import get_session
    from models.campaign import Campaign
    from sqlalchemy import func

    session = get_session()
    try:
        spend_by_platform = dict(
            session.query(Campaign.platform, func.sum(Campaign.cost))
            .group_by(Campaign.platform)
            .all()
        )
        return jsonify({
            "success": True,
            "allocated": {"google": Config.BUDGET_GOOGLE_ADS, "facebook": Config.BUDGET_FACEBOOK},
            "spent": {k: float(v or 0) for k, v in spend_by_platform.items()},
            "total_budget": Config.BUDGET_TOTAL,
        })
    finally:
        session.close()


@app.route("/api/analytics/token-usage", methods=["GET"])
@require_auth
def analytics_token_usage():
    """Return OpenAI token usage stats."""
    from services.openai_service import OpenAIService
    return jsonify({"success": True, **OpenAIService.get_token_stats()})


# =============================================================================
# A/B Testing API
# =============================================================================

@app.route("/api/ab-tests", methods=["GET"])
@require_auth
def get_ab_tests():
    from services.ab_testing import ABTestingService
    svc = ABTestingService()
    return jsonify({"success": True, "tests": svc.get_all_tests()})


@app.route("/api/ab-tests", methods=["POST"])
@require_auth
@rate_limit
def create_ab_test():
    from services.ab_testing import ABTestingService
    data = request.get_json()
    svc = ABTestingService()
    result = svc.create_test(
        name=data.get("name", ""),
        variants=data.get("variants", []),
    )
    return jsonify(result), 201 if result.get("success") else 400


@app.route("/api/ab-tests/<int:test_id>", methods=["GET"])
@require_auth
def get_ab_test_results(test_id):
    from services.ab_testing import ABTestingService
    svc = ABTestingService()
    return jsonify(svc.get_test_results(test_id))


@app.route("/api/ab-tests/<int:test_id>/end", methods=["POST"])
@require_auth
@rate_limit
def end_ab_test(test_id):
    from services.ab_testing import ABTestingService
    svc = ABTestingService()
    return jsonify(svc.end_test(test_id))


# =============================================================================
# Webhooks (Meta Lead Ads, Google Lead Forms)
# =============================================================================

@app.route("/webhooks/meta/leads", methods=["GET", "POST"])
def meta_lead_webhook():
    """
    Meta (Facebook) Lead Ads webhook.
    GET: verification challenge for subscription setup.
    POST: incoming lead data from Meta Lead Ads.
    """
    if request.method == "GET":
        # Verification handshake
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        verify_token = Config.__dict__.get("META_WEBHOOK_VERIFY_TOKEN", "marketing-system-verify")
        if mode == "subscribe" and token == verify_token:
            logger.info("Meta webhook verified")
            return challenge, 200
        return "Forbidden", 403

    # POST: process incoming lead
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False}), 400

    logger.info(f"Meta webhook received: {data.get('object', 'unknown')}")
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "leadgen":
                    lead_data = change.get("value", {})
                    result = orchestrator.capture_and_score_lead(
                        name=lead_data.get("full_name", "Meta Lead"),
                        phone=lead_data.get("phone_number", ""),
                        email=lead_data.get("email", ""),
                        source="facebook",
                        campaign=lead_data.get("form_id", "meta_lead_ad"),
                    )
                    if result.get("success"):
                        try:
                            conversion_tracker.send_lead_event(lead_data={
                                "name": lead_data.get("full_name", ""),
                                "phone": lead_data.get("phone_number", ""),
                                "email": lead_data.get("email", ""),
                            })
                        except Exception:
                            pass
    except Exception as e:
        logger.error(f"Error processing Meta webhook: {e}")

    return jsonify({"success": True}), 200


@app.route("/webhooks/google/leads", methods=["POST"])
def google_lead_webhook():
    """
    Google Lead Form Extensions webhook.
    Receives lead data from Google Ads lead form extensions.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False}), 400

    logger.info("Google lead webhook received")
    try:
        lead_info = data.get("user_column_data", [])
        name = ""
        phone = ""
        email = ""
        for col in lead_info:
            col_id = col.get("column_id", "")
            val = col.get("string_value", "")
            if col_id == "FULL_NAME":
                name = val
            elif col_id == "PHONE_NUMBER":
                phone = val
            elif col_id == "EMAIL":
                email = val

        if name or phone:
            result = orchestrator.capture_and_score_lead(
                name=name or "Google Lead",
                phone=phone,
                email=email,
                source="google",
                campaign=data.get("campaign_id", "google_lead_form"),
            )
            if result.get("success"):
                try:
                    conversion_tracker.send_lead_event(lead_data={
                        "name": name, "phone": phone, "email": email,
                    })
                except Exception:
                    pass
    except Exception as e:
        logger.error(f"Error processing Google lead webhook: {e}")

    return jsonify({"success": True}), 200


# =============================================================================
# Health
# =============================================================================

@app.route("/api/health")
def health_check():
    return jsonify(orchestrator.health_check())


@app.route("/api/docs")
def api_docs():
    """Serve Swagger UI for the API documentation."""
    return """<!DOCTYPE html>
<html><head><title>API Docs</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head><body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>SwaggerUIBundle({url:'/static/openapi.yaml',dom_id:'#swagger-ui'})</script>
</body></html>""", 200, {"Content-Type": "text/html"}


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Performance Marketing System - Autonomous Agent Platform")
    print("=" * 60)
    print(f"Budget: ₪{Config.BUDGET_TOTAL}/month")
    print(f"OpenAI: {'configured' if Config.is_openai_configured() else 'NOT configured (rule-based mode)'}")
    print(f"Dashboard: http://localhost:5000")
    print("=" * 60)

    # Start background scheduler
    from services.scheduler import init_scheduler
    init_scheduler(app, orchestrator)

    app.run(host="0.0.0.0", port=5000, debug=Config.FLASK_DEBUG)
