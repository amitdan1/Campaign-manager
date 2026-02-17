# Marketing Automation Setup Guide

## Overview

This guide will help you set up the automated performance marketing system for Ofir Assulin Interior Design.

---

## System Architecture

```
┌─────────────────┐
│  Ad Platforms   │  Google Ads, Facebook, Instagram
│  (Lead Sources) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Landing Pages   │  Lead capture forms
│  & Forms         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Marketing Agent │  Core automation engine
│  (Python)        │
└────────┬────────┘
         │
         ├──► CRM System (HubSpot/Salesforce)
         ├──► Email Service (SendGrid/Mailchimp)
         ├──► WhatsApp API (Twilio)
         └──► Analytics Dashboard
```

---

## Installation Steps

### 1. Prerequisites

```bash
# Install Python 3.8+
python3 --version

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initial Configuration

The system will create a default `config.json` file on first run. Edit it with your specific settings:

```json
{
  "business": {
    "name": "Ofir Assulin Interior Design",
    "phone": "052-626-9261",
    "email": "ofirassulin.design@gmail.com",
    "website": "https://www.ofirassulin.design/"
  },
  "target_audience": {
    "age_min": 35,
    "age_max": 55,
    "locations": ["תל אביב", "הרצליה", "רמת השרון"],
    "min_budget": 500000
  },
  "budgets": {
    "google_ads_monthly": 20000,
    "facebook_ads_monthly": 10000,
    "instagram_ads_monthly": 5000
  },
  "kpis": {
    "target_cpl": 400,
    "target_consultation_rate": 0.25,
    "target_conversion_rate": 0.45
  }
}
```

### 3. Run the Agent

```bash
python marketing_agent.py
```

---

## Integration Setup

### Google Ads Integration

1. **Create Google Ads Account:**
   - Go to https://ads.google.com
   - Set up account with business details
   - Enable conversion tracking

2. **Install Google Ads API:**
   ```bash
   pip install google-ads
   ```

3. **Get API Credentials:**
   - Create OAuth2 credentials in Google Cloud Console
   - Download client_secrets.json
   - Place in project directory

4. **Configure in Agent:**
   - Add Google Ads API credentials to config.json
   - Set up automatic lead import

### Facebook/Instagram Integration

1. **Facebook Business Manager:**
   - Create Business Manager account
   - Add Facebook Page and Instagram account
   - Set up Facebook Pixel on website

2. **Install Facebook SDK:**
   ```bash
   pip install facebook-business
   ```

3. **Get Access Token:**
   - Generate access token in Facebook Developers
   - Add to config.json

4. **Set Up Lead Forms:**
   - Create Lead Generation campaigns
   - Connect to webhook endpoint

### Email Integration (SendGrid)

1. **Create SendGrid Account:**
   - Sign up at https://sendgrid.com
   - Verify sender email

2. **Get API Key:**
   - Generate API key in SendGrid dashboard
   - Add to config.json

3. **Create Email Templates:**
   - Welcome email
   - Follow-up sequence (3 emails)
   - Consultation reminder

### WhatsApp Integration (Twilio)

1. **Create Twilio Account:**
   - Sign up at https://www.twilio.com
   - Get WhatsApp Business API access

2. **Configure:**
   - Add Twilio credentials to config.json
   - Set up webhook for incoming messages

### CRM Integration (HubSpot)

1. **Create HubSpot Account:**
   - Sign up at https://www.hubspot.com
   - Create custom properties for leads

2. **Get API Key:**
   - Generate API key in HubSpot
   - Add to config.json

3. **Set Up Workflows:**
   - Create automation workflows
   - Set up lead scoring
   - Configure email sequences

---

## Landing Page Setup

### Required Landing Pages

1. **Main Lead Magnet Landing Page:**
   - URL: `/free-guide`
   - Form fields: Name, Phone, Email, Location, Budget Range
   - CTA: "Download Free Guide"

2. **Consultation Booking Page:**
   - URL: `/consultation`
   - Form fields: Name, Phone, Email, Preferred Date/Time
   - Calendar integration

3. **Thank You Page:**
   - URL: `/thank-you`
   - Confirmation message
   - Next steps
   - Social proof

### Form Integration

Add webhook to your landing page forms:

```javascript
// Example webhook endpoint
fetch('https://your-domain.com/api/leads', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: formData.name,
    phone: formData.phone,
    email: formData.email,
    source: 'website',
    campaign: 'organic'
  })
});
```

---

## Automation Workflows

### Lead Capture Workflow

1. **Lead submits form** → Webhook triggers
2. **Agent receives lead** → Scores lead quality
3. **High-quality lead (7+)** → Immediate WhatsApp + Email
4. **Medium-quality lead (5-6)** → Email only
5. **Low-quality lead (<5)** → Email sequence only

### Follow-Up Sequence

**Email 1 (Immediate):**
- Welcome message
- Download link for lead magnet
- Introduction to services

**Email 2 (Day 2):**
- Portfolio showcase
- Client testimonials
- Case study

**Email 3 (Day 5):**
- Consultation offer
- Calendar booking link
- Limited-time offer (if applicable)

**WhatsApp (Day 1, 2 hours after lead):**
- Personal greeting
- Quick value proposition
- Call-to-action for consultation

### Retargeting Workflow

1. **Website visitor** → Pixel fires
2. **No conversion after 24h** → Retargeting ad starts
3. **Viewed pricing page** → Special offer ad
4. **Abandoned form** → Reminder ad with form link

---

## Monitoring & Optimization

### Daily Tasks (Automated)

- Check new leads (every hour)
- Send follow-up messages (automated)
- Monitor campaign performance
- Flag underperforming campaigns

### Weekly Tasks

- Review performance report
- Analyze lead quality scores
- Optimize ad creative
- Adjust budgets

### Monthly Tasks

- Full performance analysis
- Budget reallocation
- New campaign testing
- Strategy refinement

### Key Metrics to Monitor

- **Cost Per Lead (CPL)** - Target: ₪300-500
- **Lead Quality Score** - Average should be 6+
- **Response Time** - Should be <2 hours
- **Consultation Booking Rate** - Target: 20-30%
- **Conversion Rate** - Target: 40-50%
- **ROAS** - Target: 30:1+

---

## Troubleshooting

### Leads Not Being Captured

1. Check webhook endpoint is accessible
2. Verify form submission is triggering webhook
3. Check agent logs for errors
4. Verify database file permissions

### Emails Not Sending

1. Verify SendGrid API key is correct
2. Check sender email is verified
3. Review SendGrid activity logs
4. Check spam folder

### WhatsApp Messages Not Sending

1. Verify Twilio credentials
2. Check WhatsApp Business API approval status
3. Verify phone number format
4. Check Twilio logs

### Campaign Performance Issues

1. Review campaign metrics in agent
2. Check ad creative relevance
3. Verify targeting settings
4. Analyze competitor activity

---

## Security Best Practices

1. **Never commit credentials to Git**
   - Use environment variables
   - Add config.json to .gitignore

2. **Use HTTPS for all webhooks**
   - SSL certificate required
   - Encrypt sensitive data

3. **Regular backups**
   - Backup leads.json daily
   - Backup campaigns.json daily
   - Store backups securely

4. **Access control**
   - Limit API access
   - Use strong passwords
   - Enable 2FA where possible

---

## Next Steps

1. ✅ Set up all integrations
2. ✅ Create landing pages
3. ✅ Configure automation workflows
4. ✅ Launch test campaigns
5. ✅ Monitor and optimize
6. ✅ Scale successful campaigns

---

## Support & Resources

- **Marketing Agent Documentation:** See marketing_agent.py
- **Strategy Guide:** See STRATEGY.md
- **API Documentation:** Check individual service docs
- **Troubleshooting:** Review logs in console output

---

*Last updated: February 2026*
