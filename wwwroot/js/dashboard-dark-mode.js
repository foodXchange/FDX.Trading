// Dashboard-specific Dark Mode Implementation
(function() {
    // Check for saved theme preference or default to 'light' mode
    let currentTheme = localStorage.getItem('dashboardTheme') || 'light';
    
    // Apply the theme on page load
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
    
    // Create and add the dark mode toggle button
    function createDarkModeToggle() {
        const button = document.createElement('button');
        button.className = 'dark-mode-toggle';
        button.id = 'darkModeToggle';
        button.innerHTML = currentTheme === 'dark' ? '☀️' : '🌙';
        button.title = 'Toggle dark mode';
        
        // Add styles for the button
        const style = document.createElement('style');
        style.textContent = `
            .dark-mode-toggle {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                background: white;
                border: 2px solid #dee2e6;
                border-radius: 12px;
                padding: 10px;
                cursor: pointer;
                font-size: 24px;
                width: 50px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .dark-mode-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            body.dark-mode .dark-mode-toggle {
                background: #2d2d2d;
                border-color: #495057;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            }
            
            /* Dark mode styles for dashboard */
            body.dark-mode {
                background: #1a1a1a !important;
                color: #e9ecef !important;
            }
            
            body.dark-mode .dashboard-container {
                color: #e9ecef;
            }
            
            body.dark-mode .stat-card {
                background: #2d2d2d !important;
                border: 1px solid #495057;
                color: #e9ecef;
            }
            
            body.dark-mode .quick-action-card {
                background: #2d2d2d !important;
                border-color: #495057;
                color: #e9ecef;
            }
            
            body.dark-mode .quick-action-card:hover {
                background: #3a3a3a !important;
                border-color: #6c757d;
            }
            
            body.dark-mode .stat-value {
                color: #e9ecef;
            }
            
            body.dark-mode .stat-label {
                color: #adb5bd;
            }
            
            body.dark-mode .section-card {
                background: #2d2d2d !important;
                border: 1px solid #495057;
            }
            
            body.dark-mode .section-title {
                color: #e9ecef;
            }
            
            body.dark-mode .activity-item {
                background: #3a3a3a !important;
                border-color: #495057;
            }
            
            body.dark-mode .activity-time {
                color: #adb5bd;
            }
            
            body.dark-mode .trend-select {
                background: #2d2d2d;
                color: #e9ecef;
                border-color: #495057;
            }
            
            body.dark-mode .new-user-tip {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            }
            
            body.dark-mode .smart-sidebar {
                background: #2d2d2d !important;
                border-right-color: #495057;
            }
            
            body.dark-mode .nav-item:hover {
                background: #3a3a3a !important;
            }
            
            body.dark-mode .user-section {
                background: #2d2d2d;
                border-top-color: #495057;
            }
            
            body.dark-mode .user-menu {
                background: #3a3a3a;
            }
            
            body.dark-mode .sidebar-brand {
                border-bottom-color: #495057;
            }
            
            body.dark-mode .nav-section-title {
                color: #adb5bd;
            }
            
            body.dark-mode .quick-search {
                background: #3a3a3a;
                border-color: #495057;
                color: #e9ecef;
            }
            
            body.dark-mode .nav-theme-toggle {
                background: #3a3a3a;
                border-color: #495057;
            }
        `;
        document.head.appendChild(style);
        
        // Toggle functionality
        button.onclick = function() {
            if (document.body.classList.contains('dark-mode')) {
                document.body.classList.remove('dark-mode');
                currentTheme = 'light';
                button.innerHTML = '🌙';
            } else {
                document.body.classList.add('dark-mode');
                currentTheme = 'dark';
                button.innerHTML = '☀️';
            }
            
            // Save preference
            localStorage.setItem('dashboardTheme', currentTheme);
            
            // Show toast notification if available
            if (window.toast) {
                window.toast.success(`Switched to ${currentTheme} mode`);
            }
        };
        
        document.body.appendChild(button);
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createDarkModeToggle);
    } else {
        createDarkModeToggle();
    }
})();