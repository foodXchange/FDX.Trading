# Working with FoodXchange Agents - Operator Guide

## Quick Start: Your Agent Command Center

### 1. **Starting Your Day - Agent Dashboard**

Navigate to `/operator` or `/agent-dashboard` to see all agents at a glance:

```bash
# Start all agents with one command
python -m app.agents.start_all

# Or use the web interface
http://localhost:8000/operator
```

### 2. **Agent Control Methods**

#### **A. Web Interface (Easiest)**

```javascript
// Quick actions from dashboard
- Green Play Button: Start agent
- Orange Pause Button: Pause agent  
- Settings Icon: Configure agent
- Eye Icon: View detailed logs
```

#### **B. API Commands**

```bash
# Start email monitoring
curl -X POST http://localhost:8000/api/agents/email-monitor/start \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check agent status
curl http://localhost:8000/api/agents/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Run agent once (testing)
curl -X POST http://localhost:8000/api/agents/email-monitor/run-once \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### **C. Command Palette (Power User)**

Press `Ctrl+K` anywhere in the app:
```
> start all agents
> stop email monitor
> check price alerts
> run sourcing for tomatoes
> show agent logs
```

### 3. **Working with Each Agent**

## 📧 Email Monitor Agent

**What it does**: Processes supplier emails automatically

**How to work with it**:
```python
# Configure email monitoring
{
    "loop_interval": 300,  # Check every 5 minutes
    "max_emails_per_cycle": 50,
    "confidence_threshold": 0.7
}

# What you'll see:
- ✅ "Email from supplier processed"
- 📊 "Quote extracted: $2.50/kg tomatoes"
- 🔄 "Supplier record updated"

# When to intervene:
- Red badge on email icon = processing errors
- Low confidence emails flagged for review
- Unknown suppliers need verification
```

**Quick Actions**:
- **Test Email**: Send test@supplier.com to see processing
- **View Queue**: See pending emails
- **Adjust Rules**: Change auto-processing criteria

## 🎯 Smart Sourcing Agent

**What it does**: Automatically matches buyers with best suppliers

**How to work with it**:
```python
# Trigger sourcing for specific buyer
POST /api/agents/smart-sourcing/generate
{
    "buyer_id": 123,
    "urgent": true
}

# Configure matching criteria
{
    "min_match_score": 0.7,
    "max_recommendations": 5,
    "include_new_suppliers": true
}

# What you'll see:
- 🎯 "3 suppliers matched for olive oil RFQ"
- 💯 "Best match: Mediterranean Imports (95%)"
- 💰 "Potential savings: $3,200"

# When to intervene:
- No matches found (expand criteria)
- All matches below 70% (manual search needed)
- Urgent RFQs (prioritize manually)
```

**Quick Actions**:
- **Auto-Match**: Let AI pick best supplier
- **Expand Search**: Include more regions/products
- **Override Match**: Manually select supplier

## 💰 Price Intelligence Agent

**What it does**: Monitors prices and alerts on opportunities

**How to work with it**:
```python
# Set price alerts
POST /api/agents/price-intelligence/alerts
{
    "products": ["tomatoes", "olive oil", "cheese"],
    "threshold": 5,  # Alert on 5% change
    "check_frequency": "hourly"
}

# What you'll see:
- 📉 "Tomatoes down 18% - save $3,200"
- 📈 "Olive oil rising - lock in prices?"
- 🎉 "New historical low for cheese"

# When to intervene:
- Urgent price drops (buy immediately)
- Volatile products (adjust thresholds)
- Seasonal opportunities (plan ahead)
```

**Quick Actions**:
- **Lock Price**: Commit to current price for 30-60 days
- **Bulk Alert**: Combine orders for better pricing
- **Set Budget**: Auto-buy when price hits target

### 4. **Daily Agent Workflows**

## Morning Routine (8:00 AM)
```markdown
1. Open operator dashboard
2. Check overnight agent activity:
   - Emails processed: 23
   - New supplier matches: 5
   - Price alerts: 3
3. Review priority items (red badges)
4. Approve/reject agent recommendations
5. Adjust any failing agents
```

## Midday Check (12:00 PM)
```markdown
1. Quick command: "agent status" (Ctrl+K)
2. View any urgent alerts on mobile
3. Approve pending quotes < $10K
4. Let agents continue
```

## End of Day (5:00 PM)
```markdown
1. Review agent performance metrics
2. Check tomorrow's scheduled RFQs
3. Set any special monitoring for overnight
4. Agents continue working 24/7
```

### 5. **Agent Communication Patterns**

## Understanding Agent Messages

**Success Messages**:
```
✅ Email processed successfully
🎯 3 suppliers matched
💰 Price alert: Save $500
📊 Quote analysis complete
```

**Warning Messages**:
```
⚠️ Low confidence match (65%)
⚠️ Email parsing unclear
⚠️ Price data stale (>24h)
⚠️ Supplier not verified
```

**Error Messages**:
```
❌ Email server connection failed
❌ AI service unavailable  
❌ Database write failed
❌ Agent crashed - restarting
```

## Responding to Agent Notifications

**Priority Levels**:
1. **🔴 URGENT**: Respond within 1 hour
2. **🟡 HIGH**: Respond within 4 hours  
3. **🟢 NORMAL**: Respond within 24 hours
4. **⚪ INFO**: No response needed

### 6. **Advanced Agent Operations**

## Bulk Operations
```bash
# Process all pending emails at once
POST /api/agents/email-monitor/process-all

# Generate recommendations for all buyers
POST /api/agents/smart-sourcing/bulk-generate

# Update all price alerts
POST /api/agents/price-intelligence/refresh-all
```

## Agent Chaining
```python
# Chain agents for complex workflows
workflow = {
    "name": "New Supplier Onboarding",
    "steps": [
        {"agent": "email_monitor", "action": "extract_supplier_info"},
        {"agent": "trust_compliance", "action": "verify_supplier"},
        {"agent": "smart_sourcing", "action": "match_to_buyers"},
        {"agent": "notification", "action": "alert_matched_buyers"}
    ]
}
```

## Custom Agent Rules
```python
# Create custom automation rules
rule = {
    "name": "Auto-approve trusted suppliers",
    "condition": {
        "supplier_rating": ">= 4.5",
        "order_history": "> 10",
        "quote_amount": "< 5000"
    },
    "action": "auto_approve_quote"
}
```

### 7. **Troubleshooting Agents**

## Common Issues and Solutions

**Agent Not Starting**:
```bash
# Check logs
tail -f logs/agents/email_monitor.log

# Restart agent service
systemctl restart foodxchange-agents

# Clear agent state
redis-cli DEL agent:email_monitor:state
```

**Agent Processing Slowly**:
```python
# Adjust performance settings
{
    "batch_size": 10,  # Reduce from 50
    "parallel_workers": 2,  # Reduce from 4
    "timeout": 30  # Increase from 10
}
```

**Agent Making Wrong Decisions**:
```python
# Adjust confidence thresholds
{
    "min_confidence": 0.8,  # Increase from 0.7
    "require_human_review": true,  # For critical decisions
    "learning_mode": true  # Agent learns from corrections
}
```

### 8. **Mobile Agent Control**

## Working with Agents on Mobile

**Quick Actions** (Swipe gestures):
- Swipe right: Approve recommendation
- Swipe left: Reject recommendation  
- Long press: View details
- Pull down: Refresh status

**Voice Commands**:
```
"Hey FoodXchange..."
- "Run email agent"
- "Check tomato prices"
- "Find olive oil suppliers"
- "Approve all quotes under 5000"
```

**Push Notifications**:
```javascript
// Configure what triggers push alerts
{
    "urgent_quotes": true,
    "price_drops": "> 10%",
    "new_suppliers": "matching_products",
    "agent_errors": true
}
```

### 9. **Agent Performance Optimization**

## Making Agents Work Better

**1. Train Agents with Feedback**:
```python
# Mark good/bad decisions
POST /api/agents/feedback
{
    "agent": "smart_sourcing",
    "decision_id": "123",
    "feedback": "correct",
    "notes": "Perfect supplier match"
}
```

**2. Optimize Schedules**:
```python
# Run heavy agents during off-hours
schedule = {
    "price_intelligence": "*/30 * * * *",  # Every 30 min
    "email_monitor": "*/5 * * * *",  # Every 5 min
    "smart_sourcing": "0 6,12,18 * * *",  # 3x daily
    "compliance_check": "0 2 * * *"  # 2 AM daily
}
```

**3. Set Resource Limits**:
```yaml
# Prevent agents from overwhelming system
agent_limits:
  email_monitor:
    max_cpu: 25%
    max_memory: 1GB
    max_concurrent: 10
  
  smart_sourcing:
    max_cpu: 50%
    max_memory: 2GB
    max_concurrent: 5
```

### 10. **Your Agent Playbook**

## Week 1: Getting Started
- ✅ Start email monitor agent
- ✅ Configure price alerts for top 10 products
- ✅ Test smart sourcing with 1 RFQ
- ✅ Review and approve agent decisions

## Week 2: Building Trust
- 📈 Increase automation thresholds
- 🎯 Let agents handle routine quotes
- 📊 Review weekly agent performance
- 🔧 Fine-tune based on results

## Week 3: Advanced Automation
- 🔗 Create agent workflows
- 📱 Enable mobile controls
- 🎙️ Set up voice commands
- 📈 Implement custom rules

## Week 4: Full Automation
- 🚀 90%+ automation rate
- 🎯 Agents handle all routine tasks
- 👤 You focus on strategy
- 💰 Measure ROI improvement

## Emergency Agent Commands

```bash
# STOP ALL AGENTS
curl -X POST http://localhost:8000/api/agents/emergency-stop

# RESTART ALL AGENTS  
curl -X POST http://localhost:8000/api/agents/restart-all

# SAFE MODE (manual approval required)
curl -X POST http://localhost:8000/api/agents/safe-mode

# EXPORT AGENT DECISIONS (for audit)
curl http://localhost:8000/api/agents/export-decisions > decisions.json
```

Remember: Agents are your virtual team. Trust them with routine tasks, but stay in control of strategic decisions. The goal is to work 10 hours/week while providing 24/7 service to your marketplace!