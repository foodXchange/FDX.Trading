/**
 * Agent Manager - Real-time Integration for One-Person Operations
 * Provides unified control and monitoring across the entire system
 */

class AgentManager {
    constructor() {
        this.agents = new Map();
        this.notifications = [];
        this.ws = null;
        this.dashboardMode = 'overview'; // overview, details, alerts
        this.autoActions = new Map(); // Automated responses
        
        this.init();
    }
    
    init() {
        // WebSocket for real-time updates
        this.connectWebSocket();
        
        // Initialize notification system
        this.setupNotifications();
        
        // Auto-refresh data
        this.startAutoRefresh();
        
        // Keyboard shortcuts for quick actions
        this.setupKeyboardShortcuts();
    }
    
    connectWebSocket() {
        const wsUrl = `ws://${window.location.host}/ws/agents`;
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleRealtimeUpdate(data);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showNotification('Connection lost. Retrying...', 'error');
            setTimeout(() => this.connectWebSocket(), 5000);
        };
    }
    
    handleRealtimeUpdate(data) {
        switch(data.type) {
            case 'agent_state_change':
                this.updateAgentState(data.agent_id, data.state);
                if (data.state === 'error') {
                    this.showNotification(`Agent ${data.agent_id} encountered an error!`, 'error', {
                        actions: [
                            { label: 'View Details', action: () => this.showAgentDetails(data.agent_id) },
                            { label: 'Restart', action: () => this.restartAgent(data.agent_id) }
                        ]
                    });
                }
                break;
                
            case 'email_processed':
                this.updateEmailMetrics(data);
                if (data.intent === 'urgent_quote') {
                    this.showNotification('Urgent quote received!', 'warning', {
                        actions: [
                            { label: 'View Quote', action: () => this.navigateToQuote(data.quote_id) },
                            { label: 'Auto-Respond', action: () => this.autoRespond(data.email_id) }
                        ]
                    });
                }
                break;
                
            case 'supplier_updated':
                this.updateSupplierWidget(data);
                break;
                
            case 'system_alert':
                this.handleSystemAlert(data);
                break;
        }
        
        // Update main dashboard
        this.refreshDashboard();
    }
    
    showNotification(message, type = 'info', options = {}) {
        const notification = {
            id: Date.now(),
            message,
            type,
            timestamp: new Date(),
            ...options
        };
        
        this.notifications.unshift(notification);
        
        // Show toast notification
        this.showToast(notification);
        
        // Add to notification center
        this.updateNotificationCenter();
        
        // Play sound for critical alerts
        if (type === 'error' || type === 'warning') {
            this.playAlertSound();
        }
        
        // Auto-dismiss after 10 seconds (unless critical)
        if (type !== 'error') {
            setTimeout(() => this.dismissNotification(notification.id), 10000);
        }
    }
    
    showToast(notification) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${notification.type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-message">${notification.message}</div>
                ${notification.actions ? `
                    <div class="toast-actions">
                        ${notification.actions.map(action => 
                            `<button class="toast-action" onclick="agentManager.handleAction('${action.action}')">${action.label}</button>`
                        ).join('')}
                    </div>
                ` : ''}
            </div>
            <button class="toast-close" onclick="agentManager.dismissToast(this)">×</button>
        `;
        
        document.getElementById('toast-container').appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.classList.add('show'), 10);
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + Key combinations
            if ((e.ctrlKey || e.metaKey) && e.shiftKey) {
                switch(e.key) {
                    case 'A': // Toggle all agents
                        e.preventDefault();
                        this.toggleAllAgents();
                        break;
                    case 'E': // Focus on email agent
                        e.preventDefault();
                        this.focusAgent('email_monitor');
                        break;
                    case 'R': // Refresh all data
                        e.preventDefault();
                        this.refreshAllData();
                        break;
                    case 'N': // Show notifications
                        e.preventDefault();
                        this.toggleNotificationCenter();
                        break;
                }
            }
        });
    }
    
    // Unified Dashboard Integration
    createUnifiedDashboard() {
        return `
            <div class="unified-dashboard">
                <!-- System Health Overview -->
                <div class="system-health-bar">
                    <div class="health-indicator ${this.getSystemHealth()}">
                        <span class="health-icon">💚</span>
                        <span class="health-text">System ${this.getSystemHealth()}</span>
                    </div>
                    <div class="quick-stats">
                        <span>Agents: ${this.getActiveAgentCount()}/${this.getTotalAgentCount()}</span>
                        <span>Queue: ${this.getQueueSize()}</span>
                        <span>Alerts: ${this.getActiveAlertCount()}</span>
                    </div>
                </div>
                
                <!-- Main Control Panel -->
                <div class="control-panel">
                    <div class="agent-grid">
                        ${this.renderAgentCards()}
                    </div>
                    
                    <div class="automation-rules">
                        <h3>Automation Rules</h3>
                        ${this.renderAutomationRules()}
                    </div>
                </div>
                
                <!-- Real-time Activity Feed -->
                <div class="activity-feed">
                    <h3>Live Activity</h3>
                    <div class="feed-items">
                        ${this.renderActivityFeed()}
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div class="quick-actions">
                    <button onclick="agentManager.runAllAgents()" class="btn-primary">
                        <span class="icon">▶</span> Run All Agents
                    </button>
                    <button onclick="agentManager.pauseAllAgents()" class="btn-secondary">
                        <span class="icon">⏸</span> Pause All
                    </button>
                    <button onclick="agentManager.showAutomationWizard()" class="btn-secondary">
                        <span class="icon">🤖</span> Setup Automation
                    </button>
                </div>
            </div>
        `;
    }
    
    renderAgentCards() {
        const agents = [
            {
                id: 'email_monitor',
                name: 'Email Monitor',
                status: 'running',
                metrics: { processed: 145, pending: 12, errors: 2 },
                health: 95
            },
            {
                id: 'supplier_enricher',
                name: 'Supplier Enricher',
                status: 'idle',
                metrics: { enriched: 89, pending: 5, errors: 0 },
                health: 100
            },
            {
                id: 'quote_analyzer',
                name: 'Quote Analyzer',
                status: 'processing',
                metrics: { analyzed: 34, pending: 3, errors: 1 },
                health: 87
            }
        ];
        
        return agents.map(agent => `
            <div class="agent-card ${agent.status}">
                <div class="agent-header">
                    <h4>${agent.name}</h4>
                    <div class="agent-status-indicator ${agent.status}"></div>
                </div>
                <div class="agent-metrics">
                    <div class="metric">
                        <span class="value">${agent.metrics.processed}</span>
                        <span class="label">Processed</span>
                    </div>
                    <div class="metric">
                        <span class="value">${agent.metrics.pending}</span>
                        <span class="label">Pending</span>
                    </div>
                    <div class="metric ${agent.metrics.errors > 0 ? 'has-errors' : ''}">
                        <span class="value">${agent.metrics.errors}</span>
                        <span class="label">Errors</span>
                    </div>
                </div>
                <div class="agent-health">
                    <div class="health-bar">
                        <div class="health-fill" style="width: ${agent.health}%"></div>
                    </div>
                    <span class="health-percent">${agent.health}%</span>
                </div>
                <div class="agent-actions">
                    <button onclick="agentManager.toggleAgent('${agent.id}')" class="btn-small">
                        ${agent.status === 'running' ? 'Pause' : 'Start'}
                    </button>
                    <button onclick="agentManager.configureAgent('${agent.id}')" class="btn-small">
                        Configure
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    renderAutomationRules() {
        const rules = [
            {
                id: 'auto_quote_response',
                name: 'Auto Quote Response',
                condition: 'When quote < $10,000',
                action: 'Auto-approve and send PO',
                enabled: true
            },
            {
                id: 'supplier_alert',
                name: 'Supplier Quality Alert',
                condition: 'When rating drops below 4.0',
                action: 'Flag for review + Email notification',
                enabled: true
            },
            {
                id: 'inventory_reorder',
                name: 'Inventory Reorder',
                condition: 'When stock < 20% of target',
                action: 'Create RFQ automatically',
                enabled: false
            }
        ];
        
        return rules.map(rule => `
            <div class="automation-rule ${rule.enabled ? 'enabled' : 'disabled'}">
                <div class="rule-header">
                    <span class="rule-name">${rule.name}</span>
                    <label class="switch">
                        <input type="checkbox" ${rule.enabled ? 'checked' : ''} 
                               onchange="agentManager.toggleRule('${rule.id}')">
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="rule-details">
                    <div class="condition">📋 ${rule.condition}</div>
                    <div class="action">⚡ ${rule.action}</div>
                </div>
            </div>
        `).join('');
    }
    
    renderActivityFeed() {
        const activities = [
            { time: '2 min ago', icon: '📧', text: 'Email from supplier processed', type: 'email' },
            { time: '5 min ago', icon: '💰', text: 'Quote approved: $8,500', type: 'quote' },
            { time: '12 min ago', icon: '🔄', text: 'Supplier data enriched', type: 'update' },
            { time: '15 min ago', icon: '⚠️', text: 'Low inventory alert: Tomatoes', type: 'alert' },
            { time: '18 min ago', icon: '✅', text: 'RFQ sent to 5 suppliers', type: 'rfq' }
        ];
        
        return activities.map(activity => `
            <div class="feed-item ${activity.type}">
                <span class="feed-icon">${activity.icon}</span>
                <span class="feed-text">${activity.text}</span>
                <span class="feed-time">${activity.time}</span>
            </div>
        `).join('');
    }
    
    // Automation Wizard for One-Person Setup
    showAutomationWizard() {
        const wizard = `
            <div class="automation-wizard">
                <h2>Setup Automation Rule</h2>
                <p>Let the system handle routine tasks while you focus on strategic decisions</p>
                
                <div class="wizard-step">
                    <h3>1. Choose Trigger</h3>
                    <select id="trigger-select">
                        <option>When email received from supplier</option>
                        <option>When quote expires</option>
                        <option>When inventory low</option>
                        <option>When price changes by >10%</option>
                        <option>On schedule (daily/weekly)</option>
                    </select>
                </div>
                
                <div class="wizard-step">
                    <h3>2. Add Conditions</h3>
                    <div id="conditions-builder">
                        <button onclick="agentManager.addCondition()">+ Add Condition</button>
                    </div>
                </div>
                
                <div class="wizard-step">
                    <h3>3. Define Actions</h3>
                    <div class="action-templates">
                        <label><input type="checkbox"> Send email notification</label>
                        <label><input type="checkbox"> Create task/reminder</label>
                        <label><input type="checkbox"> Update supplier record</label>
                        <label><input type="checkbox"> Generate report</label>
                        <label><input type="checkbox"> Escalate to me</label>
                    </div>
                </div>
                
                <div class="wizard-actions">
                    <button onclick="agentManager.testAutomation()" class="btn-secondary">Test Rule</button>
                    <button onclick="agentManager.saveAutomation()" class="btn-primary">Save & Activate</button>
                </div>
            </div>
        `;
        
        this.showModal(wizard);
    }
    
    // Mobile Integration for On-the-Go Management
    setupMobileInterface() {
        // Detect mobile and adjust interface
        if (this.isMobile()) {
            document.body.classList.add('mobile-view');
            
            // Swipe gestures
            this.setupSwipeGestures();
            
            // Push notifications for critical alerts
            this.setupPushNotifications();
        }
    }
    
    setupPushNotifications() {
        if ('Notification' in window && Notification.permission === 'granted') {
            // Register for push notifications
            navigator.serviceWorker.ready.then(registration => {
                registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: this.urlBase64ToUint8Array(PUBLIC_VAPID_KEY)
                });
            });
        }
    }
}

// Initialize global instance
const agentManager = new AgentManager();

// CSS for unified interface
const styles = `
<style>
.unified-dashboard {
    display: grid;
    grid-template-areas:
        "health health health"
        "control control activity"
        "actions actions actions";
    gap: 1rem;
    padding: 1rem;
}

.system-health-bar {
    grid-area: health;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.control-panel {
    grid-area: control;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.agent-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
}

.agent-card {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.agent-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.agent-card.running {
    border-left: 4px solid #4caf50;
}

.agent-card.processing {
    border-left: 4px solid #ff9800;
}

.agent-card.idle {
    border-left: 4px solid #9e9e9e;
}

.agent-card.error {
    border-left: 4px solid #f44336;
}

.activity-feed {
    grid-area: activity;
    background: white;
    border-radius: 8px;
    padding: 1rem;
    max-height: 400px;
    overflow-y: auto;
}

.feed-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-bottom: 1px solid #eee;
}

.feed-item:hover {
    background: #f5f5f5;
}

.quick-actions {
    grid-area: actions;
    display: flex;
    gap: 1rem;
    justify-content: center;
    padding: 1rem;
}

.automation-rule {
    background: #f9f9f9;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
}

.automation-rule.enabled {
    background: #e8f5e9;
    border: 1px solid #4caf50;
}

.toast {
    position: fixed;
    right: -300px;
    top: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    padding: 1rem;
    min-width: 300px;
    transition: right 0.3s;
    z-index: 1000;
}

.toast.show {
    right: 20px;
}

.toast-error {
    border-left: 4px solid #f44336;
}

.toast-warning {
    border-left: 4px solid #ff9800;
}

.toast-info {
    border-left: 4px solid #2196f3;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .unified-dashboard {
        grid-template-areas:
            "health"
            "control"
            "activity"
            "actions";
    }
    
    .agent-grid {
        grid-template-columns: 1fr;
    }
    
    .quick-actions {
        flex-direction: column;
    }
    
    .toast {
        left: 10px;
        right: 10px;
        width: auto;
    }
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', styles);