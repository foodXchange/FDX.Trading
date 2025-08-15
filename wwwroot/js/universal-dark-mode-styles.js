// Universal Dark Mode Styles (No Toggle Button - Controlled from Dashboard)
(function() {
    // Check for saved theme preference from dashboard
    let currentTheme = localStorage.getItem('dashboardTheme') || 'light';
    
    // Apply the theme on page load
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
    
    // Add comprehensive dark mode styles
    function applyDarkModeStyles() {
        // Check if styles already exist
        if (document.getElementById('universalDarkModeStyles')) {
            return;
        }
        
        const style = document.createElement('style');
        style.id = 'universalDarkModeStyles';
        style.textContent = `
            /* Smooth transitions for theme changes */
            body, 
            body * {
                transition: background-color 0.3s ease, 
                            color 0.3s ease, 
                            border-color 0.3s ease,
                            box-shadow 0.3s ease;
            }
            
            /* Base Dark Mode Styles */
            body.dark-mode {
                background: linear-gradient(135deg, #0f1419 0%, #1a1d24 100%) !important;
                color: #f0f2f5 !important;
                min-height: 100vh;
            }
            
            /* Reset specific backgrounds to transparent */
            body.dark-mode div:not(.card):not(.modal-content):not(.dropdown-menu):not(.alert):not(.badge):not(.toast),
            body.dark-mode span:not(.badge):not(.btn),
            body.dark-mode p,
            body.dark-mode li:not(.list-group-item):not(.page-item) {
                background-color: transparent;
            }
            
            /* Main containers and cards - Override inline styles */
            body.dark-mode .container,
            body.dark-mode .container-fluid,
            body.dark-mode .card,
            body.dark-mode .modal-content,
            body.dark-mode .dropdown-menu,
            body.dark-mode .list-group-item,
            body.dark-mode .form-container,
            body.dark-mode .content-area,
            body.dark-mode .main-content {
                background: #1e2028 !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .card {
                border-color: #404450 !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            
            body.dark-mode .card-header,
            body.dark-mode .card-footer {
                background: #2a2d3a !important;
                border-color: #404450 !important;
            }
            
            /* Fix Bootstrap white backgrounds */
            body.dark-mode .bg-white,
            body.dark-mode .bg-light,
            body.dark-mode .bg-body,
            body.dark-mode .bg-body-secondary,
            body.dark-mode .bg-body-tertiary {
                background: #1e2028 !important;
            }
            
            /* Headers and text */
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
                text-shadow: 0 1px 3px rgba(0,0,0,0.3);
            }
            
            /* Text color inheritance for specific elements */
            body.dark-mode p,
            body.dark-mode span:not(.badge):not(.btn),
            body.dark-mode li:not(.list-group-item) {
                color: inherit;
            }
            
            body.dark-mode .text-dark,
            body.dark-mode .text-muted {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .text-secondary {
                color: #a0a6b0 !important;
            }
            
            body.dark-mode label {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode small,
            body.dark-mode .small {
                color: #a0a6b0 !important;
            }
            
            /* Forms and inputs */
            body.dark-mode input,
            body.dark-mode select,
            body.dark-mode textarea,
            body.dark-mode .form-control,
            body.dark-mode .form-select,
            body.dark-mode .form-check-input {
                background: #2a2d3a !important;
                color: #f0f2f5 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode input:focus,
            body.dark-mode select:focus,
            body.dark-mode textarea:focus,
            body.dark-mode .form-control:focus,
            body.dark-mode .form-select:focus {
                background: #32374a !important;
                border-color: #6366f1 !important;
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode input::placeholder,
            body.dark-mode textarea::placeholder {
                color: #808890 !important;
            }
            
            /* Tables */
            body.dark-mode .table {
                background: #1e2028 !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .table th,
            body.dark-mode .table td {
                color: #f0f2f5 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .table-striped > tbody > tr:nth-of-type(odd) > * {
                background: rgba(255, 255, 255, 0.02) !important;
            }
            
            /* Fix for all table row hovers in dark mode */
            body.dark-mode .table-hover > tbody > tr:hover > * {
                background: rgba(99, 102, 241, 0.08) !important;
                color: #ffffff !important;
            }
            
            /* Generic table row hover for non-.table-hover tables */
            body.dark-mode table tbody tr:hover {
                background: rgba(99, 102, 241, 0.08) !important;
            }
            
            body.dark-mode table tbody tr:hover td,
            body.dark-mode table tbody tr:hover th {
                background: transparent !important;
                color: #ffffff !important;
            }
            
            /* Specific fix for any table with hover effects */
            body.dark-mode tr:hover {
                background: rgba(99, 102, 241, 0.08) !important;
            }
            
            body.dark-mode tr:hover td,
            body.dark-mode tr:hover th,
            body.dark-mode tr:hover * {
                color: #ffffff !important;
            }
            
            body.dark-mode thead {
                background: #2a2d3a !important;
            }
            
            /* Buttons */
            body.dark-mode .btn-primary {
                background: #6366f1 !important;
                border-color: #6366f1 !important;
                color: #ffffff !important;
            }
            
            body.dark-mode .btn-primary:hover {
                background: #4f46e5 !important;
                border-color: #4f46e5 !important;
            }
            
            body.dark-mode .btn-secondary {
                background: #4b5563 !important;
                border-color: #4b5563 !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .btn-light {
                background: #2a2d3a !important;
                border-color: #404450 !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .btn-light:hover {
                background: #32374a !important;
                border-color: #6366f1 !important;
            }
            
            body.dark-mode .btn-outline-primary {
                color: #818cf8 !important;
                border-color: #6366f1 !important;
            }
            
            body.dark-mode .btn-outline-primary:hover {
                background: #6366f1 !important;
                color: #ffffff !important;
            }
            
            body.dark-mode .btn-outline-light {
                color: #f0f2f5 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .btn-outline-light:hover {
                background: #2a2d3a !important;
                color: #ffffff !important;
            }
            
            /* Navigation */
            body.dark-mode .navbar {
                background: #1e2028 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .navbar-light .navbar-brand,
            body.dark-mode .navbar-light .navbar-nav .nav-link {
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .navbar-light .navbar-nav .nav-link:hover {
                color: #818cf8 !important;
            }
            
            body.dark-mode .navbar-light .navbar-nav .nav-link.active {
                color: #6366f1 !important;
            }
            
            body.dark-mode .breadcrumb {
                background: transparent !important;
            }
            
            body.dark-mode .breadcrumb-item,
            body.dark-mode .breadcrumb-item a {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .breadcrumb-item.active {
                color: #f0f2f5 !important;
            }
            
            /* Dropdowns */
            body.dark-mode .dropdown-menu {
                background: #2a2d3a !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .dropdown-item {
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .dropdown-item:hover {
                background: #32374a !important;
                color: #ffffff !important;
            }
            
            body.dark-mode .dropdown-divider {
                border-color: #404450 !important;
            }
            
            /* Modals */
            body.dark-mode .modal-header {
                background: #2a2d3a !important;
                border-bottom-color: #404450 !important;
            }
            
            body.dark-mode .modal-body {
                background: #1e2028 !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .modal-footer {
                background: #2a2d3a !important;
                border-top-color: #404450 !important;
            }
            
            body.dark-mode .modal-title {
                color: #ffffff !important;
            }
            
            body.dark-mode .close,
            body.dark-mode .btn-close {
                color: #f0f2f5 !important;
                opacity: 0.8;
            }
            
            body.dark-mode .close:hover,
            body.dark-mode .btn-close:hover {
                opacity: 1;
            }
            
            /* Alerts */
            body.dark-mode .alert {
                color: #f0f2f5 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .alert-primary {
                background: rgba(99, 102, 241, 0.1) !important;
                border-color: #6366f1 !important;
            }
            
            body.dark-mode .alert-success {
                background: rgba(16, 185, 129, 0.1) !important;
                border-color: #10b981 !important;
            }
            
            body.dark-mode .alert-warning {
                background: rgba(245, 158, 11, 0.1) !important;
                border-color: #f59e0b !important;
            }
            
            body.dark-mode .alert-danger {
                background: rgba(239, 68, 68, 0.1) !important;
                border-color: #ef4444 !important;
            }
            
            body.dark-mode .alert-light {
                background: #2a2d3a !important;
                border-color: #404450 !important;
                color: #f0f2f5 !important;
            }
            
            /* Badges */
            body.dark-mode .badge {
                filter: brightness(0.8) saturate(1.2);
            }
            
            /* Pagination */
            body.dark-mode .pagination .page-link {
                background: #1e2028 !important;
                color: #f0f2f5 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .pagination .page-link:hover {
                background: #2a2d3a !important;
                border-color: #6366f1 !important;
            }
            
            body.dark-mode .pagination .page-item.active .page-link {
                background: #6366f1 !important;
                border-color: #6366f1 !important;
                color: #ffffff !important;
            }
            
            body.dark-mode .pagination .page-item.disabled .page-link {
                background: #1e2028 !important;
                color: #4b5563 !important;
                border-color: #404450 !important;
            }
            
            /* Progress bars */
            body.dark-mode .progress {
                background: #2a2d3a !important;
            }
            
            /* List groups */
            body.dark-mode .list-group-item {
                background: #1e2028 !important;
                color: #f0f2f5 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .list-group-item:hover {
                background: #2a2d3a !important;
            }
            
            body.dark-mode .list-group-item.active {
                background: #6366f1 !important;
                border-color: #6366f1 !important;
            }
            
            /* Toast notifications */
            body.dark-mode .toast {
                background: #1e2028 !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .toast-header {
                background: #2a2d3a !important;
                color: #f0f2f5 !important;
                border-bottom-color: #404450 !important;
            }
            
            body.dark-mode .toast-body {
                color: #f0f2f5 !important;
            }
            
            /* Links */
            body.dark-mode a {
                color: #818cf8;
            }
            
            body.dark-mode a:hover {
                color: #a78bfa;
                text-decoration: none;
            }
            
            /* Code blocks */
            body.dark-mode pre,
            body.dark-mode code {
                background: #2a2d3a !important;
                color: #f0f2f5 !important;
                border-color: #404450 !important;
            }
            
            /* Scrollbar styling */
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
            
            /* Fix any inline white backgrounds and request-create specific elements */
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
            body.dark-mode [style*="background-color:#ffffff"],
            body.dark-mode [style*="background: #f9f9f9"],
            body.dark-mode [style*="background:#f9f9f9"],
            body.dark-mode [style*="background-color: #f9f9f9"],
            body.dark-mode [style*="background-color:#f9f9f9"] {
                background: #1e2028 !important;
            }
            
            /* Prevent white backgrounds on hover */
            body.dark-mode tr:hover[style*="background"],
            body.dark-mode td:hover[style*="background"],
            body.dark-mode div:hover[style*="background: white"],
            body.dark-mode div:hover[style*="background: #fff"],
            body.dark-mode div:hover[style*="background: #f9f9f9"] {
                background: rgba(99, 102, 241, 0.08) !important;
            }
            
            /* Request Create Page Specific Fixes */
            body.dark-mode .header {
                background: linear-gradient(135deg, #4338ca 0%, #5b21b6 100%) !important;
            }
            
            body.dark-mode .form-section {
                background: transparent !important;
            }
            
            body.dark-mode .form-section h2 {
                color: #ffffff !important;
                border-bottom-color: #6366f1 !important;
            }
            
            body.dark-mode .form-group label {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .product-item,
            body.dark-mode .selected-products-list li {
                background: #2a2d3a !important;
                border-color: #404450 !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .product-item:hover {
                background: #32374a !important;
            }
            
            body.dark-mode .requirements-section,
            body.dark-mode .timeline-section,
            body.dark-mode .additional-info {
                background: #2a2d3a !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .status-badge {
                filter: brightness(0.8);
            }
            
            body.dark-mode .ai-suggestions {
                background: #2a2d3a !important;
                border-color: #6366f1 !important;
            }
            
            body.dark-mode .suggestion-item {
                background: #32374a !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .suggestion-item:hover {
                background: #3a3f52 !important;
                border-color: #6366f1 !important;
            }
            
            /* Special components */
            body.dark-mode .jumbotron {
                background: #2a2d3a !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .carousel-caption {
                background: rgba(30, 32, 40, 0.8) !important;
            }
            
            body.dark-mode .tooltip-inner {
                background: #2a2d3a !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .popover {
                background: #1e2028 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .popover-header {
                background: #2a2d3a !important;
                border-bottom-color: #404450 !important;
                color: #ffffff !important;
            }
            
            body.dark-mode .popover-body {
                color: #f0f2f5 !important;
            }
            
            /* Custom classes from your app */
            body.dark-mode .stat-card,
            body.dark-mode .quick-action-card,
            body.dark-mode .section-card,
            body.dark-mode .activity-item {
                background: linear-gradient(145deg, #1e2028, #282c37) !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .smart-sidebar {
                background: linear-gradient(180deg, #1e2028 0%, #23262f 100%) !important;
                border-right-color: #404450 !important;
            }
            
            body.dark-mode .nav-item {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .nav-item:hover {
                background: #2a2d3a !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .nav-item.active {
                background: linear-gradient(90deg, #6366f1, #7c3aed) !important;
                color: #ffffff !important;
            }
            
            /* Console Detail Page Specific Fixes - Complete Coverage */
            body.dark-mode .detail-header {
                background: #1e2028 !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .detail-header * {
                color: inherit !important;
            }
            
            body.dark-mode .console-code-large {
                color: #818cf8 !important;
            }
            
            body.dark-mode .console-title-large {
                color: #ffffff !important;
            }
            
            body.dark-mode .console-meta-row,
            body.dark-mode .console-meta-row * {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .meta-item,
            body.dark-mode .meta-item span {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .progress-overview {
                background: linear-gradient(135deg, #2a2d3a 0%, #32374a 100%) !important;
            }
            
            body.dark-mode .progress-stat-value {
                color: #ffffff !important;
                font-weight: 700;
            }
            
            body.dark-mode .progress-stat-label {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .progress-bar-large {
                background: #1e2028 !important;
            }
            
            body.dark-mode .progress-fill-large {
                background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%) !important;
            }
            
            body.dark-mode .content-tabs {
                background: #1e2028 !important;
            }
            
            body.dark-mode .tab-header {
                border-bottom-color: #404450 !important;
            }
            
            body.dark-mode .tab-button {
                color: #b8bdc6 !important;
                background: transparent !important;
            }
            
            body.dark-mode .tab-button:hover {
                background: #2a2d3a !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .tab-button.active {
                color: #818cf8 !important;
            }
            
            body.dark-mode .tab-button.active::after {
                background: #818cf8 !important;
            }
            
            body.dark-mode .tab-content {
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .stage-item {
                border-left-color: #404450 !important;
            }
            
            body.dark-mode .stage-item.completed {
                border-left-color: #10b981 !important;
            }
            
            body.dark-mode .stage-item.current {
                border-left-color: #818cf8 !important;
            }
            
            body.dark-mode .stage-marker {
                background: #1e2028 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .stage-item.completed .stage-marker {
                background: #10b981 !important;
                border-color: #10b981 !important;
            }
            
            body.dark-mode .stage-item.current .stage-marker {
                background: #818cf8 !important;
                border-color: #818cf8 !important;
            }
            
            body.dark-mode .stage-content {
                background: #2a2d3a !important;
            }
            
            body.dark-mode .stage-name {
                color: #ffffff !important;
            }
            
            body.dark-mode .stage-description {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .stage-date {
                color: #94a3b8 !important;
            }
            
            body.dark-mode .file-card {
                background: #2a2d3a !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .file-card:hover {
                border-color: #818cf8 !important;
                box-shadow: 0 4px 12px rgba(129, 140, 248, 0.2) !important;
            }
            
            body.dark-mode .file-name {
                color: #ffffff !important;
            }
            
            body.dark-mode .file-info {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .activity-item {
                background: #2a2d3a !important;
            }
            
            body.dark-mode .activity-icon {
                background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%) !important;
            }
            
            body.dark-mode .activity-title {
                color: #ffffff !important;
            }
            
            body.dark-mode .activity-description {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .activity-time {
                color: #94a3b8 !important;
            }
            
            body.dark-mode .action-bar {
                background: #1e2028 !important;
            }
            
            body.dark-mode .empty-placeholder {
                color: #94a3b8 !important;
            }
            
            body.dark-mode .empty-text {
                color: #94a3b8 !important;
            }
            
            /* Status badges in dark mode */
            body.dark-mode .status-active {
                background: rgba(16, 185, 129, 0.2) !important;
                color: #10b981 !important;
            }
            
            body.dark-mode .status-paused {
                background: rgba(249, 115, 22, 0.2) !important;
                color: #f97316 !important;
            }
            
            body.dark-mode .status-completed {
                background: rgba(139, 92, 246, 0.2) !important;
                color: #a78bfa !important;
            }
            
            /* Action buttons in dark mode */
            body.dark-mode .btn-edit {
                background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%) !important;
            }
            
            body.dark-mode .btn-pause {
                background: rgba(249, 115, 22, 0.2) !important;
                color: #f97316 !important;
            }
            
            body.dark-mode .btn-complete {
                background: rgba(16, 185, 129, 0.2) !important;
                color: #10b981 !important;
            }
            
            body.dark-mode .btn-export {
                background: #2a2d3a !important;
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .btn-delete {
                background: rgba(239, 68, 68, 0.2) !important;
                color: #ef4444 !important;
            }
            
            /* Details tab styling */
            body.dark-mode #detailsTab > div > div {
                background: #2a2d3a !important;
                color: #f0f2f5 !important;
            }
            
            body.dark-mode #detailsTab strong {
                color: #ffffff !important;
            }
            
            body.dark-mode #detailsTab span {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .detail-section {
                background: #1e2028 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .section-header {
                color: #ffffff !important;
            }
            
            body.dark-mode .info-grid {
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .info-label {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .info-value {
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .product-card {
                background: #2a2d3a !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .product-name {
                color: #ffffff !important;
            }
            
            body.dark-mode .product-details {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .supplier-card {
                background: #2a2d3a !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .supplier-name {
                color: #ffffff !important;
            }
            
            body.dark-mode .supplier-details,
            body.dark-mode .supplier-meta {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .timeline-item {
                border-color: #404450 !important;
            }
            
            body.dark-mode .timeline-item::before {
                background: #6366f1 !important;
            }
            
            body.dark-mode .timeline-date {
                color: #b8bdc6 !important;
            }
            
            body.dark-mode .timeline-title {
                color: #ffffff !important;
            }
            
            body.dark-mode .timeline-description {
                color: #f0f2f5 !important;
            }
            
            body.dark-mode .action-button {
                background: #2a2d3a !important;
                color: #f0f2f5 !important;
                border-color: #404450 !important;
            }
            
            body.dark-mode .action-button:hover {
                background: #32374a !important;
                border-color: #6366f1 !important;
            }
            
            /* Override any hardcoded black/gray colors */
            body.dark-mode [style*="color: #1e293b"],
            body.dark-mode [style*="color:#1e293b"],
            body.dark-mode [style*="color: #334155"],
            body.dark-mode [style*="color:#334155"],
            body.dark-mode [style*="color: #475569"],
            body.dark-mode [style*="color:#475569"],
            body.dark-mode [style*="color: #64748b"],
            body.dark-mode [style*="color:#64748b"],
            body.dark-mode [style*="color: #94a3b8"],
            body.dark-mode [style*="color:#94a3b8"],
            body.dark-mode [style*="color: black"],
            body.dark-mode [style*="color:black"],
            body.dark-mode [style*="color: #000"],
            body.dark-mode [style*="color:#000"],
            body.dark-mode [style*="color: #000000"],
            body.dark-mode [style*="color:#000000"] {
                color: #f0f2f5 !important;
            }
            
            /* Ensure text elements are visible */
            body.dark-mode td,
            body.dark-mode th {
                color: inherit;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Apply styles on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyDarkModeStyles);
    } else {
        applyDarkModeStyles();
    }
    
    // Listen for theme changes from dashboard
    window.addEventListener('storage', function(e) {
        if (e.key === 'dashboardTheme') {
            if (e.newValue === 'dark') {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
        }
    });
})();