// FDX Trading - Smart Navigation System
class SmartNavigation {
    constructor() {
        this.user = JSON.parse(localStorage.getItem('currentUser') || '{}');
        this.userRole = this.user.type || 0;
        this.recentTasks = [];
        this.currentContext = null;
        this.init();
    }

    init() {
        this.injectNavigation();
        this.setupEventListeners();
        this.loadUserContext();
        this.startSmartSuggestions();
    }

    // Get role-specific navigation items
    getNavigationItems() {
        // Base items for everyone
        const baseItems = [
            {
                section: 'QUICK ACTIONS',
                items: [
                    { icon: '🏠', text: 'Home', href: '/dashboard.html', badge: null },
                    { icon: '📊', text: 'My Work', href: '/my-work.html', badge: '3' }
                ]
            }
        ];

        // Role-specific items
        const roleItems = {
            0: [ // Buyer
                {
                    section: 'PROCUREMENT',
                    items: [
                        { icon: '📝', text: 'Create Request', href: '/request-create.html', badge: null },
                        { icon: '📋', text: 'My Requests', href: '/requests.html', badge: '12' },
                        { icon: '🎛️', text: 'Consoles', href: '/console-list.html', badge: 'NEW' },
                        { icon: '💰', text: 'Compare Quotes', href: '/quote-comparison.html', badge: '5' }
                    ]
                },
                {
                    section: 'SUPPLIERS',
                    items: [
                        { icon: '🏢', text: 'Find Suppliers', href: '/supplier-search.html', badge: null },
                        { icon: '⭐', text: 'Favorites', href: '/supplier-favorites.html', badge: null }
                    ]
                }
            ],
            1: [ // Supplier
                {
                    section: 'SALES',
                    items: [
                        { icon: '🔔', text: 'New Opportunities', href: '/opportunities.html', badge: '8' },
                        { icon: '💼', text: 'My Quotes', href: '/my-quotes.html', badge: '3' },
                        { icon: '📦', text: 'My Products', href: '/products.html', badge: null },
                        { icon: '💵', text: 'Pricing', href: '/price-management.html', badge: null }
                    ]
                },
                {
                    section: 'ORDERS',
                    items: [
                        { icon: '📋', text: 'Active Orders', href: '/orders.html', badge: '2' },
                        { icon: '🚚', text: 'Shipments', href: '/shipments.html', badge: null }
                    ]
                }
            ],
            5: [ // Admin
                {
                    section: 'MANAGEMENT',
                    items: [
                        { icon: '👥', text: 'Users', href: '/users.html', badge: null },
                        { icon: '📊', text: 'Analytics', href: '/analytics.html', badge: null },
                        { icon: '⚙️', text: 'Settings', href: '/settings.html', badge: null },
                        { icon: '📝', text: 'Reports', href: '/reports.html', badge: null }
                    ]
                }
            ]
        };

        // Learning section for all
        const learningSection = {
            section: 'LEARN & HELP',
            items: [
                { icon: '📖', text: 'How It Works', href: '/system-workflow.html', badge: 'NEW' },
                { icon: '🎓', text: 'University', href: '/university-dashboard.html', badge: 'START' },
                { icon: '❓', text: 'Help Center', href: '/help.html', badge: null }
            ]
        };

        // Combine sections based on role
        const sections = [...baseItems];
        if (roleItems[this.userRole]) {
            sections.push(...roleItems[this.userRole]);
        }
        sections.push(learningSection);

        return sections;
    }

    injectNavigation() {
        const navHTML = `
            <!-- Smart Sidebar -->
            <aside class="smart-sidebar" id="smartSidebar">
                <!-- Brand -->
                <a href="/dashboard.html" class="sidebar-brand" style="text-decoration: none; color: inherit; cursor: pointer;" title="Go to Dashboard">
                    <div class="brand-logo">FDX</div>
                    <div class="brand-name">Trading</div>
                </a>

                <!-- Quick Search -->
                <div class="quick-action-bar">
                    <div class="quick-search" onclick="smartNav.openCommandPalette()">
                        <span class="quick-search-icon">🔍</span>
                        <span class="quick-search-text">Quick search...</span>
                        <span class="quick-search-shortcut">⌘K</span>
                    </div>
                </div>

                <!-- Navigation Sections -->
                <nav class="nav-sections">
                    ${this.renderNavSections()}
                </nav>

                <!-- Smart Actions -->
                <div class="smart-actions">
                    <div class="action-buttons">
                        ${this.renderSmartActions()}
                    </div>
                </div>

                <!-- User Section -->
                <div class="user-section">
                    <div class="user-menu" onclick="smartNav.toggleUserMenu()">
                        <div class="user-avatar">${this.user.displayName?.charAt(0) || 'U'}</div>
                        <div class="user-info">
                            <div class="user-name">${this.user.displayName || 'User'}</div>
                            <div class="user-role">${this.getRoleName()}</div>
                        </div>
                    </div>
                </div>
            </aside>

            <!-- Main Content Wrapper -->
            <div class="main-content" id="mainContent">
                <!-- Content will be here -->
            </div>

            <!-- Smart Panel (Context-Sensitive) -->
            <aside class="smart-panel" id="smartPanel">
                <div class="panel-content">
                    <!-- Dynamic content based on context -->
                </div>
            </aside>

            <!-- Floating Action Button -->
            <button class="fab" id="fabButton" onclick="smartNav.showQuickActions()">
                <span>+</span>
            </button>

            <!-- Command Palette (Hidden) -->
            <div class="command-palette-overlay" id="commandPaletteOverlay">
                <div class="command-palette">
                    <input type="text" class="command-input" id="commandInput" 
                           placeholder="What would you like to do?" 
                           autocomplete="off">
                    <div class="command-suggestions" id="commandSuggestions"></div>
                </div>
            </div>
        `;

        // Add styles
        if (!document.getElementById('smartNavCSS')) {
            const link = document.createElement('link');
            link.id = 'smartNavCSS';
            link.rel = 'stylesheet';
            link.href = '/css/smart-navigation.css';
            document.head.appendChild(link);
        }

        // Create container
        const container = document.createElement('div');
        container.className = 'app-container';
        container.innerHTML = navHTML;
        
        // Move existing content to main-content
        const existingContent = document.body.innerHTML;
        document.body.innerHTML = '';
        document.body.appendChild(container);
        document.getElementById('mainContent').innerHTML = existingContent;

        // Set active nav item
        this.setActiveNavItem();
    }

    renderNavSections() {
        const sections = this.getNavigationItems();
        return sections.map(section => `
            <div class="nav-section">
                <div class="nav-section-title">${section.section}</div>
                ${section.items.map(item => `
                    <div class="nav-item">
                        <a href="${item.href}" class="nav-link" data-href="${item.href}">
                            <span class="nav-icon">${item.icon}</span>
                            <span class="nav-text">${item.text}</span>
                            ${item.badge ? `<span class="nav-badge">${item.badge}</span>` : ''}
                        </a>
                    </div>
                `).join('')}
            </div>
        `).join('');
    }

    renderSmartActions() {
        // Context-aware actions based on current page and user behavior
        const actions = this.getSmartActions();
        return actions.map(action => `
            <button class="action-btn" onclick="${action.onclick}">
                <span class="action-btn-icon">${action.icon}</span>
                <span class="action-btn-text">${action.text}</span>
            </button>
        `).join('');
    }

    getSmartActions() {
        const currentPath = window.location.pathname;
        const hour = new Date().getHours();
        
        // Time-based suggestions
        if (hour < 10) {
            return [
                { icon: '☕', text: 'Morning Tasks', onclick: 'smartNav.showMorningTasks()' },
                { icon: '📈', text: 'Daily Overview', onclick: 'window.location.href="/dashboard.html"' }
            ];
        }
        
        // Context-based suggestions
        if (currentPath.includes('request')) {
            return [
                { icon: '🎛️', text: 'Create Console', onclick: 'smartNav.createConsole()' },
                { icon: '📋', text: 'View Templates', onclick: 'smartNav.showTemplates()' }
            ];
        }
        
        // Default smart actions
        return [
            { icon: '✨', text: 'AI Suggestions', onclick: 'smartNav.showAISuggestions()' },
            { icon: '🚀', text: 'Quick Start', onclick: 'smartNav.showQuickStart()' }
        ];
    }

    setupEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Cmd/Ctrl + K - Open command palette
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.openCommandPalette();
            }
            
            // Cmd/Ctrl + / - Toggle sidebar
            if ((e.metaKey || e.ctrlKey) && e.key === '/') {
                e.preventDefault();
                this.toggleSidebar();
            }
            
            // Escape - Close modals
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });

        // Track user behavior
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (link) {
                this.trackUserAction('navigate', link.href);
            }
        });
    }

    setActiveNavItem() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-link').forEach(link => {
            if (link.getAttribute('data-href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    openCommandPalette() {
        const overlay = document.getElementById('commandPaletteOverlay');
        if (!overlay) {
            this.createCommandPalette();
            return;
        }
        
        overlay.style.display = 'flex';
        document.getElementById('commandInput').focus();
        this.showCommandSuggestions('');
    }

    createCommandPalette() {
        const paletteHTML = `
            <div class="command-palette-overlay" id="commandPaletteOverlay" style="
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                z-index: 1000;
                align-items: center;
                justify-content: center;
            ">
                <div class="command-palette" style="
                    background: white;
                    border-radius: 16px;
                    width: 600px;
                    max-width: 90%;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                ">
                    <input type="text" id="commandInput" style="
                        width: 100%;
                        padding: 20px;
                        border: none;
                        border-bottom: 1px solid #e2e8f0;
                        font-size: 16px;
                        outline: none;
                    " placeholder="What would you like to do?" autocomplete="off">
                    <div id="commandSuggestions" style="
                        max-height: 400px;
                        overflow-y: auto;
                        padding: 12px;
                    "></div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', paletteHTML);
        
        const input = document.getElementById('commandInput');
        input.addEventListener('input', (e) => {
            this.showCommandSuggestions(e.target.value);
        });
        
        document.getElementById('commandPaletteOverlay').addEventListener('click', (e) => {
            if (e.target.id === 'commandPaletteOverlay') {
                this.closeCommandPalette();
            }
        });
        
        this.openCommandPalette();
    }

    showCommandSuggestions(query) {
        const suggestions = [
            { icon: '📝', text: 'Create new request', action: () => window.location.href = '/request-create.html' },
            { icon: '🎛️', text: 'Open console management', action: () => window.location.href = '/console-list.html' },
            { icon: '📦', text: 'Browse products', action: () => window.location.href = '/products.html' },
            { icon: '🏢', text: 'Find suppliers', action: () => window.location.href = '/supplier-search.html' },
            { icon: '💰', text: 'Compare quotes', action: () => window.location.href = '/quote-comparison.html' },
            { icon: '🎓', text: 'Start learning', action: () => window.location.href = '/university-dashboard.html' },
            { icon: '📊', text: 'View analytics', action: () => window.location.href = '/analytics.html' },
            { icon: '⚙️', text: 'Settings', action: () => window.location.href = '/settings.html' },
            { icon: '🚪', text: 'Logout', action: () => this.logout() }
        ];
        
        const filtered = query 
            ? suggestions.filter(s => s.text.toLowerCase().includes(query.toLowerCase()))
            : suggestions;
        
        const container = document.getElementById('commandSuggestions');
        container.innerHTML = filtered.map((suggestion, index) => `
            <div class="command-suggestion" style="
                padding: 12px;
                border-radius: 8px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 12px;
                transition: background 0.2s;
            " onmouseover="this.style.background='#f1f5f9'" 
               onmouseout="this.style.background='transparent'"
               onclick="smartNav.executeCommand(${index})">
                <span style="font-size: 20px;">${suggestion.icon}</span>
                <span style="flex: 1; color: #334155;">${suggestion.text}</span>
                <span style="color: #94a3b8; font-size: 12px;">↵</span>
            </div>
        `).join('');
        
        this.currentSuggestions = filtered;
    }

    executeCommand(index) {
        if (this.currentSuggestions && this.currentSuggestions[index]) {
            this.currentSuggestions[index].action();
            this.closeCommandPalette();
        }
    }

    closeCommandPalette() {
        const overlay = document.getElementById('commandPaletteOverlay');
        if (overlay) {
            overlay.style.display = 'none';
            document.getElementById('commandInput').value = '';
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('smartSidebar');
        sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    }

    showQuickActions() {
        // Show context-sensitive quick actions
        const actions = [
            'Create Request',
            'Find Supplier', 
            'Compare Prices',
            'View Reports'
        ];
        
        const selected = prompt(`Quick Actions:\n\n${actions.map((a, i) => `${i+1}. ${a}`).join('\n')}\n\nEnter number:`);
        if (selected) {
            this.handleQuickAction(parseInt(selected) - 1);
        }
    }

    handleQuickAction(index) {
        const actions = [
            () => window.location.href = '/request-create.html',
            () => window.location.href = '/supplier-search.html',
            () => window.location.href = '/quote-comparison.html',
            () => window.location.href = '/reports.html'
        ];
        
        if (actions[index]) {
            actions[index]();
        }
    }

    showAISuggestions() {
        // AI-powered suggestions based on user behavior
        const suggestions = this.getAISuggestions();
        alert(`AI Suggestions for you:\n\n${suggestions.join('\n')}`);
    }

    getAISuggestions() {
        const hour = new Date().getHours();
        const dayOfWeek = new Date().getDay();
        
        const suggestions = [];
        
        // Time-based
        if (hour < 10) {
            suggestions.push('✅ Review 3 pending requests from yesterday');
        }
        
        // Day-based
        if (dayOfWeek === 1) {
            suggestions.push('📊 Check weekly performance report');
        }
        
        // Role-based
        if (this.userRole === 0) {
            suggestions.push('💰 2 suppliers have updated prices - review now');
            suggestions.push('🎯 Complete Console Training in University (15 min)');
        }
        
        return suggestions;
    }

    showMorningTasks() {
        alert('Good morning! Here are your priorities:\n\n1. Review 3 pending requests\n2. Approve 2 quotes\n3. Check new supplier messages\n4. Complete daily report');
    }

    showQuickStart() {
        const role = this.userRole;
        const quickStarts = {
            0: 'Buyer Quick Start:\n\n1. Create a new request\n2. Find suppliers\n3. Compare quotes\n4. Create console',
            1: 'Supplier Quick Start:\n\n1. Check new opportunities\n2. Submit quotes\n3. Update product catalog\n4. View orders',
            5: 'Admin Quick Start:\n\n1. Review user activity\n2. Check system health\n3. Generate reports\n4. Manage settings'
        };
        
        alert(quickStarts[role] || 'Welcome! Start by exploring the dashboard.');
    }

    createConsole() {
        if (confirm('Create a new console for workflow management?')) {
            window.location.href = '/console-create.html';
        }
    }

    showTemplates() {
        alert('Request Templates:\n\n• Standard Procurement\n• Urgent Order\n• Bulk Purchase\n• Sample Request\n• Custom Template');
    }

    getRoleName() {
        const roles = {
            0: 'Buyer',
            1: 'Supplier',
            2: 'Both',
            3: 'Expert',
            4: 'Agent',
            5: 'Administrator'
        };
        return roles[this.userRole] || 'User';
    }

    loadUserContext() {
        // Load user's recent activities and preferences
        this.recentTasks = JSON.parse(localStorage.getItem('recentTasks') || '[]');
        this.preferences = JSON.parse(localStorage.getItem('userPreferences') || '{}');
    }

    trackUserAction(action, data) {
        // Track user behavior for AI suggestions
        const task = {
            action: action,
            data: data,
            timestamp: new Date().toISOString()
        };
        
        this.recentTasks.unshift(task);
        this.recentTasks = this.recentTasks.slice(0, 20);
        localStorage.setItem('recentTasks', JSON.stringify(this.recentTasks));
    }

    startSmartSuggestions() {
        // Check for smart suggestions every minute
        setInterval(() => {
            this.checkForSmartActions();
        }, 60000);
    }

    checkForSmartActions() {
        // Intelligent notifications based on context
        const now = new Date();
        const hour = now.getHours();
        
        // Don't show suggestions too often
        const lastSuggestion = localStorage.getItem('lastSuggestion');
        if (lastSuggestion) {
            const lastTime = new Date(lastSuggestion);
            if (now - lastTime < 3600000) return; // 1 hour minimum
        }
        
        // Smart suggestions based on patterns
        if (hour === 14 && this.recentTasks.length > 10) {
            this.showNotification('Time for a break! You\'ve been productive today. 🎯');
            localStorage.setItem('lastSuggestion', now.toISOString());
        }
    }

    showNotification(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            z-index: 1001;
            animation: slideUp 0.3s ease;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.remove(), 5000);
    }

    toggleUserMenu() {
        if (confirm('User Menu:\n\n1. Profile\n2. Settings\n3. Help\n4. Logout\n\nSelect option:')) {
            // Handle user menu
        }
    }

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.clear();
            window.location.href = '/';
        }
    }

    closeAllModals() {
        this.closeCommandPalette();
        // Close other modals
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.smartNav = new SmartNavigation();
    });
} else {
    window.smartNav = new SmartNavigation();
}