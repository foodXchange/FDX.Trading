// FDX Trading - Modern Navigation System with Enhanced UX

class ModernNavigation {
    constructor() {
        this.currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        this.recentActions = JSON.parse(localStorage.getItem('fdx_recent_actions') || '[]');
        this.favorites = JSON.parse(localStorage.getItem('fdx_favorites') || '[]');
        this.shortcuts = this.initShortcuts();
        this.quickActionsOpen = false;
        this.contextMenuOpen = false;
        this.init();
    }

    init() {
        this.injectHTML();
        this.bindEvents();
        this.initKeyboardShortcuts();
        this.trackUserBehavior();
        this.loadUserPreferences();
        this.startIntelligentSuggestions();
    }

    injectHTML() {
        const navHTML = `
            <!-- Top Bar -->
            <div class="fdx-topbar">
                <!-- Left Section -->
                <div class="topbar-left">
                    <button class="sidebar-toggle" id="sidebarToggle">
                        <span></span>
                        <span></span>
                        <span></span>
                    </button>
                    <div class="brand">
                        <span class="brand-logo">FDX</span>
                        <span class="brand-text">Trading</span>
                    </div>
                </div>

                <!-- Center Section - Smart Search -->
                <div class="smart-search">
                    <input type="text" class="smart-search-input" id="smartSearch" 
                           placeholder="Search..." 
                           aria-label="Smart search">
                    <span class="smart-search-shortcut">Ctrl+K</span>
                    <span class="smart-search-icon">🔍</span>
                </div>

                <!-- Right Section -->
                <div class="topbar-right">
                    <!-- AI Assistant -->
                    <button class="topbar-btn ai-assistant" title="AI Assistant (Alt+A)">
                        <span class="btn-icon">🤖</span>
                        <span class="btn-badge">AI</span>
                    </button>

                    <!-- Notifications -->
                    <button class="topbar-btn notifications" title="Notifications">
                        <span class="btn-icon">🔔</span>
                        <span class="btn-count">3</span>
                    </button>

                    <!-- User Avatar -->
                    <div class="user-menu">
                        <button class="user-avatar-btn">
                            <div class="user-avatar">
                                ${this.currentUser.displayName?.charAt(0) || 'U'}
                            </div>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Sidebar -->
            <aside class="fdx-sidebar" id="fdxSidebar">
                <div class="sidebar-content">
                    <!-- Quick Stats Widget -->
                    <div class="sidebar-widget stats-widget">
                        <div class="widget-title">Today's Overview</div>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <span class="stat-value">12</span>
                                <span class="stat-label">Active Requests</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">5</span>
                                <span class="stat-label">Pending Quotes</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">3</span>
                                <span class="stat-label">New Messages</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">89%</span>
                                <span class="stat-label">Completion</span>
                            </div>
                        </div>
                    </div>

                    <!-- Main Navigation -->
                    <nav class="sidebar-nav">
                        <div class="sidebar-section">
                            <div class="sidebar-section-title">Main</div>
                            <ul class="sidebar-menu">
                                <li class="sidebar-item">
                                    <a href="/dashboard.html" class="sidebar-link" data-tooltip="Dashboard">
                                        <span class="sidebar-icon">📊</span>
                                        <span class="sidebar-text">Dashboard</span>
                                        <span class="sidebar-badge">Live</span>
                                    </a>
                                </li>
                                <li class="sidebar-item">
                                    <a href="/requests.html" class="sidebar-link" data-tooltip="Requests">
                                        <span class="sidebar-icon">📝</span>
                                        <span class="sidebar-text">Requests</span>
                                        <span class="sidebar-badge">12</span>
                                    </a>
                                </li>
                                <li class="sidebar-item">
                                    <a href="/console-list.html" class="sidebar-link" data-tooltip="Console">
                                        <span class="sidebar-icon">🎛️</span>
                                        <span class="sidebar-text">Console</span>
                                        <span class="sidebar-badge">New</span>
                                    </a>
                                </li>
                            </ul>
                        </div>

                        <div class="sidebar-section">
                            <div class="sidebar-section-title">Catalog</div>
                            <ul class="sidebar-menu">
                                <li class="sidebar-item">
                                    <a href="/products.html" class="sidebar-link" data-tooltip="Products">
                                        <span class="sidebar-icon">📦</span>
                                        <span class="sidebar-text">Products</span>
                                    </a>
                                </li>
                                <li class="sidebar-item">
                                    <a href="/suppliers.html" class="sidebar-link" data-tooltip="Suppliers">
                                        <span class="sidebar-icon">🏢</span>
                                        <span class="sidebar-text">Suppliers</span>
                                    </a>
                                </li>
                                <li class="sidebar-item">
                                    <a href="/pricing.html" class="sidebar-link" data-tooltip="Pricing">
                                        <span class="sidebar-icon">💰</span>
                                        <span class="sidebar-text">Pricing</span>
                                    </a>
                                </li>
                            </ul>
                        </div>

                        <div class="sidebar-section">
                            <div class="sidebar-section-title">Learn</div>
                            <ul class="sidebar-menu">
                                <li class="sidebar-item">
                                    <a href="/university-dashboard.html" class="sidebar-link" data-tooltip="University">
                                        <span class="sidebar-icon">🎓</span>
                                        <span class="sidebar-text">University</span>
                                        <span class="sidebar-badge pulse-animation">Start</span>
                                    </a>
                                </li>
                                <li class="sidebar-item">
                                    <a href="/help.html" class="sidebar-link" data-tooltip="Help">
                                        <span class="sidebar-icon">❓</span>
                                        <span class="sidebar-text">Help Center</span>
                                    </a>
                                </li>
                            </ul>
                        </div>

                        <!-- Recent Actions -->
                        <div class="sidebar-section">
                            <div class="sidebar-section-title">Recent</div>
                            <ul class="sidebar-menu" id="recentActions">
                                ${this.renderRecentActions()}
                            </ul>
                        </div>
                    </nav>

                    <!-- Sidebar Footer -->
                    <div class="sidebar-footer">
                        <button class="sidebar-settings-btn">
                            <span class="sidebar-icon">⚙️</span>
                            <span class="sidebar-text">Settings</span>
                        </button>
                    </div>
                </div>
            </aside>

            <!-- Mobile Sidebar Overlay -->
            <div class="sidebar-overlay" id="sidebarOverlay"></div>


            <!-- Quick Actions FAB -->
            <div class="quick-actions-fab" id="quickActionsFab">
                <span>+</span>
            </div>
            <div class="quick-actions-menu" id="quickActionsMenu">
                <div class="quick-action-item">
                    <span class="quick-action-label">New Request</span>
                    <button class="quick-action-btn" onclick="window.location.href='/request-create.html'">
                        📝
                    </button>
                </div>
                <div class="quick-action-item">
                    <span class="quick-action-label">Create Console</span>
                    <button class="quick-action-btn" onclick="modernNav.createConsole()">
                        🎛️
                    </button>
                </div>
                <div class="quick-action-item">
                    <span class="quick-action-label">Add Product</span>
                    <button class="quick-action-btn" onclick="window.location.href='/product-add.html'">
                        📦
                    </button>
                </div>
                <div class="quick-action-item">
                    <span class="quick-action-label">Quick Tutorial</span>
                    <button class="quick-action-btn" onclick="modernNav.startTutorial()">
                        🎓
                    </button>
                </div>
            </div>

            <!-- Context Menu -->
            <div class="context-menu" id="contextMenu"></div>

            <!-- Breadcrumb -->
            <div class="breadcrumb-nav" id="breadcrumbNav"></div>
        `;

        // Insert navigation HTML
        const navContainer = document.createElement('div');
        navContainer.id = 'modernNavigation';
        navContainer.innerHTML = navHTML;
        document.body.insertBefore(navContainer, document.body.firstChild);

        // Add CSS
        if (!document.getElementById('modernNavCSS')) {
            const link = document.createElement('link');
            link.id = 'modernNavCSS';
            link.rel = 'stylesheet';
            link.href = '/css/modern-navigation.css';
            document.head.appendChild(link);
        }
    }

    bindEvents() {
        // Sidebar Toggle
        document.getElementById('sidebarToggle').addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Smart Search
        const smartSearch = document.getElementById('smartSearch');
        smartSearch.addEventListener('focus', () => {
            window.location.href = '/search.html';
        });


        // Quick Actions FAB
        document.getElementById('quickActionsFab').addEventListener('click', () => {
            this.toggleQuickActions();
        });

        // Context Menu
        document.addEventListener('contextmenu', (e) => {
            if (e.target.closest('.sidebar-link') || e.target.closest('.request-card')) {
                e.preventDefault();
                this.showContextMenu(e);
            }
        });

        // Click outside handlers
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.quick-actions-fab') && !e.target.closest('.quick-actions-menu')) {
                this.closeQuickActions();
            }
            if (!e.target.closest('.context-menu')) {
                this.hideContextMenu();
            }
        });

        // Mobile sidebar overlay
        document.getElementById('sidebarOverlay').addEventListener('click', () => {
            this.closeMobileSidebar();
        });
    }

    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K - Open Search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                window.location.href = '/search.html';
            }

            // Alt + A - AI Assistant
            if (e.altKey && e.key === 'a') {
                e.preventDefault();
                this.openAIAssistant();
            }

            // Alt + N - New Request
            if (e.altKey && e.key === 'n') {
                e.preventDefault();
                window.location.href = '/request-create.html';
            }

            // Alt + S - Toggle Sidebar
            if (e.altKey && e.key === 's') {
                e.preventDefault();
                this.toggleSidebar();
            }

            // Escape - Close modals
            if (e.key === 'Escape') {
                this.closeAllModals();
            }

        });
    }

    toggleSidebar() {
        const body = document.body;
        const sidebar = document.getElementById('fdxSidebar');
        
        if (window.innerWidth <= 768) {
            sidebar.classList.toggle('mobile-open');
            document.getElementById('sidebarOverlay').classList.toggle('active');
        } else {
            body.classList.toggle('sidebar-collapsed');
            localStorage.setItem('sidebar_collapsed', body.classList.contains('sidebar-collapsed'));
        }
    }

    closeMobileSidebar() {
        document.getElementById('fdxSidebar').classList.remove('mobile-open');
        document.getElementById('sidebarOverlay').classList.remove('active');
    }


    toggleQuickActions() {
        this.quickActionsOpen = !this.quickActionsOpen;
        const fab = document.getElementById('quickActionsFab');
        const menu = document.getElementById('quickActionsMenu');

        if (this.quickActionsOpen) {
            fab.classList.add('active');
            menu.classList.add('active');
        } else {
            fab.classList.remove('active');
            menu.classList.remove('active');
        }
    }

    closeQuickActions() {
        this.quickActionsOpen = false;
        document.getElementById('quickActionsFab').classList.remove('active');
        document.getElementById('quickActionsMenu').classList.remove('active');
    }

    showContextMenu(e) {
        const menu = document.getElementById('contextMenu');
        const target = e.target.closest('.sidebar-link, .request-card');
        
        let menuItems = [];
        
        if (target.classList.contains('sidebar-link')) {
            menuItems = [
                { icon: '⭐', text: 'Add to Favorites', action: () => this.addToFavorites(target.href) },
                { icon: '📌', text: 'Pin to Top', action: () => this.pinItem(target) },
                { icon: '🔗', text: 'Copy Link', action: () => this.copyLink(target.href) },
                { divider: true },
                { icon: '🗑️', text: 'Remove from Recent', action: () => this.removeFromRecent(target) }
            ];
        }

        menu.innerHTML = menuItems.map(item => 
            item.divider ? '<div class="context-menu-divider"></div>' : 
            `<div class="context-menu-item" onclick="modernNav.${item.action}">
                <span>${item.icon}</span>
                <span>${item.text}</span>
            </div>`
        ).join('');

        menu.style.left = e.pageX + 'px';
        menu.style.top = e.pageY + 'px';
        menu.classList.add('active');
        this.contextMenuOpen = true;
    }

    hideContextMenu() {
        document.getElementById('contextMenu').classList.remove('active');
        this.contextMenuOpen = false;
    }

    trackUserBehavior() {
        // Track page visits for intelligent suggestions
        const currentPage = {
            url: window.location.pathname,
            title: document.title,
            icon: this.getPageIcon(window.location.pathname),
            desc: this.getPageDescription(window.location.pathname),
            timestamp: new Date().toISOString()
        };

        this.recentActions.unshift(currentPage);
        this.recentActions = this.recentActions.slice(0, 5);
        localStorage.setItem('fdx_recent_actions', JSON.stringify(this.recentActions));
    }

    getPageIcon(path) {
        const icons = {
            '/dashboard': '📊',
            '/requests': '📝',
            '/console': '🎛️',
            '/products': '📦',
            '/suppliers': '🏢',
            '/university': '🎓'
        };
        
        for (let key in icons) {
            if (path.includes(key)) return icons[key];
        }
        return '📄';
    }

    getPageDescription(path) {
        const descriptions = {
            '/dashboard': 'Analytics dashboard',
            '/requests': 'Procurement requests',
            '/console': 'Workflow console',
            '/products': 'Product catalog',
            '/suppliers': 'Supplier directory',
            '/university': 'Learning center'
        };
        
        for (let key in descriptions) {
            if (path.includes(key)) return descriptions[key];
        }
        return 'Page visit';
    }

    renderRecentActions() {
        return this.recentActions.slice(0, 3).map(action => `
            <li class="sidebar-item">
                <a href="${action.url}" class="sidebar-link">
                    <span class="sidebar-icon">${action.icon}</span>
                    <span class="sidebar-text">${action.title}</span>
                </a>
            </li>
        `).join('');
    }

    startIntelligentSuggestions() {
        // AI-powered suggestions based on user behavior
        setInterval(() => {
            this.checkForSuggestions();
        }, 60000); // Check every minute
    }

    checkForSuggestions() {
        const hour = new Date().getHours();
        const dayOfWeek = new Date().getDay();
        
        // Morning suggestion
        if (hour === 9 && !localStorage.getItem('morning_suggestion_shown')) {
            this.showNotification('Good morning! You have 3 pending requests to review.', 'info');
            localStorage.setItem('morning_suggestion_shown', new Date().toDateString());
        }
        
        // Weekly report suggestion
        if (dayOfWeek === 1 && hour === 14 && !localStorage.getItem('weekly_report_shown')) {
            this.showNotification('Weekly report is ready! Check your analytics dashboard.', 'success');
            localStorage.setItem('weekly_report_shown', new Date().toDateString());
        }
    }

    showNotification(message, type = 'info') {
        // Create and show notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    openAIAssistant() {
        // Open AI assistant modal
        alert('AI Assistant: How can I help you today?\\n\\nTry asking:\\n- "Show me pending requests"\\n- "Create a new console"\\n- "Find suppliers for coffee"');
    }

    startTutorial() {
        if (window.fdxTutorial) {
            fdxTutorial.start('create-request');
        } else {
            window.location.href = '/university-dashboard.html';
        }
    }

    createConsole() {
        // Quick console creation
        window.location.href = '/console-create.html';
    }

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.clear();
            window.location.href = '/';
        }
    }

    loadUserPreferences() {
        // Load saved preferences
        if (localStorage.getItem('sidebar_collapsed') === 'true') {
            document.body.classList.add('sidebar-collapsed');
        }
        
        // Set theme
        const theme = localStorage.getItem('theme') || 'light';
        document.body.dataset.theme = theme;
    }

    closeAllModals() {
        this.closeQuickActions();
        this.hideContextMenu();
    }

    initShortcuts() {
        return {
            'cmd+k': () => window.location.href = '/search.html',
            'alt+a': () => this.openAIAssistant(),
            'alt+n': () => window.location.href = '/request-create.html',
            'alt+s': () => this.toggleSidebar(),
            'alt+d': () => window.location.href = '/dashboard.html',
            'alt+c': () => window.location.href = '/console-list.html',
            'alt+u': () => window.location.href = '/university-dashboard.html'
        };
    }
}

// Initialize modern navigation
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.modernNav = new ModernNavigation();
    });
} else {
    window.modernNav = new ModernNavigation();
}