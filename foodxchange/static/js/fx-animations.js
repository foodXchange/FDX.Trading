// FoodXchange GSAP Animations - Safe Version
// This version checks for elements before animating to prevent console errors

// Wait for DOM and GSAP to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if GSAP is loaded
    if (typeof gsap === 'undefined') {
        console.warn('GSAP not loaded');
        return;
    }
    
    // Register plugins if available
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
    }
    
    console.log('✅ FoodXchange animations loading...');
    
    // Only animate elements that exist on the current page
    
    // Hero animations
    if (document.querySelector('.hero-title')) {
        gsap.from('.hero-title', {
            y: 50,
            opacity: 0,
            duration: 1,
            ease: "power3.out"
        });
    }
    
    if (document.querySelector('.hero-subtitle')) {
        gsap.from('.hero-subtitle', {
            y: 30,
            opacity: 0,
            duration: 0.8,
            delay: 0.3,
            ease: "power2.out"
        });
    }
    
    if (document.querySelector('.hero-cta')) {
        gsap.from('.hero-cta', {
            scale: 0.8,
            opacity: 0,
            duration: 0.6,
            delay: 0.6,
            ease: "back.out(1.7)"
        });
    }
    
    // Feature cards on scroll
    if (document.querySelector('.feature-card')) {
        gsap.utils.toArray('.feature-card').forEach((card, i) => {
            gsap.from(card, {
                scrollTrigger: {
                    trigger: card,
                    start: "top 85%",
                    once: true
                },
                y: 50,
                opacity: 0,
                duration: 0.8,
                delay: i * 0.1,
                ease: "power2.out"
            });
        });
    }
    
    // Fade in elements
    if (document.querySelector('.fade-in')) {
        gsap.utils.toArray('.fade-in').forEach(element => {
            gsap.from(element, {
                scrollTrigger: {
                    trigger: element,
                    start: "top 85%",
                    once: true
                },
                y: 30,
                opacity: 0,
                duration: 0.8,
                ease: "power2.out"
            });
        });
    }
    
    // Stat counters
    if (document.querySelector('.stat-number')) {
        gsap.utils.toArray('.stat-number').forEach(stat => {
            const target = parseInt(stat.dataset.target || stat.textContent);
            gsap.from(stat, {
                scrollTrigger: {
                    trigger: stat,
                    start: "top 80%",
                    once: true
                },
                textContent: 0,
                duration: 2,
                ease: "power1.out",
                snap: { textContent: 1 },
                onUpdate: function() {
                    stat.textContent = Math.ceil(this.targets()[0].textContent).toLocaleString();
                }
            });
        });
    }
    
    // Workflow steps
    if (document.querySelector('.workflow-step')) {
        gsap.from('.workflow-step', {
            scrollTrigger: {
                trigger: '.workflow-step',
                start: "top 80%",
                once: true
            },
            x: -50,
            opacity: 0,
            duration: 0.8,
            stagger: 0.2,
            ease: "power2.out"
        });
    }
    
    // Card hover effects
    document.querySelectorAll('.feature-card, .card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, {
                y: -5,
                boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
                duration: 0.3
            });
        });
        
        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                y: 0,
                boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
                duration: 0.3
            });
        });
    });
    
    // Button animations
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function() {
            gsap.to(this, {
                scale: 0.95,
                duration: 0.1,
                yoyo: true,
                repeat: 1
            });
        });
    });
    
    console.log('✅ Animations initialized for:', window.location.pathname);
});

// Export utility functions
window.foodXchangeAnimations = {
    // Simple loading animation
    showLoading: function(button) {
        const originalHTML = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        
        return function() {
            button.disabled = false;
            button.innerHTML = originalHTML;
        };
    },
    
    // Show notification
    showNotification: function(type, message) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
        notification.style.zIndex = '9999';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        gsap.from(notification, {
            x: 100,
            opacity: 0,
            duration: 0.5,
            ease: "back.out(1.7)"
        });
        
        setTimeout(() => {
            gsap.to(notification, {
                x: 100,
                opacity: 0,
                duration: 0.5,
                onComplete: () => notification.remove()
            });
        }, 3000);
    },
    
    // Animate button with options
    animateButton: function(button, options = {}) {
        const originalHTML = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${options.loadingText || 'Loading...'}`;
        
        setTimeout(() => {
            if (options.successText) {
                button.innerHTML = options.successText;
                button.classList.add('btn-success');
                setTimeout(() => {
                    button.innerHTML = originalHTML;
                    button.classList.remove('btn-success');
                    button.disabled = false;
                }, 1500);
            } else {
                button.innerHTML = originalHTML;
                button.disabled = false;
            }
        }, 2000);
    }
};