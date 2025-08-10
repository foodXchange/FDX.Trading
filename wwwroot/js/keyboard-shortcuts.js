// FDX Trading - Global Keyboard Shortcuts
// This file provides keyboard shortcuts across the entire application

(function() {
    'use strict';

    // Initialize keyboard shortcuts when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initKeyboardShortcuts);
    } else {
        initKeyboardShortcuts();
    }

    function initKeyboardShortcuts() {
        document.addEventListener('keydown', handleGlobalShortcuts);
    }

    function handleGlobalShortcuts(e) {
        // Get current page
        const currentPath = window.location.pathname;
        
        // Global Navigation Shortcuts (work on all pages)
        
        // Alt+H - Go to Dashboard/Home
        if (e.altKey && e.key === 'h') {
            e.preventDefault();
            window.location.href = '/dashboard.html';
            return false;
        }
        
        // Alt+R - Go to Requests
        if (e.altKey && e.key === 'r') {
            e.preventDefault();
            window.location.href = '/requests.html';
            return false;
        }
        
        // Alt+P - Go to Products
        if (e.altKey && e.key === 'p') {
            e.preventDefault();
            window.location.href = '/products.html';
            return false;
        }
        
        // Alt+S - Go to Suppliers
        if (e.altKey && e.key === 's') {
            e.preventDefault();
            window.location.href = '/supplier-catalog.html';
            return false;
        }
        
        // Alt+U - Go to Users
        if (e.altKey && e.key === 'u') {
            e.preventDefault();
            window.location.href = '/users.html';
            return false;
        }
        
        // Alt+M - Go to Price Management
        if (e.altKey && e.key === 'm') {
            e.preventDefault();
            window.location.href = '/price-management.html';
            return false;
        }
        
        // Ctrl+K or Cmd+K - Focus on search (if search box exists)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('#searchInput, #search, input[type="search"], input[placeholder*="Search"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
            return false;
        }
        
        // Ctrl+/ or Cmd+/ - Show keyboard shortcuts help
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            showShortcutsHelp();
            return false;
        }
        
        // Page-specific shortcuts
        if (currentPath.includes('requests.html')) {
            handleRequestsPageShortcuts(e);
        } else if (currentPath.includes('products.html')) {
            handleProductsPageShortcuts(e);
        } else if (currentPath.includes('dashboard.html')) {
            handleDashboardShortcuts(e);
        }
    }

    function handleRequestsPageShortcuts(e) {
        // Ctrl+N or Cmd+N - New Request
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            window.location.href = '/request-create.html';
            return false;
        }
        
        // Number keys 1-3 - Quick filter by status
        if (!e.ctrlKey && !e.altKey && !e.metaKey && !e.shiftKey) {
            if (e.key === '1') {
                // Filter by Draft
                const statusFilter = document.getElementById('statusFilter');
                if (statusFilter) {
                    statusFilter.value = '0';
                    statusFilter.dispatchEvent(new Event('change'));
                }
            } else if (e.key === '2') {
                // Filter by Active
                const statusFilter = document.getElementById('statusFilter');
                if (statusFilter) {
                    statusFilter.value = '1';
                    statusFilter.dispatchEvent(new Event('change'));
                }
            } else if (e.key === '3') {
                // Filter by Closed
                const statusFilter = document.getElementById('statusFilter');
                if (statusFilter) {
                    statusFilter.value = '2';
                    statusFilter.dispatchEvent(new Event('change'));
                }
            }
        }
    }

    function handleProductsPageShortcuts(e) {
        // Ctrl+N or Cmd+N - New Product
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const addButton = document.querySelector('button[onclick*="showAddProductModal"]');
            if (addButton) addButton.click();
            return false;
        }
    }

    function handleDashboardShortcuts(e) {
        // Number keys 1-6 - Quick navigation to sections
        if (!e.ctrlKey && !e.altKey && !e.metaKey && !e.shiftKey) {
            const cards = document.querySelectorAll('.dashboard-card');
            const keyNum = parseInt(e.key);
            if (keyNum >= 1 && keyNum <= cards.length) {
                const targetCard = cards[keyNum - 1];
                if (targetCard) {
                    targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    // Click the card's main action if it has one
                    const button = targetCard.querySelector('button, a');
                    if (button) button.click();
                }
            }
        }
    }

    function showShortcutsHelp() {
        const helpModal = document.createElement('div');
        helpModal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease;
        `;
        
        const helpContent = document.createElement('div');
        helpContent.style.cssText = `
            background: white;
            border-radius: 15px;
            padding: 30px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        `;
        
        helpContent.innerHTML = `
            <h2 style="color: #667eea; margin-bottom: 20px;">⌨️ Keyboard Shortcuts</h2>
            
            <div style="margin-bottom: 25px;">
                <h3 style="color: #333; margin-bottom: 10px;">🌐 Global Navigation</h3>
                <table style="width: 100%; font-size: 14px;">
                    <tr><td style="padding: 5px;"><kbd>Alt</kbd> + <kbd>H</kbd></td><td>Go to Dashboard</td></tr>
                    <tr><td style="padding: 5px;"><kbd>Alt</kbd> + <kbd>R</kbd></td><td>Go to Requests</td></tr>
                    <tr><td style="padding: 5px;"><kbd>Alt</kbd> + <kbd>P</kbd></td><td>Go to Products</td></tr>
                    <tr><td style="padding: 5px;"><kbd>Alt</kbd> + <kbd>S</kbd></td><td>Go to Suppliers</td></tr>
                    <tr><td style="padding: 5px;"><kbd>Alt</kbd> + <kbd>U</kbd></td><td>Go to Users</td></tr>
                    <tr><td style="padding: 5px;"><kbd>Alt</kbd> + <kbd>M</kbd></td><td>Go to Price Management</td></tr>
                </table>
            </div>
            
            <div style="margin-bottom: 25px;">
                <h3 style="color: #333; margin-bottom: 10px;">📝 Form Actions</h3>
                <table style="width: 100%; font-size: 14px;">
                    <tr><td style="padding: 5px;"><kbd>Ctrl/Cmd</kbd> + <kbd>S</kbd></td><td>Save form</td></tr>
                    <tr><td style="padding: 5px;"><kbd>Ctrl/Cmd</kbd> + <kbd>Enter</kbd></td><td>Save and submit</td></tr>
                    <tr><td style="padding: 5px;"><kbd>Escape</kbd></td><td>Cancel/Go back</td></tr>
                </table>
            </div>
            
            <div style="margin-bottom: 25px;">
                <h3 style="color: #333; margin-bottom: 10px;">🔍 Search & Filters</h3>
                <table style="width: 100%; font-size: 14px;">
                    <tr><td style="padding: 5px;"><kbd>Ctrl/Cmd</kbd> + <kbd>K</kbd></td><td>Focus search box</td></tr>
                    <tr><td style="padding: 5px;"><kbd>1</kbd> / <kbd>2</kbd> / <kbd>3</kbd></td><td>Quick status filter (on list pages)</td></tr>
                </table>
            </div>
            
            <div style="margin-bottom: 25px;">
                <h3 style="color: #333; margin-bottom: 10px;">➕ Quick Actions</h3>
                <table style="width: 100%; font-size: 14px;">
                    <tr><td style="padding: 5px;"><kbd>Ctrl/Cmd</kbd> + <kbd>N</kbd></td><td>New item (context-aware)</td></tr>
                    <tr><td style="padding: 5px;"><kbd>Alt</kbd> + <kbd>A</kbd></td><td>Add item (in forms)</td></tr>
                    <tr><td style="padding: 5px;"><kbd>Alt</kbd> + <kbd>D</kbd></td><td>Duplicate item</td></tr>
                </table>
            </div>
            
            <div style="margin-bottom: 25px;">
                <h3 style="color: #333; margin-bottom: 10px;">❓ Help</h3>
                <table style="width: 100%; font-size: 14px;">
                    <tr><td style="padding: 5px;"><kbd>Ctrl/Cmd</kbd> + <kbd>/</kbd></td><td>Show this help</td></tr>
                    <tr><td style="padding: 5px;"><kbd>F1</kbd></td><td>Context help</td></tr>
                </table>
            </div>
            
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                width: 100%;
                margin-top: 10px;
            ">Close (Escape)</button>
        `;
        
        helpModal.appendChild(helpContent);
        document.body.appendChild(helpModal);
        
        // Close on Escape or click outside
        helpModal.addEventListener('click', function(e) {
            if (e.target === helpModal) {
                helpModal.remove();
            }
        });
        
        document.addEventListener('keydown', function closeHelp(e) {
            if (e.key === 'Escape') {
                helpModal.remove();
                document.removeEventListener('keydown', closeHelp);
            }
        });
    }
    
    // Add CSS animation
    if (!document.getElementById('keyboard-shortcuts-styles')) {
        const style = document.createElement('style');
        style.id = 'keyboard-shortcuts-styles';
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            kbd {
                background: #f4f4f4;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 2px 6px;
                font-family: monospace;
                font-size: 12px;
                box-shadow: 0 1px 0 rgba(0,0,0,0.2);
                display: inline-block;
                margin: 0 2px;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Export for use in other scripts
    window.FDXKeyboardShortcuts = {
        showHelp: showShortcutsHelp,
        init: initKeyboardShortcuts
    };
})();