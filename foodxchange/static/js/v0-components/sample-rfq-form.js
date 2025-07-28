// Sample RFQ Form - v0 Generated JavaScript

// Food Xchange specific functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sample RFQ form component loaded');
    
    // Initialize form elements
    const form = document.getElementById('rfqForm');
    const budgetSlider = document.getElementById('budget');
    const budgetValue = document.querySelector('.budget-value');
    const submitBtn = document.getElementById('submitBtn');
    
    // Budget slider functionality
    if (budgetSlider && budgetValue) {
        budgetSlider.addEventListener('input', function() {
            const value = this.value;
            budgetValue.textContent = `$${parseInt(value).toLocaleString()}`;
        });
    }
    
    // Form submission
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading state
            submitBtn.classList.add('loading');
            
            try {
                // Collect form data
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                
                // Validate form
                if (!validateForm(data)) {
                    return;
                }
                
                // Submit to API
                const response = await callAPI('/rfq/create', data);
                
                if (response.status === 'success') {
                    showSuccess('RFQ created successfully!');
                    // Redirect to dashboard after 2 seconds
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 2000);
                } else {
                    showError('Failed to create RFQ. Please try again.');
                }
                
            } catch (error) {
                console.error('Form submission error:', error);
                showError('An error occurred. Please try again.');
            } finally {
                // Hide loading state
                submitBtn.classList.remove('loading');
            }
        });
    }
    
    // Form validation
    function validateForm(data) {
        let isValid = true;
        
        // Clear previous errors
        clearErrors();
        
        // Validate required fields
        if (!data.category) {
            showFieldError('productCategory', 'Please select a product category');
            isValid = false;
        }
        
        if (!data.quantity || data.quantity < 1) {
            showFieldError('quantity', 'Please enter a valid quantity');
            isValid = false;
        }
        
        if (!data.unit) {
            showFieldError('unit', 'Please select a unit');
            isValid = false;
        }
        
        if (!data.deliveryDate) {
            showFieldError('deliveryDate', 'Please select a delivery date');
            isValid = false;
        }
        
        // Validate delivery date is in the future
        if (data.deliveryDate) {
            const deliveryDate = new Date(data.deliveryDate);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (deliveryDate <= today) {
                showFieldError('deliveryDate', 'Delivery date must be in the future');
                isValid = false;
            }
        }
        
        // Validate budget
        if (!data.budget || data.budget < 100) {
            showFieldError('budget', 'Budget must be at least $100');
            isValid = false;
        }
        
        return isValid;
    }
    
    // Error handling functions
    function showFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (field) {
            const formGroup = field.closest('.form-group');
            formGroup.classList.add('error');
            
            // Remove existing error message
            const existingError = formGroup.querySelector('.error-message');
            if (existingError) {
                existingError.remove();
            }
            
            // Add new error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = message;
            formGroup.appendChild(errorDiv);
        }
    }
    
    function clearErrors() {
        // Remove all error states
        document.querySelectorAll('.form-group.error').forEach(group => {
            group.classList.remove('error');
        });
        
        // Remove all error messages
        document.querySelectorAll('.error-message').forEach(error => {
            error.remove();
        });
    }
    
    function showSuccess(message) {
        // Create success notification
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    function showError(message) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ef4444;
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Real-time validation
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            const fieldData = { [this.name]: this.value };
            validateField(this.name, this.value);
        });
    });
    
    function validateField(fieldName, value) {
        // Clear previous error for this field
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            const formGroup = field.closest('.form-group');
            formGroup.classList.remove('error');
            const errorMessage = formGroup.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.remove();
            }
        }
        
        // Validate specific fields
        switch (fieldName) {
            case 'quantity':
                if (value && (isNaN(value) || value < 1)) {
                    showFieldError(fieldName, 'Quantity must be a positive number');
                }
                break;
            case 'deliveryDate':
                if (value) {
                    const deliveryDate = new Date(value);
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    
                    if (deliveryDate <= today) {
                        showFieldError(fieldName, 'Delivery date must be in the future');
                    }
                }
                break;
            case 'budget':
                if (value && (isNaN(value) || value < 100)) {
                    showFieldError(fieldName, 'Budget must be at least $100');
                }
                break;
        }
    }
}); 