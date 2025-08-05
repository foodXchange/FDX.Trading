# 🎯 FoodXchange Quick Reference Card

## 🔑 Essential Info
- **VM IP**: `4.206.1.15`
- **SSH**: `ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15`
- **App**: http://4.206.1.15:8000
- **Cost**: $0/month (Founders Hub)

## ⚡ Daily Commands
```bash
# Connect to VM
ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15

# Check everything
fdx-status

# Work with Claude
fdx-claude

# Detach (keep running)
Ctrl+B, D

# View logs
fdx-logs
```

## 🚨 Emergency Fixes
```bash
# App down
sudo systemctl restart fdx-app

# High CPU/Memory
htop  # Then kill process

# Can't connect
az vm start --resource-group foodxchange-founders-rg --name fdx-founders-vm

# Disk full
df -h
rm -rf /tmp/*
```

## 📱 iPhone Commands
```bash
# In Termius, create snippets:

# Quick health
fdx-status && echo "✅ All good"

# Restart app
sudo systemctl restart fdx-app

# Check logs
tail -20 ~/fdx/logs/app.log
```

## 💰 Cost Control
```bash
# Check credits (local)
./monitor_costs_automated.sh

# Stop VM (save $4/day)
az vm deallocate --resource-group foodxchange-founders-rg --name fdx-founders-vm

# Start VM
az vm start --resource-group foodxchange-founders-rg --name fdx-founders-vm
```

## 🔧 Business Tools
| Tool | Status | Cost | Action |
|------|--------|------|--------|
| SendGrid | Ready | $19.95/mo | Add API key to .env |
| Wave | Ready | FREE | Sign up at waveapps.com |
| Stripe | Template | 2.9% | Add keys when ready |
| Domain | Pending | $12/yr | Buy when ready |

## 📊 Success Metrics
- **Uptime Target**: 99.9%
- **Response Time**: <200ms
- **Daily Tasks**: 10 mins
- **Break-even**: 1 customer

## 🎯 Growth Targets
- **Week 1**: First user
- **Month 1**: First customer
- **Month 3**: $1K MRR
- **Month 6**: $10K MRR

## 📞 Quick Contacts
- **Azure Support**: Included with Founders Hub
- **Your GitHub**: github.com/foodXchange/FDX.Trading
- **Monitoring**: http://4.206.1.15:3000

## 💡 Remember
1. **tmux = persistent** (never lose work)
2. **Costs = $0** (for 2 years!)
3. **Automate everything** (time is money)
4. **Track metrics** (data drives growth)
5. **Stay lean** (only buy what pays)

---
**Manager Script**: `./fdx_manager.sh`
**Full Docs**: `LEAN_STARTUP_COMPLETE.md`