// FoodXchange Navigation Handler
(function() {
    'use strict';
    
    // Configuration
    const DEBUG = false; // Set to true for development debugging
    const NAVBAR_OFFSET = 80; // Fixed navbar height
    const SCROLL_OFFSET = 20; // Additional offset for better positioning
    
    // Debug logger that only logs in development
    function log(...args) {
        if (DEBUG) {
            console.log('[FDX Nav]', ...args);
        }
    }
    
    function initNavigation() {
        log('Navigation initialized');
        
        // Handle navigation clicks for anchor links
        const navLinks = document.querySelectorAll('.navbar a.nav-link');
        log('Found nav links:', navLinks.length);
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            
            // Only process links that start with /#
            if (href && href.startsWith('/#')) {
                link.addEventListener('click', function(e) {
                    const targetId = href.substring(2); // Remove '/#'
                    
                    // Check if we're on the homepage
                    if (window.location.pathname === '/') {
                        // We're on homepage, just scroll to section
                        e.preventDefault();
                        const targetSection = document.getElementById(targetId);
                        
                        if (targetSection) {
                            // Calculate offset accounting for fixed navbar
                            const navbarHeight = document.querySelector('.navbar').offsetHeight || NAVBAR_OFFSET;
                            const targetPosition = targetSection.offsetTop - navbarHeight - SCROLL_OFFSET;
                            
                            window.scrollTo({
                                top: targetPosition,
                                behavior: 'smooth'
                            });
                            
                            // Update URL hash
                            history.pushState(null, null, '#' + targetId);
                            
                            // Close mobile menu if open
                            const navbarCollapse = document.querySelector('.navbar-collapse');
                            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                                navbarCollapse.classList.remove('show');
                            }
                        }
                    }
                    // If on another page, let browser handle navigation naturally
                });
            }
        });
        
        // Handle hash on page load (when coming from another page)
        if (window.location.hash) {
            const targetId = window.location.hash.substring(1);
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                // Small delay to ensure page layout is complete
                setTimeout(() => {
                    const navbarHeight = document.querySelector('.navbar').offsetHeight || NAVBAR_OFFSET;
                    const targetPosition = targetSection.offsetTop - navbarHeight - SCROLL_OFFSET;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }, 100);
            }
        }
    }
    
    // Initialize on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNavigation);
    } else {
        // DOM already loaded
        initNavigation();
    }
    
    // Export for potential use in other scripts
    window.FDXNavigation = {
        init: initNavigation,
        scrollToSection: function(sectionId) {
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                const navbarHeight = document.querySelector('.navbar').offsetHeight || NAVBAR_OFFSET;
                const targetPosition = targetSection.offsetTop - navbarHeight - SCROLL_OFFSET;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        }
    };
})();