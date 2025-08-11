// FDX Trading - Enhanced Navigation System
class FDXNavigation {
    constructor() {
        this.currentUser = null;
        this.currentPath = window.location.pathname;
        this.init();
    }

    init() {
        // Load user info
        this.loadUserInfo();
        
        // Inject navigation
        this.injectNavigation();
        
        // Set active state
        this.setActiveState();
        
        // Initialize interactions
        this.initializeInteractions();
    }

    loadUserInfo() {
        const userStr = localStorage.getItem('currentUser');
        if (userStr) {
            this.currentUser = JSON.parse(userStr);
        }
    }

    getNavigationHTML() {
        const userRole = this.currentUser?.type || 0;
        const userName = this.currentUser?.displayName || this.currentUser?.username || 'Guest';
        const userCompany = this.currentUser?.companyName || '';

        return `
            <nav class="fdx-navbar">
                <div class="navbar-container">
                    <!-- Logo -->
                    <a href="/dashboard.html" class="navbar-brand">
                        <div class="brand-logo">
                            <span class="logo-text">FDX</span>
                        </div>
                        <span class="brand-name">Trading</span>
                    </a>

                    <!-- Main Navigation -->
                    <div class="navbar-main">
                        <!-- Procurement Menu -->
                        <div class="nav-dropdown">
                            <button class="nav-dropdown-btn">
                                <span>📦 Procurement</span>
                                <svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 12 12">
                                    <path d="M6 9L2 4h8z" fill="currentColor"/>
                                </svg>
                            </button>
                            <div class="nav-dropdown-menu">
                                <a href="/requests.html" class="dropdown-item">
                                    <i>📝</i>
                                    <div>
                                        <span class="item-title">Requests</span>
                                        <span class="item-desc">Create & manage procurement requests</span>
                                    </div>
                                </a>
                                <a href="/console-list.html" class="dropdown-item">
                                    <i>🎛️</i>
                                    <div>
                                        <span class="item-title">Consoles</span>
                                        <span class="item-desc">Workflow management & tracking</span>
                                    </div>
                                </a>
                                <a href="/quotes.html" class="dropdown-item">
                                    <i>💰</i>
                                    <div>
                                        <span class="item-title">Quotes</span>
                                        <span class="item-desc">View & compare supplier quotes</span>
                                    </div>
                                </a>
                                <a href="/orders.html" class="dropdown-item">
                                    <i>📋</i>
                                    <div>
                                        <span class="item-title">Orders</span>
                                        <span class="item-desc">Track purchase orders</span>
                                    </div>
                                </a>
                            </div>
                        </div>

                        <!-- Catalog Menu -->
                        <div class="nav-dropdown">
                            <button class="nav-dropdown-btn">
                                <span>🏪 Catalog</span>
                                <svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 12 12">
                                    <path d="M6 9L2 4h8z" fill="currentColor"/>
                                </svg>
                            </button>
                            <div class="nav-dropdown-menu">
                                <a href="/products.html" class="dropdown-item">
                                    <i>📦</i>
                                    <div>
                                        <span class="item-title">Products</span>
                                        <span class="item-desc">Browse product catalog</span>
                                    </div>
                                </a>
                                <a href="/supplier-catalog.html" class="dropdown-item">
                                    <i>🏢</i>
                                    <div>
                                        <span class="item-title">Suppliers</span>
                                        <span class="item-desc">Supplier directory & profiles</span>
                                    </div>
                                </a>
                                <a href="/price-management.html" class="dropdown-item">
                                    <i>💵</i>
                                    <div>
                                        <span class="item-title">Pricing</span>
                                        <span class="item-desc">Price lists & history</span>
                                    </div>
                                </a>
                                <a href="/categories.html" class="dropdown-item">
                                    <i>🏷️</i>
                                    <div>
                                        <span class="item-title">Categories</span>
                                        <span class="item-desc">Product categories</span>
                                    </div>
                                </a>
                            </div>
                        </div>

                        <!-- Tools Menu -->
                        <div class="nav-dropdown">
                            <button class="nav-dropdown-btn">
                                <span>🛠️ Tools</span>
                                <svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 12 12">
                                    <path d="M6 9L2 4h8z" fill="currentColor"/>
                                </svg>
                            </button>
                            <div class="nav-dropdown-menu">
                                <a href="/analytics.html" class="dropdown-item">
                                    <i>📊</i>
                                    <div>
                                        <span class="item-title">Analytics</span>
                                        <span class="item-desc">Reports & insights</span>
                                    </div>
                                </a>
                                <a href="/contacts.html" class="dropdown-item">
                                    <i>👥</i>
                                    <div>
                                        <span class="item-title">Contacts</span>
                                        <span class="item-desc">Manage contacts</span>
                                    </div>
                                </a>
                                <a href="/documents.html" class="dropdown-item">
                                    <i>📄</i>
                                    <div>
                                        <span class="item-title">Documents</span>
                                        <span class="item-desc">Contracts & certificates</span>
                                    </div>
                                </a>
                                <a href="/messages.html" class="dropdown-item">
                                    <i>💬</i>
                                    <div>
                                        <span class="item-title">Messages</span>
                                        <span class="item-desc">Communication center</span>
                                    </div>
                                </a>
                            </div>
                        </div>

                        <!-- Quick Links -->
                        <a href="/dashboard.html" class="nav-link">
                            <span>📈 Dashboard</span>
                        </a>

                        <!-- University -->
                        <a href="/university-dashboard.html" class="nav-link nav-university">
                            <span>🎓 University</span>
                            <span class="badge-new">NEW</span>
                        </a>
                    </div>

                    <!-- Right Section -->
                    <div class="navbar-right">
                        <!-- Search -->
                        <button class="nav-search-btn" onclick="fdxNav.toggleSearch()">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M9 17C13.4183 17 17 13.4183 17 9C17 4.58172 13.4183 1 9 1C4.58172 1 1 4.58172 1 9C1 13.4183 4.58172 17 9 17Z" stroke="currentColor" stroke-width="2"/>
                                <path d="M19 19L14.65 14.65" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                            </svg>
                        </button>

                        <!-- Notifications -->
                        <button class="nav-notif-btn">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M15 7C15 5.67392 14.4732 4.40215 13.5355 3.46447C12.5979 2.52678 11.3261 2 10 2C8.67392 2 7.40215 2.52678 6.46447 3.46447C5.52678 4.40215 5 5.67392 5 7C5 14 2 16 2 16H18C18 16 15 14 15 7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M11.73 19C11.5542 19.3031 11.3019 19.5547 10.9982 19.7295C10.6946 19.9044 10.3504 19.9965 10 19.9965C9.64964 19.9965 9.30541 19.9044 9.00179 19.7295C8.69818 19.5547 8.44583 19.3031 8.27 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            <span class="notif-badge">3</span>
                        </button>

                        <!-- User Menu -->
                        <div class="nav-dropdown user-dropdown">
                            <button class="user-dropdown-btn">
                                <div class="user-avatar">
                                    ${userName.charAt(0).toUpperCase()}
                                </div>
                                <div class="user-info">
                                    <span class="user-name">${userName}</span>
                                    <span class="user-role">${this.getRoleName(userRole)}</span>
                                </div>
                                <svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 12 12">
                                    <path d="M6 9L2 4h8z" fill="currentColor"/>
                                </svg>
                            </button>
                            <div class="nav-dropdown-menu user-menu">
                                <div class="user-menu-header">
                                    <div class="user-avatar-large">
                                        ${userName.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <div class="user-name">${userName}</div>
                                        <div class="user-email">${this.currentUser?.email || ''}</div>
                                        <div class="user-company">${userCompany}</div>
                                    </div>
                                </div>
                                <div class="menu-divider"></div>
                                <a href="/user-profile.html" class="dropdown-item">
                                    <i>👤</i>
                                    <span>My Profile</span>
                                </a>
                                <a href="/settings.html" class="dropdown-item">
                                    <i>⚙️</i>
                                    <span>Settings</span>
                                </a>
                                <a href="/help.html" class="dropdown-item">
                                    <i>❓</i>
                                    <span>Help & Support</span>
                                </a>
                                ${userRole === 5 ? `
                                <div class="menu-divider"></div>
                                <a href="/users.html" class="dropdown-item">
                                    <i>👥</i>
                                    <span>User Management</span>
                                </a>
                                <a href="/admin.html" class="dropdown-item">
                                    <i>🔧</i>
                                    <span>Admin Panel</span>
                                </a>
                                ` : ''}
                                <div class="menu-divider"></div>
                                <a href="#" onclick="fdxNav.logout()" class="dropdown-item text-danger">
                                    <i>🚪</i>
                                    <span>Logout</span>
                                </a>
                            </div>
                        </div>

                        <!-- Mobile Menu Toggle -->
                        <button class="mobile-menu-toggle" onclick="fdxNav.toggleMobileMenu()">
                            <span></span>
                            <span></span>
                            <span></span>
                        </button>
                    </div>
                </div>

                <!-- Search Bar (Hidden by default) -->
                <div class="navbar-search" id="navbarSearch">
                    <div class="search-container">
                        <input type="text" class="search-input" placeholder="Search products, suppliers, requests..." id="globalSearch">
                        <button class="search-close" onclick="fdxNav.toggleSearch()">×</button>
                    </div>
                </div>
            </nav>
        `;
    }

    getRoleName(type) {
        const roles = {
            0: 'Buyer',
            1: 'Supplier',
            2: 'Both',
            3: 'Expert',
            4: 'Agent',
            5: 'Admin'
        };
        return roles[type] || 'User';
    }

    injectNavigation() {
        // Create navigation container
        const navContainer = document.createElement('div');
        navContainer.id = 'fdx-navigation';
        navContainer.innerHTML = this.getNavigationHTML();
        
        // Insert at beginning of body
        document.body.insertBefore(navContainer, document.body.firstChild);
    }

    setActiveState() {
        // Remove any existing active states
        document.querySelectorAll('.nav-link, .dropdown-item').forEach(link => {
            link.classList.remove('active');
        });

        // Set active based on current path
        const currentLink = document.querySelector(`a[href="${this.currentPath}"]`);
        if (currentLink) {
            currentLink.classList.add('active');
            
            // If it's in a dropdown, mark the dropdown as active too
            const dropdown = currentLink.closest('.nav-dropdown');
            if (dropdown) {
                dropdown.classList.add('active');
            }
        }
    }

    initializeInteractions() {
        // Dropdown interactions
        document.querySelectorAll('.nav-dropdown').forEach(dropdown => {
            const btn = dropdown.querySelector('.nav-dropdown-btn');
            const menu = dropdown.querySelector('.nav-dropdown-menu');
            
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.closeAllDropdowns();
                dropdown.classList.toggle('open');
            });
        });

        // Close dropdowns on outside click
        document.addEventListener('click', () => {
            this.closeAllDropdowns();
        });

        // Search functionality
        const searchInput = document.getElementById('globalSearch');
        if (searchInput) {
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch(searchInput.value);
                }
            });
        }
    }

    closeAllDropdowns() {
        document.querySelectorAll('.nav-dropdown').forEach(dropdown => {
            dropdown.classList.remove('open');
        });
    }

    toggleSearch() {
        const searchBar = document.getElementById('navbarSearch');
        searchBar.classList.toggle('active');
        if (searchBar.classList.contains('active')) {
            document.getElementById('globalSearch').focus();
        }
    }

    toggleMobileMenu() {
        document.querySelector('.navbar-main').classList.toggle('mobile-open');
        document.querySelector('.mobile-menu-toggle').classList.toggle('active');
    }

    performSearch(query) {
        if (query.trim()) {
            window.location.href = `/search.html?q=${encodeURIComponent(query)}`;
        }
    }

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.removeItem('currentUser');
            localStorage.removeItem('authToken');
            window.location.href = '/';
        }
    }
}

// Initialize navigation when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.fdxNav = new FDXNavigation();
    });
} else {
    window.fdxNav = new FDXNavigation();
}