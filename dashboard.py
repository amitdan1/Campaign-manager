"""
Performance Marketing Dashboard
Real-time monitoring and analytics for marketing campaigns
"""

from marketing_agent import MarketingAgent
from datetime import datetime, timedelta
import json


class Dashboard:
    """Marketing performance dashboard"""
    
    def __init__(self):
        self.agent = MarketingAgent()
    
    def display_dashboard(self):
        """Display main dashboard"""
        print("\n" + "=" * 80)
        print(" " * 25 + "MARKETING PERFORMANCE DASHBOARD")
        print(" " * 20 + "Ofir Assulin Interior Design")
        print("=" * 80)
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Get 30-day report
        report = self.agent.get_performance_report(days=30)
        
        # Overview Section
        print("📊 OVERVIEW (Last 30 Days)")
        print("-" * 80)
        print(f"Total Leads:           {report['total_leads']:>6}")
        print(f"Qualified Leads (7+):  {report['qualified_leads']:>6}")
        print(f"Consultations Booked:  {report['consultations_booked']:>6}")
        print(f"Projects Converted:    {report['projects_converted']:>6}")
        print()
        
        # Performance Metrics
        print("💰 PERFORMANCE METRICS")
        print("-" * 80)
        print(f"Total Ad Spend:        ₪{report['total_ad_spend']:>12,.2f}")
        print(f"Average CPL:          ₪{report['average_cpl']:>12,.2f}")
        print(f"Target CPL:           ₪{self.agent.config['kpis']['target_cpl']:>12,.2f}")
        
        if report['projects_converted'] > 0:
            cac = report['cac']
            print(f"Customer Acquisition:  ₪{cac:>12,.2f}")
            print(f"Target CAC:           ₪{self.agent.config['kpis']['target_cac']:>12,.2f}")
        
        print()
        
        # Conversion Rates
        print("📈 CONVERSION RATES")
        print("-" * 80)
        print(f"Consultation Rate:     {report['consultation_rate']:>6.2f}%")
        print(f"Target Rate:          {self.agent.config['kpis']['target_consultation_rate']*100:>6.2f}%")
        print(f"Conversion Rate:      {report['conversion_rate']:>6.2f}%")
        print(f"Target Rate:          {self.agent.config['kpis']['target_conversion_rate']*100:>6.2f}%")
        print()
        
        # Leads by Source
        print("📱 LEADS BY SOURCE")
        print("-" * 80)
        leads_by_source = report['leads_by_source']
        total_leads = report['total_leads']
        for source, count in sorted(leads_by_source.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_leads * 100) if total_leads > 0 else 0
            print(f"{source.capitalize():<20} {count:>6} ({percentage:>5.1f}%)")
        print()
        
        # Recent High-Quality Leads
        print("⭐ HIGH-QUALITY LEADS (Score 7+)")
        print("-" * 80)
        high_quality = self.agent.get_high_quality_leads(min_score=7)
        recent_high_quality = [l for l in high_quality 
                              if datetime.fromisoformat(l.timestamp) >= datetime.now() - timedelta(days=7)]
        
        if recent_high_quality:
            print(f"{'Name':<25} {'Source':<15} {'Score':<8} {'Status':<20}")
            print("-" * 80)
            for lead in recent_high_quality[:10]:
                print(f"{lead.name[:24]:<25} {lead.source:<15} {lead.quality_score or 'N/A':<8} {lead.status:<20}")
        else:
            print("No high-quality leads in the last 7 days")
        print()
        
        # Lead Status Breakdown
        print("📋 LEAD STATUS BREAKDOWN")
        print("-" * 80)
        statuses = ['new', 'contacted', 'qualified', 'consultation_booked', 'converted', 'lost']
        for status in statuses:
            leads = self.agent.get_leads_by_status(status)
            count = len([l for l in leads 
                        if datetime.fromisoformat(l.timestamp) >= datetime.now() - timedelta(days=30)])
            if count > 0:
                print(f"{status.replace('_', ' ').title():<25} {count:>6}")
        print()
        
        # Optimization Recommendations
        print("🔧 OPTIMIZATION RECOMMENDATIONS")
        print("-" * 80)
        recommendations = self.agent.optimize_campaigns()
        
        if recommendations:
            priority_order = {'high': 1, 'medium': 2, 'low': 3}
            sorted_recs = sorted(recommendations, key=lambda x: priority_order.get(x['priority'], 99))
            
            for rec in sorted_recs[:5]:
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                print(f"{priority_icon} [{rec['priority'].upper()}] {rec['action'].upper()}: {rec['campaign']}")
                print(f"   └─ {rec['reason']}")
        else:
            print("✅ No immediate optimization needed")
        print()
        
        # Top Campaigns
        print("🏆 TOP 5 CAMPAIGNS")
        print("-" * 80)
        top_campaigns = report['top_campaigns']
        if top_campaigns:
            print(f"{'Campaign':<30} {'Platform':<12} {'Leads':<8} {'CPL':<12}")
            print("-" * 80)
            for campaign in top_campaigns[:5]:
                name = campaign['campaign_name'][:29]
                platform = campaign['platform'][:11]
                conversions = campaign['conversions']
                cpl = campaign['cpl']
                print(f"{name:<30} {platform:<12} {conversions:<8} ₪{cpl:>10,.2f}")
        else:
            print("No campaign data available")
        print()
        
        print("=" * 80)
        print()
    
    def display_lead_details(self, lead_id: str):
        """Display detailed lead information"""
        lead = next((l for l in self.agent.leads if l.id == lead_id), None)
        
        if not lead:
            print(f"Lead {lead_id} not found")
            return
        
        print("\n" + "=" * 80)
        print("LEAD DETAILS")
        print("=" * 80)
        print(f"ID:              {lead.id}")
        print(f"Name:            {lead.name}")
        print(f"Phone:           {lead.phone}")
        print(f"Email:           {lead.email}")
        print(f"Source:          {lead.source}")
        print(f"Campaign:        {lead.campaign}")
        print(f"Status:          {lead.status}")
        print(f"Quality Score:   {lead.quality_score or 'N/A'}/10")
        print(f"Location:        {lead.location or 'N/A'}")
        print(f"Budget:          {lead.budget or 'N/A'}")
        print(f"Project Type:    {lead.project_type or 'N/A'}")
        print(f"Timestamp:       {lead.timestamp}")
        if lead.notes:
            print(f"Notes:           {lead.notes}")
        print("=" * 80)
        print()


def main():
    """Main dashboard function"""
    dashboard = Dashboard()
    
    while True:
        dashboard.display_dashboard()
        
        print("Options:")
        print("1. Refresh dashboard")
        print("2. View lead details (enter lead ID)")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            continue
        elif choice == '2':
            lead_id = input("Enter lead ID: ").strip()
            dashboard.display_lead_details(lead_id)
        elif choice == '3':
            print("Exiting dashboard...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
