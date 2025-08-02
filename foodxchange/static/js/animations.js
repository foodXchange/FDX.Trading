// FoodXchange GSAP Animations - Safe Loading Version
// This file handles all GSAP animations with proper element checks

(function() {
    'use strict';
    
    // Configuration
    const config = {
        debug: false,
        animationsEnabled: true,
        scrollTriggerDefaults: {
            start: "top 85%",
            once: true
        }
    };
    
    // Safe console logging
    const log = (...args) => {
        if (config.debug) console.log('[FX Animations]', ...args);
    };
    
    // Check if element exists before animating
    const safeAnimate = (selector, animationFunc) => {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
            animationFunc(elements);
            return true;
        }
        return false;
    };
    
    // Initialize GSAP and plugins
    function initializeGSAP() {
        if (typeof gsap === 'undefined') {
            log('GSAP not loaded, retrying...');
            setTimeout(initializeGSAP, 100);
            return;
        }
        
        // Register plugins if available
        if (typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);
            log('ScrollTrigger registered');
        }
        
        if (typeof ScrollToPlugin !== 'undefined') {
            gsap.registerPlugin(ScrollToPlugin);
            log('ScrollToPlugin registered');
        }
        
        log('GSAP initialized successfully');
        initializeAnimations();
    }
    
    // Initialize all animations
    function initializeAnimations() {
        if (!config.animationsEnabled) return;
        
        log('Initializing animations for path:', window.location.pathname);
        
        // Page load animations
        animatePageLoad();
        
        // Component-specific animations
        animateHero();
        animateFeatureCards();
        animateWorkflow();
        animateStatistics();
        animatePricing();
        animateFooter();
        
        // Interactive animations
        setupFormAnimations();
        setupScrollAnimations();
        setupHoverEffects();
        
        log('All animations initialized');
    }
    
    // Page load animations
    function animatePageLoad() {
        // Fade in main content
        safeAnimate('main, .main-content', (elements) => {
            gsap.from(elements, {
                opacity: 0,
                y: 20,
                duration: 0.8,
                ease: "power2.out"
            });
        });
        
        // Animate navbar
        safeAnimate('.navbar', (elements) => {
            gsap.from(elements, {
                y: -100,
                opacity: 0,
                duration: 0.6,
                ease: "power3.out"
            });
        });
    }
    
    // Hero section animations
    function animateHero() {
        // Hero title
        safeAnimate('.hero-title', (elements) => {
            gsap.from(elements, {
                y: 50,
                opacity: 0,
                duration: 1,
                ease: "power3.out"
            });
        });
        
        // Hero subtitle
        safeAnimate('.hero-subtitle', (elements) => {
            gsap.from(elements, {
                y: 30,
                opacity: 0,
                duration: 0.8,
                delay: 0.3,
                ease: "power2.out"
            });
        });
        
        // Hero CTA buttons
        safeAnimate('.hero-cta-button, .hero-button', (elements) => {
            gsap.from(elements, {
                scale: 0.8,
                opacity: 0,
                duration: 0.6,
                delay: 0.6,
                stagger: 0.1,
                ease: "back.out(1.7)"
            });
        });
    }
    
    // Feature cards animations
    function animateFeatureCards() {
        safeAnimate('.feature-card, .features-grid .card', (elements) => {
            elements.forEach((card, i) => {
                if (ScrollTrigger) {
                    gsap.from(card, {
                        scrollTrigger: {
                            trigger: card,
                            ...config.scrollTriggerDefaults
                        },
                        y: 50,
                        opacity: 0,
                        duration: 0.8,
                        delay: i * 0.1,
                        ease: "power2.out"
                    });
                } else {
                    // Fallback without ScrollTrigger
                    gsap.from(card, {
                        y: 50,
                        opacity: 0,
                        duration: 0.8,
                        delay: 0.5 + (i * 0.1),
                        ease: "power2.out"
                    });
                }
            });
        });
    }
    
    // Workflow animations
    function animateWorkflow() {
        safeAnimate('.workflow-step', (elements) => {
            if (ScrollTrigger) {
                gsap.from(elements, {
                    scrollTrigger: {
                        trigger: elements[0],
                        ...config.scrollTriggerDefaults
                    },
                    x: -50,
                    opacity: 0,
                    duration: 0.8,
                    stagger: 0.2,
                    ease: "power2.out"
                });
            }
        });
    }
    
    // Statistics counter animations
    function animateStatistics() {
        safeAnimate('.stat-number', (elements) => {
            elements.forEach(stat => {
                const target = parseInt(stat.dataset.target || stat.textContent.replace(/[^0-9]/g, ''));
                
                if (ScrollTrigger) {
                    gsap.from(stat, {
                        scrollTrigger: {
                            trigger: stat,
                            ...config.scrollTriggerDefaults
                        },
                        textContent: 0,
                        duration: 2,
                        ease: "power1.out",
                        snap: { textContent: 1 },
                        onUpdate: function() {
                            stat.textContent = Math.ceil(this.targets()[0].textContent).toLocaleString();
                        }
                    });
                }
            });
        });
    }
    
    // Pricing section animations
    function animatePricing() {
        safeAnimate('.pricing-tier, .pricing-card', (elements) => {
            if (ScrollTrigger) {
                gsap.from(elements, {
                    scrollTrigger: {
                        trigger: elements[0],
                        ...config.scrollTriggerDefaults
                    },
                    y: 50,
                    opacity: 0,
                    duration: 0.8,
                    stagger: 0.15,
                    ease: "power2.out"
                });
            }
        });
        
        // Highlight recommended plan
        safeAnimate('.recommended-plan, .featured', (elements) => {
            gsap.to(elements, {
                scale: 1.05,
                duration: 0.8,
                ease: "power2.inOut",
                repeat: -1,
                yoyo: true,
                repeatDelay: 3
            });
        });
    }
    
    // Footer animations
    function animateFooter() {
        safeAnimate('footer', (elements) => {
            if (ScrollTrigger) {
                gsap.from(elements, {
                    scrollTrigger: {
                        trigger: elements[0],
                        start: "top 95%",
                        once: true
                    },
                    y: 30,
                    opacity: 0,
                    duration: 0.8,
                    ease: "power2.out"
                });
            }
        });
    }
    
    // Form animations
    function setupFormAnimations() {
        // Form inputs focus effect
        document.querySelectorAll('.form-control, .form-input').forEach(input => {
            input.addEventListener('focus', function() {
                gsap.to(this, {
                    scale: 1.02,
                    duration: 0.2,
                    ease: "power2.out"
                });
            });
            
            input.addEventListener('blur', function() {
                gsap.to(this, {
                    scale: 1,
                    duration: 0.2,
                    ease: "power2.out"
                });
            });
        });
        
        // Form submission animation
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitBtn = this.querySelector('[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    gsap.to(submitBtn, {
                        scale: 0.95,
                        duration: 0.1,
                        yoyo: true,
                        repeat: 1
                    });
                }
            });
        });
    }
    
    // Scroll animations
    function setupScrollAnimations() {
        // Fade in elements on scroll
        safeAnimate('.fade-in-scroll', (elements) => {
            elements.forEach(element => {
                if (ScrollTrigger) {
                    gsap.from(element, {
                        scrollTrigger: {
                            trigger: element,
                            ...config.scrollTriggerDefaults
                        },
                        y: 30,
                        opacity: 0,
                        duration: 0.8,
                        ease: "power2.out"
                    });
                }
            });
        });
        
        // Parallax effects
        safeAnimate('[data-parallax]', (elements) => {
            elements.forEach(element => {
                const speed = element.dataset.parallax || 0.5;
                if (ScrollTrigger) {
                    gsap.to(element, {
                        scrollTrigger: {
                            trigger: element,
                            scrub: true
                        },
                        y: (i, target) => -ScrollTrigger.maxScroll(window) * speed,
                        ease: "none"
                    });
                }
            });
        });
    }
    
    // Hover effects
    function setupHoverEffects() {
        // Card hover animations
        document.querySelectorAll('.card, .feature-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                gsap.to(card, {
                    y: -5,
                    boxShadow: "0 10px 30px rgba(0,0,0,0.15)",
                    duration: 0.3,
                    ease: "power2.out"
                });
            });
            
            card.addEventListener('mouseleave', () => {
                gsap.to(card, {
                    y: 0,
                    boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
                    duration: 0.3,
                    ease: "power2.out"
                });
            });
        });
        
        // Button hover effects
        document.querySelectorAll('.btn, button').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                gsap.to(btn, {
                    scale: 1.05,
                    duration: 0.2,
                    ease: "power2.out"
                });
            });
            
            btn.addEventListener('mouseleave', () => {
                gsap.to(btn, {
                    scale: 1,
                    duration: 0.2,
                    ease: "power2.out"
                });
            });
        });
    }
    
    // Public API
    window.FXAnimations = {
        init: initializeGSAP,
        enable: () => { config.animationsEnabled = true; },
        disable: () => { config.animationsEnabled = false; },
        debug: (enabled) => { config.debug = enabled; }
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeGSAP);
    } else {
        initializeGSAP();
    }
    
})();