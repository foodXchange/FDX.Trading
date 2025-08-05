# 🚀 Lean Business Setup Guide for FoodXchange

## ✅ Current Status
- **Infrastructure**: Azure VM running (FREE with Founders Hub)
- **App**: FastAPI running at http://4.206.1.15:8000
- **Database**: Connected to your existing PostgreSQL
- **Sessions**: Persistent Claude sessions active

## 📧 1. Email Setup with SendGrid ($19.95/month)

### Why SendGrid?
- 50,000 emails/month for $19.95
- 99.9% deliverability
- Built-in analytics
- Easy API integration

### Setup Steps:
```bash
# 1. Sign up at sendgrid.com
# 2. Choose "Email API" → "Web API"
# 3. Create API key with 'Mail Send' permission
# 4. Add to your VM's .env file:

ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15
cd ~/fdx/app
nano .env

# Add:
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@fdx.trading
```

### Integration Code:
```python
# Already in your app! Just add the API key
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to_email, subject, content):
    message = Mail(
        from_email=os.getenv('FROM_EMAIL'),
        to_emails=to_email,
        subject=subject,
        html_content=content
    )
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        print(f"Error: {e}")
```

## 💰 2. Accounting with Wave (FREE)

### Setup:
1. Sign up at [waveapps.com](https://www.waveapps.com)
2. Connect your business bank account
3. Set up invoice templates
4. Enable payment processing (2.9% + 30¢ per transaction)

### Key Features:
- ✅ Unlimited invoicing
- ✅ Receipt scanning
- ✅ Financial reports
- ✅ Tax preparation
- ✅ Multi-currency support

### Monthly Workflow:
1. Import bank transactions
2. Categorize expenses
3. Send invoices to clients
4. Generate P&L report
5. Export for taxes

## 💳 3. Payment Processing with Stripe

### Setup:
```bash
# 1. Sign up at stripe.com
# 2. Complete business verification
# 3. Get API keys from dashboard
# 4. Add to .env:

STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Integration:
```python
import stripe
stripe.api_key = os.getenv('STRIPE_API_KEY')

# Create payment intent
def create_payment(amount, currency='usd'):
    intent = stripe.PaymentIntent.create(
        amount=amount * 100,  # cents
        currency=currency,
        automatic_payment_methods={'enabled': True}
    )
    return intent.client_secret
```

### Fees:
- 2.9% + 30¢ per transaction
- No monthly fees
- International: +1%

## 📊 4. CRM with HubSpot (FREE)

### Setup:
1. Sign up at [hubspot.com](https://www.hubspot.com)
2. Import contacts via CSV
3. Get API key: Settings → Integrations → API Key
4. Connect to FoodXchange

### Features (Free Tier):
- 1,000,000 contacts
- Email tracking
- Deal pipeline
- Basic automation
- Mobile app

### API Integration:
```python
from hubspot import HubSpot

api_client = HubSpot(access_token=os.getenv('HUBSPOT_TOKEN'))

# Create contact
contact = api_client.crm.contacts.basic_api.create(
    simple_public_object_input={
        "properties": {
            "email": "supplier@example.com",
            "firstname": "John",
            "lastname": "Doe",
            "company": "Supplier Co"
        }
    }
)
```

## 📈 5. Analytics Setup

### Google Analytics 4 (FREE)
```html
<!-- Add to base.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXX');
</script>
```

### Mixpanel ($20/month after free tier)
- User behavior tracking
- Funnel analysis
- Retention reports
- A/B testing

## 🔧 6. Business Operations Tools

### Communication
- **Slack** (Free): Team chat when you grow
- **Calendly** (Free): Appointment scheduling
- **Loom** ($12.50/month): Video tutorials

### Project Management
- **Notion** ($8/month): Documentation + tasks
- **GitHub Projects** (Free): Development tracking

### Customer Support
- **Crisp** (Free tier): Live chat widget
- **Help Scout** ($20/month): When you scale

## 💼 7. Legal & Compliance

### Business Structure
```bash
# LLC Formation (~$200)
1. Choose state (Delaware or your home state)
2. File Articles of Organization
3. Get EIN from IRS (free)
4. Open business bank account
```

### Required Documents
- [ ] Operating Agreement
- [ ] Privacy Policy
- [ ] Terms of Service
- [ ] Cookie Policy (for EU)

### Insurance
- **General Liability**: $200-400/year
- **Professional Liability**: $300-500/year
- **Cyber Insurance**: $150-300/year

## 📊 8. Monthly Cost Summary

### Essential (Start Here)
- Azure VM: $0 (Founders Hub)
- SendGrid: $19.95
- Wave: $0
- **Total: $19.95/month**

### Growth Phase (+3 months)
- Add Stripe: 2.9% of revenue
- Add Notion: $8
- Add Mixpanel: $20
- **Total: ~$48/month + fees**

### Scale Phase (+6 months)
- Add Help Scout: $20
- Add Loom: $12.50
- Add Reserved Instance: Save 35%
- **Total: ~$80/month + fees**

## 🎯 Next Steps Checklist

### This Week:
- [ ] Set up SendGrid account
- [ ] Configure Wave Accounting
- [ ] Form LLC (if not done)
- [ ] Get business insurance quotes

### Next Month:
- [ ] Implement Stripe payments
- [ ] Set up HubSpot CRM
- [ ] Add Google Analytics
- [ ] Create legal documents

### In 3 Months:
- [ ] Evaluate analytics data
- [ ] Optimize conversion funnel
- [ ] Consider hiring VA
- [ ] Plan for scale

## 🚀 Quick Commands

### Check VM costs:
```bash
./monitor_founders_credits.sh
```

### Set up business tools:
```bash
ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15
./setup_business_tools.sh
```

### View app metrics:
```bash
# Grafana dashboard
open http://4.206.1.15:3000
```

## 💡 Pro Tips

1. **Start minimal**: Just SendGrid + Wave first month
2. **Track everything**: Every expense, every customer interaction
3. **Automate early**: Set up email sequences, invoice reminders
4. **Stay lean**: Don't buy tools until you need them
5. **Focus on revenue**: Tools should pay for themselves

---

**Remember**: You have $150/month in Azure credits for 2 years. Use them wisely to build a profitable business before they expire!