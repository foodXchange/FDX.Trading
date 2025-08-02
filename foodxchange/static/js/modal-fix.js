// Modal Fix Script - Force close any stuck modals
console.log('Modal fix script loaded');

// Function to completely remove all modals and their effects
function forceCloseAllModals() {
    console.log('Force closing all modals...');
    
    // Remove all modal backdrops
    document.querySelectorAll('.modal-backdrop').forEach(el => {
        el.parentNode.removeChild(el);
    });
    
    // Hide all modals
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('show');
        modal.classList.remove('fade');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        modal.removeAttribute('aria-modal');
        modal.removeAttribute('role');
    });
    
    // Reset body
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    document.body.style.removeProperty('overflow');
    document.body.style.removeProperty('padding-right');
    
    // Remove any inline styles that might have been added
    const htmlElement = document.documentElement;
    htmlElement.style.overflow = '';
    htmlElement.style.paddingRight = '';
    
    // Clear any Bootstrap modal data
    if (typeof bootstrap !== 'undefined') {
        document.querySelectorAll('.modal').forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                try {
                    bsModal.dispose();
                } catch (e) {
                    console.error('Error disposing modal:', e);
                }
            }
        });
    }
    
    console.log('All modals closed');
}

// Run immediately when script loads
forceCloseAllModals();

// Run again after a short delay to catch any async modals
setTimeout(forceCloseAllModals, 500);
setTimeout(forceCloseAllModals, 1000);

// Make it globally available
window.forceCloseAllModals = forceCloseAllModals;

// Add keyboard shortcut (Ctrl+Q) to close all modals
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'q') {
        e.preventDefault();
        forceCloseAllModals();
    }
});

// Override Bootstrap modal show to prevent issues
if (typeof bootstrap !== 'undefined') {
    const originalShow = bootstrap.Modal.prototype.show;
    bootstrap.Modal.prototype.show = function() {
        try {
            // Close any existing modals first
            forceCloseAllModals();
            // Then show the new modal
            originalShow.call(this);
        } catch (e) {
            console.error('Error showing modal:', e);
        }
    };
}