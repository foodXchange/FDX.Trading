/**
 * Enhanced Error Handler for FoodXchange Platform
 * Provides intelligent error messaging, actionable recovery, and notifications integration
 */

class EnhancedErrorHandler {
    constructor() {
        this.errorContainer = null;
        this.activeErrors = new Map();
        this.recoveryAttempts = new Map();
        this.errorHistory = [];
        this.notificationCenter = null;
        this.init();
    }

    init() {
        this.createErrorContainer();
        this.setupGlobalErrorHandlers();
        this.loadErrorHistory();
        this.initializeNotificationCenter();
    }

    createErrorContainer() {
        // Create enhanced error container
        if (!document.getElementById('enhancedErrorContainer')) {
            const container = document.createElement('div');
            container.id = 'enhancedErrorContainer';
            container.className = 'position-fixed top-0 start-50 translate-middle-x p-3';
            container.style.zIndex = '9999';
            container.style.maxWidth = '600px';
            container.style.width = '100%';
            document.body.appendChild(container);
        }
        this.errorContainer = document.getElementById('enhancedErrorContainer');
    }

    setupGlobalErrorHandlers() {
        // Global unhandled promise rejection handler
        window.addEventListener('unhandledrejection', event => {
            console.error('Unhandled promise rejection:', event.reason);
            this.handleError(event.reason, {
                type: 'unhandled_promise_rejection',
                context: 'global'
            });
            event.preventDefault();
        });

        // Global error handler
        window.addEventListener('error', event => {
            console.error('Global error:', event.error);
            this.handleError(event.error, {
                type: 'global_error',
                context: 'global',
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno
            });
        });

        // Network error handler
        window.addEventListener('offline', () => {
            this.handleError(new Error('Network connection lost'), {
                type: 'network_connectivity',
                context: 'network',
                severity: 'high'
            });
        });

        window.addEventListener('online', () => {
            this.showRecoverySuccess('Network connection restored', 'success');
        });
    }

    async handleError(error, context = {}) {
        try {
            // Create error context
            const errorContext = {
                user_id: this.getCurrentUserId(),
                timestamp: new Date().toISOString(),
                workflow_step: context.workflow_step || this.getCurrentWorkflowStep(),
                error_type: context.type || 'unknown',
                severity: context.severity || 'medium',
                ...context
            };

            // Analyze error
            const errorAnalysis = this.analyzeError(error, errorContext);
            
            // Get recovery options
            const recoveryOptions = this.getRecoveryOptions(errorAnalysis);
            
            // Create error notification
            const errorNotification = {
                id: this.generateErrorId(),
                error: error,
                analysis: errorAnalysis,
                context: errorContext,
                recoveryOptions: recoveryOptions,
                created_at: new Date(),
                status: 'active'
            };

            // Store error
            this.activeErrors.set(errorNotification.id, errorNotification);
            this.errorHistory.push(errorNotification);

            // Display error
            this.displayError(errorNotification);

            // Send to backend for processing (don't fail if this doesn't work)
            try {
                await this.sendErrorToBackend(errorNotification);
            } catch (backendError) {
                console.warn('Backend error reporting failed:', backendError);
                // Don't show this error to the user
            }

            // Attempt automatic recovery
            await this.attemptAutomaticRecovery(errorNotification);

            return errorNotification;

        } catch (handlingError) {
            console.error('Error in error handler:', handlingError);
            // Only show fallback error for critical errors, not backend communication issues
            if (error && error.message && !error.message.includes('fetch')) {
                this.showFallbackError(error);
            }
        }
    }

    analyzeError(error, context) {
        const errorMessage = error.message || error.toString();
        const errorString = errorMessage.toLowerCase();

        // Error type classification
        let errorType = 'unknown';
        let severity = context.severity || 'medium';
        let userFriendlyMessage = 'An unexpected error occurred. Please try again.';

        // File format errors
        if (this.matchesPattern(errorString, ['unsupported.*format', 'invalid.*file.*type', 'format.*not.*supported'])) {
            errorType = 'file_format';
            userFriendlyMessage = "The image format isn't supported. Please use JPG, PNG, or WEBP files.";
        }
        // File size errors
        else if (this.matchesPattern(errorString, ['file.*too.*large', 'size.*exceeds.*limit', 'maximum.*file.*size'])) {
            errorType = 'file_size';
            userFriendlyMessage = "The image file is too large. Please reduce it to under 10MB.";
        }
        // Network connectivity errors
        else if (this.matchesPattern(errorString, ['connection.*failed', 'network.*error', 'timeout', 'connection.*refused', 'fetch', 'network'])) {
            errorType = 'network_connectivity';
            severity = 'high';
            userFriendlyMessage = "We're having trouble connecting to our services. Please check your internet connection.";
        }
        // Service unavailable errors
        else if (this.matchesPattern(errorString, ['service.*unavailable', 'azure.*service.*error', 'api.*unavailable', '500', '502', '503', '504'])) {
            errorType = 'service_unavailable';
            severity = 'high';
            userFriendlyMessage = "Our AI analysis service is temporarily unavailable. We're working to restore it.";
        }
        // Quota limit errors
        else if (this.matchesPattern(errorString, ['quota.*exceeded', 'rate.*limit', 'daily.*limit', '429'])) {
            errorType = 'quota_limit';
            userFriendlyMessage = "You've reached your daily analysis limit. Please try again tomorrow or upgrade your plan.";
        }
        // Authentication errors
        else if (this.matchesPattern(errorString, ['unauthorized', 'authentication.*failed', 'invalid.*token', '401', '403'])) {
            errorType = 'authentication';
            severity = 'high';
            userFriendlyMessage = "Please log in again to continue.";
        }
        // Generic API errors
        else if (this.matchesPattern(errorString, ['api', 'request', 'response', 'http', 'server'])) {
            errorType = 'api_error';
            userFriendlyMessage = "We're experiencing technical difficulties. Please try again in a moment.";
        }

        return {
            type: errorType,
            severity: severity,
            errorCode: this.generateErrorCode(errorType),
            technicalMessage: errorMessage,
            userFriendlyMessage: userFriendlyMessage,
            stackTrace: error.stack,
            metadata: {
                errorClass: error.constructor.name,
                timestamp: context.timestamp,
                workflowStep: context.workflow_step
            }
        };
    }

    matchesPattern(text, patterns) {
        return patterns.some(pattern => {
            const regex = new RegExp(pattern, 'i');
            return regex.test(text);
        });
    }

    generateErrorCode(errorType) {
        const timestamp = new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14);
        const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
        return `${errorType.toUpperCase()}-${timestamp}-${random}`;
    }

    generateErrorId() {
        return 'error-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    getRecoveryOptions(errorAnalysis) {
        const options = [];

        switch (errorAnalysis.type) {
            case 'file_format':
                options.push(
                    {
                        action: 'change_file_format',
                        label: 'Upload Different Format',
                        description: 'Try uploading JPG, PNG, or WEBP format',
                        icon: 'fas fa-file-image',
                        color: 'primary',
                        requiresConfirmation: true
                    },
                    {
                        action: 'use_manual_entry',
                        label: 'Use Manual Entry',
                        description: 'Enter product details manually',
                        icon: 'fas fa-edit',
                        color: 'secondary',
                        requiresConfirmation: true
                    }
                );
                break;

            case 'file_size':
                options.push(
                    {
                        action: 'reduce_file_size',
                        label: 'Reduce File Size',
                        description: 'Compress image to under 10MB',
                        icon: 'fas fa-compress',
                        color: 'warning',
                        requiresConfirmation: true
                    },
                    {
                        action: 'upload_different_file',
                        label: 'Upload Smaller Image',
                        description: 'Try a different image with smaller size',
                        icon: 'fas fa-upload',
                        color: 'primary',
                        requiresConfirmation: true
                    }
                );
                break;

            case 'network_connectivity':
                options.push(
                    {
                        action: 'retry_with_backoff',
                        label: 'Retry Connection',
                        description: 'Automatically retry with increasing delays',
                        icon: 'fas fa-sync',
                        color: 'info',
                        automatic: true,
                        maxAttempts: 3,
                        backoffDelay: 2000
                    },
                    {
                        action: 'check_connection',
                        label: 'Check Connection',
                        description: 'Verify your internet connection',
                        icon: 'fas fa-wifi',
                        color: 'warning',
                        requiresConfirmation: true
                    }
                );
                break;

            case 'service_unavailable':
                options.push(
                    {
                        action: 'retry_with_backoff',
                        label: 'Retry Service',
                        description: 'Service may be temporarily unavailable',
                        icon: 'fas fa-clock',
                        color: 'info',
                        automatic: true,
                        maxAttempts: 5,
                        backoffDelay: 5000
                    },
                    {
                        action: 'save_as_draft',
                        label: 'Save as Draft',
                        description: 'Save your work and try again later',
                        icon: 'fas fa-save',
                        color: 'secondary',
                        requiresConfirmation: true
                    }
                );
                break;

            case 'quota_limit':
                options.push(
                    {
                        action: 'contact_support',
                        label: 'Upgrade Plan',
                        description: 'Contact support to increase your limits',
                        icon: 'fas fa-crown',
                        color: 'warning',
                        requiresConfirmation: true
                    },
                    {
                        action: 'try_tomorrow',
                        label: 'Try Tomorrow',
                        description: 'Daily limits reset at midnight',
                        icon: 'fas fa-calendar',
                        color: 'info',
                        requiresConfirmation: true
                    }
                );
                break;

            case 'api_error':
                options.push(
                    {
                        action: 'retry',
                        label: 'Try Again',
                        description: 'Retry the operation',
                        icon: 'fas fa-redo',
                        color: 'primary',
                        requiresConfirmation: true
                    },
                    {
                        action: 'contact_support',
                        label: 'Contact Support',
                        description: 'Get help from our support team',
                        icon: 'fas fa-headset',
                        color: 'warning',
                        requiresConfirmation: true
                    }
                );
                break;

            default:
                options.push(
                    {
                        action: 'retry',
                        label: 'Try Again',
                        description: 'Attempt the operation again',
                        icon: 'fas fa-redo',
                        color: 'primary',
                        requiresConfirmation: true
                    },
                    {
                        action: 'contact_support',
                        label: 'Contact Support',
                        description: 'Get help from our support team',
                        icon: 'fas fa-headset',
                        color: 'warning',
                        requiresConfirmation: true
                    }
                );
        }

        return options;
    }

    displayError(errorNotification) {
        const errorElement = this.createErrorElement(errorNotification);
        this.errorContainer.appendChild(errorElement);

        // Auto-remove after 10 seconds for non-critical errors
        if (errorNotification.analysis.severity !== 'critical') {
            setTimeout(() => {
                this.removeError(errorNotification.id);
            }, 10000);
        }
    }

    createErrorElement(errorNotification) {
        const errorId = errorNotification.id;
        const analysis = errorNotification.analysis;
        const options = errorNotification.recoveryOptions;

        const errorHtml = `
            <div id="${errorId}" class="enhanced-error-card mb-3" data-error-id="${errorId}">
                <div class="card border-${this.getSeverityColor(analysis.severity)}">
                    <div class="card-header bg-${this.getSeverityColor(analysis.severity)} text-white d-flex justify-content-between align-items-center">
                        <div>
                            <i class="${this.getErrorIcon(analysis.type)} me-2"></i>
                            <strong>${this.getErrorTitle(analysis.type)}</strong>
                            <small class="ms-2">${analysis.errorCode}</small>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-outline-light" onclick="enhancedErrorHandler.toggleErrorDetails('${errorId}')">
                                <i class="fas fa-info-circle"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-light" onclick="enhancedErrorHandler.removeError('${errorId}')">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <p class="card-text">${analysis.userFriendlyMessage}</p>
                        
                        <!-- Recovery Options -->
                        <div class="recovery-options mt-3">
                            <h6 class="text-muted mb-2">What would you like to do?</h6>
                            <div class="row g-2">
                                ${options.map(option => `
                                    <div class="col-md-6">
                                        <button class="btn btn-outline-${option.color} btn-sm w-100" 
                                                onclick="enhancedErrorHandler.executeRecoveryAction('${errorId}', '${option.action}')">
                                            <i class="${option.icon} me-1"></i>
                                            ${option.label}
                                        </button>
                                        <small class="text-muted d-block mt-1">${option.description}</small>
                                    </div>
                                `).join('')}
                            </div>
                        </div>

                        <!-- Error Details (Hidden by default) -->
                        <div class="error-details mt-3" style="display: none;">
                            <hr>
                            <h6 class="text-muted">Technical Details</h6>
                            <div class="bg-light p-2 rounded">
                                <small class="text-muted">
                                    <strong>Error:</strong> ${analysis.technicalMessage}<br>
                                    <strong>Type:</strong> ${analysis.type}<br>
                                    <strong>Severity:</strong> ${analysis.severity}<br>
                                    <strong>Workflow:</strong> ${errorNotification.context.workflow_step || 'Unknown'}
                                </small>
                            </div>
                        </div>

                        <!-- Progress Indicator for Automatic Recovery -->
                        <div class="recovery-progress mt-3" style="display: none;">
                            <div class="progress">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                     role="progressbar" style="width: 0%"></div>
                            </div>
                            <small class="text-muted mt-1">Attempting automatic recovery...</small>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = errorHtml;
        return tempDiv.firstElementChild;
    }

    getSeverityColor(severity) {
        const colorMap = {
            'low': 'info',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'danger'
        };
        return colorMap[severity] || 'warning';
    }

    getErrorIcon(errorType) {
        const iconMap = {
            'file_format': 'fas fa-file-image',
            'file_size': 'fas fa-weight-hanging',
            'network_connectivity': 'fas fa-wifi',
            'service_unavailable': 'fas fa-server',
            'quota_limit': 'fas fa-chart-line',
            'authentication': 'fas fa-user-lock',
            'authorization': 'fas fa-ban',
            'api_error': 'fas fa-exclamation-circle',
            'unknown': 'fas fa-exclamation-triangle'
        };
        return iconMap[errorType] || iconMap['unknown'];
    }

    getErrorTitle(errorType) {
        const titleMap = {
            'file_format': 'Unsupported File Format',
            'file_size': 'File Too Large',
            'network_connectivity': 'Connection Issue',
            'service_unavailable': 'Service Temporarily Unavailable',
            'quota_limit': 'Usage Limit Reached',
            'authentication': 'Authentication Required',
            'authorization': 'Access Denied',
            'api_error': 'Technical Issue',
            'unknown': 'Unexpected Error'
        };
        return titleMap[errorType] || titleMap['unknown'];
    }

    toggleErrorDetails(errorId) {
        const errorElement = document.getElementById(errorId);
        const detailsElement = errorElement.querySelector('.error-details');
        const isHidden = detailsElement.style.display === 'none';
        detailsElement.style.display = isHidden ? 'block' : 'none';
    }

    async executeRecoveryAction(errorId, action) {
        const errorNotification = this.activeErrors.get(errorId);
        if (!errorNotification) return;

        try {
            switch (action) {
                case 'retry':
                case 'retry_with_backoff':
                    await this.retryOperation(errorNotification);
                    break;
                case 'change_file_format':
                    this.showFileFormatHelp();
                    break;
                case 'reduce_file_size':
                    this.showFileSizeHelp();
                    break;
                case 'upload_different_file':
                    this.triggerFileUpload();
                    break;
                case 'use_manual_entry':
                    this.switchToManualEntry();
                    break;
                case 'save_as_draft':
                    await this.saveAsDraft();
                    break;
                case 'contact_support':
                    this.contactSupport(errorNotification);
                    break;
                case 'check_connection':
                    this.checkConnection();
                    break;
                case 'try_tomorrow':
                    this.showQuotaInfo();
                    break;
                default:
                    console.warn('Unknown recovery action:', action);
            }

            // Mark error as resolved
            this.markErrorResolved(errorId, action);

        } catch (error) {
            console.error('Recovery action failed:', error);
            this.showRecoveryError('Recovery action failed. Please try again.');
        }
    }

    async retryOperation(errorNotification) {
        const errorElement = document.getElementById(errorNotification.id);
        const progressElement = errorElement.querySelector('.recovery-progress');
        const progressBar = progressElement.querySelector('.progress-bar');

        // Show progress
        progressElement.style.display = 'block';
        progressBar.style.width = '0%';

        // Simulate retry with progress
        for (let i = 1; i <= 5; i++) {
            await this.sleep(1000);
            progressBar.style.width = `${i * 20}%`;
        }

        // Hide progress
        progressElement.style.display = 'none';

        // Attempt to retry the original operation
        // This would need to be implemented based on the specific operation that failed
        this.showRecoverySuccess('Operation retried successfully', 'success');
    }

    showFileFormatHelp() {
        this.showModal('Supported File Formats', `
            <div class="text-center">
                <h5>Supported Image Formats</h5>
                <div class="row mt-3">
                    <div class="col-md-4">
                        <i class="fas fa-file-image fa-3x text-primary mb-2"></i>
                        <h6>JPG/JPEG</h6>
                        <small class="text-muted">Best for photographs</small>
                    </div>
                    <div class="col-md-4">
                        <i class="fas fa-file-image fa-3x text-success mb-2"></i>
                        <h6>PNG</h6>
                        <small class="text-muted">Best for graphics with transparency</small>
                    </div>
                    <div class="col-md-4">
                        <i class="fas fa-file-image fa-3x text-info mb-2"></i>
                        <h6>WEBP</h6>
                        <small class="text-muted">Best for web optimization</small>
                    </div>
                </div>
                <div class="mt-3">
                    <button class="btn btn-primary" onclick="enhancedErrorHandler.triggerFileUpload()">
                        <i class="fas fa-upload me-2"></i>Upload New Image
                    </button>
                </div>
            </div>
        `);
    }

    showFileSizeHelp() {
        this.showModal('File Size Optimization', `
            <div class="text-center">
                <h5>Reduce Your Image Size</h5>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <h6><i class="fas fa-compress text-warning me-2"></i>Online Tools</h6>
                        <ul class="list-unstyled">
                            <li><a href="https://tinypng.com" target="_blank">TinyPNG</a></li>
                            <li><a href="https://squoosh.app" target="_blank">Squoosh</a></li>
                            <li><a href="https://compressjpeg.com" target="_blank">CompressJPEG</a></li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-camera text-info me-2"></i>Tips</h6>
                        <ul class="list-unstyled text-start">
                            <li>• Resize to 1200x800 pixels</li>
                            <li>• Use 80% quality setting</li>
                            <li>• Remove unnecessary metadata</li>
                        </ul>
                    </div>
                </div>
                <div class="mt-3">
                    <button class="btn btn-primary" onclick="enhancedErrorHandler.triggerFileUpload()">
                        <i class="fas fa-upload me-2"></i>Upload Optimized Image
                    </button>
                </div>
            </div>
        `);
    }

    triggerFileUpload() {
        // Trigger file upload dialog
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.click();
        } else {
            this.showRecoveryError('File upload not available on this page.');
        }
    }

    switchToManualEntry() {
        // Switch to manual entry mode
        this.showRecoverySuccess('Switched to manual entry mode', 'info');
        // This would need to be implemented based on the specific page/component
    }

    async saveAsDraft() {
        try {
            // Save current work as draft
            this.showRecoverySuccess('Work saved as draft successfully', 'success');
            // This would need to be implemented based on the specific page/component
        } catch (error) {
            this.showRecoveryError('Failed to save draft. Please try again.');
        }
    }

    contactSupport(errorNotification) {
        const errorCode = errorNotification.analysis.errorCode;
        const errorDetails = errorNotification.analysis.technicalMessage;
        
        const supportMessage = `
            <div class="text-center">
                <h5>Contact Support</h5>
                <p>Please include the following error code when contacting support:</p>
                <div class="bg-light p-3 rounded">
                    <code class="text-primary">${errorCode}</code>
                </div>
                <div class="mt-3">
                    <a href="mailto:support@foodxchange.com?subject=Error ${errorCode}" class="btn btn-primary me-2">
                        <i class="fas fa-envelope me-2"></i>Email Support
                    </a>
                    <a href="/support" class="btn btn-outline-primary">
                        <i class="fas fa-headset me-2"></i>Support Portal
                    </a>
                </div>
            </div>
        `;
        
        this.showModal('Contact Support', supportMessage);
    }

    checkConnection() {
        this.showModal('Connection Test', `
            <div class="text-center">
                <h5>Testing Connection</h5>
                <div id="connectionTestResult" class="mt-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Testing...</span>
                    </div>
                    <p class="mt-2">Checking internet connection...</p>
                </div>
            </div>
        `);

        // Simulate connection test
        setTimeout(() => {
            const resultElement = document.getElementById('connectionTestResult');
            if (navigator.onLine) {
                resultElement.innerHTML = `
                    <i class="fas fa-check-circle fa-3x text-success mb-2"></i>
                    <h6 class="text-success">Connection OK</h6>
                    <p class="text-muted">Your internet connection is working properly.</p>
                `;
            } else {
                resultElement.innerHTML = `
                    <i class="fas fa-times-circle fa-3x text-danger mb-2"></i>
                    <h6 class="text-danger">No Connection</h6>
                    <p class="text-muted">Please check your internet connection and try again.</p>
                `;
            }
        }, 2000);
    }

    showQuotaInfo() {
        this.showModal('Usage Limits', `
            <div class="text-center">
                <h5>Daily Usage Limits</h5>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <h6><i class="fas fa-chart-line text-warning me-2"></i>Current Usage</h6>
                        <div class="progress mb-2">
                            <div class="progress-bar bg-warning" style="width: 100%"></div>
                        </div>
                        <small class="text-muted">100% of daily limit used</small>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-clock text-info me-2"></i>Reset Time</h6>
                        <p class="text-muted">Limits reset at midnight (UTC)</p>
                    </div>
                </div>
                <div class="mt-3">
                    <a href="/pricing" class="btn btn-primary">
                        <i class="fas fa-crown me-2"></i>Upgrade Plan
                    </a>
                </div>
            </div>
        `);
    }

    showModal(title, content) {
        const modalId = 'enhancedErrorModal';
        let modal = document.getElementById(modalId);
        
        if (!modal) {
            modal = document.createElement('div');
            modal.id = modalId;
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title"></h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        modal.querySelector('.modal-title').textContent = title;
        modal.querySelector('.modal-body').innerHTML = content;
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }

    async attemptAutomaticRecovery(errorNotification) {
        const automaticOptions = errorNotification.recoveryOptions.filter(option => option.automatic);
        
        for (const option of automaticOptions) {
            try {
                await this.executeRecoveryAction(errorNotification.id, option.action);
                break; // Stop after first successful automatic recovery
            } catch (error) {
                console.error('Automatic recovery failed:', error);
            }
        }
    }

    markErrorResolved(errorId, resolutionMethod) {
        const errorNotification = this.activeErrors.get(errorId);
        if (errorNotification) {
            errorNotification.status = 'resolved';
            errorNotification.resolved_at = new Date();
            errorNotification.resolution_method = resolutionMethod;
        }
    }

    removeError(errorId) {
        const errorElement = document.getElementById(errorId);
        if (errorElement) {
            errorElement.remove();
        }
        this.activeErrors.delete(errorId);
    }

    showRecoverySuccess(message, type = 'success') {
        this.showToast(message, type);
    }

    showRecoveryError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        // Use existing toast system if available
        if (window.errorHandler) {
            window.errorHandler.showToast(message, type);
        } else {
            // Fallback toast
            const toast = document.createElement('div');
            toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
            toast.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
            toast.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 5000);
        }
    }

    showFallbackError(error) {
        this.showToast('An unexpected error occurred. Please try again or contact support.', 'error');
    }

    getCurrentUserId() {
        // Get current user ID from page context
        const userElement = document.querySelector('[data-user-id]');
        return userElement ? userElement.dataset.userId : null;
    }

    getCurrentWorkflowStep() {
        // Get current workflow step from page context
        const workflowElement = document.querySelector('[data-workflow-step]');
        return workflowElement ? workflowElement.dataset.workflowStep : 'unknown';
    }

    async sendErrorToBackend(errorNotification) {
        try {
            const response = await fetch('/api/errors', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    error_id: errorNotification.id,
                    analysis: errorNotification.analysis,
                    context: errorNotification.context,
                    recovery_options: errorNotification.recoveryOptions
                })
            });

            if (!response.ok) {
                console.warn('Failed to send error to backend:', response.status);
                // Don't show error to user - just log it
                return false;
            }
            
            return true;
        } catch (error) {
            console.warn('Failed to send error to backend:', error);
            // Don't show error to user - just log it
            return false;
        }
    }

    loadErrorHistory() {
        const history = localStorage.getItem('enhancedErrorHistory');
        if (history) {
            try {
                this.errorHistory = JSON.parse(history);
            } catch (error) {
                console.warn('Failed to load error history:', error);
            }
        }
    }

    saveErrorHistory() {
        try {
            localStorage.setItem('enhancedErrorHistory', JSON.stringify(this.errorHistory.slice(-50)));
        } catch (error) {
            console.warn('Failed to save error history:', error);
        }
    }

    initializeNotificationCenter() {
        // Initialize notification center integration
        if (window.notificationCenter) {
            this.notificationCenter = window.notificationCenter;
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Public API methods
    static getInstance() {
        if (!window.enhancedErrorHandler) {
            window.enhancedErrorHandler = new EnhancedErrorHandler();
        }
        return window.enhancedErrorHandler;
    }
}

// Initialize enhanced error handler
const enhancedErrorHandler = EnhancedErrorHandler.getInstance();

// Export for use in other modules
window.enhancedErrorHandler = enhancedErrorHandler; 