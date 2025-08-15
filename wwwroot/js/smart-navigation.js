// FDX Trading - Smart Navigation System
class SmartNavigation {
    constructor() {
        this.user = JSON.parse(localStorage.getItem('currentUser') || '{}');
        // Set default user data if not present
        if (!this.user.displayName) {
            this.user = {
                ...this.user,
                displayName: 'U.S',
                email: 'admin@fdxtrading.com',
                type: 5 // Admin role
            };
            localStorage.setItem('currentUser', JSON.stringify(this.user));
        }
        this.waitingForSecondKey = false;
        this.userRole = this.user.type || 5; // Default to Admin (5)
        this.recentTasks = [];
        this.currentContext = null;
        this.init();
    }

    init() {
        this.initializeTheme(); // Initialize theme before everything else
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
                    { icon: '📊', text: 'My Work', href: '/my-work.html', badge: '3' },
                    { icon: '🏢', text: 'Companies', href: '/companies.html', badge: null },
                    { icon: '👥', text: 'Users', href: '/users.html', badge: null }
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
                        { icon: '📊', text: 'Analytics', href: '/analytics.html', badge: null },
                        { icon: '⚙️', text: 'Settings', href: '/settings.html', badge: null },
                        { icon: '📝', text: 'Reports', href: '/reports.html', badge: null }
                    ]
                }
            ]
        };

        // Learning section removed - now in footer
        // const learningSection = {
        //     section: 'LEARN & HELP',
        //     items: [
        //         { icon: '📖', text: 'How It Works', href: '/system-workflow.html', badge: 'NEW' },
        //         { icon: '🎓', text: 'University', href: '/university-dashboard.html', badge: 'START' },
        //         { icon: '❓', text: 'Help Center', href: '/help.html', badge: null }
        //     ]
        // };

        // Combine sections based on role
        const sections = [...baseItems];
        if (roleItems[this.userRole]) {
            sections.push(...roleItems[this.userRole]);
        }
        // sections.push(learningSection); // Removed - now in footer

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

                <!-- Quick Search - Hidden (moved to navbar) -->
                <!-- <div class="quick-action-bar">
                    <div class="quick-search" onclick="smartNav.openCommandPalette()">
                        <span class="quick-search-icon">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="11" cy="11" r="8"/>
                                <path d="m21 21-4.35-4.35"/>
                            </svg>
                        </span>
                        <span class="quick-search-text">Quick search...</span>
                        <span class="quick-search-shortcut">⌘K</span>
                    </div>
                </div> -->

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
                    <div class="user-menu" onclick="smartNav.toggleUserMenu(event)">
                        <div class="user-avatar">
                            ${this.user.profileImage ? 
                                `<img src="${this.user.profileImage}" alt="Profile" class="avatar-image" />` :
                                `<img src="https://ui-avatars.com/api/?name=${encodeURIComponent(this.user.displayName || 'U.S')}&background=6366f1&color=fff&size=36&bold=true" alt="Profile" class="avatar-image" />`
                            }
                        </div>
                        <div class="user-info">
                            <div class="user-name">${this.user.displayName || 'U.S'}</div>
                            <div class="user-role">${this.getRoleName()}</div>
                        </div>
                    </div>
                    
                    <!-- User Dropdown Menu -->
                    <div class="user-dropdown" id="userDropdown" style="display: none;">
                        <div class="dropdown-header">
                            <div class="dropdown-avatar-large">
                                ${this.user.profileImage ? 
                                    `<img src="${this.user.profileImage}" alt="Profile" class="avatar-image-large" />` :
                                    `<img src="https://ui-avatars.com/api/?name=${encodeURIComponent(this.user.displayName || 'U.S')}&background=6366f1&color=fff&size=56&bold=true" alt="Profile" class="avatar-image-large" />`
                                }
                            </div>
                            <div class="dropdown-user-info">
                                <div class="dropdown-name">${this.user.displayName || 'U.S'}</div>
                                <div class="dropdown-email">${this.user.email || 'admin@fdxtrading.com'}</div>
                                <div class="dropdown-role">${this.getRoleName()}</div>
                            </div>
                        </div>
                        
                        <div class="dropdown-stats">
                            <div class="stat-item">
                                <span class="stat-number">${this.user.requestCount || '12'}</span>
                                <span class="stat-label">Requests</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">${this.user.consoleCount || '3'}</span>
                                <span class="stat-label">Consoles</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">${this.user.savingsPercent || '24%'}</span>
                                <span class="stat-label">Savings</span>
                            </div>
                        </div>
                        
                        <div class="dropdown-divider"></div>
                        
                        <a href="/user-profile.html" class="dropdown-item">
                            <span class="dropdown-icon">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                    <circle cx="12" cy="7" r="4"></circle>
                                </svg>
                            </span>
                            <span>My Profile</span>
                            <span class="dropdown-badge">New</span>
                        </a>
                        
                        <a href="/my-work.html" class="dropdown-item">
                            <span class="dropdown-icon">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                                    <line x1="9" y1="9" x2="15" y2="9"></line>
                                    <line x1="9" y1="13" x2="15" y2="13"></line>
                                </svg>
                            </span>
                            <span>My Activity</span>
                        </a>
                        
                        <a href="/user-profile.html#notifications" class="dropdown-item">
                            <span class="dropdown-icon">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                                    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                                </svg>
                            </span>
                            <span>Notifications</span>
                            <span class="dropdown-count">5</span>
                        </a>
                        
                        <div class="dropdown-divider"></div>
                        
                        <a href="#" onclick="smartNav.logout(); return false;" class="dropdown-item dropdown-danger">
                            <span class="dropdown-icon">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                                    <polyline points="16 17 21 12 16 7"></polyline>
                                    <line x1="21" y1="12" x2="9" y2="12"></line>
                                </svg>
                            </span>
                            <span>Sign Out</span>
                        </a>
                    </div>
                </div>
            </aside>

            <!-- Main Content Wrapper -->
            <div class="main-content" id="mainContent">
                <!-- Content will be here -->
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

        // FAB button removed - now in global footer
        
        // Create and append command palette overlay directly to body
        const commandPalette = document.createElement('div');
        commandPalette.className = 'command-palette-overlay';
        commandPalette.id = 'commandPaletteOverlay';
        commandPalette.onclick = (e) => this.closeCommandPalette(e);
        commandPalette.innerHTML = `
            <div class="command-palette" onclick="event.stopPropagation()">
                <div class="command-search">
                    <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"/>
                        <path d="m21 21-4.35-4.35"/>
                    </svg>
                    <input type="text" id="commandInput" placeholder="Type a command or search..." autocomplete="off" spellcheck="false">
                    <div class="command-search-actions">
                        <button class="command-options-btn" onclick="smartNav.toggleCommandOptions()" title="Settings">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="3"/>
                                <path d="M12 1v6m0 6v6m3.96-10.73l4.24-4.24M7.8 16.2l-4.24 4.24M1 12h6m6 0h6m-10.73 3.96l-4.24 4.24M16.2 7.8l4.24-4.24"/>
                            </svg>
                        </button>
                        <kbd class="shortcut-hint">ESC</kbd>
                    </div>
                </div>
                <div class="command-options" id="commandOptions" style="display: none;">
                    <div class="options-grid">
                        <label class="option-item">
                            <input type="checkbox" checked onchange="smartNav.toggleOption('showRecent')">
                            <span>Show Recent Commands</span>
                        </label>
                        <label class="option-item">
                            <input type="checkbox" checked onchange="smartNav.toggleOption('showIcons')">
                            <span>Show Icons</span>
                        </label>
                        <label class="option-item">
                            <input type="checkbox" checked onchange="smartNav.toggleOption('showShortcuts')">
                            <span>Show Keyboard Shortcuts</span>
                        </label>
                        <label class="option-item">
                            <input type="checkbox" onchange="smartNav.toggleOption('compactMode')">
                            <span>Compact Mode</span>
                        </label>
                    </div>
                </div>
                <div class="command-results" id="commandResults">
                    <div class="command-section">
                        <div class="command-section-title">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                            </svg>
                            Quick Actions
                        </div>
                        <div class="command-item" onclick="smartNav.executeCommand('new-request')">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M12 5v14m-7-7h14"/>
                            </svg>
                            <span>Create New Request</span>
                            <kbd>Alt+N</kbd>
                        </div>
                        <div class="command-item" onclick="smartNav.executeCommand('search-products')">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <circle cx="11" cy="11" r="8"/>
                                <path d="m21 21-4.35-4.35"/>
                            </svg>
                            <span>Search Products</span>
                            <kbd>Alt+P</kbd>
                        </div>
                        <div class="command-item" onclick="smartNav.executeCommand('search-suppliers')">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                                <circle cx="9" cy="7" r="4"/>
                                <path d="M23 21v-2a4 4 0 00-3-3.87m-4-12a4 4 0 010 7.75"/>
                            </svg>
                            <span>Search Suppliers</span>
                            <kbd>Alt+S</kbd>
                        </div>
                        <div class="command-item" onclick="smartNav.executeCommand('toggle-dark')">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <circle cx="12" cy="12" r="5"/>
                                <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
                            </svg>
                            <span>Toggle Dark Mode</span>
                            <kbd>Alt+D</kbd>
                        </div>
                    </div>
                    <div class="command-section">
                        <div class="command-section-title">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                                <polyline points="9 22 9 12 15 12 15 22"/>
                            </svg>
                            Navigation
                        </div>
                        <div class="command-item" onclick="smartNav.navigateTo('/dashboard.html')">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <rect x="3" y="3" width="7" height="7"/>
                                <rect x="14" y="3" width="7" height="7"/>
                                <rect x="14" y="14" width="7" height="7"/>
                                <rect x="3" y="14" width="7" height="7"/>
                            </svg>
                            <span>Dashboard</span>
                            <kbd>G D</kbd>
                        </div>
                        <div class="command-item" onclick="smartNav.navigateTo('/products.html')">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/>
                                <line x1="7" y1="7" x2="7.01" y2="7"/>
                            </svg>
                            <span>Products</span>
                            <kbd>G P</kbd>
                        </div>
                        <div class="command-item" onclick="smartNav.navigateTo('/requests.html')">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                                <polyline points="14 2 14 8 20 8"/>
                                <line x1="16" y1="13" x2="8" y2="13"/>
                                <line x1="16" y1="17" x2="8" y2="17"/>
                                <polyline points="10 9 9 9 8 9"/>
                            </svg>
                            <span>Requests</span>
                            <kbd>G R</kbd>
                        </div>
                        <div class="command-item" onclick="smartNav.navigateTo('/users.html')">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                                <circle cx="9" cy="7" r="4"/>
                                <path d="M23 21v-2a4 4 0 00-3-3.87m-4-12a4 4 0 010 7.75"/>
                            </svg>
                            <span>Users</span>
                            <kbd>G U</kbd>
                        </div>
                        <div class="command-item" onclick="smartNav.navigateTo('/supplier-search.html')">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <circle cx="11" cy="11" r="8"/>
                                <path d="m21 21-4.35-4.35"/>
                                <path d="M8 11h6"/>
                            </svg>
                            <span>Supplier Search</span>
                            <kbd>G S</kbd>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(commandPalette);

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
                { icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>', text: 'Morning Tasks', onclick: 'smartNav.showMorningTasks()' },
                { icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>', text: 'Daily Overview', onclick: 'window.location.href="/dashboard.html"' }
            ];
        }
        
        // Context-based suggestions
        if (currentPath.includes('request')) {
            return [
                { icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="10" x2="15" y2="10"/><line x1="9" y1="14" x2="15" y2="14"/></svg>', text: 'Create Console', onclick: 'smartNav.createConsole()' },
                { icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>', text: 'View Templates', onclick: 'smartNav.showTemplates()' }
            ];
        }
        
        // Default smart actions
        return [
            { icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>', text: 'AI Suggestions', onclick: 'smartNav.showAISuggestions()' },
            { icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13"/><path d="M22 2L15 22L11 13L2 9L22 2Z"/></svg>', text: 'Quick Start', onclick: 'smartNav.showQuickStart()' }
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
            
            // Alt+N - Create New Request
            if (e.altKey && e.key === 'n') {
                e.preventDefault();
                this.executeCommand('new-request');
            }
            
            // Alt+P - Search Products
            if (e.altKey && e.key === 'p') {
                e.preventDefault();
                this.executeCommand('search-products');
            }
            
            // Alt+S - Search Suppliers
            if (e.altKey && e.key === 's') {
                e.preventDefault();
                this.executeCommand('search-suppliers');
            }
            
            // Alt+D - Toggle Dark Mode
            if (e.altKey && e.key === 'd') {
                e.preventDefault();
                this.executeCommand('toggle-dark');
            }
            
            // Alt+H - Go to Dashboard
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                window.location.href = '/dashboard.html';
            }
            
            // Alt+R - Go to Requests
            if (e.altKey && e.key === 'r') {
                e.preventDefault();
                window.location.href = '/requests.html';
            }
            
            // Alt+U - Go to Users
            if (e.altKey && e.key === 'u') {
                e.preventDefault();
                window.location.href = '/users.html';
            }
            
            // Alt+M - Go to Price Management
            if (e.altKey && e.key === 'm') {
                e.preventDefault();
                window.location.href = '/price-management.html';
            }
            
            // Vim-style "G" shortcuts
            if (!e.ctrlKey && !e.altKey && !e.metaKey && e.key === 'g') {
                // Don't trigger if user is typing in an input/textarea
                const activeElement = document.activeElement;
                const isTyping = activeElement && (
                    activeElement.tagName === 'INPUT' || 
                    activeElement.tagName === 'TEXTAREA' || 
                    activeElement.contentEditable === 'true'
                );
                
                if (!isTyping) {
                    if (this.waitingForSecondKey) {
                        // If already waiting, reset
                        this.waitingForSecondKey = false;
                    } else {
                        // Start waiting for second key
                        e.preventDefault();
                        this.waitingForSecondKey = true;
                        
                        // Reset after 2 seconds if no second key pressed
                        setTimeout(() => {
                            this.waitingForSecondKey = false;
                        }, 2000);
                    }
                }
            }
            
            // Handle second key of vim-style shortcuts
            if (this.waitingForSecondKey && !e.ctrlKey && !e.altKey && !e.metaKey) {
                this.waitingForSecondKey = false;
                e.preventDefault();
                
                switch(e.key.toLowerCase()) {
                    case 'd':
                        window.location.href = '/dashboard.html';
                        break;
                    case 'p':
                        window.location.href = '/products.html';
                        break;
                    case 'r':
                        window.location.href = '/requests.html';
                        break;
                    case 'u':
                        window.location.href = '/users.html';
                        break;
                    case 's':
                        window.location.href = '/supplier-search.html';
                        break;
                }
            }
            
            // Escape - Close modals
            if (e.key === 'Escape') {
                this.closeAllModals();
                this.waitingForSecondKey = false; // Also reset vim-style shortcut state
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


    toggleSidebar() {
        const sidebar = document.getElementById('smartSidebar');
        sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    }

    toggleCommandPalette() {
        const overlay = document.getElementById('commandPaletteOverlay');
        if (!overlay) return;
        
        if (overlay.classList.contains('active')) {
            this.closeCommandPalette();
        } else {
            this.openCommandPalette();
        }
    }

    openCommandPalette() {
        const overlay = document.getElementById('commandPaletteOverlay');
        const input = document.getElementById('commandInput');
        if (!overlay || !input) return;
        
        overlay.classList.add('active');
        setTimeout(() => {
            input.focus();
            input.select();
        }, 100);
        
        // Initialize command search
        this.initializeCommandSearch();
    }

    closeCommandPalette(event) {
        if (event && event.target && event.target.id !== 'commandPaletteOverlay') return;
        const overlay = document.getElementById('commandPaletteOverlay');
        if (overlay) overlay.classList.remove('active');
    }

    initializeCommandSearch() {
        const input = document.getElementById('commandInput');
        if (!input) return;
        
        // Remove existing listeners to avoid duplicates
        const newInput = input.cloneNode(true);
        input.parentNode.replaceChild(newInput, input);
        
        newInput.addEventListener('input', (e) => this.filterCommands(e.target.value));
        newInput.addEventListener('keydown', (e) => this.handleCommandKeydown(e));
    }

    filterCommands(query) {
        const lowerQuery = query.toLowerCase();
        const items = document.querySelectorAll('.command-item');
        
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(lowerQuery)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    handleCommandKeydown(e) {
        if (e.key === 'Escape') {
            this.closeCommandPalette();
        } else if (e.key === 'Enter') {
            const activeItem = document.querySelector('.command-item.active');
            if (activeItem) {
                activeItem.click();
            }
        } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault();
            this.navigateCommands(e.key === 'ArrowDown' ? 1 : -1);
        }
    }

    navigateCommands(direction) {
        const items = Array.from(document.querySelectorAll('.command-item:not([style*="display: none"])'));
        const currentActive = document.querySelector('.command-item.active');
        let currentIndex = currentActive ? items.indexOf(currentActive) : -1;
        
        if (currentActive) currentActive.classList.remove('active');
        
        currentIndex += direction;
        if (currentIndex < 0) currentIndex = items.length - 1;
        if (currentIndex >= items.length) currentIndex = 0;
        
        if (items[currentIndex]) {
            items[currentIndex].classList.add('active');
            items[currentIndex].scrollIntoView({ block: 'nearest' });
        }
    }

    executeCommand(command) {
        switch(command) {
            case 'new-request':
                window.location.href = '/request-create.html';
                break;
            case 'search-products':
                window.location.href = '/products.html';
                break;
            case 'search-suppliers':
                window.location.href = '/supplier-search.html';
                break;
            case 'toggle-dark':
                this.toggleGlobalTheme();
                break;
            default:
                console.log(`Executing command: ${command}`);
        }
        this.closeCommandPalette();
    }
    
    toggleGlobalTheme() {
        // Toggle the dark mode class
        const isDark = document.body.classList.toggle('dark-mode');
        const theme = isDark ? 'dark' : 'light';
        
        // Save to multiple localStorage keys for compatibility
        localStorage.setItem('darkMode', isDark);
        localStorage.setItem('dashboardTheme', theme);
        localStorage.setItem('theme', theme);
        
        // Update any theme toggle buttons on the page
        const toggleButtons = document.querySelectorAll('.nav-theme-toggle .theme-icon, #dashboardDarkModeToggle .theme-icon');
        toggleButtons.forEach(icon => {
            if (icon) {
                icon.style.transform = 'rotate(360deg)';
                setTimeout(() => {
                    if (isDark) {
                        icon.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="5"></circle>
                            <line x1="12" y1="1" x2="12" y2="3"></line>
                            <line x1="12" y1="21" x2="12" y2="23"></line>
                            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                            <line x1="1" y1="12" x2="3" y2="12"></line>
                            <line x1="21" y1="12" x2="23" y2="12"></line>
                            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                        </svg>`;
                    } else {
                        icon.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                        </svg>`;
                    }
                    icon.style.transform = '';
                }, 300);
            }
        });
        
        // If dashboard's toggle function exists, use it for compatibility
        if (window.toggleDashboardDarkMode) {
            // Dashboard page has its own handler, let it know theme changed
            return;
        }
    }
    
    toggleCommandOptions() {
        const optionsPanel = document.getElementById('commandOptions');
        if (optionsPanel) {
            const isVisible = optionsPanel.style.display !== 'none';
            optionsPanel.style.display = isVisible ? 'none' : 'block';
            
            // Rotate the settings icon
            const btn = document.querySelector('.command-options-btn');
            if (btn) {
                btn.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(90deg)';
            }
        }
    }
    
    toggleOption(option) {
        console.log(`Toggling option: ${option}`);
        // Store preferences in localStorage
        const preferences = JSON.parse(localStorage.getItem('commandPalettePrefs') || '{}');
        const checkbox = event.target;
        preferences[option] = checkbox.checked;
        localStorage.setItem('commandPalettePrefs', JSON.stringify(preferences));
        
        // Apply the option changes
        switch(option) {
            case 'showIcons':
                document.querySelectorAll('.command-item svg').forEach(icon => {
                    icon.style.display = checkbox.checked ? 'block' : 'none';
                });
                break;
            case 'showShortcuts':
                document.querySelectorAll('.command-item kbd').forEach(kbd => {
                    kbd.style.display = checkbox.checked ? 'inline-block' : 'none';
                });
                break;
            case 'compactMode':
                document.querySelectorAll('.command-item').forEach(item => {
                    item.style.padding = checkbox.checked ? '8px 12px' : '12px 14px';
                });
                break;
        }
    }

    navigateTo(path) {
        window.location.href = path;
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
            5: 'Admin'
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

    toggleUserMenu(event) {
        event.stopPropagation();
        const dropdown = document.getElementById('userDropdown');
        
        if (dropdown) {
            const isVisible = dropdown.style.display === 'block';
            
            // Hide all dropdowns first
            document.querySelectorAll('.user-dropdown').forEach(d => {
                d.style.display = 'none';
            });
            
            // Toggle this dropdown
            dropdown.style.display = isVisible ? 'none' : 'block';
            
            // Add click outside listener
            if (!isVisible) {
                setTimeout(() => {
                    document.addEventListener('click', this.hideUserMenu);
                }, 100);
            }
        }
    }
    
    hideUserMenu = () => {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
        document.removeEventListener('click', this.hideUserMenu);
    }

    logout() {
        if (confirm('Are you sure you want to sign out?')) {
            localStorage.clear();
            window.location.href = '/';
        }
    }
    
    showKeyboardShortcuts() {
        const shortcuts = [
            { keys: 'Ctrl + K', action: 'Open quick search' },
            { keys: 'Ctrl + /', action: 'Toggle sidebar' },
            { keys: 'Ctrl + B', action: 'Toggle dark mode' },
            { keys: 'Esc', action: 'Close modals' },
            { keys: 'Alt + N', action: 'Create new request' },
            { keys: 'Alt + H', action: 'Go to home' },
        ];
        
        let message = 'Keyboard Shortcuts:\n\n';
        shortcuts.forEach(s => {
            message += `${s.keys.padEnd(15)} - ${s.action}\n`;
        });
        
        alert(message);
    }

    initializeTheme() {
        // Apply saved theme on page load from dashboard preference
        const savedTheme = localStorage.getItem('dashboardTheme') || 'light';
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
        }
        // Update the icon to match current theme
        setTimeout(() => {
            const icon = document.getElementById('navThemeIcon');
            if (icon) {
                icon.innerHTML = savedTheme === 'dark' ? 
                    `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="5"></circle>
                        <line x1="12" y1="1" x2="12" y2="3"></line>
                        <line x1="12" y1="21" x2="12" y2="23"></line>
                        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                        <line x1="1" y1="12" x2="3" y2="12"></line>
                        <line x1="21" y1="12" x2="23" y2="12"></line>
                        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                    </svg>` : 
                    `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                    </svg>`;
            }
        }, 100);
    }

    toggleTheme() {
        // For dashboard page, use the dashboard dark mode controller
        if (window.toggleDashboardDarkMode) {
            window.toggleDashboardDarkMode();
        } else {
            // For other pages, toggle the dark-mode class directly
            const isDark = document.body.classList.contains('dark-mode');
            
            if (isDark) {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('dashboardTheme', 'light');
            } else {
                document.body.classList.add('dark-mode');
                localStorage.setItem('dashboardTheme', 'dark');
            }
            
            // Update icon
            const icon = document.getElementById('navThemeIcon');
            if (icon) {
                icon.innerHTML = isDark ? 
                    `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                    </svg>` : 
                    `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="5"></circle>
                        <line x1="12" y1="1" x2="12" y2="3"></line>
                        <line x1="12" y1="21" x2="12" y2="23"></line>
                        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                        <line x1="1" y1="12" x2="3" y2="12"></line>
                        <line x1="21" y1="12" x2="23" y2="12"></line>
                        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                    </svg>`;
            }
            
            // Show toast if available
            if (window.toast) {
                window.toast.success(`Dark mode ${!isDark ? 'enabled' : 'disabled'}`, 'Theme Changed');
            }
        }
    }

    closeAllModals() {
        // Close modals if any
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