/**
 * Intelligent Help System Frontend
 * 
 * Provides:
 * - Interactive tooltips with AI-powered content
 * - Contextual help suggestions
 * - Help center integration
 * - User session tracking
 * - Feedback collection
 */

class IntelligentHelpSystem {
    constructor() {
        this.currentSessionId = null;
        this.helpSuggestions = [];
        this.activeTooltips = new Map();
        this.helpCenterOpen = false;
        this.userSkillLevel = 'beginner';
        this.helpPreferences = {
            showTooltips: true,
            showContextualHelp: true,
            autoSuggest: true
        };
        
        this.init();
    }
    
    async init() {
        // Load user preferences
        this.loadPreferences();
        
        // Start help session
        await this.startHelpSession();
        
        // Initialize tooltips
        this.initializeTooltips();
        
        // Initialize contextual help
        this.initializeContextualHelp();
        
        // Initialize help center integration
        this.initializeHelpCenter();
        
        // Track page changes
        this.trackPageChanges();
        
        console.log('✅ Intelligent Help System initialized');
    }
    
    async startHelpSession() {
        try {
            const response = await fetch('/api/help/session/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    page_url: window.location.pathname,
                    user_id: this.getCurrentUserId()
                })
            });
            
            const data = await response.json();
            this.currentSessionId = data.session_id;
            
            // End session when page unloads
            window.addEventListener('beforeunload', () => {
                this.endHelpSession();
            });
            
        } catch (error) {
            console.error('Failed to start help session:', error);
        }
    }
    
    async endHelpSession() {
        if (this.currentSessionId) {
            try {
                await fetch(`/api/help/session/${this.currentSessionId}/end`, {
                    method: 'POST'
                });
            } catch (error) {
                console.error('Failed to end help session:', error);
            }
        }
    }
    
    initializeTooltips() {
        if (!this.helpPreferences.showTooltips) return;
        
        // Find elements with help tooltips
        const tooltipElements = document.querySelectorAll('[data-help-tooltip]');
        
        tooltipElements.forEach(element => {
            this.setupTooltip(element);
        });
        
        // Watch for dynamically added elements
        this.observeTooltipElements();
    }
    
    setupTooltip(element) {
        const tooltipId = element.getAttribute('data-help-tooltip');
        const pageUrl = window.location.pathname;
        
        // Create tooltip trigger
        element.addEventListener('mouseenter', async (e) => {
            await this.showTooltip(element, tooltipId, pageUrl);
        });
        
        element.addEventListener('mouseleave', (e) => {
            this.hideTooltip(element);
        });
        
        // Add help icon if not present
        if (!element.querySelector('.help-icon')) {
            const helpIcon = document.createElement('i');
            helpIcon.className = 'fas fa-question-circle help-icon text-muted ms-1';
            helpIcon.style.fontSize = '0.8em';
            helpIcon.style.cursor = 'help';
            element.appendChild(helpIcon);
        }
    }
    
    async showTooltip(element, tooltipId, pageUrl) {
        try {
            const response = await fetch(`/api/help/tooltip/${tooltipId}?page_url=${encodeURIComponent(pageUrl)}`);
            
            if (response.ok) {
                const tooltipData = await response.json();
                this.displayTooltip(element, tooltipData);
                
                // Record access
                if (this.currentSessionId) {
                    await fetch(`/api/help/session/${this.currentSessionId}/access`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ content_id: tooltipData.id })
                    });
                }
            }
        } catch (error) {
            console.error('Failed to load tooltip:', error);
        }
    }
    
    displayTooltip(element, tooltipData) {
        // Remove existing tooltip
        this.hideTooltip(element);
        
        // Create tooltip element
        const tooltip = document.createElement('div');
        tooltip.className = 'intelligent-tooltip';
        tooltip.innerHTML = `
            <div class="tooltip-header">
                <h6 class="mb-1">${tooltipData.title}</h6>
                <span class="badge bg-${this.getPriorityColor(tooltipData.priority)}">${tooltipData.priority}</span>
            </div>
            <div class="tooltip-content">
                <p class="mb-2">${tooltipData.content}</p>
                <div class="tooltip-footer">
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-success btn-sm" onclick="helpSystem.recordFeedback('${tooltipData.id}', true)">
                            <i class="fas fa-thumbs-up"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="helpSystem.recordFeedback('${tooltipData.id}', false)">
                            <i class="fas fa-thumbs-down"></i>
                        </button>
                    </div>
                    <small class="text-muted">${tooltipData.usage_count} views</small>
                </div>
            </div>
        `;
        
        // Position tooltip
        const rect = element.getBoundingClientRect();
        tooltip.style.position = 'absolute';
        tooltip.style.top = `${rect.bottom + 5}px`;
        tooltip.style.left = `${rect.left}px`;
        tooltip.style.zIndex = '9999';
        
        // Add to page
        document.body.appendChild(tooltip);
        this.activeTooltips.set(element, tooltip);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            this.hideTooltip(element);
        }, 10000);
    }
    
    hideTooltip(element) {
        const tooltip = this.activeTooltips.get(element);
        if (tooltip) {
            tooltip.remove();
            this.activeTooltips.delete(element);
        }
    }
    
    observeTooltipElements() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const tooltipElements = node.querySelectorAll('[data-help-tooltip]');
                        tooltipElements.forEach(element => {
                            this.setupTooltip(element);
                        });
                        
                        if (node.hasAttribute && node.hasAttribute('data-help-tooltip')) {
                            this.setupTooltip(node);
                        }
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    initializeContextualHelp() {
        if (!this.helpPreferences.showContextualHelp) return;
        
        // Get contextual help for current page
        this.loadContextualHelp();
        
        // Show contextual help button
        this.showContextualHelpButton();
    }
    
    async loadContextualHelp() {
        try {
            const response = await fetch('/api/help/contextual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    page_url: window.location.pathname,
                    user_id: this.getCurrentUserId()
                })
            });
            
            if (response.ok) {
                this.helpSuggestions = await response.json();
                this.displayContextualHelp();
            }
        } catch (error) {
            console.error('Failed to load contextual help:', error);
        }
    }
    
    displayContextualHelp() {
        if (this.helpSuggestions.length === 0) return;
        
        // Create contextual help panel
        const panel = document.createElement('div');
        panel.id = 'contextualHelpPanel';
        panel.className = 'contextual-help-panel';
        panel.innerHTML = `
            <div class="panel-header">
                <h6 class="mb-0">
                    <i class="fas fa-lightbulb text-warning me-2"></i>
                    Helpful Tips
                </h6>
                <button class="btn-close" onclick="helpSystem.hideContextualHelp()"></button>
            </div>
            <div class="panel-content">
                ${this.helpSuggestions.map(suggestion => `
                    <div class="help-suggestion" onclick="helpSystem.showHelpContent('${suggestion.content_id}')">
                        <div class="suggestion-header">
                            <h6 class="mb-1">${suggestion.title}</h6>
                            <span class="badge bg-${this.getPriorityColor(suggestion.priority)}">${suggestion.priority}</span>
                        </div>
                        <p class="mb-1 small">${suggestion.reason}</p>
                        <small class="text-muted">Relevance: ${Math.round(suggestion.relevance_score * 100)}%</small>
                    </div>
                `).join('')}
            </div>
        `;
        
        // Add to page
        document.body.appendChild(panel);
        
        // Auto-hide after 30 seconds
        setTimeout(() => {
            this.hideContextualHelp();
        }, 30000);
    }
    
    hideContextualHelp() {
        const panel = document.getElementById('contextualHelpPanel');
        if (panel) {
            panel.remove();
        }
    }
    
    showContextualHelpButton() {
        // Create floating help button
        const button = document.createElement('div');
        button.id = 'contextualHelpButton';
        button.className = 'contextual-help-button';
        button.innerHTML = `
            <i class="fas fa-question-circle"></i>
            <span class="help-count">${this.helpSuggestions.length}</span>
        `;
        button.onclick = () => this.toggleContextualHelp();
        
        document.body.appendChild(button);
    }
    
    toggleContextualHelp() {
        const panel = document.getElementById('contextualHelpPanel');
        if (panel) {
            this.hideContextualHelp();
        } else {
            this.displayContextualHelp();
        }
    }
    
    initializeHelpCenter() {
        // Add help center button to navbar
        this.addHelpCenterButton();
        
        // Initialize help center modal
        this.createHelpCenterModal();
    }
    
    addHelpCenterButton() {
        // Find navbar and add help center button
        const navbar = document.querySelector('.navbar-nav');
        if (navbar) {
            const helpButton = document.createElement('li');
            helpButton.className = 'nav-item';
            helpButton.innerHTML = `
                <a class="nav-link" href="#" onclick="helpSystem.openHelpCenter()">
                    <i class="fas fa-question-circle me-1"></i>
                    Help
                </a>
            `;
            navbar.appendChild(helpButton);
        }
    }
    
    createHelpCenterModal() {
        const modal = document.createElement('div');
        modal.id = 'helpCenterModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-question-circle text-primary me-2"></i>
                            Help Center
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-3">
                                <div class="list-group" id="helpCategories">
                                    <!-- Categories will be loaded here -->
                                </div>
                            </div>
                            <div class="col-md-9">
                                <div class="mb-3">
                                    <div class="input-group">
                                        <input type="text" class="form-control" id="helpSearchInput" 
                                               placeholder="Search help content...">
                                        <button class="btn btn-primary" type="button" onclick="helpSystem.searchHelp()">
                                            <i class="fas fa-search"></i>
                                        </button>
                                    </div>
                                </div>
                                <div id="helpContent">
                                    <div class="text-center text-muted">
                                        <i class="fas fa-question-circle fa-3x mb-3"></i>
                                        <h5>How can we help you?</h5>
                                        <p>Search for help content or browse categories to get started.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    async openHelpCenter() {
        const modal = new bootstrap.Modal(document.getElementById('helpCenterModal'));
        modal.show();
        
        // Load categories
        await this.loadHelpCategories();
        
        // Load getting started content
        await this.loadHelpContent('getting_started');
    }
    
    async loadHelpCategories() {
        try {
            const response = await fetch('/api/help/categories');
            const categories = await response.json();
            
            const categoryList = document.getElementById('helpCategories');
            categoryList.innerHTML = categories.map(category => `
                <a href="#" class="list-group-item list-group-item-action" 
                   onclick="helpSystem.loadHelpContent('${category.value}')">
                    ${category.label}
                </a>
            `).join('');
        } catch (error) {
            console.error('Failed to load help categories:', error);
        }
    }
    
    async loadHelpContent(category) {
        try {
            const response = await fetch(`/api/help/content/category/${category}`);
            const content = await response.json();
            this.displayHelpContent(content);
        } catch (error) {
            console.error('Failed to load help content:', error);
        }
    }
    
    async searchHelp() {
        const query = document.getElementById('helpSearchInput').value;
        if (!query.trim()) return;
        
        try {
            const response = await fetch('/api/help/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            
            const content = await response.json();
            this.displayHelpContent(content);
            
            // Record search
            if (this.currentSessionId) {
                await fetch(`/api/help/session/${this.currentSessionId}/search`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
            }
        } catch (error) {
            console.error('Failed to search help content:', error);
        }
    }
    
    displayHelpContent(contentList) {
        const contentArea = document.getElementById('helpContent');
        
        if (contentList.length === 0) {
            contentArea.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-search fa-3x mb-3"></i>
                    <h5>No help content found</h5>
                    <p>Try a different search term or browse categories.</p>
                </div>
            `;
            return;
        }
        
        contentArea.innerHTML = contentList.map(content => `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">${content.title}</h6>
                    <span class="badge bg-${this.getPriorityColor(content.priority)}">${content.priority}</span>
                </div>
                <div class="card-body">
                    <p>${content.content}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="small text-muted">
                            <i class="fas fa-tag me-1"></i>${content.category.replace('_', ' ')}
                            <span class="ms-3"><i class="fas fa-eye me-1"></i>${content.usage_count}</span>
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-success" onclick="helpSystem.recordFeedback('${content.id}', true)">
                                <i class="fas fa-thumbs-up"></i> Helpful
                            </button>
                            <button class="btn btn-outline-danger" onclick="helpSystem.recordFeedback('${content.id}', false)">
                                <i class="fas fa-thumbs-down"></i> Not Helpful
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    async showHelpContent(contentId) {
        try {
            const response = await fetch(`/api/help/content/${contentId}`);
            const content = await response.json();
            
            // Show in modal
            const modal = new bootstrap.Modal(document.getElementById('helpContentModal'));
            const modalBody = document.querySelector('#helpContentModal .modal-body');
            modalBody.innerHTML = `
                <h5>${content.title}</h5>
                <p>${content.content}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <div class="small text-muted">
                        <i class="fas fa-tag me-1"></i>${content.category.replace('_', ' ')}
                        <span class="ms-3"><i class="fas fa-eye me-1"></i>${content.usage_count}</span>
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-success" onclick="helpSystem.recordFeedback('${content.id}', true)">
                            <i class="fas fa-thumbs-up"></i> Helpful
                        </button>
                        <button class="btn btn-outline-danger" onclick="helpSystem.recordFeedback('${content.id}', false)">
                            <i class="fas fa-thumbs-down"></i> Not Helpful
                        </button>
                    </div>
                </div>
            `;
            modal.show();
            
            // Record access
            if (this.currentSessionId) {
                await fetch(`/api/help/session/${this.currentSessionId}/access`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content_id: contentId })
                });
            }
        } catch (error) {
            console.error('Failed to load help content:', error);
        }
    }
    
    async recordFeedback(contentId, helpful) {
        try {
            await fetch('/api/help/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content_id: contentId,
                    helpful: helpful,
                    user_id: this.getCurrentUserId()
                })
            });
            
            // Show feedback confirmation
            const button = event.target.closest('button');
            const originalText = button.innerHTML;
            button.innerHTML = helpful ? '<i class="fas fa-check"></i> Thank you!' : '<i class="fas fa-times"></i> Noted';
            button.disabled = true;
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 2000);
        } catch (error) {
            console.error('Failed to record feedback:', error);
        }
    }
    
    trackPageChanges() {
        // Track when user navigates to different pages
        let currentUrl = window.location.pathname;
        
        setInterval(() => {
            if (window.location.pathname !== currentUrl) {
                currentUrl = window.location.pathname;
                this.onPageChange(currentUrl);
            }
        }, 1000);
    }
    
    async onPageChange(newUrl) {
        // End current session
        await this.endHelpSession();
        
        // Start new session
        await this.startHelpSession();
        
        // Load contextual help for new page
        this.loadContextualHelp();
    }
    
    loadPreferences() {
        const saved = localStorage.getItem('helpPreferences');
        if (saved) {
            this.helpPreferences = { ...this.helpPreferences, ...JSON.parse(saved) };
        }
        
        const skillLevel = localStorage.getItem('userSkillLevel');
        if (skillLevel) {
            this.userSkillLevel = skillLevel;
        }
    }
    
    savePreferences() {
        localStorage.setItem('helpPreferences', JSON.stringify(this.helpPreferences));
        localStorage.setItem('userSkillLevel', this.userSkillLevel);
    }
    
    getCurrentUserId() {
        // Placeholder - in real implementation, get from authentication
        return localStorage.getItem('userId') || null;
    }
    
    getPriorityColor(priority) {
        switch (priority) {
            case 'critical': return 'danger';
            case 'high': return 'warning';
            case 'medium': return 'info';
            case 'low': return 'secondary';
            default: return 'secondary';
        }
    }
    
    // Public API methods
    setUserSkillLevel(level) {
        this.userSkillLevel = level;
        this.savePreferences();
        
        // Update on server
        fetch('/api/help/user/skill-level', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: this.getCurrentUserId(),
                skill_level: level
            })
        });
    }
    
    toggleTooltips() {
        this.helpPreferences.showTooltips = !this.helpPreferences.showTooltips;
        this.savePreferences();
        
        if (this.helpPreferences.showTooltips) {
            this.initializeTooltips();
        } else {
            // Remove all tooltips
            this.activeTooltips.forEach((tooltip, element) => {
                this.hideTooltip(element);
            });
        }
    }
    
    toggleContextualHelp() {
        this.helpPreferences.showContextualHelp = !this.helpPreferences.showContextualHelp;
        this.savePreferences();
        
        if (this.helpPreferences.showContextualHelp) {
            this.initializeContextualHelp();
        } else {
            this.hideContextualHelp();
            const button = document.getElementById('contextualHelpButton');
            if (button) button.remove();
        }
    }
    
    async getAnalytics() {
        try {
            const response = await fetch('/api/help/analytics');
            return await response.json();
        } catch (error) {
            console.error('Failed to get help analytics:', error);
            return null;
        }
    }
}

// Initialize help system when DOM is ready
let helpSystem;
document.addEventListener('DOMContentLoaded', () => {
    helpSystem = new IntelligentHelpSystem();
});

// Global functions for easy access
window.openHelpCenter = () => helpSystem.openHelpCenter();
window.recordHelpFeedback = (contentId, helpful) => helpSystem.recordFeedback(contentId, helpful);
window.setUserSkillLevel = (level) => helpSystem.setUserSkillLevel(level); 