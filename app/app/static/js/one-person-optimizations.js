/**
 * One-Person Enterprise Operations Optimizations
 * Designed for managing large B2B food operations single-handedly
 */

class OnePersonOperations {
    constructor() {
        this.enterpriseAccounts = new Map();
        this.quickActions = [];
        this.automationRules = new Map();
        this.voiceEnabled = false;
        this.touchGestures = new Map();
        
        this.init();
    }
    
    init() {
        this.setupKeyboardMacros();
        this.initializeQuickActions();
        this.loadEnterpriseRelationships();
        this.setupMobileGestures();
        this.initializeTimeZoneAwareness();
        this.setupBulkOperations();
    }
    
    // Keyboard Macros for Power Users
    setupKeyboardMacros() {
        const macros = {
            // Single key press for common enterprise operations
            'a': () => this.approveAllUnder(50000), // Approve all quotes under $50K
            'r': () => this.reorderTopProducts(),   // Reorder frequently purchased items
            'p': () => this.checkPaymentStatus(),   // Check all overdue payments
            'e': () => this.exportDailyReport(),    // Export daily summary
            'c': () => this.callNextAccount(),      // Call next scheduled account
            's': () => this.scanNewRFQs(),          // Scan and categorize new RFQs
            'w': () => this.checkWarnings(),        // Check all system warnings
            'q': () => this.quickQuote(),           // Generate quick quote template
        };
        
        // Hold Shift for macro mode
        let macroMode = false;
        document.addEventListener('keydown', (e) => {
            if (e.shiftKey && e.altKey) {
                macroMode = true;
                this.showMacroIndicator();
            }
            
            if (macroMode && macros[e.key]) {
                e.preventDefault();
                macros[e.key]();
                this.showMacroFeedback(e.key);
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (!e.shiftKey || !e.altKey) {
                macroMode = false;
                this.hideMacroIndicator();
            }
        });
    }
    
    // Quick Actions for Mobile/Touch
    initializeQuickActions() {
        this.quickActions = [
            {
                id: 'approve-all-safe',
                label: 'Approve Safe Orders',
                icon: '✅',
                description: 'Approve all orders from platinum accounts under $100K',
                action: async () => {
                    const result = await this.bulkApprove({
                        maxAmount: 100000,
                        accountTier: 'platinum',
                        requiresCompliance: true
                    });
                    this.notify(`Approved ${result.count} orders totaling $${result.total.toLocaleString()}`);
                }
            },
            {
                id: 'daily-checkin',
                label: 'Daily Check-in',
                icon: '📱',
                description: 'Send status updates to all key accounts',
                action: async () => {
                    const updates = await this.sendBulkStatusUpdates();
                    this.notify(`Sent updates to ${updates.length} accounts`);
                }
            },
            {
                id: 'smart-reorder',
                label: 'Smart Reorder',
                icon: '🔄',
                description: 'Reorder all products below safety stock',
                action: async () => {
                    const orders = await this.createSmartReorders();
                    this.notify(`Created ${orders.length} reorders saving $${orders.totalSavings}`);
                }
            },
            {
                id: 'payment-chase',
                label: 'Chase Payments',
                icon: '💰',
                description: 'Auto-follow up on overdue payments',
                action: async () => {
                    const result = await this.chaseOverduePayments();
                    this.notify(`Sent ${result.reminders} reminders for $${result.totalDue.toLocaleString()}`);
                }
            }
        ];
    }
    
    // Enterprise Relationship Memory
    loadEnterpriseRelationships() {
        // Store key information about each major account
        this.enterpriseAccounts.set('walmart', {
            tier: 'platinum',
            monthlyVolume: 2800000,
            paymentTerms: 'NET30',
            keyContact: 'Sarah Johnson',
            preferences: {
                communication: 'email',
                orderTime: '6AM EST',
                requiresDocs: ['invoice', 'packing-list', 'cert-of-origin'],
                specialRequirements: ['GFSI certification', 'sustainability report']
            },
            automatedActions: {
                autoApproveUnder: 100000,
                priorityFulfillment: true,
                customPricing: true
            },
            lastInteraction: new Date(),
            notes: 'Prefers early morning deliveries, very strict on compliance'
        });
        
        this.enterpriseAccounts.set('wholefoods', {
            tier: 'platinum',
            monthlyVolume: 1900000,
            paymentTerms: 'NET15',
            keyContact: 'Mike Chen',
            preferences: {
                communication: 'phone',
                orderTime: '8AM PST',
                requiresDocs: ['organic-cert', 'non-gmo-cert', 'invoice'],
                specialRequirements: ['organic only', 'local sourcing preferred']
            },
            automatedActions: {
                autoApproveUnder: 75000,
                priorityFulfillment: true,
                qualityCheckRequired: true
            },
            lastInteraction: new Date(),
            notes: 'Very quality focused, appreciates proactive communication'
        });
    }
    
    // Time Zone Aware Scheduling
    initializeTimeZoneAwareness() {
        this.timeZones = {
            'walmart': 'America/New_York',
            'wholefoods': 'America/Los_Angeles',
            'sysco': 'America/Chicago',
            'kroger': 'America/New_York',
            'costco': 'America/Los_Angeles'
        };
        
        // Schedule actions based on customer time zones
        this.scheduleTimeZoneActions();
    }
    
    scheduleTimeZoneActions() {
        // Check each account's local time and schedule appropriate actions
        setInterval(() => {
            for (const [account, timezone] of Object.entries(this.timeZones)) {
                const localTime = new Date().toLocaleTimeString('en-US', { 
                    timeZone: timezone,
                    hour: 'numeric',
                    hour12: false 
                });
                
                // Morning check-ins (8 AM local time)
                if (localTime === '8') {
                    this.sendMorningUpdate(account);
                }
                
                // End of day summaries (5 PM local time)
                if (localTime === '17') {
                    this.sendEODSummary(account);
                }
            }
        }, 3600000); // Check every hour
    }
    
    // Bulk Operations for Enterprise Scale
    setupBulkOperations() {
        this.bulkOperations = {
            // Approve multiple quotes at once
            approveQuotes: async (filters) => {
                const quotes = await this.getFilteredQuotes(filters);
                const approved = [];
                
                for (const quote of quotes) {
                    if (this.isAutoApprovable(quote)) {
                        await this.approveQuote(quote.id);
                        approved.push(quote);
                    }
                }
                
                return {
                    total: quotes.length,
                    approved: approved.length,
                    totalValue: approved.reduce((sum, q) => sum + q.value, 0)
                };
            },
            
            // Bulk price updates
            updatePrices: async (priceChanges) => {
                const updates = [];
                
                for (const change of priceChanges) {
                    // Notify affected customers
                    const affectedOrders = await this.getAffectedOrders(change.product);
                    
                    for (const order of affectedOrders) {
                        if (change.increase && order.account.tier === 'platinum') {
                            // Grandfather pricing for platinum accounts
                            continue;
                        }
                        
                        updates.push({
                            order: order.id,
                            oldPrice: order.price,
                            newPrice: change.newPrice,
                            impact: (change.newPrice - order.price) * order.quantity
                        });
                    }
                }
                
                return updates;
            },
            
            // Bulk compliance checks
            verifyCompliance: async () => {
                const suppliers = await this.getAllActiveSuppliers();
                const nonCompliant = [];
                
                for (const supplier of suppliers) {
                    const complianceStatus = await this.checkSupplierCompliance(supplier);
                    
                    if (!complianceStatus.isCompliant) {
                        nonCompliant.push({
                            supplier: supplier.name,
                            issues: complianceStatus.issues,
                            action: complianceStatus.requiredAction
                        });
                    }
                }
                
                // Auto-notify and set reminders
                if (nonCompliant.length > 0) {
                    await this.handleNonCompliance(nonCompliant);
                }
                
                return nonCompliant;
            }
        };
    }
    
    // Mobile Gesture Controls
    setupMobileGestures() {
        if (!this.isMobile()) return;
        
        let touchStartX = 0;
        let touchStartY = 0;
        
        document.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', (e) => {
            if (!touchStartX || !touchStartY) return;
            
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            
            const deltaX = touchEndX - touchStartX;
            const deltaY = touchEndY - touchStartY;
            
            // Swipe actions
            if (Math.abs(deltaX) > Math.abs(deltaY)) {
                if (deltaX > 50) {
                    // Swipe right - Approve
                    this.handleSwipeApprove();
                } else if (deltaX < -50) {
                    // Swipe left - Decline/Skip
                    this.handleSwipeDecline();
                }
            } else {
                if (deltaY > 50) {
                    // Swipe down - Refresh
                    this.refreshDashboard();
                } else if (deltaY < -50) {
                    // Swipe up - Quick actions
                    this.showQuickActionsMenu();
                }
            }
            
            touchStartX = 0;
            touchStartY = 0;
        });
        
        // Long press for details
        let pressTimer;
        document.addEventListener('touchstart', (e) => {
            pressTimer = setTimeout(() => {
                this.showDetailedView(e.target);
            }, 500);
        });
        
        document.addEventListener('touchend', () => {
            clearTimeout(pressTimer);
        });
    }
    
    // Smart Notifications
    notify(message, options = {}) {
        const {
            priority = 'normal',
            requiresAction = false,
            account = null,
            amount = null
        } = options;
        
        // Desktop notification
        if (Notification.permission === 'granted') {
            const notification = new Notification('FoodXchange', {
                body: message,
                icon: '/static/img/logo.png',
                badge: '/static/img/badge.png',
                tag: priority === 'urgent' ? 'urgent' : 'normal',
                requireInteraction: requiresAction
            });
            
            notification.onclick = () => {
                window.focus();
                if (account) {
                    this.openAccount(account);
                }
            };
        }
        
        // In-app notification
        this.showInAppNotification(message, priority);
        
        // Log for audit trail
        this.logActivity({
            type: 'notification',
            message,
            priority,
            account,
            amount,
            timestamp: new Date()
        });
    }
    
    // Voice Commands Integration
    setupVoiceCommands() {
        const commands = {
            'approve all': () => this.approveAllUnder(100000),
            'check walmart': () => this.openAccount('walmart'),
            'payment status': () => this.checkPaymentStatus(),
            'daily summary': () => this.generateDailySummary(),
            'call': (account) => this.initiateCall(account),
            'quote for': (params) => this.generateQuickQuote(params),
            'reorder': (product) => this.reorderProduct(product),
            'urgent': () => this.showUrgentItems()
        };
        
        // Voice command processor
        this.processVoiceCommand = (transcript) => {
            const lower = transcript.toLowerCase();
            
            for (const [command, action] of Object.entries(commands)) {
                if (lower.includes(command)) {
                    const params = lower.replace(command, '').trim();
                    action(params);
                    return true;
                }
            }
            
            return false;
        };
    }
    
    // Automation Rules Engine
    createAutomationRule(rule) {
        this.automationRules.set(rule.id, {
            ...rule,
            active: true,
            created: new Date(),
            lastTriggered: null,
            triggerCount: 0
        });
        
        // Example rules for one-person operation
        this.automationRules.set('auto-approve-trusted', {
            name: 'Auto-approve trusted accounts',
            condition: (order) => {
                const account = this.enterpriseAccounts.get(order.accountId);
                return account && 
                       account.tier === 'platinum' && 
                       order.total < account.automatedActions.autoApproveUnder;
            },
            action: async (order) => {
                await this.approveOrder(order.id);
                this.notify(`Auto-approved order #${order.id} for ${order.accountName}`, {
                    account: order.accountId,
                    amount: order.total
                });
            }
        });
        
        this.automationRules.set('payment-reminder', {
            name: 'Automatic payment reminders',
            schedule: '0 9 * * *', // 9 AM daily
            action: async () => {
                const overdue = await this.getOverduePayments();
                for (const payment of overdue) {
                    if (payment.daysOverdue > 5) {
                        await this.sendPaymentReminder(payment);
                    }
                }
            }
        });
    }
    
    // Helper Methods
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    showMacroIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'macro-indicator';
        indicator.innerHTML = '⌨️ Macro Mode Active';
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #1e293b;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 30px;
            font-weight: 600;
            z-index: 10000;
            animation: fadeIn 0.3s;
        `;
        document.body.appendChild(indicator);
    }
    
    hideMacroIndicator() {
        const indicator = document.getElementById('macro-indicator');
        if (indicator) indicator.remove();
    }
    
    showMacroFeedback(key) {
        const feedback = document.createElement('div');
        feedback.innerHTML = `✓ Macro '${key}' executed`;
        feedback.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: #22c55e;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            animation: slideIn 0.3s;
            z-index: 10001;
        `;
        document.body.appendChild(feedback);
        
        setTimeout(() => feedback.remove(), 2000);
    }
    
    async generateDailySummary() {
        const summary = {
            revenue: await this.getTodayRevenue(),
            orders: await this.getTodayOrders(),
            newAccounts: await this.getNewAccounts(),
            issues: await this.getActiveIssues(),
            opportunities: await this.getOpportunities()
        };
        
        return summary;
    }
}

// Initialize on page load
const onePersonOps = new OnePersonOperations();

// Global keyboard shortcut for command palette
document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        onePersonOps.openCommandPalette();
    }
});

// Export for use in other modules
window.OnePersonOperations = OnePersonOperations;