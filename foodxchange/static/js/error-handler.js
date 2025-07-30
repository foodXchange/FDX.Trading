/**
 * Global Error Handler for FoodXchange
 * Provides consistent error handling and user feedback
 */

class ErrorHandler {
    constructor() {
        this.toastContainer = null;
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toastContainer')) {
            const container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        this.toastContainer = document.getElementById('toastContainer');

        // Set up global error handler
        window.addEventListener('unhandledrejection', event => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showError('An unexpected error occurred. Please try again.');
            event.preventDefault();
        });
    }

    showToast(message, type = 'info', duration = 5000) {
        const toastId = 'toast-' + Date.now();
        const iconMap = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };

        const colorMap = {
            'success': 'bg-success',
            'error': 'bg-danger',
            'warning': 'bg-warning',
            'info': 'bg-primary'
        };

        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert">
                <div class="toast-header ${colorMap[type]} text-white">
                    <i class="${iconMap[type]} me-2"></i>
                    <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        this.toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: duration });
        toast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showWarning(message) {
        this.showToast(message, 'warning');
    }

    showInfo(message) {
        this.showToast(message, 'info');
    }

    async handleApiCall(apiCall, options = {}) {
        const {
            loadingMessage = 'Processing...',
            successMessage = 'Operation completed successfully',
            errorMessage = 'An error occurred',
            showLoading = true
        } = options;

        let loadingToast;
        
        try {
            if (showLoading) {
                loadingToast = this.showLoadingToast(loadingMessage);
            }

            const result = await apiCall();

            if (loadingToast) {
                loadingToast.hide();
            }

            if (successMessage) {
                this.showSuccess(successMessage);
            }

            return result;
        } catch (error) {
            if (loadingToast) {
                loadingToast.hide();
            }

            console.error('API call error:', error);
            
            let errorMsg = errorMessage;
            if (error.response) {
                // Server responded with error
                if (error.response.data && error.response.data.detail) {
                    errorMsg = error.response.data.detail;
                } else if (error.response.status === 404) {
                    errorMsg = 'Requested resource not found';
                } else if (error.response.status === 403) {
                    errorMsg = 'You do not have permission to perform this action';
                } else if (error.response.status === 500) {
                    errorMsg = 'Server error. Please try again later';
                }
            } else if (error.request) {
                // Request made but no response
                errorMsg = 'Network error. Please check your connection';
            }

            this.showError(errorMsg);
            throw error;
        }
    }

    showLoadingToast(message) {
        const toastId = 'loading-toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" data-bs-autohide="false">
                <div class="toast-body">
                    <div class="d-flex align-items-center">
                        <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                        <div>${message}</div>
                    </div>
                </div>
            </div>
        `;

        this.toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { autohide: false });
        toast.show();

        return {
            hide: () => {
                toast.hide();
                setTimeout(() => toastElement.remove(), 300);
            }
        };
    }

    // Form validation helper
    validateForm(formId) {
        const form = document.getElementById(formId);
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            this.showWarning('Please fill in all required fields');
            return false;
        }
        return true;
    }

    // File upload validation
    validateFileUpload(file, options = {}) {
        const {
            maxSize = 10 * 1024 * 1024, // 10MB default
            allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'],
            allowedExtensions = ['.jpg', '.jpeg', '.png', '.webp']
        } = options;

        // Check file size
        if (file.size > maxSize) {
            this.showError(`File size must be less than ${(maxSize / 1024 / 1024).toFixed(1)}MB`);
            return false;
        }

        // Check file type
        if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
            this.showError('Invalid file type. Please upload an image file');
            return false;
        }

        // Check file extension
        const fileName = file.name.toLowerCase();
        const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
        if (!hasValidExtension) {
            this.showError(`Invalid file extension. Allowed: ${allowedExtensions.join(', ')}`);
            return false;
        }

        return true;
    }
}

// Create global instance
window.errorHandler = new ErrorHandler();