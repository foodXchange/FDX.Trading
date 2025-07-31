/**
 * Enhanced Profile Edit JavaScript
 * FoodXchange Platform - Profile Edit Optimization
 */

class ProfileEditManager {
    constructor() {
        this.form = document.getElementById('profileForm');
        this.formData = new FormData();
        this.autoSaveInterval = null;
        this.hasUnsavedChanges = false;
        this.profileCompletion = 0;
        this.requiredFields = ['name', 'email'];
        this.importantFields = ['job_title', 'industry', 'bio', 'country', 'city'];
        this.undoStack = [];
        this.redoStack = [];
        this.maxUndoSteps = 10;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeProfileCompletion();
        this.setupAutoSave();
        this.setupDragAndDrop();
        this.setupRealTimeValidation();
        this.setupCharacterCounters();
        this.setupSmartSuggestions();
        this.setupUnsavedChangesWarning();
        this.setupKeyboardNavigation();
        this.setupAccessibility();
        this.setupSpellCheck();
        this.setupProfessionalNetworkIntegration();
        this.setupAdvancedPrivacyControls();
    }

    setupEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        
        // Profile picture handling
        const profilePicture = document.getElementById('profilePicture');
        if (profilePicture) {
            profilePicture.addEventListener('change', (e) => this.handleProfilePictureUpload(e));
        }

        // Remove picture
        const removePicture = document.getElementById('removePicture');
        if (removePicture) {
            removePicture.addEventListener('click', () => this.handleRemovePicture());
        }

        // Preview profile
        const previewProfile = document.getElementById('previewProfile');
        if (previewProfile) {
            previewProfile.addEventListener('click', () => this.showProfilePreview());
        }

        // Save draft
        const saveDraft = document.getElementById('saveDraft');
        if (saveDraft) {
            saveDraft.addEventListener('click', () => this.saveDraft());
        }

        // Crop picture
        const cropPicture = document.getElementById('cropPicture');
        if (cropPicture) {
            cropPicture.addEventListener('click', () => this.showCropModal());
        }

        // Apply crop
        const applyCrop = document.getElementById('applyCrop');
        if (applyCrop) {
            applyCrop.addEventListener('click', () => this.applyCrop());
        }

        // Form field changes with undo/redo support
        this.form.addEventListener('input', (e) => {
            this.hasUnsavedChanges = true;
            this.updateProfileCompletion();
            this.addToUndoStack(e.target);
        });

        // Country change for timezone auto-detection
        const countrySelect = document.getElementById('country');
        if (countrySelect) {
            countrySelect.addEventListener('change', () => this.autoDetectTimezone());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    }

    setupKeyboardNavigation() {
        // Add keyboard navigation support
        const focusableElements = this.form.querySelectorAll(
            'input, select, textarea, button, [tabindex]:not([tabindex="-1"])'
        );

        focusableElements.forEach((element, index) => {
            element.setAttribute('tabindex', index + 1);
            
            // Add visual focus indicators
            element.addEventListener('focus', () => {
                element.classList.add('ring-2', 'ring-fx-blue', 'ring-opacity-50');
            });
            
            element.addEventListener('blur', () => {
                element.classList.remove('ring-2', 'ring-fx-blue', 'ring-opacity-50');
            });
        });
    }

    setupAccessibility() {
        // Add ARIA labels and descriptions
        const fields = {
            'name': 'Full name (required)',
            'email': 'Email address (required)',
            'phone': 'Phone number (optional)',
            'job_title': 'Job title or position',
            'bio': 'Professional bio or summary',
            'country': 'Country of residence',
            'city': 'City or town',
            'industry': 'Industry or sector',
            'company_size': 'Company size in employees',
            'website': 'Personal or company website',
            'linkedin': 'LinkedIn profile URL'
        };

        Object.entries(fields).forEach(([fieldName, description]) => {
            const field = document.getElementById(fieldName);
            if (field) {
                field.setAttribute('aria-describedby', `${fieldName}-help`);
                
                // Create help text element
                const helpText = document.createElement('div');
                helpText.id = `${fieldName}-help`;
                helpText.className = 'sr-only';
                helpText.textContent = description;
                
                field.parentNode.appendChild(helpText);
            }
        });

        // Add skip links for screen readers
        const skipLink = document.createElement('a');
        skipLink.href = '#profileForm';
        skipLink.className = 'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-fx-blue text-white px-4 py-2 rounded';
        skipLink.textContent = 'Skip to main content';
        document.body.insertBefore(skipLink, document.body.firstChild);
    }

    setupSpellCheck() {
        // Enable spell check for text fields
        const textFields = this.form.querySelectorAll('input[type="text"], textarea');
        textFields.forEach(field => {
            field.setAttribute('spellcheck', 'true');
            
            // Add spell check indicator
            field.addEventListener('input', () => {
                this.checkSpelling(field);
            });
        });
    }

    checkSpelling(field) {
        // Simple spell check implementation
        const words = field.value.split(' ');
        const misspelledWords = [];
        
        // This is a simplified spell check - in production, you'd use a proper spell check library
        const commonWords = [
            'food', 'beverage', 'industry', 'management', 'procurement', 'quality', 'assurance',
            'supply', 'chain', 'operations', 'director', 'manager', 'specialist', 'coordinator',
            'analyst', 'consultant', 'advisor', 'expert', 'professional', 'certified', 'licensed'
        ];
        
        words.forEach(word => {
            const cleanWord = word.replace(/[^\w]/g, '').toLowerCase();
            if (cleanWord.length > 3 && !commonWords.includes(cleanWord)) {
                // This is a simplified check - in reality, you'd use a proper dictionary
                misspelledWords.push(word);
            }
        });
        
        if (misspelledWords.length > 0) {
            this.showSpellCheckSuggestions(field, misspelledWords);
        }
    }

    showSpellCheckSuggestions(field, misspelledWords) {
        // Remove existing spell check indicators
        const existingIndicator = field.parentNode.querySelector('.spell-check-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }
        
        // Create spell check indicator
        const indicator = document.createElement('div');
        indicator.className = 'spell-check-indicator text-xs text-orange-600 mt-1';
        indicator.innerHTML = `
            <i class="fas fa-exclamation-triangle mr-1"></i>
            Possible spelling issues detected
        `;
        
        field.parentNode.appendChild(indicator);
    }

    setupProfessionalNetworkIntegration() {
        // Add professional network suggestions
        const industryField = document.getElementById('industry');
        if (industryField) {
            industryField.addEventListener('change', () => {
                this.suggestProfessionalConnections();
            });
        }
    }

    suggestProfessionalConnections() {
        const industry = document.getElementById('industry').value;
        const location = document.getElementById('city').value;
        
        if (industry && location) {
            // Create professional network suggestions
            const suggestions = this.generateNetworkSuggestions(industry, location);
            this.showNetworkSuggestions(suggestions);
        }
    }

    generateNetworkSuggestions(industry, location) {
        const suggestions = {
            'Food & Beverage': [
                'Food Safety Professionals Network',
                'Beverage Industry Association',
                'Food Quality Assurance Group'
            ],
            'Agriculture': [
                'Agricultural Supply Chain Network',
                'Sustainable Farming Professionals',
                'Crop Management Specialists'
            ],
            'Hospitality': [
                'Hospitality Procurement Network',
                'Restaurant Management Professionals',
                'Food Service Directors Group'
            ]
        };
        
        return suggestions[industry] || [];
    }

    showNetworkSuggestions(suggestions) {
        // Remove existing suggestions
        const existingSuggestions = document.querySelector('.network-suggestions');
        if (existingSuggestions) {
            existingSuggestions.remove();
        }
        
        if (suggestions.length > 0) {
            const suggestionsContainer = document.createElement('div');
            suggestionsContainer.className = 'network-suggestions bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4';
            suggestionsContainer.innerHTML = `
                <h4 class="font-semibold text-blue-900 mb-2">
                    <i class="fas fa-network-wired mr-2"></i>
                    Suggested Professional Networks
                </h4>
                <ul class="space-y-2">
                    ${suggestions.map(suggestion => `
                        <li class="text-sm text-blue-800">
                            <i class="fas fa-users mr-2"></i>
                            ${suggestion}
                        </li>
                    `).join('')}
                </ul>
            `;
            
            // Insert after the industry field
            const industryField = document.getElementById('industry');
            industryField.parentNode.appendChild(suggestionsContainer);
        }
    }

    setupAdvancedPrivacyControls() {
        // Add granular privacy controls
        const privacyFields = ['profile_visibility', 'contact_visibility'];
        
        privacyFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field) {
                field.addEventListener('change', () => {
                    this.updatePrivacyPreview();
                });
            }
        });
    }

    updatePrivacyPreview() {
        const profileVisibility = document.getElementById('profile_visibility').value;
        const contactVisibility = document.getElementById('contact_visibility').value;
        
        // Create privacy preview
        const preview = this.generatePrivacyPreview(profileVisibility, contactVisibility);
        this.showPrivacyPreview(preview);
    }

    generatePrivacyPreview(profileVisibility, contactVisibility) {
        const previews = {
            'public': 'Your profile will be visible to all users',
            'network': 'Your profile will only be visible to your connections',
            'private': 'Your profile will only be visible to you'
        };
        
        return {
            profile: previews[profileVisibility] || 'Profile visibility not set',
            contact: contactVisibility === 'public' ? 'Contact information will be visible to all users' :
                    contactVisibility === 'network' ? 'Contact information will only be visible to your connections' :
                    'Contact information will be private'
        };
    }

    showPrivacyPreview(preview) {
        // Remove existing preview
        const existingPreview = document.querySelector('.privacy-preview');
        if (existingPreview) {
            existingPreview.remove();
        }
        
        // Create privacy preview
        const previewContainer = document.createElement('div');
        previewContainer.className = 'privacy-preview bg-gray-50 border border-gray-200 rounded-lg p-4 mt-4';
        previewContainer.innerHTML = `
            <h4 class="font-semibold text-gray-900 mb-2">
                <i class="fas fa-eye mr-2"></i>
                Privacy Preview
            </h4>
            <div class="space-y-2 text-sm text-gray-700">
                <p><strong>Profile:</strong> ${preview.profile}</p>
                <p><strong>Contact:</strong> ${preview.contact}</p>
            </div>
        `;
        
        // Insert after privacy settings
        const privacySection = document.querySelector('.bg-white.dark\\:bg-gray-800.rounded-xl.shadow-lg.p-6:last-child');
        if (privacySection) {
            privacySection.appendChild(previewContainer);
        }
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + S to save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            this.saveDraft();
        }
        
        // Ctrl/Cmd + Z to undo
        if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
            e.preventDefault();
            this.undo();
        }
        
        // Ctrl/Cmd + Shift + Z to redo
        if ((e.ctrlKey || e.metaKey) && e.key === 'z' && e.shiftKey) {
            e.preventDefault();
            this.redo();
        }
        
        // Escape to cancel
        if (e.key === 'Escape') {
            this.showCancelConfirmation();
        }
    }

    addToUndoStack(field) {
        const fieldData = {
            field: field,
            value: field.value,
            timestamp: Date.now()
        };
        
        this.undoStack.push(fieldData);
        
        // Limit undo stack size
        if (this.undoStack.length > this.maxUndoSteps) {
            this.undoStack.shift();
        }
        
        // Clear redo stack when new action is performed
        this.redoStack = [];
    }

    undo() {
        if (this.undoStack.length > 0) {
            const lastAction = this.undoStack.pop();
            const currentValue = lastAction.field.value;
            
            // Store current state for redo
            this.redoStack.push({
                field: lastAction.field,
                value: currentValue,
                timestamp: Date.now()
            });
            
            // Restore previous value
            lastAction.field.value = lastAction.value;
            lastAction.field.dispatchEvent(new Event('input'));
            
            this.showNotification('Undo completed', 'info');
        }
    }

    redo() {
        if (this.redoStack.length > 0) {
            const nextAction = this.redoStack.pop();
            const currentValue = nextAction.field.value;
            
            // Store current state for undo
            this.undoStack.push({
                field: nextAction.field,
                value: currentValue,
                timestamp: Date.now()
            });
            
            // Restore next value
            nextAction.field.value = nextAction.value;
            nextAction.field.dispatchEvent(new Event('input'));
            
            this.showNotification('Redo completed', 'info');
        }
    }

    showCancelConfirmation() {
        if (this.hasUnsavedChanges) {
            if (confirm('You have unsaved changes. Are you sure you want to cancel?')) {
                window.location.href = '/profile/';
            }
        } else {
            window.location.href = '/profile/';
        }
    }

    setupDragAndDrop() {
        const dragDropArea = document.getElementById('dragDropArea');
        const profileImageContainer = document.getElementById('profileImageContainer');

        if (dragDropArea) {
            dragDropArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                dragDropArea.classList.add('border-fx-blue', 'bg-blue-50');
            });

            dragDropArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                dragDropArea.classList.remove('border-fx-blue', 'bg-blue-50');
            });

            dragDropArea.addEventListener('drop', (e) => {
                e.preventDefault();
                dragDropArea.classList.remove('border-fx-blue', 'bg-blue-50');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileUpload(files[0]);
                }
            });
        }

        if (profileImageContainer) {
            profileImageContainer.addEventListener('click', () => {
                document.getElementById('profilePicture').click();
            });
        }
    }

    setupRealTimeValidation() {
        const fields = {
            email: {
                validate: (value) => this.validateEmail(value),
                message: 'Please enter a valid email address'
            },
            phone: {
                validate: (value) => this.validatePhone(value),
                message: 'Please enter a valid phone number'
            },
            website: {
                validate: (value) => this.validateUrl(value),
                message: 'Please enter a valid website URL'
            },
            linkedin: {
                validate: (value) => this.validateLinkedIn(value),
                message: 'Please enter a valid LinkedIn profile URL'
            }
        };

        Object.entries(fields).forEach(([fieldName, config]) => {
            const field = document.getElementById(fieldName);
            if (field) {
                field.addEventListener('blur', () => {
                    this.validateField(field, config.validate, config.message);
                });
                field.addEventListener('input', () => {
                    this.clearFieldValidation(field);
                });
            }
        });
    }

    setupCharacterCounters() {
        const bioField = document.getElementById('bio');
        const bioCharCount = document.getElementById('bioCharCount');
        
        if (bioField && bioCharCount) {
            bioField.addEventListener('input', () => {
                const length = bioField.value.length;
                const maxLength = bioField.maxLength;
                bioCharCount.textContent = `${length}/${maxLength}`;
                
                if (length > maxLength * 0.9) {
                    bioCharCount.classList.add('text-orange-500');
                } else {
                    bioCharCount.classList.remove('text-orange-500');
                }
            });
            
            // Initialize counter
            bioField.dispatchEvent(new Event('input'));
        }
    }

    setupSmartSuggestions() {
        // Job title suggestions
        const jobTitleField = document.getElementById('job_title');
        if (jobTitleField) {
            jobTitleField.addEventListener('input', () => {
                this.suggestJobTitles(jobTitleField.value);
            });
        }

        // LinkedIn URL auto-formatting
        const linkedinField = document.getElementById('linkedin');
        if (linkedinField) {
            linkedinField.addEventListener('blur', () => {
                this.formatLinkedInUrl(linkedinField);
            });
        }

        // Phone number formatting
        const phoneField = document.getElementById('phone');
        if (phoneField) {
            phoneField.addEventListener('input', () => {
                this.formatPhoneNumber(phoneField);
            });
        }
    }

    setupAutoSave() {
        this.autoSaveInterval = setInterval(() => {
            if (this.hasUnsavedChanges) {
                this.saveDraft(true); // Silent save
            }
        }, 30000); // Auto-save every 30 seconds
    }

    setupUnsavedChangesWarning() {
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    }

    initializeProfileCompletion() {
        this.updateProfileCompletion();
    }

    updateProfileCompletion() {
        let completedFields = 0;
        let totalFields = this.requiredFields.length + this.importantFields.length;

        // Check required fields
        this.requiredFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field && field.value.trim()) {
                completedFields++;
            }
        });

        // Check important fields
        this.importantFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field && field.value.trim()) {
                completedFields++;
            }
        });

        // Check profile picture
        const profilePreview = document.getElementById('profilePreview');
        if (profilePreview && !profilePreview.classList.contains('hidden')) {
            completedFields++;
            totalFields++;
        }

        this.profileCompletion = Math.round((completedFields / totalFields) * 100);
        this.updateCompletionUI();
    }

    updateCompletionUI() {
        const percentageElement = document.getElementById('completionPercentage');
        const barElement = document.getElementById('completionBar');
        const tipsElement = document.getElementById('completionTips');

        if (percentageElement) {
            percentageElement.textContent = `${this.profileCompletion}%`;
        }

        if (barElement) {
            barElement.style.width = `${this.profileCompletion}%`;
        }

        if (tipsElement) {
            this.updateCompletionTips(tipsElement);
        }
    }

    updateCompletionTips(tipsElement) {
        const missingFields = [];
        
        if (!document.getElementById('name').value.trim()) missingFields.push('full name');
        if (!document.getElementById('email').value.trim()) missingFields.push('email');
        if (!document.getElementById('job_title').value.trim()) missingFields.push('job title');
        if (!document.getElementById('industry').value.trim()) missingFields.push('industry');
        if (!document.getElementById('bio').value.trim()) missingFields.push('professional bio');
        if (!document.getElementById('country').value.trim()) missingFields.push('country');

        if (missingFields.length > 0) {
            tipsElement.innerHTML = `
                <i class="fas fa-lightbulb mr-2"></i>
                <span>Add your ${missingFields.slice(0, 2).join(' and ')} to improve your profile visibility</span>
            `;
        } else {
            tipsElement.innerHTML = `
                <i class="fas fa-check-circle mr-2 text-green-500"></i>
                <span>Great! Your profile is complete and optimized for networking</span>
            `;
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (!this.validateForm()) {
            showNotification('Please fix the validation errors before saving', 'error');
            return;
        }

        const submitButton = document.getElementById('saveChanges');
        const originalText = submitButton.innerHTML;
        
        try {
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Saving...';
            submitButton.disabled = true;

            const formData = new FormData(this.form);
            
            const response = await fetch('/profile/update', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.hasUnsavedChanges = false;
                showNotification('Profile updated successfully!', 'success');
                setTimeout(() => window.location.href = '/profile/', 1500);
            } else {
                showNotification(result.message || 'Error updating profile', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error updating profile', 'error');
        } finally {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }
    }

    async handleProfilePictureUpload(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        await this.handleFileUpload(file);
    }

    async handleFileUpload(file) {
        // Validate file
        if (!this.validateImageFile(file)) {
            return;
        }

        // Show preview
        this.showImagePreview(file);
        
        // Show upload progress
        this.showUploadProgress();
        
        // Upload file
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/profile/upload-picture', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.hideUploadProgress();
                showNotification('Profile picture updated!', 'success');
                this.updateProfileCompletion();
            } else {
                this.hideUploadProgress();
                showNotification(result.message || 'Error uploading picture', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.hideUploadProgress();
            showNotification('Error uploading picture', 'error');
        }
    }

    validateImageFile(file) {
        const maxSize = 5 * 1024 * 1024; // 5MB
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        
        if (!allowedTypes.includes(file.type)) {
            showNotification('Please select a valid image file (JPEG, PNG, GIF, or WebP)', 'error');
            return false;
        }
        
        if (file.size > maxSize) {
            showNotification('Image file size must be less than 5MB', 'error');
            return false;
        }
        
        return true;
    }

    showImagePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('profilePreview');
            const initial = document.getElementById('profileInitial');
            const cropButton = document.getElementById('cropPicture');
            
            preview.src = e.target.result;
            preview.classList.remove('hidden');
            
            if (initial) {
                initial.classList.add('hidden');
            }
            
            if (cropButton) {
                cropButton.classList.remove('hidden');
            }
        };
        reader.readAsDataURL(file);
    }

    showUploadProgress() {
        const progressContainer = document.getElementById('uploadProgress');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (progressContainer) {
            progressContainer.classList.remove('hidden');
        }
        
        // Simulate progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress > 90) progress = 90;
            
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
            
            if (progressText) {
                progressText.textContent = `Uploading... ${Math.round(progress)}%`;
            }
        }, 200);
        
        this.progressInterval = interval;
    }

    hideUploadProgress() {
        const progressContainer = document.getElementById('uploadProgress');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        if (progressBar) {
            progressBar.style.width = '100%';
        }
        
        if (progressText) {
            progressText.textContent = 'Upload complete!';
        }
        
        setTimeout(() => {
            if (progressContainer) {
                progressContainer.classList.add('hidden');
            }
        }, 1000);
    }

    async handleRemovePicture() {
        if (!confirm('Are you sure you want to remove your profile picture?')) {
            return;
        }
        
        try {
            const response = await fetch('/profile/remove-picture', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                showNotification('Profile picture removed!', 'success');
                location.reload();
            } else {
                showNotification(result.message || 'Error removing picture', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error removing picture', 'error');
        }
    }

    showProfilePreview() {
        const modal = new bootstrap.Modal(document.getElementById('previewModal'));
        const content = document.getElementById('profilePreviewContent');
        
        // Generate preview HTML
        const previewHTML = this.generateProfilePreview();
        content.innerHTML = previewHTML;
        
        modal.show();
    }

    generateProfilePreview() {
        const name = document.getElementById('name').value || 'Your Name';
        const jobTitle = document.getElementById('job_title').value || 'Job Title';
        const industry = document.getElementById('industry').value || 'Industry';
        const bio = document.getElementById('bio').value || 'No bio provided';
        const country = document.getElementById('country').value || 'Country';
        const city = document.getElementById('city').value || 'City';
        
        return `
            <div class="bg-white rounded-lg p-6">
                <div class="flex items-center space-x-4 mb-4">
                    <div class="w-16 h-16 bg-gradient-to-br from-fx-blue to-blue-600 rounded-full flex items-center justify-center text-white text-xl font-bold">
                        ${name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h3 class="text-xl font-semibold text-gray-900">${name}</h3>
                        <p class="text-gray-600">${jobTitle}</p>
                        <p class="text-sm text-gray-500">${industry} • ${city}, ${country}</p>
                    </div>
                </div>
                <div class="border-t pt-4">
                    <h4 class="font-medium text-gray-900 mb-2">About</h4>
                    <p class="text-gray-600">${bio}</p>
                </div>
            </div>
        `;
    }

    async saveDraft(silent = false) {
        try {
            const formData = new FormData(this.form);
            formData.append('draft', 'true');
            
            const response = await fetch('/profile/save-draft', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success && !silent) {
                showNotification('Draft saved successfully!', 'success');
                this.hasUnsavedChanges = false;
            }
        } catch (error) {
            console.error('Error saving draft:', error);
            if (!silent) {
                showNotification('Error saving draft', 'error');
            }
        }
    }

    showCropModal() {
        const modal = new bootstrap.Modal(document.getElementById('cropModal'));
        const container = document.getElementById('cropContainer');
        
        // Simple crop interface (in a real implementation, you'd use a library like Cropper.js)
        container.innerHTML = `
            <div class="text-center">
                <p class="text-gray-600 mb-4">Crop functionality would be implemented here</p>
                <div class="w-64 h-64 mx-auto bg-gray-200 rounded-lg flex items-center justify-center">
                    <i class="fas fa-crop text-4xl text-gray-400"></i>
                </div>
            </div>
        `;
        
        modal.show();
    }

    applyCrop() {
        // In a real implementation, this would apply the crop
        showNotification('Crop applied successfully!', 'success');
        bootstrap.Modal.getInstance(document.getElementById('cropModal')).hide();
    }

    validateForm() {
        let isValid = true;
        
        // Validate required fields
        this.requiredFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field && !field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            }
        });
        
        return isValid;
    }

    validateField(field, validator, message) {
        const value = field.value.trim();
        if (value && !validator(value)) {
            this.showFieldError(field, message);
            return false;
        }
        return true;
    }

    showFieldError(field, message) {
        const validationMessage = field.parentNode.querySelector('.validation-message');
        if (validationMessage) {
            validationMessage.textContent = message;
            validationMessage.classList.add('text-red-500');
        }
        field.classList.add('border-red-500');
    }

    clearFieldValidation(field) {
        const validationMessage = field.parentNode.querySelector('.validation-message');
        if (validationMessage) {
            validationMessage.textContent = '';
            validationMessage.classList.remove('text-red-500');
        }
        field.classList.remove('border-red-500');
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    validatePhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
    }

    validateUrl(url) {
        if (!url) return true;
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    validateLinkedIn(url) {
        if (!url) return true;
        return url.includes('linkedin.com/in/');
    }

    suggestJobTitles(query) {
        // In a real implementation, this would fetch suggestions from an API
        const suggestions = [
            'Food Safety Manager',
            'Procurement Specialist',
            'Quality Assurance Manager',
            'Supply Chain Manager',
            'Operations Director',
            'Executive Chef',
            'Restaurant Manager',
            'Food Service Director'
        ];
        
        // Filter suggestions based on query
        const filtered = suggestions.filter(title => 
            title.toLowerCase().includes(query.toLowerCase())
        );
        
        // Update datalist
        const datalist = document.getElementById('jobTitles');
        if (datalist) {
            datalist.innerHTML = filtered.map(title => 
                `<option value="${title}">`
            ).join('');
        }
    }

    formatLinkedInUrl(field) {
        let value = field.value.trim();
        if (!value) return;
        
        if (!value.startsWith('http')) {
            value = 'https://' + value;
        }
        
        if (!value.includes('linkedin.com/in/')) {
            value = value.replace('linkedin.com', 'linkedin.com/in/');
        }
        
        field.value = value;
    }

    formatPhoneNumber(field) {
        let value = field.value.replace(/\D/g, '');
        
        if (value.length > 0) {
            if (value.length <= 3) {
                value = `(${value}`;
            } else if (value.length <= 6) {
                value = `(${value.slice(0, 3)}) ${value.slice(3)}`;
            } else {
                value = `(${value.slice(0, 3)}) ${value.slice(3, 6)}-${value.slice(6, 10)}`;
            }
        }
        
        field.value = value;
    }

    autoDetectTimezone() {
        const country = document.getElementById('country').value;
        const timezoneField = document.getElementById('timezone');
        
        if (!timezoneField) return;
        
        const timezoneMap = {
            'United States': 'America/New_York',
            'Canada': 'America/Toronto',
            'United Kingdom': 'Europe/London',
            'Germany': 'Europe/Berlin',
            'France': 'Europe/Paris',
            'Spain': 'Europe/Madrid',
            'Italy': 'Europe/Rome',
            'Australia': 'Australia/Sydney',
            'Japan': 'Asia/Tokyo',
            'China': 'Asia/Shanghai',
            'India': 'Asia/Kolkata',
            'Brazil': 'America/Sao_Paulo',
            'Mexico': 'America/Mexico_City'
        };
        
        if (timezoneMap[country]) {
            timezoneField.value = timezoneMap[country];
        }
    }
}

// Initialize the profile edit manager when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProfileEditManager();
});

// Global notification function (if not already defined)
if (typeof showNotification === 'undefined') {
    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
} 