// FDX University - Interactive Tutorial System
class FDXTutorial {
    constructor() {
        this.currentStep = 0;
        this.isActive = false;
        this.tutorials = {
            'create-request': {
                title: 'Creating Your First Request',
                steps: [
                    {
                        element: '#navRequests',
                        title: 'Navigate to Requests',
                        content: 'Click on the Requests menu to see all your procurement requests.',
                        position: 'bottom'
                    },
                    {
                        element: '.btn-create-request',
                        title: 'Start New Request',
                        content: 'Click this button to create a new procurement request.',
                        position: 'bottom'
                    },
                    {
                        element: '#requestTitle',
                        title: 'Add Request Title',
                        content: 'Enter a clear, descriptive title for your request.',
                        position: 'right',
                        action: 'input'
                    },
                    {
                        element: '#requestDescription',
                        title: 'Describe Your Needs',
                        content: 'Provide detailed information about what you need.',
                        position: 'right',
                        action: 'input'
                    },
                    {
                        element: '.add-item-btn',
                        title: 'Add Items',
                        content: 'Click here to add products to your request.',
                        position: 'left'
                    },
                    {
                        element: '.save-request-btn',
                        title: 'Save Your Request',
                        content: 'Click Save to publish your request to suppliers.',
                        position: 'top'
                    }
                ]
            },
            'manage-console': {
                title: 'Managing Your Console Workflow',
                steps: [
                    {
                        element: '.console-card',
                        title: 'Understanding Consoles',
                        content: 'Each console represents a complete procurement workflow.',
                        position: 'bottom'
                    },
                    {
                        element: '.stage-item.active',
                        title: 'Current Stage',
                        content: 'This is your current active stage. You need to complete it to progress.',
                        position: 'right'
                    },
                    {
                        element: '.btn-start-stage',
                        title: 'Start Working',
                        content: 'Click here to begin working on this stage.',
                        position: 'bottom'
                    },
                    {
                        element: '.btn-complete-stage',
                        title: 'Complete Stage',
                        content: 'Once done, mark the stage as complete to move forward.',
                        position: 'bottom'
                    },
                    {
                        element: '#messagesList',
                        title: 'Communication',
                        content: 'Use messages to communicate with all participants.',
                        position: 'top'
                    }
                ]
            },
            'supplier-products': {
                title: 'Managing Your Product Catalog',
                steps: [
                    {
                        element: '#navProducts',
                        title: 'Products Section',
                        content: 'Access your product catalog from here.',
                        position: 'bottom'
                    },
                    {
                        element: '.btn-add-product',
                        title: 'Add New Product',
                        content: 'Click to add a new product to your catalog.',
                        position: 'bottom'
                    },
                    {
                        element: '#productName',
                        title: 'Product Details',
                        content: 'Enter complete product information for better visibility.',
                        position: 'right'
                    },
                    {
                        element: '#pricing-section',
                        title: 'Set Pricing',
                        content: 'Add competitive pricing for units and cartons.',
                        position: 'left'
                    },
                    {
                        element: '#kosher-certification',
                        title: 'Certifications',
                        content: 'Add any relevant certifications like Kosher, Organic, etc.',
                        position: 'right'
                    }
                ]
            }
        };
        this.overlay = null;
        this.tooltip = null;
    }

    start(tutorialId) {
        if (!this.tutorials[tutorialId]) {
            console.error('Tutorial not found:', tutorialId);
            return;
        }
        
        this.currentTutorial = this.tutorials[tutorialId];
        this.currentStep = 0;
        this.isActive = true;
        
        this.createOverlay();
        this.showStep();
        this.trackProgress(tutorialId, 'started');
    }

    showStep() {
        if (!this.isActive || this.currentStep >= this.currentTutorial.steps.length) {
            this.complete();
            return;
        }

        const step = this.currentTutorial.steps[this.currentStep];
        const element = document.querySelector(step.element);
        
        if (!element) {
            console.warn('Element not found:', step.element);
            this.nextStep();
            return;
        }

        this.highlightElement(element);
        this.showTooltip(element, step);
    }

    highlightElement(element) {
        // Remove previous highlight
        document.querySelectorAll('.tutorial-highlight').forEach(el => {
            el.classList.remove('tutorial-highlight');
        });
        
        // Add highlight class
        element.classList.add('tutorial-highlight');
        
        // Scroll into view
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    showTooltip(element, step) {
        // Remove existing tooltip
        if (this.tooltip) {
            this.tooltip.remove();
        }

        // Create tooltip
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'tutorial-tooltip';
        this.tooltip.innerHTML = `
            <div class="tutorial-tooltip-header">
                <span class="tutorial-step-number">Step ${this.currentStep + 1} of ${this.currentTutorial.steps.length}</span>
                <button class="tutorial-close" onclick="fdxTutorial.stop()">×</button>
            </div>
            <div class="tutorial-tooltip-content">
                <h3>${step.title}</h3>
                <p>${step.content}</p>
            </div>
            <div class="tutorial-tooltip-footer">
                ${this.currentStep > 0 ? '<button class="tutorial-btn-prev" onclick="fdxTutorial.previousStep()">Previous</button>' : ''}
                <button class="tutorial-btn-next" onclick="fdxTutorial.nextStep()">
                    ${this.currentStep < this.currentTutorial.steps.length - 1 ? 'Next' : 'Complete'}
                </button>
            </div>
        `;

        document.body.appendChild(this.tooltip);
        this.positionTooltip(element, step.position);
    }

    positionTooltip(element, position) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = this.tooltip.getBoundingClientRect();
        
        let top, left;
        
        switch(position) {
            case 'top':
                top = rect.top - tooltipRect.height - 10;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'bottom':
                top = rect.bottom + 10;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'left':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.left - tooltipRect.width - 10;
                break;
            case 'right':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.right + 10;
                break;
            default:
                top = rect.bottom + 10;
                left = rect.left;
        }
        
        // Ensure tooltip stays within viewport
        top = Math.max(10, Math.min(top, window.innerHeight - tooltipRect.height - 10));
        left = Math.max(10, Math.min(left, window.innerWidth - tooltipRect.width - 10));
        
        this.tooltip.style.top = top + 'px';
        this.tooltip.style.left = left + 'px';
    }

    nextStep() {
        this.currentStep++;
        this.showStep();
    }

    previousStep() {
        this.currentStep--;
        this.showStep();
    }

    complete() {
        const tutorialId = Object.keys(this.tutorials).find(
            key => this.tutorials[key] === this.currentTutorial
        );
        this.trackProgress(tutorialId, 'completed');
        this.stop();
        this.showCompletionMessage();
    }

    stop() {
        this.isActive = false;
        
        // Remove overlay
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
        
        // Remove tooltip
        if (this.tooltip) {
            this.tooltip.remove();
            this.tooltip = null;
        }
        
        // Remove highlights
        document.querySelectorAll('.tutorial-highlight').forEach(el => {
            el.classList.remove('tutorial-highlight');
        });
    }

    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'tutorial-overlay';
        document.body.appendChild(this.overlay);
    }

    showCompletionMessage() {
        const message = document.createElement('div');
        message.className = 'tutorial-completion';
        message.innerHTML = `
            <div class="completion-content">
                <h2>🎉 Tutorial Complete!</h2>
                <p>Great job! You've completed "${this.currentTutorial.title}"</p>
                <button onclick="this.parentElement.parentElement.remove()">Continue</button>
            </div>
        `;
        document.body.appendChild(message);
        
        setTimeout(() => {
            if (message.parentElement) {
                message.remove();
            }
        }, 5000);
    }

    trackProgress(tutorialId, status) {
        // Save progress to localStorage
        const progress = JSON.parse(localStorage.getItem('fdx_tutorial_progress') || '{}');
        progress[tutorialId] = {
            status: status,
            timestamp: new Date().toISOString(),
            steps_completed: this.currentStep + 1
        };
        localStorage.setItem('fdx_tutorial_progress', JSON.stringify(progress));
        
        // Send to server if needed
        if (window.currentUser) {
            fetch('/api/university/progress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userId: window.currentUser.id,
                    tutorialId: tutorialId,
                    status: status,
                    progress: (this.currentStep + 1) / this.currentTutorial.steps.length * 100
                })
            }).catch(console.error);
        }
    }

    getUserProgress() {
        return JSON.parse(localStorage.getItem('fdx_tutorial_progress') || '{}');
    }

    resetProgress() {
        localStorage.removeItem('fdx_tutorial_progress');
    }
}

// Initialize global instance
const fdxTutorial = new FDXTutorial();

// Auto-start tutorial for new users
document.addEventListener('DOMContentLoaded', () => {
    const progress = fdxTutorial.getUserProgress();
    const isNewUser = Object.keys(progress).length === 0;
    
    if (isNewUser && window.location.pathname === '/requests.html') {
        // Offer tutorial to new users
        setTimeout(() => {
            if (confirm('Welcome to FDX Trading! Would you like a quick tutorial on creating your first request?')) {
                fdxTutorial.start('create-request');
            }
        }, 1000);
    }
});