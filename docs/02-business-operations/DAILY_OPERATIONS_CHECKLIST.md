# 📋 FoodXchange Daily Operations Checklist

## 🌅 Morning Routine (5 minutes)

### 1. Check System Health
```bash
# From your local machine or phone
ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15

# Quick health check
fdx-health
fdx-status

# Check app is running
curl -s http://localhost:8000/health || echo "App needs restart"
```

### 2. Review Overnight Activity
- [ ] Check email for customer inquiries
- [ ] Review any error alerts
- [ ] Check backup completion
- [ ] Monitor disk/memory usage

### 3. Start Development Session
```bash
# Attach to Claude if needed
fdx-claude

# Or attach to production monitoring
fdx-prod
```

## 📊 Midday Check (2 minutes)

### Quick Metrics Review
- [ ] New user signups
- [ ] Active RFQs
- [ ] Email delivery status
- [ ] API response times

### Cost Check (Mondays only)
```bash
# From local machine
./monitor_costs_automated.sh
```

## 🌙 Evening Routine (3 minutes)

### 1. Backup Verification
```bash
# Check today's backup
ls -la ~/fdx/backups/
```

### 2. Update Task List
- [ ] Mark completed tasks
- [ ] Add tomorrow's priorities
- [ ] Note any issues for follow-up

### 3. Secure Shutdown
```bash
# Detach from tmux (keeps running)
Ctrl+B then D

# Exit SSH
exit
```

## 📱 Mobile Quick Checks (1 minute)

### From iPhone (Termius)
```bash
# Quick connect
ssh fdx

# One-line health check
fdx-status && echo "✅ All good" || echo "❌ Check needed"

# Detach
Ctrl+B, D
```

## 🚨 Emergency Procedures

### App Down
```bash
# Restart FastAPI
sudo systemctl restart fdx-app

# Or manually
cd ~/fdx/app
source venv/bin/activate
killall uvicorn
nohup uvicorn app:app --host 0.0.0.0 --port 8000 &
```

### Database Issues
```bash
# Check connection
psql $DATABASE_URL -c "SELECT 1"

# Restart if needed
sudo systemctl restart postgresql
```

### High Resource Usage
```bash
# Check what's consuming resources
htop

# Clear cache/temp files
rm -rf /tmp/*
df -h  # Check disk space
```

## 📊 Weekly Tasks

### Monday - Financial Review
- [ ] Run cost report: `./monitor_costs_automated.sh`
- [ ] Check Wave Accounting
- [ ] Review revenue vs expenses
- [ ] Plan week's development priorities

### Wednesday - System Maintenance  
- [ ] Test backup recovery
- [ ] Update dependencies
- [ ] Clear old logs
- [ ] Check SSL certificate expiry

### Friday - Business Development
- [ ] Review customer feedback
- [ ] Update CRM (when set up)
- [ ] Plan next week's outreach
- [ ] Document lessons learned

## 🎯 Key Metrics to Track

### Daily
- **Uptime**: Target 99.9%
- **Response Time**: <200ms
- **Email Delivery**: >95%
- **Error Rate**: <1%

### Weekly
- **New Users**: Track growth %
- **Active RFQs**: Measure engagement
- **Cost per User**: Keep under $0.50
- **Revenue**: Progress to break-even

### Monthly
- **MRR**: Monthly Recurring Revenue
- **Churn**: User retention rate
- **CAC**: Customer Acquisition Cost
- **LTV**: Lifetime Value

## 🛠️ Automation Opportunities

### Already Automated
- ✅ Daily backups (2 AM)
- ✅ Health checks (every 5 min)
- ✅ Auto-shutdown (10 PM)
- ✅ SSL renewal (Certbot)

### To Automate Next
- [ ] Customer onboarding emails
- [ ] Invoice generation
- [ ] Usage reports
- [ ] Social media posts

## 💡 Time-Saving Aliases

Add to your local `~/.bashrc`:
```bash
# FoodXchange shortcuts
alias fdx-ssh='ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15'
alias fdx-health='fdx-ssh "fdx-health"'
alias fdx-logs='fdx-ssh "fdx-logs"'
alias fdx-costs='./monitor_costs_automated.sh'

# Quick monitoring
alias fdx-check='fdx-ssh "fdx-status && df -h && free -h"'
```

## 📈 Growth Checklist

### When you hit 10 users:
- [ ] Set up proper email sequences
- [ ] Implement basic analytics
- [ ] Create help documentation

### When you hit 50 users:
- [ ] Add customer support tool
- [ ] Implement caching layer
- [ ] Set up staging environment

### When you hit 100 users:
- [ ] Hire virtual assistant
- [ ] Upgrade to B4ms VM
- [ ] Implement CDN

## 🎯 Daily Success Criteria

A successful day includes:
- ✅ 100% uptime maintained
- ✅ All customer emails answered
- ✅ At least 1 feature improved
- ✅ Costs tracked and optimized
- ✅ Progress toward revenue goals

---

**Remember**: 10 minutes/day of operations work keeps everything running smoothly!