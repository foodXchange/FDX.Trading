// FDX Trading Platform - Main JavaScript
// Following deployment guide standards

(function() {
    'use strict';
    
    // Error logging helper
    function logError(context, error) {
        console.error(`[FDX] ${context}:`, error);
    }
    
    // Initialize page when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        try {
            // Initialize all components
            initializeNavigation();
            initializeAnimations();
            initializeForms();
            initializeInteractiveElements();
            
            console.log('[FDX] Page initialized successfully');
            
        } catch (error) {
            logError('Page initialization', error);
        }
    });
    
    // Navigation functionality
    function initializeNavigation() {
        const navbar = document.querySelector('.navbar');
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('section');
        
        // Navbar scroll effect
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('shadow-sm');
                navbar.style.padding = '0.5rem 0';
            } else {
                navbar.classList.remove('shadow-sm');
                navbar.style.padding = '1rem 0';
            }
            
            // Active navigation highlighting
            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop - 100;
                const sectionHeight = section.clientHeight;
                if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                    current = section.getAttribute('id');
                }
            });
            
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${current}`) {
                    link.classList.add('active');
                }
            });
        });
        
        // Smooth scrolling
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                if (this.getAttribute('href').startsWith('#')) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetSection = document.getElementById(targetId);
                    if (targetSection) {
                        window.scrollTo({
                            top: targetSection.offsetTop - 80,
                            behavior: 'smooth'
                        });
                    }
                    document.querySelector('.navbar-collapse').classList.remove('show');
                }
            });
        });
    }
    
    // Animation functionality
    function initializeAnimations() {
        // Workflow steps animation
        const workflowSteps = document.querySelectorAll('.workflow-step');
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px'
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);
        
        workflowSteps.forEach(step => {
            observer.observe(step);
        });
        
        // Animated counters for statistics
        const statItems = document.querySelectorAll('.stat-item h3, .stat-card h4');
        const animateValue = (obj, start, end, duration) => {
            let startTimestamp = null;
            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                
                let currentValue = Math.floor(progress * (end - start) + start);
                let displayValue = currentValue;
                
                // Handle different formats
                if (obj.innerHTML.includes('%')) {
                    displayValue = currentValue + '%';
                } else if (obj.innerHTML.includes('€')) {
                    displayValue = '€' + currentValue.toLocaleString() + '+';
                } else if (obj.innerHTML.includes('+')) {
                    displayValue = currentValue + '+';
                } else {
                    displayValue = currentValue;
                }
                
                obj.innerHTML = displayValue;
                
                if (progress < 1) {
                    window.requestAnimationFrame(step);
                }
            };
            window.requestAnimationFrame(step);
        };
        
        const statObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
                    const text = entry.target.innerText;
                    let value = parseInt(text.replace(/[^\d]/g, ''));
                    
                    // Handle large numbers
                    if (text.includes('M') || text.includes('000')) {
                        value = Math.max(value, 2000000);
                    }
                    
                    animateValue(entry.target, 0, value, 2000);
                    entry.target.classList.add('animated');
                }
            });
        }, { threshold: 0.5 });
        
        statItems.forEach(item => {
            statObserver.observe(item);
        });
        
        // Fade-in animations for content sections
        const animatedElements = document.querySelectorAll(
            '.benefit-card, .problem-card, .ai-feature, .transformation-card'
        );
        
        const fadeInObserver = new IntersectionObserver(function(entries) {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, index * 100);
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(element => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            element.style.transition = 'all 0.6s ease';
            fadeInObserver.observe(element);
        });
    }
    
    // Interactive elements
    function initializeInteractiveElements() {
        // Dashboard animation
        const dashboardCards = document.querySelectorAll('.dashboard-card');
        dashboardCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 500 + (index * 200));
        });
        
        // AI brain neural network animation
        const neurons = document.querySelectorAll('.neuron');
        if (neurons.length > 0) {
            setInterval(() => {
                const randomNeuron = neurons[Math.floor(Math.random() * neurons.length)];
                randomNeuron.style.boxShadow = '0 0 30px rgba(255,255,255,0.8)';
                setTimeout(() => {
                    randomNeuron.style.boxShadow = '';
                }, 500);
            }, 1500);
        }
        
        // Progress bar animations
        const progressBars = document.querySelectorAll('.progress-fill');
        const progressObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'progress-animation 2s ease-in-out';
                }
            });
        }, { threshold: 0.5 });
        
        progressBars.forEach(bar => {
            progressObserver.observe(bar);
        });
        
        // Activity dots animation
        const activityDots = document.querySelectorAll('.activity-dot');
        activityDots.forEach((dot, index) => {
            setTimeout(() => {
                dot.style.animation = 'pulse 2s ease-in-out infinite';
            }, index * 500);
        });
        
        // Button hover effects
        const ctaButtons = document.querySelectorAll('.btn-primary');
        ctaButtons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.05)';
            });
            button.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        });
    }
    
    // Form handling
    function initializeForms() {
        // Demo form
        const demoForm = document.getElementById('demoForm');
        if (demoForm) {
            demoForm.addEventListener('submit', function(e) {
                e.preventDefault();
                handleFormSubmission(this, '/api/demo', 'Demo request submitted successfully!');
            });
        }
        
        // Contact form
        const contactForm = document.getElementById('contactForm');
        if (contactForm) {
            contactForm.addEventListener('submit', function(e) {
                e.preventDefault();
                handleFormSubmission(this, '/api/contact', 'Message sent successfully!');
            });
        }
    }
    
    // Form submission handler
    function handleFormSubmission(form, endpoint, successMessage) {
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        // Show loading state
        submitButton.disabled = true;
        submitButton.textContent = 'Sending...';
        
        fetch(endpoint, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showAlert('success', successMessage);
                form.reset();
                
                // Close modal if it exists
                const modal = form.closest('.modal');
                if (modal) {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
            } else {
                showAlert('error', data.message || 'An error occurred. Please try again.');
            }
        })
        .catch(error => {
            logError('Form submission', error);
            showAlert('error', 'An error occurred. Please try again.');
        })
        .finally(() => {
            // Restore button state
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        });
    }
    
    // Alert system
    function showAlert(type, message) {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
        alertContainer.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertContainer);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.remove();
            }
        }, 5000);
    }
    
    // Export for debugging in development
    if (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
        window.FDXTrading = {
            version: '1.0.0',
            initialized: true,
            logError: logError
        };
    }
    
})();