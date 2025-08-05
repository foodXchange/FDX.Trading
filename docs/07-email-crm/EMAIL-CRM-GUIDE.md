# FoodXchange Email CRM - User Guide

> **For**: 1-person food sourcing operations  
> **Time to Learn**: 15 minutes  
> **Time Saved**: 2+ hours per day  

---

## 📋 Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Daily Workflow](#daily-workflow)
3. [Sending Your First Email Campaign](#sending-emails)
4. [Understanding the Pipeline](#pipeline-view)
5. [Tracking & Analytics](#tracking)
6. [AI Features](#ai-features)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Access the Email CRM

1. **From Navbar**: Click "📧 Email" in the top navigation
2. **Direct URL**: Go to `http://localhost:9000/email`

### What You'll See

```
📧 Email Center

[12]        [75%]       [25%]       [3]
Sent      Open Rate   Click Rate  Interested

[✉️ Compose Email] [📊 Supplier Pipeline] [👥 Select Suppliers]
```

### Your First Email Campaign (3 Steps)

1. Click **"✉️ Compose Email"**
2. Select suppliers → Type products → Click **"🤖 Generate with AI"**
3. Review → Click **"📤 Send Emails"**

That's it! Emails are sent and tracked automatically.

---

## 📅 Daily Workflow

### Morning Routine (10 minutes)

1. **Check Dashboard** (`/email`)
   - See overnight email activity
   - Note any new "Interested" suppliers
   - Review open rates

2. **Check Pipeline** (`/email/pipeline`)
   - See who moved from "Contacted" → "Opened"
   - Identify suppliers ready for follow-up
   - Note new responses

3. **Send New Campaigns**
   - Target "New" suppliers with inquiries
   - Follow up with "Opened" suppliers
   - Thank "Interested" suppliers

### Afternoon Check (5 minutes)

1. Review response notifications
2. Check tasks generated from responses
3. Plan tomorrow's outreach

---

## 📤 Sending Emails

### Step 1: Access Compose Page

Click **"✉️ Compose Email"** from dashboard or go to `/email/compose`

### Step 2: Choose Email Type

```
[🔍 New Inquiry] [🔄 Follow-up]
```

- **New Inquiry**: First contact with supplier
- **Follow-up**: Check on previous email

### Step 3: Select Suppliers

```
┌─────────────────────────────┐
│ Mediterranean Oil Co (Italy) │ <- Click to select
│ Nordic Seafood AS (Norway)   │ <- Ctrl+Click for multiple
│ Asian Spice Trading (India)  │
└─────────────────────────────┘
```

**Tips**:
- Hold Ctrl (or Cmd on Mac) to select multiple
- Can select up to 50 at once
- Selected suppliers highlight in blue

### Step 4: Add Product Interest

```
Products/Interest: [sunflower oil, olive oil, organic]
```

Be specific! The AI uses this to personalize each email.

### Step 5: Generate with AI

Click **"🤖 Generate Emails with AI"**

You'll see a preview:
```
To: Mediterranean Oil Co (Italy)
Subject: Partnership Opportunity - FDX Trading
─────────────────────────────────
Dear Mediterranean Oil Co team,

I hope this message finds you well. I'm Udi from FDX Trading,
and we're interested in your sunflower oil products...

[Personalized for each supplier]
```

### Step 6: Send

Click **"📤 Send Emails"** → Confirm → Done!

---

## 📊 Understanding the Pipeline

### Pipeline View (`/email/pipeline`)

Your suppliers move through 4 stages:

```
🆕 New          📤 Contacted      👁️ Opened        ✅ Interested
(45)            (23)              (12)             (3)
│               │                 │                │
├─ Not emailed  ├─ Email sent     ├─ They opened   ├─ They replied
├─ Fresh leads  ├─ Waiting        ├─ Engaged       ├─ Want to deal
└─ [Send Email] └─ [Wait]         └─ [Follow Up]   └─ [View Details]
```

### What Each Stage Means

1. **🆕 New**: Suppliers you haven't contacted yet
2. **📤 Contacted**: Email sent, waiting for action
3. **👁️ Opened**: They opened your email (interested!)
4. **✅ Interested**: They responded positively

### Quick Actions from Pipeline

- **Send Email**: One-click to compose for that supplier
- **Follow Up**: Pre-fills follow-up email type
- **View Details**: See full supplier info and history

---

## 📈 Tracking & Analytics

### Dashboard Metrics

```
┌─────────┬──────────┬──────────┬────────────┐
│ Sent    │ Open Rate│ Click Rate│ Interested │
│ 156     │ 68%      │ 24%      │ 12         │
└─────────┴──────────┴──────────┴────────────┘
```

**What's Good?**
- Open Rate > 50% = Great
- Click Rate > 20% = Excellent  
- Interested > 5% = Success

### Email Status Indicators

In your recent emails list:

- **Sent** (gray) = Delivered
- **Opened** (blue) = They saw it
- **Clicked** (green) = They engaged

### What's Tracked Automatically

✅ **Opens**: When they view your email  
✅ **Clicks**: When they click your email/website  
✅ **Responses**: When they reply  
✅ **Time**: When each action happened  

---

## 🤖 AI Features

### 1. Email Generation

The AI writes personalized emails based on:
- Supplier name & country
- Products you specify
- Email type (inquiry/follow-up)

**Example Input**:
```
Supplier: Mediterranean Oil Co (Italy)
Products: organic sunflower oil
Type: Inquiry
```

**AI Output**:
```
Dear Mediterranean Oil Co team,

I hope this finds you well. I'm Udi from FDX Trading, and we're 
particularly interested in your organic sunflower oil products.

As a B2B food trading platform, we work with quality suppliers 
across Europe. Your Italian organic oils align perfectly with our 
buyers' requirements.

Could you share:
- Current pricing and MOQ
- Organic certifications
- Export capabilities

Looking forward to exploring partnership opportunities.

Best regards,
Udi - FDX Trading
```

### 2. Response Analysis

When suppliers reply, AI automatically:
- Categorizes: Interested / Not Interested / Needs Info
- Creates tasks: "Follow up with pricing" / "Send certifications"
- Summarizes: One-line summary of their response

---

## 💡 Best Practices

### Email Timing

**Best Days**: Tuesday - Thursday  
**Best Times**: 9-11 AM supplier's time zone  
**Avoid**: Mondays, Fridays, weekends  

### Subject Lines (Auto-generated)

The system uses proven subject lines:
- "Partnership Opportunity - FDX Trading"
- "Following up - FDX Trading"
- "Re: Your products - FDX Trading"

### Follow-up Schedule

```
Day 1: Initial inquiry
Day 3: Follow-up if opened but no response  
Day 7: Final follow-up
Day 14: Move to "cold" - try again in 3 months
```

### Volume Guidelines

As a 1-person operation:
- **Daily Max**: 50 new inquiries
- **Why**: Manageable responses
- **Focus**: Quality over quantity

---

## 🎯 Practical Examples

### Example 1: Monday Morning Outreach

```
1. Go to /email
2. Click "Compose Email"
3. Filter suppliers by country (e.g., "Italy")
4. Select 10-15 suppliers
5. Products: "olive oil, organic preferred"
6. Generate → Send
7. Total time: 5 minutes
```

### Example 2: Following Up on Opens

```
1. Go to /email/pipeline
2. Look at "Opened" column
3. For each supplier opened 2+ days ago:
   - Click "Follow Up"
   - AI generates follow-up
   - Send
4. Total time: 10 minutes for 20 follow-ups
```

### Example 3: Responding to Interest

```
1. Dashboard shows "3 Interested"
2. Click on supplier name
3. Read their requirements
4. Use "Compose" with specific answers
5. Send personalized response
6. Create task for next action
```

---

## 🔧 Troubleshooting

### Email Not Sending?

1. Check supplier has email address
2. Verify your SMTP settings (if configured)
3. Check logs in `/email` dashboard

### Low Open Rates?

1. Check spam folder instructions
2. Vary sending times
3. Ensure subject lines aren't too "salesy"

### No Responses?

1. Make emails more specific to their products
2. Follow up after 3 days
3. Try different product interests

### Can't See Tracking?

- Opens track when images are loaded
- Some email clients block tracking
- Clicks always track when they click links

---

## 📱 Mobile Usage

The Email CRM works on mobile:
1. Access same URL on phone
2. All features work
3. Tap to select suppliers
4. Swipe to see pipeline stages

---

## 🎓 Advanced Tips

### Bulk Operations

**Select All Italian Suppliers**:
1. Use browser search (Ctrl+F)
2. Type "Italy"
3. Click each highlighted supplier

**Template Your Products**:
Save common product searches:
- "organic oils and vinegars"
- "dried fruits and nuts"  
- "pasta and grains"

### Export Data

From dashboard, you can:
- Copy email list to clipboard
- Screenshot pipeline for reports
- Track weekly progress

---

## 📞 Quick Reference

### Keyboard Shortcuts

- `Ctrl+Click`: Select multiple suppliers
- `Ctrl+A`: Select all (in supplier box)
- `Enter`: Send form
- `Esc`: Cancel dialog

### URLs to Remember

- Dashboard: `/email`
- Compose: `/email/compose`  
- Pipeline: `/email/pipeline`
- Suppliers: `/suppliers`

### Daily Checklist

- [ ] Check overnight email activity
- [ ] Send 20-30 new inquiries  
- [ ] Follow up on yesterday's opens
- [ ] Respond to interested suppliers
- [ ] Plan tomorrow's targets

---

## 🎉 Success Metrics

After 1 month, you should see:
- 500+ suppliers contacted
- 60%+ open rate
- 20+ interested suppliers
- 5-10 active conversations
- 2-3 new partnerships

---

## Need Help?

1. **Technical Issues**: Check app logs
2. **Strategy Questions**: Follow best practices above
3. **Feature Requests**: The system is designed to stay simple!

Remember: The best email is the one that gets sent. Don't overthink - let AI help and focus on building relationships!

---

*Last updated: [Current Date] | Version 1.0*