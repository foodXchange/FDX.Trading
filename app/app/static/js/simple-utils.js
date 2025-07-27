/**
 * Simple JavaScript Utilities for FoodXchange
 * Philosophy: Defensive programming, graceful degradation, minimal dependencies
 */

// Namespace to avoid global conflicts
const FX = {
    // Safe DOM ready function
    ready: function(fn) {
        if (document.readyState !== 'loading') {
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    },

    // Safe element selector with error handling
    $: function(selector, parent = document) {
        try {
            return parent.querySelector(selector);
        } catch (e) {
            console.error('Invalid selector:', selector);
            return null;
        }
    },

    // Safe element selector for multiple elements
    $$: function(selector, parent = document) {
        try {
            return Array.from(parent.querySelectorAll(selector));
        } catch (e) {
            console.error('Invalid selector:', selector);
            return [];
        }
    },

    // Safe event listener with error boundary
    on: function(element, event, handler, options = false) {
        if (!element || !event || !handler) return;
        
        try {
            // Wrap handler in error boundary
            const safeHandler = function(e) {
                try {
                    handler.call(this, e);
                } catch (error) {
                    console.error('Event handler error:', error);
                }
            };
            
            element.addEventListener(event, safeHandler, options);
            
            // Return function to remove listener
            return function() {
                element.removeEventListener(event, safeHandler, options);
            };
        } catch (e) {
            console.error('Failed to add event listener:', e);
        }
    },

    // Debounce function for performance
    debounce: function(func, wait = 250) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Simple AJAX with error handling
    ajax: function(options) {
        const defaults = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 30000, // 30 seconds
        };

        const settings = Object.assign({}, defaults, options);

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.open(settings.method, settings.url);
            
            // Set headers
            Object.keys(settings.headers).forEach(key => {
                xhr.setRequestHeader(key, settings.headers[key]);
            });
            
            // Set timeout
            xhr.timeout = settings.timeout;
            
            xhr.onload = function() {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (e) {
                        resolve(xhr.responseText);
                    }
                } else {
                    reject({
                        status: xhr.status,
                        statusText: xhr.statusText,
                        response: xhr.responseText
                    });
                }
            };
            
            xhr.onerror = () => reject({ status: 0, statusText: 'Network Error' });
            xhr.ontimeout = () => reject({ status: 0, statusText: 'Request Timeout' });
            
            xhr.send(settings.data ? JSON.stringify(settings.data) : null);
        });
    },

    // Simple form validation
    validateForm: function(formElement) {
        if (!formElement) return false;
        
        const inputs = FX.$$('input[required], select[required], textarea[required]', formElement);
        let isValid = true;
        
        inputs.forEach(input => {
            // Remove previous error state
            input.classList.remove('error');
            
            // Check if empty
            if (!input.value.trim()) {
                input.classList.add('error');
                isValid = false;
            }
            
            // Email validation
            if (input.type === 'email' && input.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(input.value)) {
                    input.classList.add('error');
                    isValid = false;
                }
            }
        });
        
        return isValid;
    },

    // Simple toast notification
    toast: function(message, type = 'info', duration = 3000) {
        // Remove existing toasts
        const existingToast = FX.$('.toast-notification');
        if (existingToast) {
            existingToast.remove();
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.textContent = message;
        
        // Simple styles
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 16px 24px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        // Fade in
        setTimeout(() => toast.style.opacity = '1', 10);
        
        // Remove after duration
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    // Simple loading overlay
    loading: {
        show: function(message = 'Loading...') {
            const overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-content">
                    <div class="spinner"></div>
                    <p>${message}</p>
                </div>
            `;
            document.body.appendChild(overlay);
        },
        
        hide: function() {
            const overlay = FX.$('#loading-overlay');
            if (overlay) {
                overlay.remove();
            }
        }
    },

    // Local storage wrapper with error handling
    storage: {
        get: function(key) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : null;
            } catch (e) {
                console.error('Storage get error:', e);
                return null;
            }
        },
        
        set: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (e) {
                console.error('Storage set error:', e);
                return false;
            }
        },
        
        remove: function(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (e) {
                console.error('Storage remove error:', e);
                return false;
            }
        }
    },

    // Simple modal
    modal: {
        show: function(content, options = {}) {
            const modalHtml = `
                <div class="modal-backdrop" id="modal-backdrop">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>${options.title || 'Modal'}</h3>
                            <button class="modal-close" onclick="FX.modal.hide()">&times;</button>
                        </div>
                        <div class="modal-body">
                            ${content}
                        </div>
                        ${options.footer ? `<div class="modal-footer">${options.footer}</div>` : ''}
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // Add styles if not exists
            if (!FX.$('#modal-styles')) {
                const styles = `
                    <style id="modal-styles">
                        .modal-backdrop {
                            position: fixed;
                            top: 0;
                            left: 0;
                            right: 0;
                            bottom: 0;
                            background: rgba(0, 0, 0, 0.5);
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            z-index: 1050;
                        }
                        .modal-content {
                            background: white;
                            border-radius: 8px;
                            max-width: 500px;
                            width: 90%;
                            max-height: 90vh;
                            overflow: auto;
                        }
                        .modal-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            padding: 20px;
                            border-bottom: 1px solid #e5e7eb;
                        }
                        .modal-close {
                            background: none;
                            border: none;
                            font-size: 24px;
                            cursor: pointer;
                        }
                        .modal-body {
                            padding: 20px;
                        }
                        .modal-footer {
                            padding: 20px;
                            border-top: 1px solid #e5e7eb;
                        }
                    </style>
                `;
                document.head.insertAdjacentHTML('beforeend', styles);
            }
        },
        
        hide: function() {
            const modal = FX.$('#modal-backdrop');
            if (modal) {
                modal.remove();
            }
        }
    },

    // Format currency safely
    formatCurrency: function(amount, currency = 'USD') {
        try {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: currency
            }).format(amount);
        } catch (e) {
            return `$${parseFloat(amount).toFixed(2)}`;
        }
    },

    // Format date safely
    formatDate: function(date, format = 'short') {
        try {
            const d = new Date(date);
            if (isNaN(d.getTime())) {
                return 'Invalid Date';
            }
            
            if (format === 'short') {
                return d.toLocaleDateString();
            } else if (format === 'long') {
                return d.toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
            } else {
                return d.toLocaleString();
            }
        } catch (e) {
            return 'Invalid Date';
        }
    },

    // Simple table sort
    sortTable: function(tableId, columnIndex) {
        const table = FX.$(`#${tableId}`);
        if (!table) return;
        
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Toggle sort direction
        const isAscending = table.dataset.sortDir !== 'asc';
        table.dataset.sortDir = isAscending ? 'asc' : 'desc';
        
        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            // Try to parse as number
            const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
            const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? aNum - bNum : bNum - aNum;
            }
            
            // Sort as string
            return isAscending ? 
                aValue.localeCompare(bValue) : 
                bValue.localeCompare(aValue);
        });
        
        // Re-append sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }
};

// Initialize common functionality when DOM is ready
FX.ready(function() {
    // Mobile menu toggle
    const menuToggle = FX.$('.navbar-toggle');
    if (menuToggle) {
        FX.on(menuToggle, 'click', function() {
            const menu = FX.$('.navbar-menu');
            if (menu) {
                menu.classList.toggle('active');
            }
        });
    }
    
    // Form submission with validation
    FX.$$('form[data-validate]').forEach(form => {
        FX.on(form, 'submit', function(e) {
            if (!FX.validateForm(form)) {
                e.preventDefault();
                FX.toast('Please fill in all required fields', 'error');
            }
        });
    });
    
    // Sortable tables
    FX.$$('th[data-sortable]').forEach(th => {
        th.style.cursor = 'pointer';
        FX.on(th, 'click', function() {
            const table = th.closest('table');
            const columnIndex = Array.from(th.parentNode.children).indexOf(th);
            FX.sortTable(table.id, columnIndex);
        });
    });
    
    // Auto-hide alerts after 5 seconds
    FX.$$('.alert[data-auto-dismiss]').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Make FX available globally
window.FX = FX;