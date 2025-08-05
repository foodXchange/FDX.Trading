// FoodXchange VM Control Center JavaScript

class VMControlCenter {
    constructor() {
        this.toast = null;
        this.uptimeInterval = null;
        this.statusCheckInterval = null;
        this.init();
    }

    init() {
        this.initializeToast();
        this.setupEventListeners();
        this.startUptimeCounter();
        this.startStatusChecks();
        this.setupKeyboardShortcuts();
    }

    initializeToast() {
        const toastEl = document.getElementById('notification-toast');
        if (toastEl) {
            this.toast = new bootstrap.Toast(toastEl, {
                autohide: true,
                delay: 3000
            });
        }
    }

    setupEventListeners() {
        // Copy buttons
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const text = btn.dataset.text || btn.dataset.url;
                this.copyToClipboard(text);
            });
        });

        // Copy credentials button
        const copyCredentialsBtn = document.querySelector('.copy-credentials');
        if (copyCredentialsBtn) {
            copyCredentialsBtn.addEventListener('click', () => {
                const credentials = 'Username: admin\nPassword: admin';
                this.copyToClipboard(credentials);
            });
        }

        // Open service buttons
        document.querySelectorAll('.open-service').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const url = btn.dataset.url;
                this.openService(url);
            });
        });

        // Service cards
        document.querySelectorAll('.service-card').forEach(card => {
            card.addEventListener('click', () => {
                const url = card.dataset.url;
                this.openService(url);
            });
        });

        // Shortcut buttons
        document.querySelectorAll('.shortcut-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const url = btn.dataset.url;
                this.openService(url);
            });
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Don't trigger shortcuts when typing in input fields
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }

            switch(e.key) {
                case '1':
                    this.openService('http://4.206.1.15');
                    break;
                case '2':
                    this.openService('http://4.206.1.15:8003');
                    break;
                case '3':
                    this.openService('http://4.206.1.15:3000');
                    break;
                case '4':
                    this.openService('http://4.206.1.15:19999');
                    break;
                case 'h':
                case 'H':
                    this.showNotification('Press 1-4 for quick access to services', 'info');
                    break;
            }
        });
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('Copied to clipboard!', 'success');
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showNotification('Copied to clipboard!', 'success');
        }
    }

    openService(url) {
        const newWindow = window.open(url, '_blank');
        if (!newWindow) {
            this.showNotification('Popup blocked! Please allow popups for this site.', 'warning');
        } else {
            this.showNotification(`Opening ${url}`, 'success');
        }
    }

    showNotification(message, type = 'info') {
        const toastEl = document.getElementById('notification-toast');
        const messageEl = document.getElementById('toast-message');
        
        if (toastEl && messageEl) {
            // Update toast header icon and color based on type
            const headerEl = toastEl.querySelector('.toast-header');
            const iconEl = headerEl.querySelector('i');
            
            // Remove existing color classes
            headerEl.classList.remove('text-success', 'text-warning', 'text-danger', 'text-info');
            iconEl.className = 'fas me-2';
            
            // Set appropriate styling based on type
            switch(type) {
                case 'success':
                    headerEl.classList.add('text-success');
                    iconEl.classList.add('fa-check-circle');
                    break;
                case 'warning':
                    headerEl.classList.add('text-warning');
                    iconEl.classList.add('fa-exclamation-triangle');
                    break;
                case 'error':
                case 'danger':
                    headerEl.classList.add('text-danger');
                    iconEl.classList.add('fa-times-circle');
                    break;
                default:
                    headerEl.classList.add('text-info');
                    iconEl.classList.add('fa-info-circle');
            }
            
            messageEl.textContent = message;
            
            if (this.toast) {
                this.toast.show();
            }
        }
    }

    startUptimeCounter() {
        let seconds = 0;
        this.uptimeInterval = setInterval(() => {
            seconds++;
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            const uptimeEl = document.getElementById('uptime');
            if (uptimeEl) {
                uptimeEl.textContent = `${hours}h ${minutes}m ${secs}s`;
            }
        }, 1000);
    }

    async startStatusChecks() {
        // Check service statuses every 30 seconds
        this.statusCheckInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/services');
                const data = await response.json();
                
                // Update status badges
                data.services.forEach(service => {
                    const serviceCard = document.querySelector(`[data-service-name="${service.name}"]`);
                    if (serviceCard) {
                        const badge = serviceCard.querySelector('.status-badge');
                        if (badge) {
                            badge.className = `badge status-badge ${
                                service.status === 'online' ? 'bg-success' : 
                                service.status === 'offline' ? 'bg-danger' : 'bg-warning'
                            }`;
                            badge.textContent = service.status.charAt(0).toUpperCase() + service.status.slice(1);
                        }
                    }
                });
            } catch (error) {
                console.log('Status check failed:', error);
            }
        }, 30000);
    }

    async updateVMStatus() {
        try {
            const response = await fetch('/api/vm-status');
            const data = await response.json();
            
            const vmStatusEl = document.getElementById('vm-status');
            if (vmStatusEl) {
                vmStatusEl.textContent = data.vm_status;
            }
        } catch (error) {
            console.log('VM status update failed:', error);
        }
    }

    destroy() {
        if (this.uptimeInterval) {
            clearInterval(this.uptimeInterval);
        }
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.vmControlCenter = new VMControlCenter();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.vmControlCenter) {
        window.vmControlCenter.destroy();
    }
}); 