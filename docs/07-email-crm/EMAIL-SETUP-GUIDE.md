# Email CRM Setup & Configuration Guide

## 📋 Initial Setup (One-Time)

### 1. Database Setup

Run this command to create all email tables:

```bash
python setup_email_crm_tables.py
```

Expected output:
```
Creating Email CRM tables...
✅ Email CRM tables created successfully!

Created tables:
  - email_campaigns
  - email_clicks
  - email_log
  - email_responses
  - tasks
```

### 2. Environment Variables

Add these to your `.env` file:

```env
# === EMAIL CONFIGURATION (Optional) ===
# Leave empty to simulate sending
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# For receiving responses (optional)
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993

# Your app URL (for tracking)
APP_URL=http://localhost:9000
```

**Note**: Email sending works in "simulation mode" without SMTP config - perfect for testing!

### 3. Test the System

1. Start your app:
   ```bash
   python app.py
   ```

2. Navigate to: `http://localhost:9000/email`

3. You should see:
   ```
   📧 Email Center
   
   [0 Sent] [0% Open Rate] [0% Click Rate] [0 Interested]
   ```

---

## 🔧 Configuration Options

### Email Sending Modes

**1. Simulation Mode (Default)**
- No SMTP config needed
- Emails logged but not sent
- Perfect for testing
- See all features work

**2. Real Email Mode**
- Add SMTP settings
- Actually sends emails
- Requires email account
- For production use

### Setting Up Gmail (If Needed)

1. Enable 2-factor authentication
2. Generate app password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use app password in `SMTP_PASSWORD`

---

## 🎨 Customization

### Modify Email Templates

The AI generates emails, but you can guide it:

```python
# In app/email_crm/service.py, modify prompts:

'inquiry': f"""Write a brief, professional email...
Add: Mention we're a premium B2B platform
Focus: Quality and long-term partnerships
Tone: Professional but friendly
"""
```

### Adjust Tracking

In `app/email_crm/tracker.py`:

```python
# Change tracking ID length
return str(uuid.uuid4())[:8]  # Current: 8 chars
return str(uuid.uuid4())[:12] # Longer IDs
```

### Pipeline Stages

Current stages are fixed:
- New → Contacted → Opened → Interested

To modify, update SQL queries in `routes.py`.

---

## 🔒 Security Notes

### Email Tracking Privacy

- Tracking pixels are standard practice
- Only tracks opens/clicks
- No personal data collected
- Complies with B2B norms

### Database Security

- All emails stored locally
- No external services required
- Passwords in .env (gitignored)
- Use Azure PostgreSQL SSL

---

## 🚀 Performance Tips

### For 1-Person Operation

**Recommended Settings**:
- Daily emails: 30-50 max
- Follow-up delay: 3 days
- Pipeline refresh: 2x daily
- Response time: Same day

### Database Optimization

Indexes are auto-created for:
- Tracking IDs (fast pixel loading)
- Supplier IDs (quick filtering)
- Timestamps (recent activity)
- Email status (pipeline view)

---

## 📊 Monitoring

### Daily Health Check

```sql
-- Run in your database:
SELECT 
    COUNT(*) as total_sent,
    COUNT(CASE WHEN opened_at IS NOT NULL THEN 1 END) as opened,
    COUNT(CASE WHEN clicked_at IS NOT NULL THEN 1 END) as clicked,
    AVG(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END)*100 as open_rate
FROM email_log
WHERE sent_at >= CURRENT_DATE - INTERVAL '7 days';
```

### Check Email Queue

```python
# See pending emails:
SELECT COUNT(*) FROM suppliers 
WHERE email_status = 'new' 
AND company_email IS NOT NULL;
```

---

## 🐛 Troubleshooting Setup

### "Module not found" Error

```bash
# Make sure you're in the right directory:
cd /path/to/FoodXchange
python setup_email_crm_tables.py
```

### Tables Already Exist

This is fine! The script uses "IF NOT EXISTS" so it's safe to run multiple times.

### Can't Access /email

1. Check app is running: `http://localhost:9000`
2. Check console for errors
3. Verify email router is loaded:
   ```
   Look for: "Email CRM module loaded" in console
   ```

### No Suppliers Showing

```sql
-- Check if suppliers have emails:
SELECT COUNT(*) FROM suppliers WHERE company_email IS NOT NULL;

-- If 0, update some suppliers:
UPDATE suppliers 
SET company_email = 'test@' || supplier_name || '.com' 
WHERE id < 10;
```

---

## 🔄 Updates & Maintenance

### Weekly Maintenance

1. **Clean old tracking**:
   ```sql
   DELETE FROM email_clicks 
   WHERE clicked_at < CURRENT_DATE - INTERVAL '30 days';
   ```

2. **Archive old emails**:
   ```sql
   UPDATE email_log 
   SET status = 'archived' 
   WHERE sent_at < CURRENT_DATE - INTERVAL '90 days';
   ```

### Monthly Review

- Check open rates trend
- Review AI email quality
- Update product interests
- Clean test data

---

## 🎯 Integration Points

### With Existing Suppliers Page

The email system reads from your `suppliers` table:
- Uses: company_email, supplier_name, country
- Updates: email_status, last_contacted

### With Projects

Can filter by project:
- Pass project_id to email campaigns
- Track emails per project
- Measure project success rates

### Event System

Listen for email events:
```python
from app.core.events import bus, Events

def on_email_sent(data):
    print(f"Email sent to {data['email']}")
    
bus.on(Events.EMAIL_SENT, on_email_sent)
```

---

## 📝 Final Checklist

- [ ] Run setup_email_crm_tables.py
- [ ] Add email button to navbar (already done)
- [ ] Test /email route works
- [ ] Try sending test email
- [ ] Check pipeline view
- [ ] Set up daily routine

---

## Need Help?

Common issues:
1. **Blank page**: Check browser console
2. **No suppliers**: Need email addresses in DB
3. **Errors**: Check Python console
4. **Tracking not working**: Check APP_URL in .env

The system is designed to be simple and reliable. If something seems complex, there's probably an easier way!

---

*Setup Time: ~10 minutes | Daily Operation: ~5 minutes*