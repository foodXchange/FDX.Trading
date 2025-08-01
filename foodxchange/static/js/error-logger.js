/**
 * Client-side Error Logger
 * Automatically captures and logs JavaScript errors to the server
 */

(function() {
    'use strict';

    // Configuration
    const ERROR_LOG_ENDPOINT = '/api/errors/log';
    const MAX_STACK_LENGTH = 5000;
    const ERROR_BATCH_SIZE = 5;
    const ERROR_BATCH_TIMEOUT = 5000; // 5 seconds
    
    // Error queue for batching
    let errorQueue = [];
    let batchTimeout = null;

    /**
     * Get error severity based on error type and message
     */
    function getErrorSeverity(error) {
        const message = error.message || '';
        const type = error.name || 'Error';
        
        // Critical errors
        if (message.includes('SecurityError') || 
            message.includes('CORS') ||
            message.includes('unauthorized') ||
            message.includes('403') ||
            message.includes('401')) {
            return 'critical';
        }
        
        // High severity
        if (type === 'TypeError' || 
            type === 'ReferenceError' ||
            message.includes('undefined') ||
            message.includes('null') ||
            message.includes('500')) {
            return 'high';
        }
        
        // Medium severity
        if (type === 'SyntaxError' ||
            message.includes('404') ||
            message.includes('timeout')) {
            return 'medium';
        }
        
        // Low severity
        return 'low';
    }

    /**
     * Get current page path
     */
    function getCurrentPage() {
        return window.location.pathname;
    }

    /**
     * Get browser information
     */
    function getBrowserInfo() {
        const ua = navigator.userAgent;
        let browser = 'Unknown';
        let version = '';
        
        if (ua.indexOf('Chrome') > -1) {
            browser = 'Chrome';
            version = ua.match(/Chrome\/(\d+)/)?.[1] || '';
        } else if (ua.indexOf('Safari') > -1) {
            browser = 'Safari';
            version = ua.match(/Version\/(\d+)/)?.[1] || '';
        } else if (ua.indexOf('Firefox') > -1) {
            browser = 'Firefox';
            version = ua.match(/Firefox\/(\d+)/)?.[1] || '';
        } else if (ua.indexOf('Edge') > -1) {
            browser = 'Edge';
            version = ua.match(/Edge\/(\d+)/)?.[1] || '';
        }
        
        return browser + (version ? ' ' + version : '');
    }

    /**
     * Format error for logging
     */
    function formatError(error, context = {}) {
        const errorData = {
            message: error.message || 'Unknown error',
            stack: error.stack ? error.stack.substring(0, MAX_STACK_LENGTH) : '',
            type: error.name || 'Error',
            page: getCurrentPage(),
            severity: getErrorSeverity(error),
            browser: getBrowserInfo(),
            timestamp: new Date().toISOString(),
            additional_data: {
                url: window.location.href,
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                screenResolution: `${screen.width}x${screen.height}`,
                viewport: `${window.innerWidth}x${window.innerHeight}`,
                ...context
            }
        };
        
        // Add source information if available
        if (error.filename) {
            errorData.additional_data.filename = error.filename;
            errorData.additional_data.lineno = error.lineno;
            errorData.additional_data.colno = error.colno;
        }
        
        return errorData;
    }

    /**
     * Send error batch to server
     */
    async function sendErrorBatch() {
        if (errorQueue.length === 0) return;
        
        const batch = errorQueue.splice(0, ERROR_BATCH_SIZE);
        
        try {
            // Send individual errors for now
            // In future, could implement batch endpoint
            for (const errorData of batch) {
                await fetch(ERROR_LOG_ENDPOINT, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(errorData)
                });
            }
        } catch (err) {
            // If logging fails, don't create infinite loop
            console.error('Failed to log error to server:', err);
            
            // Put errors back in queue if needed
            if (errorQueue.length < 50) { // Prevent memory issues
                errorQueue.unshift(...batch);
            }
        }
    }

    /**
     * Queue error for logging
     */
    function queueError(errorData) {
        errorQueue.push(errorData);
        
        // Clear existing timeout
        if (batchTimeout) {
            clearTimeout(batchTimeout);
        }
        
        // Send immediately if batch is full
        if (errorQueue.length >= ERROR_BATCH_SIZE) {
            sendErrorBatch();
        } else {
            // Otherwise, set timeout for batch send
            batchTimeout = setTimeout(sendErrorBatch, ERROR_BATCH_TIMEOUT);
        }
    }

    /**
     * Log error to server
     */
    function logError(error, context = {}) {
        try {
            const errorData = formatError(error, context);
            queueError(errorData);
        } catch (err) {
            console.error('Failed to format error for logging:', err);
        }
    }

    /**
     * Global error handler
     */
    window.addEventListener('error', function(event) {
        const error = {
            message: event.message,
            stack: event.error ? event.error.stack : '',
            name: event.error ? event.error.name : 'Error',
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno
        };
        
        logError(error, {
            source: 'window.error'
        });
        
        // Don't prevent default error handling
        return false;
    });

    /**
     * Unhandled promise rejection handler
     */
    window.addEventListener('unhandledrejection', function(event) {
        const error = {
            message: event.reason ? 
                (event.reason.message || String(event.reason)) : 
                'Unhandled Promise Rejection',
            stack: event.reason && event.reason.stack ? event.reason.stack : '',
            name: 'UnhandledPromiseRejection'
        };
        
        logError(error, {
            source: 'unhandledrejection',
            promise: String(event.promise)
        });
    });

    /**
     * Manual error logging function for use in try-catch blocks
     */
    window.logError = function(error, context = {}) {
        if (error instanceof Error) {
            logError(error, { ...context, source: 'manual' });
        } else {
            logError({
                message: String(error),
                name: 'ManualError',
                stack: new Error().stack
            }, { ...context, source: 'manual' });
        }
    };

    /**
     * Log custom events (warnings, info, etc.)
     */
    window.logEvent = function(level, message, data = {}) {
        const error = {
            message: message,
            name: 'CustomEvent',
            stack: new Error().stack
        };
        
        let severity = 'low';
        if (level === 'error') severity = 'high';
        else if (level === 'warning') severity = 'medium';
        
        logError(error, {
            source: 'custom',
            level: level,
            severity: severity,
            ...data
        });
    };

    /**
     * Monitor AJAX errors (for fetch)
     */
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        return originalFetch.apply(this, args)
            .then(response => {
                if (!response.ok && response.status >= 500) {
                    logError({
                        message: `HTTP ${response.status}: ${response.statusText}`,
                        name: 'FetchError',
                        stack: new Error().stack
                    }, {
                        source: 'fetch',
                        url: args[0],
                        status: response.status,
                        statusText: response.statusText
                    });
                }
                return response;
            })
            .catch(error => {
                logError(error, {
                    source: 'fetch',
                    url: args[0]
                });
                throw error;
            });
    };

    /**
     * Monitor console errors
     */
    const originalConsoleError = console.error;
    console.error = function(...args) {
        originalConsoleError.apply(console, args);
        
        // Only log if it looks like an actual error
        const message = args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
        ).join(' ');
        
        if (message.toLowerCase().includes('error') || 
            message.toLowerCase().includes('exception') ||
            message.toLowerCase().includes('failed')) {
            logError({
                message: message,
                name: 'ConsoleError',
                stack: new Error().stack
            }, {
                source: 'console.error'
            });
        }
    };

    /**
     * Send any remaining errors before page unload
     */
    window.addEventListener('beforeunload', function() {
        if (errorQueue.length > 0) {
            // Try to send synchronously
            const xhr = new XMLHttpRequest();
            xhr.open('POST', ERROR_LOG_ENDPOINT, false); // Synchronous
            xhr.setRequestHeader('Content-Type', 'application/json');
            
            errorQueue.forEach(errorData => {
                try {
                    xhr.send(JSON.stringify(errorData));
                } catch (e) {
                    // Ignore errors during unload
                }
            });
        }
    });

    // Expose error logger for debugging
    window.ErrorLogger = {
        logError: logError,
        logEvent: window.logEvent,
        getQueue: () => errorQueue,
        sendBatch: sendErrorBatch,
        clearQueue: () => { errorQueue = []; }
    };

    console.log('Error logger initialized');
})();