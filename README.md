# Performance Marketing System for Ofir Assulin Interior Design

Automated performance marketing and lead generation system for high-end interior design clients in central Israel.

---

## 🎯 Overview

This system provides:
- **Automated lead capture** from multiple channels (Google Ads, Facebook, Instagram, website)
- **Lead scoring and qualification** to prioritize high-value prospects
- **Automated follow-up** via email and WhatsApp
- **Campaign performance tracking** with real-time analytics
- **Optimization recommendations** based on KPIs

---

## 📁 Project Structure

```
.
├── STRATEGY.md                 # Comprehensive marketing strategy
├── ACTION_PLAN.md              # Week-by-week execution plan
├── app.py                      # Main Flask web application
├── marketing_agent.py         # Core automation engine
├── webhook_server.py           # Standalone webhook server (optional)
├── dashboard.py                # CLI dashboard (optional)
├── monday_integration.py       # Monday.com integration module
├── templates/                  # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── leads.html
│   ├── campaigns.html
│   ├── landing_pages.html
│   └── strategy.html
├── static/                     # Static assets
│   ├── css/style.css
│   └── js/main.js
├── landing_page_example.html   # Example landing page
├── automation_guide.md         # Setup and integration guide
├── requirements.txt            # Python dependencies
├── config.json                 # Configuration (created on first run)
├── leads.json                  # Lead database (created automatically)
└── campaigns.json              # Campaign metrics (created automatically)
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to project directory
cd "Ofir assulin performance marketing"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initial Setup

Run the marketing agent once to create default configuration:

```bash
python marketing_agent.py
```

This creates `config.json` with default settings. Edit it with your specific values.

### 3. Start Web Application

```bash
python app.py
```

The web application will start on `http://localhost:5000`

### 4. Access the Dashboard

Open your browser and go to:
- **Dashboard:** http://localhost:5000
- **Leads Management:** http://localhost:5000/leads
- **Campaigns:** http://localhost:5000/campaigns
- **Landing Pages:** http://localhost:5000/landing-pages
- **Strategy:** http://localhost:5000/strategy

### 5. Webhook Server (Optional)

If you need the standalone webhook server for external integrations:

```bash
python webhook_server.py
```

---

## 🔧 Configuration

Edit `config.json` to customize:

- **Business information** (name, phone, email, website)
- **Target audience** (age, locations, minimum budget)
- **Monthly budgets** per platform
- **KPI targets** (CPL, conversion rates, CAC, ROAS)
- **Automation settings** (follow-up delays, enabled channels)

---

## 📊 Key Features

### Lead Management
- Automatic lead capture from multiple sources
- Quality scoring (1-10) based on location, budget, project type
- Status tracking (new → contacted → qualified → consultation → converted)
- Notes and custom fields

### Campaign Tracking
- Performance metrics per campaign
- Cost Per Lead (CPL) monitoring
- Click-through rates (CTR)
- Conversion rates
- Automatic alerts for underperforming campaigns

### Automation
- **Email sequences**: Welcome email + 3 follow-ups
- **WhatsApp messages**: Personalized follow-up within 2 hours
- **CRM integration**: Automatic lead sync (HubSpot, Salesforce)
- **Retargeting**: Automatic pixel tracking for retargeting campaigns

### Analytics & Reporting
- 30-day performance reports
- Lead source breakdown
- Conversion funnel analysis
- Campaign comparison
- Optimization recommendations

---

## 🔌 Integrations

### Required Integrations (See `automation_guide.md` for details)

1. **Google Ads API** - Import leads and campaign data
2. **Facebook Marketing API** - Lead forms and campaign metrics
3. **SendGrid** - Email automation
4. **Twilio** - WhatsApp messaging
5. **HubSpot/Salesforce** - CRM sync

### Optional Integrations

- **Google Analytics** - Website tracking
- **Zapier** - Additional automation workflows
- **Calendly** - Consultation booking

---

## 📈 Usage Examples

### Add a Lead Manually

```python
from marketing_agent import MarketingAgent

agent = MarketingAgent()

lead = agent.add_lead(
    name="דני כהן",
    phone="050-1234567",
    email="danny@example.com",
    source="google",
    campaign="עיצוב פנים הרצליה",
    location="הרצליה",
    budget="800000",
    project_type="renovation"
)

print(f"Lead added: {lead.id}, Quality Score: {lead.quality_score}")
```

### Get Performance Report

```python
report = agent.get_performance_report(days=30)
print(f"Total Leads: {report['total_leads']}")
print(f"Average CPL: ₪{report['average_cpl']:.2f}")
print(f"Conversion Rate: {report['conversion_rate']:.2f}%")
```

### Get Optimization Recommendations

```python
recommendations = agent.optimize_campaigns()
for rec in recommendations:
    print(f"{rec['action']}: {rec['campaign']} - {rec['reason']}")
```

---

## 🌐 API Endpoints

When running `webhook_server.py`, the following endpoints are available:

- `POST /api/leads` - Receive new lead
- `GET /api/leads` - Get leads (with optional filters)
- `PUT /api/leads/<id>/status` - Update lead status
- `POST /api/campaigns/metrics` - Add campaign metrics
- `GET /api/report` - Get performance report
- `GET /api/optimize` - Get optimization recommendations

---

## 📱 Landing Page Integration

1. Deploy `landing_page_example.html` to your web server
2. Update the webhook URL in the JavaScript:
   ```javascript
   const webhookUrl = 'https://your-domain.com/api/leads';
   ```
3. Add Facebook Pixel ID (replace `YOUR_PIXEL_ID`)
4. Customize form fields and styling

---

## 🎯 Target KPIs

**Budget:** ₪500/month

- Google Ads: ₪300/month (high-intent search)
- Facebook/Instagram: ₪200/month (targeted lead gen)

**Target KPIs:**

- **Cost Per Lead (CPL):** ₪150-250
- **Consultation Booking Rate:** 40%+
- **Project Conversion Rate:** 50%+
- **Customer Acquisition Cost (CAC):** ₪200-400
- **Return on Ad Spend (ROAS):** 200:1+ (even 1 project/month = 200X+ ROI)

**Expected Results:**
- 8-15 leads/month
- 3-6 consultations/month
- 1-3 projects/month
- AI-powered lead scoring and optimization

---

## 📋 Daily Workflow

### Automated (Runs Every Hour)
- Check for new leads
- Send follow-up messages
- Score new leads
- Monitor campaign performance

### Manual (Daily Review)
- Review high-quality leads (score 7+)
- Follow up on consultation bookings
- Check campaign alerts
- Review optimization recommendations

### Weekly Tasks
- Analyze performance report
- Adjust campaign budgets
- Test new ad creative
- Review lead quality trends

---

## 🔒 Security Notes

- **Never commit `config.json` to Git** - Contains API keys
- **Use environment variables** for sensitive credentials
- **Enable HTTPS** for webhook endpoints in production
- **Regular backups** of `leads.json` and `campaigns.json`

---

## 📚 Documentation

- **STRATEGY.md** - Complete marketing strategy and tactics
- **automation_guide.md** - Detailed setup instructions for all integrations
- **marketing_agent.py** - Code documentation in docstrings

---

## 🆘 Troubleshooting

### Leads Not Being Captured
- Check webhook server is running
- Verify webhook URL in landing page
- Check server logs for errors

### Emails Not Sending
- Verify SendGrid API key in config
- Check sender email is verified
- Review SendGrid activity logs

### Dashboard Not Showing Data
- Ensure leads.json and campaigns.json exist
- Check date filters in report
- Verify data format is correct

---

## 🚀 Next Steps

1. ✅ Review and customize `config.json`
2. ✅ Set up integrations (see `automation_guide.md`)
3. ✅ Deploy landing pages
4. ✅ Launch test campaigns
5. ✅ Monitor dashboard daily
6. ✅ Scale successful campaigns

---

## 📞 Support

For questions or issues:
- Review `automation_guide.md` for detailed setup
- Check code comments in Python files
- Review logs for error messages

---

**Built for Ofir Assulin Interior Design**  
*Maximizing lead generation for high-end clients in central Israel*
