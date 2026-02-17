"""
Performance Marketing Agent for Ofir Assulin Interior Design
Automated lead generation and campaign management system
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Lead:
    """Lead data structure"""
    id: str
    name: str
    phone: str
    email: str
    source: str  # 'google', 'facebook', 'instagram', 'organic'
    campaign: str
    timestamp: str
    status: str  # 'new', 'contacted', 'qualified', 'consultation_booked', 'converted', 'lost'
    budget: Optional[str] = None
    project_type: Optional[str] = None  # 'new_build', 'renovation', 'commercial'
    location: Optional[str] = None
    notes: Optional[str] = None
    quality_score: Optional[int] = None  # 1-10


@dataclass
class CampaignMetrics:
    """Campaign performance metrics"""
    campaign_id: str
    campaign_name: str
    platform: str  # 'google', 'facebook', 'instagram'
    date: str
    impressions: int
    clicks: int
    conversions: int
    cost: float
    cpl: float  # Cost per lead
    ctr: float  # Click-through rate
    conversion_rate: float


class MarketingAgent:
    """
    Main marketing agent that manages campaigns, leads, and automation
    """
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.leads_db = "leads.json"
        self.campaigns_db = "campaigns.json"
        self.leads = self._load_leads()
        self.campaigns = self._load_campaigns()
        
    def _load_config(self) -> Dict:
        """Load configuration file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default configuration"""
        config = {
            "business": {
                "name": "Ofir Assulin Interior Design",
                "phone": "052-626-9261",
                "email": "ofirassulin.design@gmail.com",
                "website": "https://www.ofirassulin.design/"
            },
            "target_audience": {
                "age_min": 35,
                "age_max": 55,
                "locations": ["תל אביב", "הרצליה", "רמת השרון", "כפר שמריהו", "סביון"],
                "min_budget": 500000
            },
            "budgets": {
                "google_ads_monthly": 300,  # 300 NIS/month
                "facebook_ads_monthly": 200,  # 200 NIS/month
                "instagram_ads_monthly": 0,
                "retargeting_monthly": 0,
                "total_monthly": 500,  # 500 NIS/month total
                "currency": "NIS"
            },
            "kpis": {
                "target_cpl": 200,  # Target CPL with 500 NIS budget
                "target_consultation_rate": 0.40,  # Higher rate needed with fewer leads
                "target_conversion_rate": 0.50,  # Higher conversion rate needed
                "target_cac": 300,  # Target CAC with 500 NIS budget
                "target_roas": 200  # Target ROAS (even 1 project = 200X+)
            },
            "automation": {
                "auto_followup": True,
                "followup_delay_hours": 2,
                "lead_scoring_enabled": True,
                "whatsapp_enabled": True,
                "email_enabled": True
            }
        }
        self._save_config(config)
        return config
    
    def _save_config(self, config: Dict):
        """Save configuration"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _load_leads(self) -> List[Lead]:
        """Load leads from database"""
        if os.path.exists(self.leads_db):
            with open(self.leads_db, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Lead(**lead) for lead in data]
        return []
    
    def _save_leads(self):
        """Save leads to database"""
        with open(self.leads_db, 'w', encoding='utf-8') as f:
            json.dump([asdict(lead) for lead in self.leads], f, ensure_ascii=False, indent=2)
    
    def _load_campaigns(self) -> List[CampaignMetrics]:
        """Load campaign metrics"""
        if os.path.exists(self.campaigns_db):
            with open(self.campaigns_db, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [CampaignMetrics(**campaign) for campaign in data]
        return []
    
    def _save_campaigns(self):
        """Save campaign metrics"""
        with open(self.campaigns_db, 'w', encoding='utf-8') as f:
            json.dump([asdict(campaign) for campaign in self.campaigns], f, ensure_ascii=False, indent=2)
    
    def add_lead(self, name: str, phone: str, email: str, source: str, 
                 campaign: str, **kwargs) -> Lead:
        """Add a new lead"""
        lead_id = f"L{datetime.now().strftime('%Y%m%d%H%M%S')}"
        lead = Lead(
            id=lead_id,
            name=name,
            phone=phone,
            email=email,
            source=source,
            campaign=campaign,
            timestamp=datetime.now().isoformat(),
            status='new',
            **kwargs
        )
        
        # Score the lead
        if self.config['automation']['lead_scoring_enabled']:
            lead.quality_score = self._score_lead(lead)
        
        self.leads.append(lead)
        self._save_leads()
        
        logger.info(f"New lead added: {lead_id} - {name} from {source}")
        
        # Trigger automation
        self._trigger_automation(lead)
        
        return lead
    
    def _score_lead(self, lead: Lead) -> int:
        """Score lead quality (1-10)"""
        score = 5  # Base score
        
        # Location scoring
        if lead.location:
            target_locations = self.config['target_audience']['locations']
            if any(loc in lead.location for loc in target_locations):
                score += 2
        
        # Budget scoring
        if lead.budget:
            try:
                budget_num = int(lead.budget.replace(',', '').replace('₪', ''))
                if budget_num >= self.config['target_audience']['min_budget']:
                    score += 2
                elif budget_num >= self.config['target_audience']['min_budget'] * 0.7:
                    score += 1
            except:
                pass
        
        # Project type scoring
        if lead.project_type in ['new_build', 'renovation']:
            score += 1
        
        # Source scoring
        if lead.source == 'google':
            score += 1  # Google leads are warmer
        
        return min(score, 10)
    
    def _trigger_automation(self, lead: Lead):
        """Trigger automated follow-up actions"""
        if not self.config['automation']['auto_followup']:
            return
        
        logger.info(f"Triggering automation for lead {lead.id}")
        
        # Schedule WhatsApp message
        if self.config['automation']['whatsapp_enabled']:
            self._schedule_whatsapp(lead)
        
        # Send email sequence
        if self.config['automation']['email_enabled']:
            self._send_welcome_email(lead)
        
        # Add to CRM (if integrated)
        self._add_to_crm(lead)
    
    def _schedule_whatsapp(self, lead: Lead):
        """Schedule WhatsApp follow-up message"""
        message = f"""שלום {lead.name} 👋

תודה על פנייתך לסטודיו של אופיר אסולין עיצוב פנים!

אני רוצה לספר לך קצת על התהליך שלנו:
✨ ליווי מקצועי משלב התכנון ועד ההלבשה הסופית
✨ בניית קונספט עיצובי מותאם אישית
✨ ניהול פרויקט מלא כולל בקרת איכות

האם תרצה לקבוע שיחה טלפונית קצרה כדי להבין טוב יותר את הצרכים שלך?

אופיר אסולין
052-626-9261
"""
        logger.info(f"WhatsApp message scheduled for {lead.phone}")
        # TODO: Integrate with WhatsApp Business API
    
    def _send_welcome_email(self, lead: Lead):
        """Send welcome email"""
        subject = "תודה על פנייתך - אופיר אסולין עיצוב פנים"
        body = f"""שלום {lead.name},

תודה על פנייתך לסטודיו של אופיר אסולין עיצוב פנים ואמנות.

אני שמחה להכיר אותך ולהבין את החזון שלך לבית שלך.

כמעצבת פנים עם ניסיון של שנים, אני מתמחה ביצירת מרחבים אישיים ומותאמים בדיוק לצרכים שלך.

בהמשך אשלח לך:
📥 מדריך חינמי: "5 שאלות שחייבים לשאול לפני תחילת שיפוץ"
📅 אפשרות לקביעת שיחת ייעוץ חינמית

בינתיים, אני מזמינה אותך להכיר את העבודות שלנו:
{self.config['business']['website']}

בברכה,
אופיר אסולין
מעצבת פנים ואמנית
052-626-9261
ofirassulin.design@gmail.com
"""
        logger.info(f"Welcome email sent to {lead.email}")
        # TODO: Integrate with email service (SendGrid, Mailchimp, etc.)
    
    def _add_to_crm(self, lead: Lead):
        """Add lead to CRM system"""
        logger.info(f"Lead {lead.id} added to CRM")
        # TODO: Integrate with CRM (HubSpot, Salesforce, etc.)
    
    def update_lead_status(self, lead_id: str, status: str, notes: Optional[str] = None):
        """Update lead status"""
        for lead in self.leads:
            if lead.id == lead_id:
                lead.status = status
                if notes:
                    lead.notes = notes
                self._save_leads()
                logger.info(f"Lead {lead_id} status updated to {status}")
                return
        logger.warning(f"Lead {lead_id} not found")
    
    def get_leads_by_status(self, status: str) -> List[Lead]:
        """Get leads by status"""
        return [lead for lead in self.leads if lead.status == status]
    
    def get_high_quality_leads(self, min_score: int = 7) -> List[Lead]:
        """Get high-quality leads"""
        return [lead for lead in self.leads 
                if lead.quality_score and lead.quality_score >= min_score]
    
    def add_campaign_metrics(self, campaign_id: str, campaign_name: str, 
                            platform: str, impressions: int, clicks: int,
                            conversions: int, cost: float):
        """Add campaign performance metrics"""
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
        cpl = (cost / conversions) if conversions > 0 else 0
        
        metrics = CampaignMetrics(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            platform=platform,
            date=datetime.now().isoformat(),
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            cost=cost,
            cpl=cpl,
            ctr=ctr,
            conversion_rate=conversion_rate
        )
        
        self.campaigns.append(metrics)
        self._save_campaigns()
        
        # Check if campaign needs optimization
        self._check_campaign_performance(metrics)
        
        return metrics
    
    def _check_campaign_performance(self, metrics: CampaignMetrics):
        """Check campaign performance against KPIs"""
        target_cpl = self.config['kpis']['target_cpl']
        
        if metrics.cpl > target_cpl * 1.5:
            logger.warning(f"Campaign {metrics.campaign_name} CPL ({metrics.cpl:.2f}) "
                         f"exceeds target ({target_cpl}) by 50% - Consider pausing")
        elif metrics.cpl < target_cpl * 0.7:
            logger.info(f"Campaign {metrics.campaign_name} performing well "
                       f"(CPL: {metrics.cpl:.2f}) - Consider increasing budget")
    
    def get_performance_report(self, days: int = 30) -> Dict:
        """Generate performance report"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_leads = [lead for lead in self.leads 
                       if datetime.fromisoformat(lead.timestamp) >= cutoff_date]
        recent_campaigns = [c for c in self.campaigns 
                           if datetime.fromisoformat(c.date) >= cutoff_date]
        
        total_leads = len(recent_leads)
        qualified_leads = len([l for l in recent_leads if l.quality_score and l.quality_score >= 7])
        consultations = len([l for l in recent_leads if l.status == 'consultation_booked'])
        conversions = len([l for l in recent_leads if l.status == 'converted'])
        
        total_cost = sum(c.cost for c in recent_campaigns)
        total_conversions = sum(c.conversions for c in recent_campaigns)
        avg_cpl = (total_cost / total_conversions) if total_conversions > 0 else 0
        
        consultation_rate = (consultations / total_leads * 100) if total_leads > 0 else 0
        conversion_rate = (conversions / consultations * 100) if consultations > 0 else 0
        
        return {
            'period_days': days,
            'total_leads': total_leads,
            'qualified_leads': qualified_leads,
            'consultations_booked': consultations,
            'projects_converted': conversions,
            'total_ad_spend': total_cost,
            'average_cpl': avg_cpl,
            'consultation_rate': consultation_rate,
            'conversion_rate': conversion_rate,
            'cac': (total_cost / conversions) if conversions > 0 else 0,
            'leads_by_source': self._get_leads_by_source(recent_leads),
            'top_campaigns': self._get_top_campaigns(recent_campaigns)
        }
    
    def _get_leads_by_source(self, leads: List[Lead]) -> Dict:
        """Get lead breakdown by source"""
        sources = {}
        for lead in leads:
            sources[lead.source] = sources.get(lead.source, 0) + 1
        return sources
    
    def _get_top_campaigns(self, campaigns: List[CampaignMetrics]) -> List[Dict]:
        """Get top performing campaigns"""
        sorted_campaigns = sorted(campaigns, key=lambda x: x.conversions, reverse=True)
        return [asdict(c) for c in sorted_campaigns[:5]]
    
    def optimize_campaigns(self):
        """Automated campaign optimization recommendations"""
        recommendations = []
        
        for campaign in self.campaigns[-30:]:  # Last 30 campaigns
            if campaign.cpl > self.config['kpis']['target_cpl'] * 1.3:
                recommendations.append({
                    'action': 'pause',
                    'campaign': campaign.campaign_name,
                    'reason': f'High CPL: {campaign.cpl:.2f}',
                    'priority': 'high'
                })
            elif campaign.conversion_rate < 2:
                recommendations.append({
                    'action': 'optimize',
                    'campaign': campaign.campaign_name,
                    'reason': f'Low conversion rate: {campaign.conversion_rate:.2f}%',
                    'priority': 'medium'
                })
            elif campaign.cpl < self.config['kpis']['target_cpl'] * 0.8:
                recommendations.append({
                    'action': 'scale',
                    'campaign': campaign.campaign_name,
                    'reason': f'Low CPL: {campaign.cpl:.2f} - Consider increasing budget',
                    'priority': 'high'
                })
        
        return recommendations


def main():
    """Main function to run the marketing agent"""
    agent = MarketingAgent()
    
    print("=" * 60)
    print("Performance Marketing Agent - Ofir Assulin Interior Design")
    print("=" * 60)
    print()
    
    # Example: Add a test lead
    # agent.add_lead(
    #     name="דני כהן",
    #     phone="050-1234567",
    #     email="danny@example.com",
    #     source="google",
    #     campaign="עיצוב פנים הרצליה",
    #     location="הרצליה",
    #     budget="800000",
    #     project_type="renovation"
    # )
    
    # Generate report
    report = agent.get_performance_report(days=30)
    print("Performance Report (Last 30 Days):")
    print(f"Total Leads: {report['total_leads']}")
    print(f"Qualified Leads: {report['qualified_leads']}")
    print(f"Consultations: {report['consultations_booked']}")
    print(f"Conversions: {report['projects_converted']}")
    print(f"Average CPL: ₪{report['average_cpl']:.2f}")
    print(f"Consultation Rate: {report['consultation_rate']:.2f}%")
    print(f"Conversion Rate: {report['conversion_rate']:.2f}%")
    print()
    
    # Get optimization recommendations
    recommendations = agent.optimize_campaigns()
    if recommendations:
        print("Optimization Recommendations:")
        for rec in recommendations:
            print(f"- [{rec['priority'].upper()}] {rec['action']}: {rec['campaign']} - {rec['reason']}")
    else:
        print("No optimization recommendations at this time.")


if __name__ == "__main__":
    main()
