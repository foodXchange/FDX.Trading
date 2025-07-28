/**
 * FoodXchange JavaScript Component Library
 * Lightweight, reusable UI components
 */

class FXComponents {
  constructor() {
    this.initializeComponents();
  }

  initializeComponents() {
    // Auto-initialize components on DOM ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.scanAndInit());
    } else {
      this.scanAndInit();
    }
  }

  scanAndInit() {
    // Initialize all components
    this.initDropdowns();
    this.initModals();
    this.initTooltips();
    this.initTabs();
    this.initNotifications();
    this.initQuickActions();
  }

  // === DROPDOWN COMPONENT === 
  initDropdowns() {
    document.querySelectorAll('[data-dropdown]').forEach(trigger => {
      const targetId = trigger.getAttribute('data-dropdown');
      const dropdown = document.getElementById(targetId);
      
      if (!dropdown) return;

      trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleDropdown(dropdown);
      });

      // Close on outside click
      document.addEventListener('click', () => {
        this.closeDropdown(dropdown);
      });

      dropdown.addEventListener('click', (e) => e.stopPropagation());
    });
  }

  toggleDropdown(dropdown) {
    const isOpen = dropdown.classList.contains('show');
    this.closeAllDropdowns();
    if (!isOpen) {
      dropdown.classList.add('show');
      dropdown.style.display = 'block';
    }
  }

  closeDropdown(dropdown) {
    dropdown.classList.remove('show');
    dropdown.style.display = 'none';
  }

  closeAllDropdowns() {
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
      this.closeDropdown(menu);
    });
  }

  // === MODAL COMPONENT ===
  initModals() {
    // Modal triggers
    document.querySelectorAll('[data-modal]').forEach(trigger => {
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = trigger.getAttribute('data-modal');
        this.openModal(targetId);
      });
    });

    // Modal close buttons
    document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
      closeBtn.addEventListener('click', () => {
        this.closeModal();
      });
    });

    // Close on backdrop click
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
      backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) {
          this.closeModal();
        }
      });
    });

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeModal();
      }
    });
  }

  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    // Focus first focusable element
    const focusable = modal.querySelector('input, button, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusable) focusable.focus();

    // Trap focus within modal
    this.trapFocus(modal);
  }

  closeModal() {
    document.querySelectorAll('.modal').forEach(modal => {
      modal.style.display = 'none';
    });
    document.body.style.overflow = '';
  }

  trapFocus(container) {
    const focusableElements = container.querySelectorAll(
      'input, button, select, textarea, [href], [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    container.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    });
  }

  // === TOOLTIP COMPONENT ===
  initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
      const text = element.getAttribute('data-tooltip');
      const position = element.getAttribute('data-tooltip-position') || 'top';

      element.addEventListener('mouseenter', () => {
        this.showTooltip(element, text, position);
      });

      element.addEventListener('mouseleave', () => {
        this.hideTooltip();
      });

      element.addEventListener('focus', () => {
        this.showTooltip(element, text, position);
      });

      element.addEventListener('blur', () => {
        this.hideTooltip();
      });
    });
  }

  showTooltip(element, text, position) {
    this.hideTooltip(); // Hide any existing tooltip

    const tooltip = document.createElement('div');
    tooltip.className = `tooltip tooltip-${position}`;
    tooltip.textContent = text;
    tooltip.id = 'fx-tooltip';

    document.body.appendChild(tooltip);

    // Position tooltip
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();

    let left, top;

    switch (position) {
      case 'top':
        left = rect.left + (rect.width - tooltipRect.width) / 2;
        top = rect.top - tooltipRect.height - 8;
        break;
      case 'bottom':
        left = rect.left + (rect.width - tooltipRect.width) / 2;
        top = rect.bottom + 8;
        break;
      case 'left':
        left = rect.left - tooltipRect.width - 8;
        top = rect.top + (rect.height - tooltipRect.height) / 2;
        break;
      case 'right':
        left = rect.right + 8;
        top = rect.top + (rect.height - tooltipRect.height) / 2;
        break;
    }

    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
    tooltip.style.opacity = '1';
  }

  hideTooltip() {
    const tooltip = document.getElementById('fx-tooltip');
    if (tooltip) {
      tooltip.remove();
    }
  }

  // === TAB COMPONENT ===
  initTabs() {
    document.querySelectorAll('[data-tabs]').forEach(tabContainer => {
      const tabs = tabContainer.querySelectorAll('[data-tab]');
      const panels = tabContainer.querySelectorAll('[data-tab-panel]');

      tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
          e.preventDefault();
          const targetPanel = tab.getAttribute('data-tab');
          this.switchTab(tabs, panels, targetPanel);
        });
      });
    });
  }

  switchTab(tabs, panels, targetPanel) {
    // Deactivate all tabs and panels
    tabs.forEach(tab => tab.classList.remove('active'));
    panels.forEach(panel => panel.classList.remove('active'));

    // Activate selected tab and panel
    const selectedTab = Array.from(tabs).find(tab => tab.getAttribute('data-tab') === targetPanel);
    const selectedPanel = Array.from(panels).find(panel => panel.getAttribute('data-tab-panel') === targetPanel);

    if (selectedTab) selectedTab.classList.add('active');
    if (selectedPanel) selectedPanel.classList.add('active');
  }

  // === NOTIFICATION COMPONENT ===
  initNotifications() {
    // Auto-dismiss notifications
    document.querySelectorAll('.alert[data-auto-dismiss]').forEach(alert => {
      const delay = parseInt(alert.getAttribute('data-auto-dismiss')) || 5000;
      setTimeout(() => {
        this.dismissNotification(alert);
      }, delay);
    });

    // Manual dismiss buttons
    document.querySelectorAll('[data-dismiss="alert"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const alert = btn.closest('.alert');
        this.dismissNotification(alert);
      });
    });
  }

  dismissNotification(alert) {
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(100%)';
    setTimeout(() => {
      alert.remove();
    }, 300);
  }

  // === QUICK ACTIONS COMPONENT ===
  initQuickActions() {
    const quickActionBtn = document.querySelector('[data-quick-actions]');
    if (!quickActionBtn) return;

    quickActionBtn.addEventListener('click', () => {
      this.showQuickActions();
    });
  }

  showQuickActions() {
    const actions = [
      { icon: '📝', label: 'New RFQ', action: 'createRFQ()' },
      { icon: '📦', label: 'New Order', action: 'createOrder()' },
      { icon: '📧', label: 'Scan Emails', action: 'scanEmails()' },
      { icon: '📊', label: 'View Analytics', action: 'viewAnalytics()' }
    ];

    const content = actions.map(action => `
      <button class="quick-action-item" onclick="${action.action}">
        <span class="icon">${action.icon}</span>
        <span class="label">${action.label}</span>
      </button>
    `).join('');

    this.createModal('quick-actions-modal', 'Quick Actions', content, {
      size: 'sm',
      footer: '<button class="btn btn-secondary" data-modal-close>Close</button>'
    });
  }

  // === UTILITY METHODS ===

  createModal(id, title, content, options = {}) {
    const modalHtml = `
      <div class="modal" id="${id}">
        <div class="modal-backdrop">
          <div class="modal-dialog ${options.size ? `modal-${options.size}` : ''}">
            <div class="modal-content">
              <div class="modal-header">
                <h3 class="modal-title">${title}</h3>
                <button class="btn btn-ghost btn-sm" data-modal-close>&times;</button>
              </div>
              <div class="modal-body">
                ${content}
              </div>
              ${options.footer ? `<div class="modal-footer">${options.footer}</div>` : ''}
            </div>
          </div>
        </div>
      </div>
    `;

    // Remove existing modal with same ID
    const existing = document.getElementById(id);
    if (existing) existing.remove();

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    this.openModal(id);

    // Re-initialize modal events for the new modal
    this.initModals();
  }

  toast(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
      </div>
    `;

    // Toast container
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    container.appendChild(toast);

    // Auto-remove after duration
    setTimeout(() => {
      if (toast.parentNode) {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
      }
    }, duration);
  }

  confirm(message, onConfirm, onCancel) {
    const content = `
      <p class="text-base mb-6">${message}</p>
      <div class="flex gap-3 justify-end">
        <button class="btn btn-secondary" onclick="FX.closeModal(); ${onCancel || ''}">Cancel</button>
        <button class="btn btn-critical" onclick="FX.closeModal(); ${onConfirm}">Confirm</button>
      </div>
    `;

    this.createModal('confirm-modal', 'Confirm Action', content, { size: 'sm' });
  }

  loading(show = true, message = 'Loading...') {
    const loadingId = 'fx-loading-overlay';
    
    if (show) {
      const overlay = document.createElement('div');
      overlay.id = loadingId;
      overlay.className = 'loading-overlay';
      overlay.innerHTML = `
        <div class="loading-content">
          <div class="spinner"></div>
          <p class="loading-message">${message}</p>
        </div>
      `;
      document.body.appendChild(overlay);
    } else {
      const overlay = document.getElementById(loadingId);
      if (overlay) overlay.remove();
    }
  }

  // === DATA BINDING ===
  
  bindData(element, data) {
    const template = element.getAttribute('data-template');
    if (!template) return;

    element.innerHTML = this.renderTemplate(template, data);
  }

  renderTemplate(template, data) {
    return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return data[key] || '';
    });
  }

  // === FORM HELPERS ===

  validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
      const isFieldValid = this.validateField(input);
      if (!isFieldValid) isValid = false;
    });

    return isValid;
  }

  validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    let isValid = true;

    // Remove previous error states
    field.classList.remove('error');
    const errorElement = field.parentNode.querySelector('.form-error');
    if (errorElement) errorElement.remove();

    // Required validation
    if (field.hasAttribute('required') && !value) {
      isValid = false;
      this.showFieldError(field, 'This field is required');
    }

    // Email validation
    if (type === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        isValid = false;
        this.showFieldError(field, 'Please enter a valid email address');
      }
    }

    // Number validation
    if (type === 'number' && value) {
      const min = field.getAttribute('min');
      const max = field.getAttribute('max');
      const numValue = parseFloat(value);

      if (isNaN(numValue)) {
        isValid = false;
        this.showFieldError(field, 'Please enter a valid number');
      } else if (min && numValue < parseFloat(min)) {
        isValid = false;
        this.showFieldError(field, `Value must be at least ${min}`);
      } else if (max && numValue > parseFloat(max)) {
        isValid = false;
        this.showFieldError(field, `Value must be no more than ${max}`);
      }
    }

    return isValid;
  }

  showFieldError(field, message) {
    field.classList.add('error');
    const errorElement = document.createElement('div');
    errorElement.className = 'form-error';
    errorElement.textContent = message;
    field.parentNode.appendChild(errorElement);
  }
}

// Initialize components
const FX = new FXComponents();

// Make FX available globally
window.FX = FX;

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FXComponents;
}