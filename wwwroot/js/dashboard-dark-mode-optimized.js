// Dashboard Dark Mode Controller - Integrated with Navigation
(function() {
    // Check for saved theme preference or default to 'light' mode
    let currentTheme = localStorage.getItem('dashboardTheme') || 'light';
    
    // Apply the theme on page load
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
    
    // Remove navigation dark mode toggle since it's now in the footer
    function removeNavigationDarkModeToggle() {
        // Check for and remove any existing navigation dark mode toggle
        const checkForToggle = setInterval(() => {
            const existingToggle = document.querySelector('.nav-theme-toggle, #dashboardDarkModeToggle');
            if (existingToggle) {
                existingToggle.remove();
                clearInterval(checkForToggle);
            }
            
            // Stop checking after 3 seconds
            setTimeout(() => clearInterval(checkForToggle), 3000);
        }, 100);
        
        // Add optimized styles
        const style = document.createElement('style');
        style.textContent = `
            /* Smooth transitions for all elements */
            * {
                transition: background-color 0.3s ease, 
                            color 0.3s ease, 
                            border-color 0.3s ease,
                            box-shadow 0.3s ease !important;
            }
            
            /* Enhanced toggle button in navigation */
            .nav-theme-toggle {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
                color: #fff;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-right: 10px;
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .nav-theme-toggle:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: scale(1.05);
            }
            
            body.dark-mode .nav-theme-toggle {
                background: rgba(99, 102, 241, 0.2);
                border-color: rgba(99, 102, 241, 0.4);
            }
            
            body.dark-mode .nav-theme-toggle:hover {
                background: rgba(99, 102, 241, 0.3);
            }
            
            .theme-icon {
                font-size: 18px;
                display: inline-block;
                transition: transform 0.3s ease;
            }
            
            .nav-theme-toggle:active .theme-icon {
                transform: rotate(360deg);
            }
            
            /* Optimized Dark Mode Color Scheme */
            body.dark-mode {
                background: linear-gradient(135deg, #0f1419 0%, #1a1d24 100%) !important;
                color: #f0f2f5 !important;  /* Lighter text for better visibility */
            }
            
            /* Fix all white backgrounds to dark */
            body.dark-mode * {
                background-color: transparent;
            }
            
            body.dark-mode input,
            body.dark-mode select,
            body.dark-mode textarea,
            body.dark-mode .form-control,
            body.dark-mode .form-select {
                background: #1e2028 !important;
                color: #f0f2f5 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .card,
            body.dark-mode .modal-content,
            body.dark-mode .dropdown-menu {
                background: #1e2028 !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .bg-white,
            body.dark-mode .bg-light {
                background: #1e2028 !important;
            }
            
            body.dark-mode .text-dark,
            body.dark-mode .text-muted {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode h1,
            body.dark-mode h2,
            body.dark-mode h3,
            body.dark-mode h4,
            body.dark-mode h5,
            body.dark-mode h6,
            body.dark-mode .h1,
            body.dark-mode .h2,
            body.dark-mode .h3,
            body.dark-mode .h4,
            body.dark-mode .h5,
            body.dark-mode .h6 {
                color: #ffffff !important;
            }
            
            body.dark-mode p,
            body.dark-mode span,
            body.dark-mode div,
            body.dark-mode li {
                color: inherit;
            }
            
            /* Dashboard container */
            body.dark-mode .dashboard-container {
                color: #f0f2f5;
                background: transparent !important;
            }
            
            /* Stat cards with gradient borders */
            body.dark-mode .stat-card {
                background: linear-gradient(145deg, #1e2028, #282c37) !important;
                border: 1px solid transparent;
                background-clip: padding-box;
                position: relative;
                color: #f0f2f5 !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            
            body.dark-mode .stat-card * {
                color: inherit !important;
            }
            
            body.dark-mode .stat-card::before {
                content: '';
                position: absolute;
                top: 0; right: 0; bottom: 0; left: 0;
                z-index: -1;
                margin: -1px;
                border-radius: inherit;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            body.dark-mode .stat-card:hover::before {
                opacity: 0.3;
            }
            
            /* Quick action cards */
            body.dark-mode .quick-action-card {
                background: linear-gradient(145deg, #1e2028, #282c37) !important;
                border: 1px solid #404450;
                color: #f0f2f5 !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }
            
            body.dark-mode .quick-action-card * {
                color: inherit !important;
            }
            
            body.dark-mode .quick-action-card:hover {
                background: linear-gradient(145deg, #282c37, #32374a) !important;
                border-color: #6366f1;
                transform: translateY(-4px);
                box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);
            }
            
            /* Values and labels */
            body.dark-mode .stat-value {
                color: #ffffff !important;
                font-weight: 700;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            
            body.dark-mode .stat-label {
                color: #b8bdc6 !important;
                font-weight: 500;
            }
            
            /* Section cards with subtle gradient */
            body.dark-mode .section-card {
                background: linear-gradient(145deg, #1e2028, #23262f) !important;
                border: 1px solid #363a45;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .section-card * {
                color: inherit;
            }
            
            body.dark-mode .section-card:hover {
                box-shadow: 0 6px 20px rgba(0,0,0,0.25);
            }
            
            body.dark-mode .section-title {
                color: #ffffff !important;
                font-weight: 600;
            }
            
            /* Activity items with hover effect */
            body.dark-mode .activity-item {
                background: linear-gradient(145deg, #23262f, #2a2d3a) !important;
                border: 1px solid #404450;
                border-left: 3px solid #6366f1;
                transition: all 0.2s ease;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .activity-item * {
                color: inherit;
            }
            
            body.dark-mode .activity-item:hover {
                background: linear-gradient(145deg, #2a2d3a, #32374a) !important;
                transform: translateX(4px);
                border-left-color: #8b5cf6;
            }
            
            body.dark-mode .activity-time {
                color: #b8bdc6 !important;
                font-size: 0.875rem;
            }
            
            /* Form elements */
            body.dark-mode .trend-select {
                background: #1e2028 !important;
                color: #f0f2f5 !important;
                border: 1px solid #404450;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            body.dark-mode .trend-select:hover {
                border-color: #6366f1;
            }
            
            body.dark-mode .trend-select:focus {
                outline: none;
                border-color: #6366f1;
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
            }
            
            /* Welcome section with vibrant gradient */
            body.dark-mode .welcome-section {
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
                box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3);
            }
            
            body.dark-mode .new-user-tip {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
            }
            
            /* Navigation sidebar */
            body.dark-mode .smart-sidebar {
                background: linear-gradient(180deg, #1e2028 0%, #23262f 100%) !important;
                border-right: 1px solid #363a45;
                box-shadow: 4px 0 12px rgba(0,0,0,0.1);
            }
            
            body.dark-mode .nav-item {
                color: #a8b3cf;
                transition: all 0.2s ease;
            }
            
            body.dark-mode .nav-item:hover {
                background: linear-gradient(90deg, #2a2d3a, #32374a) !important;
                color: #ffffff;
                padding-left: 28px;
            }
            
            body.dark-mode .nav-item.active {
                background: linear-gradient(90deg, #6366f1, #7c3aed) !important;
                color: #ffffff;
                font-weight: 600;
            }
            
            body.dark-mode .user-section {
                background: #1e2028;
                border-top: 1px solid #363a45;
            }
            
            body.dark-mode .user-menu {
                background: #23262f;
                border: 1px solid #363a45;
            }
            
            body.dark-mode .user-menu:hover {
                background: #2a2d3a;
                border-color: #6366f1;
            }
            
            body.dark-mode .sidebar-brand {
                border-bottom: 1px solid #363a45;
            }
            
            body.dark-mode .brand-logo {
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
            }
            
            body.dark-mode .nav-section-title {
                color: #8b97b1;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.75rem;
                letter-spacing: 0.5px;
            }
            
            body.dark-mode .quick-search {
                background: #23262f;
                border: 1px solid #363a45;
                color: #a8b3cf;
            }
            
            body.dark-mode .quick-search:hover {
                background: #2a2d3a;
                border-color: #6366f1;
            }
            
            /* Activity icons with better colors */
            body.dark-mode .activity-icon-primary {
                background: linear-gradient(135deg, #6366f1, #818cf8) !important;
                box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
            }
            
            body.dark-mode .activity-icon-success {
                background: linear-gradient(135deg, #10b981, #34d399) !important;
                box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
            }
            
            body.dark-mode .activity-icon-warning {
                background: linear-gradient(135deg, #f59e0b, #fbbf24) !important;
                box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
            }
            
            body.dark-mode .activity-icon-info {
                background: linear-gradient(135deg, #3b82f6, #60a5fa) !important;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
            }
            
            /* Charts and SVG elements */
            body.dark-mode svg text {
                fill: #a8b3cf;
            }
            
            body.dark-mode .chart-container {
                filter: brightness(0.9) contrast(1.1);
            }
            
            /* Scrollbar styling for dark mode */
            body.dark-mode::-webkit-scrollbar {
                width: 12px;
                background: #1e2028;
            }
            
            body.dark-mode::-webkit-scrollbar-track {
                background: #1e2028;
                border-radius: 10px;
            }
            
            body.dark-mode::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, #6366f1, #8b5cf6);
                border-radius: 10px;
                border: 2px solid #1e2028;
            }
            
            body.dark-mode::-webkit-scrollbar-thumb:hover {
                background: linear-gradient(180deg, #818cf8, #a78bfa);
            }
            
            /* Smooth color transition for badges */
            body.dark-mode .badge {
                filter: brightness(0.8) saturate(1.2);
            }
            
            /* Links in dark mode */
            body.dark-mode a {
                color: #818cf8;
            }
            
            body.dark-mode a:hover {
                color: #a78bfa;
                text-decoration: none;
            }
            
            /* Tables and other elements */
            body.dark-mode .table {
                background: #1e2028 !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .table th,
            body.dark-mode .table td {
                color: #f0f2f5 !important;
                border-color: #404450 !important;
            }
            
            /* Fix any remaining white backgrounds */
            body.dark-mode [style*="background: white"],
            body.dark-mode [style*="background:white"],
            body.dark-mode [style*="background-color: white"],
            body.dark-mode [style*="background-color:white"],
            body.dark-mode [style*="background: #fff"],
            body.dark-mode [style*="background:#fff"],
            body.dark-mode [style*="background-color: #fff"],
            body.dark-mode [style*="background-color:#fff"],
            body.dark-mode [style*="background: #ffffff"],
            body.dark-mode [style*="background:#ffffff"],
            body.dark-mode [style*="background-color: #ffffff"],
            body.dark-mode [style*="background-color:#ffffff"] {
                background: #1e2028 !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Toggle dark mode function
    function toggleDarkMode() {
        // Add animation
        const icon = document.querySelector('#dashboardDarkModeToggle .theme-icon, .nav-theme-toggle .theme-icon');
        if (icon) {
            icon.style.transform = 'rotate(360deg)';
        }
        
        setTimeout(() => {
            if (document.body.classList.contains('dark-mode')) {
                document.body.classList.remove('dark-mode');
                currentTheme = 'light';
                if (icon) {
                    icon.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                    </svg>`;
                    icon.style.transform = '';
                }
            } else {
                document.body.classList.add('dark-mode');
                currentTheme = 'dark';
                if (icon) {
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
                    icon.style.transform = '';
                }
            }
            
            // Save preference (this will be read by all pages)
            localStorage.setItem('dashboardTheme', currentTheme);
            
            // Show toast notification if available
            if (window.toast) {
                window.toast.success(`Dark mode ${currentTheme === 'dark' ? 'enabled' : 'disabled'} for all pages`, `Theme Changed`);
            }
        }, 300);
    }
    
    // Make toggle function globally available
    window.toggleDashboardDarkMode = toggleDarkMode;
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', removeNavigationDarkModeToggle);
    } else {
        removeNavigationDarkModeToggle();
    }
})();