# Quick Start Guide
## Performance Marketing System - Ofir Assulin Interior Design

---

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Initialize Configuration

```bash
python marketing_agent.py
```

This creates `config.json` with default settings. The system is configured for **$100/month budget**.

### Step 3: Start the Web Application

```bash
python app.py
```

You'll see:
```
Starting Performance Marketing Web Application...
Access the dashboard at: http://localhost:5000
 * Running on http://0.0.0.0:5000
```

### Step 4: Open the Dashboard

Open your browser and go to: **http://localhost:5000**

You'll see:
- 📊 **Dashboard** - Overview of leads, campaigns, and performance
- 👥 **Leads** - Manage and track all leads
- 📢 **Campaigns** - View campaign performance
- 📄 **Landing Pages** - Generate landing pages for campaigns
- 💡 **Strategy** - View marketing strategy

---

## 🎯 First Steps

### 1. Add Your First Lead

1. Go to **Leads** page
2. Click **"הוסף ליד חדש"** (Add New Lead)
3. Fill in the form:
   - Name, Phone, Email (required)
   - Source (Google, Facebook, Instagram, Organic)
   - Campaign name
   - Location, Budget, Project Type (optional)
4. Click **"שמור"** (Save)

The system will:
- ✅ Score the lead (1-10)
- ✅ Trigger automated follow-up
- ✅ Add to database

### 2. Create a Landing Page

1. Go to **Landing Pages** page
2. Fill in the form:
   - Page Type: "דף ליד מגנט" (Lead Magnet Page)
   - Campaign Name
   - Headline
   - Description
   - CTA Text
3. Click **"צור דף נחיתה"** (Generate Landing Page)
4. Preview and download the HTML file
5. Upload to your web server

### 3. Add Campaign Metrics

1. Go to **Campaigns** page
2. Click **"הוסף מדדי קמפיין"** (Add Campaign Metrics)
3. Fill in:
   - Campaign ID and Name
   - Platform (Google, Facebook, Instagram)
   - Impressions, Clicks, Conversions
   - Cost
4. Click **"שמור"** (Save)

The system will calculate:
- Cost Per Lead (CPL)
- Click-Through Rate (CTR)
- Conversion Rate

### 4. View Performance

Go to **Dashboard** to see:
- Total leads and trends
- Qualified leads (score 7+)
- Consultations booked
- Projects converted
- Cost metrics
- Charts and visualizations
- Optimization recommendations

---

## 📊 Understanding the Dashboard

### Stats Cards

- **סה"כ לידים** - Total leads in last 30 days
- **לידים איכותיים** - Leads with quality score 7+
- **ייעוצים שנקבעו** - Consultations booked
- **פרויקטים שהתקבלו** - Projects converted
- **הוצאה כוללת** - Total ad spend
- **ממוצע עלות לליד** - Average Cost Per Lead

### Charts

- **לידים לפי מקור** - Leads breakdown by source (Google, Facebook, etc.)
- **סטטוס לידים** - Leads by status (new, contacted, converted, etc.)

### Recommendations

The system provides optimization recommendations:
- 🔴 **High Priority** - Immediate action needed
- 🟡 **Medium Priority** - Should address soon
- 🟢 **Low Priority** - Nice to have

---

## 🔧 Configuration

### Edit `config.json`

```json
{
  "business": {
    "name": "Ofir Assulin Interior Design",
    "phone": "052-626-9261",
    "email": "ofirassulin.design@gmail.com"
  },
  "budgets": {
    "google_ads_monthly": 60,
    "facebook_ads_monthly": 40,
    "total_monthly": 100
  },
  "kpis": {
    "target_cpl": 150,
    "target_consultation_rate": 0.40,
    "target_conversion_rate": 0.50
  }
}
```

---

## 📤 Export & Integrations

### Export Leads

1. Go to **Leads** page
2. Use filters to select leads
3. Click **"ייצא ל-CSV"** (Export to CSV)
4. File downloads automatically

### Monday.com Integration

1. Get Monday.com API key:
   - Go to Monday.com → Profile → Admin → API
   - Generate API token

2. Create a board for leads with columns:
   - Name, Phone, Email, Status, Source, Campaign, Quality Score, etc.

3. Add to `config.json`:
```json
{
  "monday": {
    "api_key": "your_api_key",
    "board_id": "your_board_id"
  }
}
```

4. Sync leads:
   - Go to **Leads** page
   - Select leads to sync
   - Click **"סנכרן ל-Monday.com"** (Sync to Monday.com)

---

## 💡 Tips for $100/Month Budget

### Focus Areas:

1. **Organic Content (70% effort, $0 cost)**
   - Daily Instagram posts
   - SEO optimization
   - Email marketing
   - Content creation

2. **Strategic Paid Ads (30% effort, $100 cost)**
   - Google Ads: $60/month - Only 3-5 highest-intent keywords
   - Facebook/Instagram: $40/month - Highly targeted campaigns

### Optimization Tips:

- ✅ Use long-tail keywords (lower CPC)
- ✅ Geographic targeting (central Israel only)
- ✅ Time-based bidding (peak hours only)
- ✅ Focus on quality over quantity
- ✅ Monitor daily and optimize weekly

---

## 🆘 Troubleshooting

### Web app won't start
- Check if port 5000 is available
- Make sure Flask is installed: `pip install flask`

### Leads not showing
- Check `leads.json` file exists
- Verify JSON format is valid
- Check browser console for errors

### Landing page form not working
- Update webhook URL in generated HTML
- Change `http://localhost:5000` to your server URL
- Check CORS settings if hosting externally

### Monday.com sync fails
- Verify API key is correct
- Check board ID matches
- Ensure board columns match expected format
- See `monday_integration.py` for details

---

## 📚 Next Steps

1. ✅ Set up your first landing page
2. ✅ Add test leads manually
3. ✅ Configure Monday.com (optional)
4. ✅ Review strategy page
5. ✅ Launch your first campaign
6. ✅ Monitor dashboard daily

---

## 📞 Need Help?

- **Strategy:** See `STRATEGY.md`
- **Action Plan:** See `ACTION_PLAN.md`
- **Automation:** See `automation_guide.md`
- **Code:** Check docstrings in Python files

---

**Ready to maximize your lead generation! 🚀**
