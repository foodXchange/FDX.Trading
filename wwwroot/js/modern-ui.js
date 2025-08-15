// Modern UI System - JavaScript Components

// Toast Notification System
class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }

    show(message, type = 'info', title = null, duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>',
            error: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>',
            warning: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>',
            info: '<svg class="toast-icon" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>'
        };

        const defaultTitles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };

        toast.innerHTML = `
            ${icons[type] || icons.info}
            <div class="toast-content">
                ${title || defaultTitles[type] ? `<div class="toast-title">${title || defaultTitles[type]}</div>` : ''}
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>
        `;

        this.container.appendChild(toast);

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }

        return toast;
    }

    success(message, title = null) {
        return this.show(message, 'success', title);
    }

    error(message, title = null) {
        return this.show(message, 'error', title);
    }

    warning(message, title = null) {
        return this.show(message, 'warning', title);
    }

    info(message, title = null) {
        return this.show(message, 'info', title);
    }
}

// Initialize toast manager globally
window.toast = new ToastManager();

// Dark Mode Manager
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        // Apply saved theme
        document.documentElement.setAttribute('data-theme', this.theme);
        
        // Don't create floating button anymore - it's in the navigation now
        // Just update the nav theme icon if it exists
        const navIcon = document.getElementById('navThemeIcon');
        if (navIcon) {
            navIcon.textContent = this.theme === 'dark' ? '☀️' : '🌙';
        }
    }

    toggle() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);
        
        const button = document.querySelector('.theme-toggle');
        if (button) {
            button.innerHTML = this.theme === 'dark' ? this.getSunIcon() : this.getMoonIcon();
        }

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('themechange', { detail: this.theme }));
    }

    getMoonIcon() {
        return '<svg width="24" height="24" fill="currentColor" viewBox="0 0 20 20"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path></svg>';
    }

    getSunIcon() {
        return '<svg width="24" height="24" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"></path></svg>';
    }
}

// Initialize theme manager
window.themeManager = new ThemeManager();

// Loading Spinner Manager
class LoadingManager {
    show(message = 'Loading...') {
        if (!document.querySelector('.spinner-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'spinner-overlay';
            overlay.innerHTML = `
                <div style="text-align: center;">
                    <div class="spinner"></div>
                    <div style="color: white; margin-top: 1rem;">${message}</div>
                </div>
            `;
            document.body.appendChild(overlay);
        }
    }

    hide() {
        const overlay = document.querySelector('.spinner-overlay');
        if (overlay) {
            overlay.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => overlay.remove(), 300);
        }
    }
}

window.loading = new LoadingManager();

// Auto-save Manager
class AutoSaveManager {
    constructor(formSelector, saveFunction, delay = 2000) {
        this.form = document.querySelector(formSelector);
        this.saveFunction = saveFunction;
        this.delay = delay;
        this.timeoutId = null;
        this.lastSavedData = null;
        
        if (this.form) {
            this.init();
        }
    }

    init() {
        // Listen to all form inputs
        this.form.addEventListener('input', (e) => this.handleInput(e));
        this.form.addEventListener('change', (e) => this.handleInput(e));
        
        // Store initial state
        this.lastSavedData = this.getFormData();
    }

    handleInput(e) {
        // Clear existing timeout
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }

        // Show saving indicator
        this.showSavingIndicator();

        // Set new timeout
        this.timeoutId = setTimeout(() => {
            this.save();
        }, this.delay);
    }

    getFormData() {
        const formData = new FormData(this.form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        return JSON.stringify(data);
    }

    async save() {
        const currentData = this.getFormData();
        
        // Only save if data has changed
        if (currentData === this.lastSavedData) {
            this.hideSavingIndicator();
            return;
        }

        try {
            await this.saveFunction(JSON.parse(currentData));
            this.lastSavedData = currentData;
            this.showSavedIndicator();
            
            // Show success toast
            window.toast.success('Changes saved automatically');
        } catch (error) {
            this.showErrorIndicator();
            window.toast.error('Failed to save changes');
        }
    }

    showSavingIndicator() {
        this.updateIndicator('Saving...', 'text-warning');
    }

    showSavedIndicator() {
        this.updateIndicator('Saved', 'text-success');
        setTimeout(() => this.hideSavingIndicator(), 2000);
    }

    showErrorIndicator() {
        this.updateIndicator('Error saving', 'text-danger');
    }

    hideSavingIndicator() {
        const indicator = document.querySelector('.autosave-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    updateIndicator(text, className) {
        let indicator = document.querySelector('.autosave-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'autosave-indicator';
            indicator.style.cssText = 'position: fixed; top: 70px; right: 20px; padding: 0.5rem 1rem; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); z-index: 1000;';
            document.body.appendChild(indicator);
        }

        indicator.className = `autosave-indicator ${className}`;
        indicator.textContent = text;
    }
}

// Keyboard Shortcuts Manager
class KeyboardShortcuts {
    constructor() {
        this.shortcuts = new Map();
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Register default shortcuts
        this.register('ctrl+s', (e) => {
            e.preventDefault();
            this.saveCurrentForm();
        }, 'Save current form');

        this.register('ctrl+/', (e) => {
            e.preventDefault();
            this.showShortcutsList();
        }, 'Show keyboard shortcuts');

        this.register('ctrl+k', (e) => {
            e.preventDefault();
            this.openQuickSearch();
        }, 'Quick search');

        this.register('alt+n', (e) => {
            e.preventDefault();
            this.createNew();
        }, 'Create new item');

        this.register('esc', (e) => {
            this.closeModals();
        }, 'Close modals');
    }

    register(shortcut, handler, description) {
        this.shortcuts.set(shortcut.toLowerCase(), { handler, description });
    }

    handleKeyDown(e) {
        const key = this.getKeyString(e);
        const shortcut = this.shortcuts.get(key);
        
        if (shortcut) {
            shortcut.handler(e);
        }
    }

    getKeyString(e) {
        const keys = [];
        
        if (e.ctrlKey) keys.push('ctrl');
        if (e.altKey) keys.push('alt');
        if (e.shiftKey) keys.push('shift');
        if (e.metaKey) keys.push('meta');
        
        let key = e.key.toLowerCase();
        if (key === ' ') key = 'space';
        if (key === 'escape') key = 'esc';
        
        keys.push(key);
        
        return keys.join('+');
    }

    saveCurrentForm() {
        const activeForm = document.querySelector('form:not([hidden])');
        if (activeForm) {
            const submitBtn = activeForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.click();
                window.toast.success('Form saved');
            }
        }
    }

    showShortcutsList() {
        let modal = document.getElementById('shortcuts-modal');
        
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'shortcuts-modal';
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Keyboard Shortcuts</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Shortcut</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${Array.from(this.shortcuts.entries()).map(([key, { description }]) => `
                                        <tr>
                                            <td><kbd>${key.split('+').join('</kbd> + <kbd>')}</kbd></td>
                                            <td>${description}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    openQuickSearch() {
        // Quick search implementation
        const searchInput = document.querySelector('.search-input, input[type="search"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    createNew() {
        // Find and click the primary "New" or "Create" button
        const createBtn = document.querySelector('.btn-primary[href*="create"], .btn-primary[onclick*="create"], button:contains("New")');
        if (createBtn) {
            createBtn.click();
        }
    }

    closeModals() {
        // Close all open modals
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    }
}

// Initialize keyboard shortcuts
window.shortcuts = new KeyboardShortcuts();

// Form Validation with Real-time Feedback
class FormValidator {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        if (this.form) {
            this.init();
        }
    }

    init() {
        const inputs = this.form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            // Add modern styling
            input.classList.add('form-modern-input');
            
            // Real-time validation
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.validateField(input));
        });

        // Prevent form submission if invalid
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                window.toast.error('Please fix the errors before submitting');
            }
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');
        const type = field.type;
        const pattern = field.getAttribute('pattern');
        
        let isValid = true;
        let message = '';

        // Required field validation
        if (isRequired && !value) {
            isValid = false;
            message = 'This field is required';
        }

        // Email validation
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                message = 'Please enter a valid email address';
            }
        }

        // Pattern validation
        if (pattern && value) {
            const regex = new RegExp(pattern);
            if (!regex.test(value)) {
                isValid = false;
                message = field.getAttribute('data-pattern-message') || 'Invalid format';
            }
        }

        // Number validation
        if (type === 'number') {
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');
            
            if (min && parseFloat(value) < parseFloat(min)) {
                isValid = false;
                message = `Value must be at least ${min}`;
            }
            
            if (max && parseFloat(value) > parseFloat(max)) {
                isValid = false;
                message = `Value must be at most ${max}`;
            }
        }

        // Update field styling
        field.classList.remove('is-valid', 'is-invalid');
        
        if (value) {
            field.classList.add(isValid ? 'is-valid' : 'is-invalid');
        }

        // Update feedback message
        this.updateFeedback(field, isValid, message);

        return isValid;
    }

    updateFeedback(field, isValid, message) {
        // Remove existing feedback
        const existingFeedback = field.parentElement.querySelector('.form-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Add new feedback if invalid
        if (!isValid && message) {
            const feedback = document.createElement('div');
            feedback.className = 'form-feedback form-feedback-error';
            feedback.innerHTML = `
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                </svg>
                ${message}
            `;
            field.parentElement.appendChild(feedback);
        }
    }

    validateForm() {
        const inputs = this.form.querySelectorAll('input, textarea, select');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }
}

// Enhanced API calls with loading states
class APIHelper {
    static async request(url, options = {}) {
        // Show loading
        window.loading.show();

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Request failed');
            }

            window.loading.hide();
            return data;

        } catch (error) {
            window.loading.hide();
            window.toast.error(error.message);
            throw error;
        }
    }

    static get(url) {
        return this.request(url, { method: 'GET' });
    }

    static post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    static delete(url) {
        return this.request(url, { method: 'DELETE' });
    }
}

window.API = APIHelper;

// Initialize all components when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Add modern styling to existing elements
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('modern-card', 'hover-lift');
    });

    document.querySelectorAll('.btn').forEach(btn => {
        if (btn.classList.contains('btn-primary')) {
            btn.classList.add('btn-modern', 'btn-modern-primary');
        } else if (btn.classList.contains('btn-secondary')) {
            btn.classList.add('btn-modern', 'btn-modern-secondary');
        } else if (btn.classList.contains('btn-success')) {
            btn.classList.add('btn-modern', 'btn-modern-success');
        }
    });

    document.querySelectorAll('table').forEach(table => {
        table.classList.add('table-modern');
    });

    // Add page transition
    document.body.classList.add('page-transition');

    // Initialize form validators
    document.querySelectorAll('form').forEach(form => {
        if (form.id) {
            new FormValidator(`#${form.id}`);
        }
    });
});

// Export for use in other scripts
window.ModernUI = {
    ToastManager,
    ThemeManager,
    LoadingManager,
    AutoSaveManager,
    KeyboardShortcuts,
    FormValidator,
    APIHelper
};