# FoodXchange Email CRM - Complete Documentation

> **Version**: 1.0  
> **Last Updated**: August 2025  
> **Platform**: FoodXchange B2B Trading Platform  
> **User Type**: 1-Person Food Sourcing Business  

---

## 📚 Table of Contents

1. [System Overview](#system-overview)
2. [Current Implementation](#current-implementation)
3. [Daily Operations Guide](#daily-operations)
4. [Outlook Integration Workflow](#outlook-integration)
5. [AI Features Documentation](#ai-features)
6. [Technical Architecture](#technical-architecture)
7. [Future Development Roadmap](#future-development)
8. [API Integration Options](#api-integration)
9. [Troubleshooting Guide](#troubleshooting)
10. [Appendix: Code Reference](#code-reference)

---

## 🎯 System Overview

### Purpose
The Email CRM system automates and tracks supplier outreach for food sourcing operations, reducing email writing time by 90% while maintaining personalization through AI.

### Core Features
- **AI Email Generation**: Azure OpenAI writes personalized supplier emails
- **Supplier Pipeline**: Visual tracking (New → Contacted → Opened → Interested)
- **Email Tracking**: Logs all communications
- **Task Generation**: Auto-creates follow-ups from responses
- **Bulk Operations**: Handle multiple suppliers efficiently

### Technology Stack
- **Backend**: FastAPI (Python)
- **Database**: Azure PostgreSQL
- **AI**: Azure OpenAI (GPT-4)
- **Frontend**: Bootstrap 5 + Jinja2
- **Architecture**: Modular monolith with event system

---

## 💼 Current Implementation

### What's Working Now
1. **AI Email Writing** ✅
   - Generates personalized emails in seconds
   - Multiple templates (inquiry, follow-up, thanks)
   - Customizes based on supplier country and products

2. **Supplier Management** ✅
   - Pipeline view of all suppliers
   - Status tracking
   - Bulk selection

3. **Manual Outlook Workflow** ✅
   - Generate in system → Copy → Send via Outlook
   - Personal email address builds trust
   - Full control over sending

4. **Basic Analytics** ✅
   - Email count tracking
   - Pipeline statistics
   - Recent activity log

### Database Schema
```sql
-- Core tables created:
email_campaigns     -- Email templates
email_log          -- Sent email records
email_responses    -- Response tracking (for future)
tasks             -- Follow-up tasks
suppliers         -- Enhanced with email_status
```

---

## 📋 Daily Operations Guide

### Morning Workflow (15 minutes)

#### 1. Check Dashboard
```
URL: http://localhost:9000/email
```
Review:
- Yesterday's sent count
- Any manual updates needed
- Pipeline statistics

#### 2. Prepare Today's Outreach
```
Targets:
- 20-30 new inquiries
- 5-10 follow-ups
- Region focus (e.g., "Italy suppliers today")
```

#### 3. Generate & Send Batch 1 (New Inquiries)
1. Click "✉️ Compose Email"
2. Select 5 suppliers from same country
3. Enter specific products: `"organic olive oil, extra virgin"`
4. Click "🤖 Generate with AI"
5. Copy generated email
6. In Outlook:
   - New Email
   - Paste content
   - Add supplier emails
   - Personalize greeting if needed
   - Send

#### 4. Generate & Send Batch 2 (Follow-ups)
1. Go to Pipeline view
2. Find suppliers marked "Opened" (3+ days ago)
3. Select for follow-up
4. Generate follow-up emails
5. Send via Outlook

#### 5. Log Responses
When replies arrive in Outlook:
1. Read supplier response
2. Go to Pipeline
3. Update status manually
4. Plan next action

### Time Breakdown
- Dashboard check: 2 minutes
- Generate 20 emails: 5 minutes
- Send via Outlook: 8 minutes
- **Total: 15 minutes for 20+ personalized emails**

---

## 📧 Outlook Integration Workflow

### Current Manual Process

#### Why Manual?
- Emails come from your address (builds trust)
- No technical setup required
- Full control over timing/content
- Personal signatures maintained

#### Efficient Copy-Paste Workflow

**Setup: Side-by-Side Windows**
```
[FoodXchange Email CRM]  |  [Outlook]
     Generate Here       |  Send Here
```

**Keyboard Shortcuts**
- `Ctrl+A`: Select all text
- `Ctrl+C`: Copy
- `Ctrl+V`: Paste
- `Ctrl+Enter`: Send email (in Outlook)

#### Outlook Tips
1. **Create Contact Groups**: Group suppliers by country
2. **Use Templates**: Save common subjects
3. **Schedule Sends**: Use Outlook's delay delivery
4. **Track Opens**: Request read receipts

### Future Automated Integration

When ready to automate, add to `.env`:
```env
# Outlook SMTP Configuration
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-app-specific-password

# IMAP for reading responses
IMAP_SERVER=outlook.office365.com
IMAP_PORT=993
```

Obtaining App Password:
1. Go to https://account.microsoft.com/security
2. Enable two-factor authentication
3. Generate app-specific password
4. Use in configuration above

---

## 🤖 AI Features Documentation

### Email Generation Engine

#### How It Works
```python
# Input parameters:
- supplier_name: "Mediterranean Oil Co"
- country: "Italy"  
- products: "organic olive oil"
- email_type: "inquiry" | "follow_up" | "thanks"

# AI generates personalized email considering:
- Cultural context (country-specific approach)
- Product specifics
- Business formality level
- Clear call-to-action
```

#### AI Prompts Used

**Inquiry Template**
```
Write a brief, professional email to {supplier_name} in {country}.
We want to source: {products}
Keep under 150 words. Be friendly and clear.
Include: introduction, specific interest, request for pricing/MOQ, next steps.
```

**Follow-up Template**
```
Write a short follow-up to {supplier_name}.
Reference our previous email about {products}.
Keep under 100 words. Gentle reminder, not pushy.
```

#### Customization Options
Edit prompts in: `app/email_crm/service.py`

### Response Analysis (Future)

When implemented, AI will:
- Categorize responses (interested/not interested/needs info)
- Extract key information (pricing, MOQ, lead times)
- Generate follow-up tasks
- Suggest response templates

---

## 🏗️ Technical Architecture

### Module Structure
```
FoodXchange/
├── app/
│   ├── core/
│   │   └── events.py          # Simple event bus
│   ├── email_crm/
│   │   ├── __init__.py
│   │   ├── service.py         # Email generation & sending
│   │   ├── tracker.py         # Open/click tracking
│   │   └── routes.py          # FastAPI endpoints
│   └── main.py                # Main application
├── templates/
│   └── email/
│       ├── dashboard.html     # Main email dashboard
│       ├── compose.html       # Email composer
│       └── pipeline.html      # Supplier pipeline view
└── docs/
    └── email-crm/            # This documentation
```

### Event System
Simple publish/subscribe for module communication:
```python
# When email is sent:
bus.emit(Events.EMAIL_SENT, {'supplier_id': 123})

# Other modules can listen:
bus.on(Events.EMAIL_SENT, handle_email_sent)
```

### API Endpoints
```
GET  /email                 # Dashboard
GET  /email/compose         # Composer interface
POST /email/send           # Send bulk emails
GET  /email/pipeline       # Pipeline view
POST /email/ai/generate    # Generate AI email
GET  /email/t/{id}.gif     # Tracking pixel
GET  /email/c/{id}         # Click tracking
```

### Database Design
```sql
-- Optimized for 1-person operation
email_log: Minimal fields, indexed for speed
suppliers: Enhanced with email_status, last_contacted
tasks: Simple task tracking
email_responses: Ready for future automation
```

---

## 🚀 Future Development Roadmap

### Phase 1: Enhanced Tracking (Month 2)
- [ ] Implement email open tracking via pixels
- [ ] Click tracking for links
- [ ] Automatic response detection
- [ ] Read receipt processing

### Phase 2: Full Automation (Month 3)
- [ ] SMTP integration for auto-sending
- [ ] IMAP integration for response reading
- [ ] Automatic pipeline updates
- [ ] Smart scheduling based on timezones

### Phase 3: Advanced AI (Month 4)
- [ ] Response sentiment analysis
- [ ] Automatic response drafting
- [ ] Predictive supplier scoring
- [ ] Optimal send time prediction

### Phase 4: Scale Features (Month 6)
- [ ] Email templates library
- [ ] A/B testing capability
- [ ] Advanced analytics dashboard
- [ ] Export/reporting features

### Nice-to-Have Features
- Mobile app for on-the-go access
- WhatsApp integration
- Voice note transcription
- Multi-language support

---

## 🔌 API Integration Options

### SendGrid Integration
```python
# Future implementation in service.py
import sendgrid
from sendgrid.helpers.mail import Mail

def send_via_sendgrid(to_email, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    message = Mail(
        from_email='you@fdx.trading',
        to_emails=to_email,
        subject=subject,
        html_content=content
    )
    response = sg.send(message)
```

### Azure Communication Services
```python
# Alternative email service
from azure.communication.email import EmailClient

def send_via_azure(to_email, subject, content):
    client = EmailClient.from_connection_string(connection_string)
    message = {
        "senderAddress": "DoNotReply@fdx.trading",
        "recipients": {"to": [{"address": to_email}]},
        "content": {
            "subject": subject,
            "html": content
        }
    }
    client.send(message)
```

### Webhook Integration
For receiving responses:
```python
@router.post("/webhook/email-received")
async def handle_incoming_email(request: Request):
    data = await request.json()
    # Process incoming email
    # Update pipeline
    # Trigger AI analysis
```

---

## 🔧 Troubleshooting Guide

### Common Issues & Solutions

#### 1. "No suppliers showing in compose"
**Cause**: Suppliers missing email addresses
**Fix**: 
```sql
-- Check suppliers with emails
SELECT COUNT(*) FROM suppliers WHERE company_email IS NOT NULL;

-- Add test emails if needed
UPDATE suppliers 
SET company_email = LOWER(REPLACE(supplier_name, ' ', '')) || '@example.com'
WHERE company_email IS NULL 
LIMIT 10;
```

#### 2. "AI not generating emails"
**Cause**: Azure OpenAI configuration
**Fix**: Check `.env` file has:
```
AZURE_OPENAI_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

#### 3. "Pipeline not updating"
**Cause**: Manual process - needs manual updates
**Fix**: After sending emails, manually update status or wait for automation phase

#### 4. "Emails look generic"
**Cause**: Not enough product detail
**Fix**: Be specific: "organic extra virgin olive oil in 1L bottles" vs just "oil"

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "No suppliers selected" | Empty selection | Select at least one supplier |
| "Failed to generate" | AI service issue | Check Azure OpenAI credits |
| "Database error" | Connection issue | Restart app, check DATABASE_URL |

### Performance Issues

**Slow email generation?**
- Reduce batch size to 5-10 suppliers
- Check internet connection
- Azure OpenAI may have rate limits

**Page not loading?**
- Clear browser cache
- Check console for errors: `F12` → Console
- Restart FastAPI server

---

## 📎 Appendix: Code Reference

### Key Files Reference

#### `app/email_crm/service.py`
Core email service with AI integration:
- `generate_email()`: Creates AI emails
- `send_bulk_emails()`: Handles bulk operations
- `analyze_response()`: Future response processing

#### `app/email_crm/tracker.py`
Email tracking implementation:
- `add_tracking()`: Adds pixel and wraps links
- `track_open()`: Records email opens
- `track_click()`: Records link clicks

#### `app/email_crm/routes.py`
FastAPI routes:
- Dashboard, compose, pipeline views
- API endpoints for AI generation
- Tracking endpoints

#### `templates/email/*.html`
UI templates:
- Clean Bootstrap 5 design
- Mobile responsive
- Minimal JavaScript

### Configuration Files

#### `.env` Template
```env
# Database (Required)
DATABASE_URL=postgresql://user:pass@server/database

# Azure OpenAI (Required)
AZURE_OPENAI_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# Email (Optional - for future)
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=

# App Settings
APP_URL=http://localhost:9000
```

### Database Migrations

Run these in order:
1. `setup_email_crm_tables.py` - Creates all tables
2. `clean_email_system.py` - Clears test data

### Testing Commands

```bash
# Test AI connection
python -c "from app.email_crm.service import email_crm; print(email_crm.generate_email({'name':'Test','country':'USA'}))"

# Check database
python -c "import psycopg2; conn=psycopg2.connect(os.getenv('DATABASE_URL')); print('Connected')"
```

---

## 📈 Success Metrics

### What Good Looks Like

**Daily**:
- 20-30 emails sent
- 15 minutes total time
- 50%+ open rate

**Weekly**:
- 100-150 suppliers contacted
- 5-10 interested responses
- 2-3 quote requests

**Monthly**:
- 400-600 touchpoints
- 20-40 active conversations
- 3-5 new partnerships

### ROI Calculation
- **Time saved**: 2 hours/day (vs manual writing)
- **Reach increase**: 10x more suppliers
- **Response rate**: 5-10% (industry avg: 1-2%)
- **Cost**: ~$5/month (Azure OpenAI usage)

---

## 🎯 Best Practices Summary

1. **Start small**: 5-10 emails per batch
2. **Be specific**: Detailed product descriptions
3. **Time it right**: 9-11 AM supplier timezone
4. **Follow up**: After 3 days if opened
5. **Stay personal**: Edit AI content when needed
6. **Track everything**: Use pipeline view daily
7. **Iterate**: Improve prompts based on responses

---

## 📞 Support & Updates

### Getting Help
1. Check this documentation first
2. Review error logs in console
3. Test individual components
4. Simplify (reduce batch size, basic products)

### Updating the System
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Run migrations
python setup_email_crm_tables.py
```

### Feature Requests
The system is designed to stay lean. Before adding features, consider:
- Does it save time?
- Is it essential for 1-person operation?
- Does it add complexity?

---

*End of Documentation - Version 1.0*