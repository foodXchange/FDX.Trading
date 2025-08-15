// Global UI Enhancements - Applied to all pages

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Enhanced API calls with automatic toast notifications
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        const [url, options = {}] = args;
        
        // Skip for non-API calls
        if (!url.includes('/api/')) {
            return originalFetch.apply(this, args);
        }
        
        // Add loading indicator for long requests
        let loadingTimeout = setTimeout(() => {
            if (options.method && options.method !== 'GET') {
                window.loading.show('Processing...');
            }
        }, 500);
        
        try {
            const response = await originalFetch.apply(this, args);
            clearTimeout(loadingTimeout);
            window.loading.hide();
            
            // Show success for mutations
            if (options.method && options.method !== 'GET' && response.ok) {
                const messages = {
                    'POST': 'Created successfully',
                    'PUT': 'Updated successfully',
                    'PATCH': 'Changes saved',
                    'DELETE': 'Deleted successfully'
                };
                
                if (!options.silent) {
                    window.toast.success(messages[options.method] || 'Operation successful');
                }
            }
            
            // Handle errors
            if (!response.ok && response.status !== 404) {
                const errorData = await response.clone().json().catch(() => ({}));
                window.toast.error(errorData.message || `Error: ${response.statusText}`);
            }
            
            return response;
        } catch (error) {
            clearTimeout(loadingTimeout);
            window.loading.hide();
            
            if (!options.silent) {
                window.toast.error('Network error. Please check your connection.');
            }
            throw error;
        }
    };
    
    // 2. Smooth scroll to sections
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // 3. Enhanced table interactions
    document.querySelectorAll('table').forEach(table => {
        // Add hover effects
        table.classList.add('table-modern');
        
        // Make rows clickable if they have data-href
        table.querySelectorAll('tr[data-href]').forEach(row => {
            row.style.cursor = 'pointer';
            row.addEventListener('click', function() {
                window.location.href = this.dataset.href;
            });
        });
        
        // Add sorting indicators
        table.querySelectorAll('th').forEach(th => {
            if (th.dataset.sortable) {
                th.style.cursor = 'pointer';
                th.innerHTML += ' <span class="sort-indicator">⇅</span>';
            }
        });
    });
    
    // 4. Form enhancements
    document.querySelectorAll('form').forEach(form => {
        // Prevent double submission
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner spinner-sm"></span> Processing...';
                
                // Re-enable after 5 seconds (failsafe)
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Submit';
                }, 5000);
            }
        });
        
        // Add character counters to textareas
        form.querySelectorAll('textarea[maxlength]').forEach(textarea => {
            const maxLength = textarea.getAttribute('maxlength');
            const counter = document.createElement('div');
            counter.className = 'character-counter';
            counter.style.cssText = 'text-align: right; font-size: 12px; color: #666; margin-top: 4px;';
            counter.textContent = `0 / ${maxLength}`;
            
            textarea.parentNode.insertBefore(counter, textarea.nextSibling);
            
            textarea.addEventListener('input', function() {
                const remaining = maxLength - this.value.length;
                counter.textContent = `${this.value.length} / ${maxLength}`;
                counter.style.color = remaining < 20 ? '#ef4444' : '#666';
            });
        });
    });
    
    // 5. Add copy-to-clipboard functionality
    document.querySelectorAll('[data-copy]').forEach(element => {
        element.style.cursor = 'pointer';
        element.title = 'Click to copy';
        
        element.addEventListener('click', async function() {
            const textToCopy = this.dataset.copy || this.textContent;
            
            try {
                await navigator.clipboard.writeText(textToCopy);
                window.toast.success('Copied to clipboard');
                
                // Visual feedback
                const originalText = this.innerHTML;
                this.innerHTML = '✓ Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            } catch (err) {
                window.toast.error('Failed to copy');
            }
        });
    });
    
    // 6. Enhanced number inputs
    document.querySelectorAll('input[type="number"]').forEach(input => {
        // Add increment/decrement with mouse wheel
        input.addEventListener('wheel', function(e) {
            if (this === document.activeElement) {
                e.preventDefault();
                const step = parseFloat(this.step) || 1;
                const delta = e.deltaY < 0 ? step : -step;
                const newValue = parseFloat(this.value || 0) + delta;
                
                // Respect min/max
                const min = this.min ? parseFloat(this.min) : -Infinity;
                const max = this.max ? parseFloat(this.max) : Infinity;
                
                this.value = Math.min(Math.max(newValue, min), max);
                this.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
    });
    
    // 7. Confirmation dialogs for destructive actions
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });
    
    // 8. Time ago formatting
    function formatTimeAgo(date) {
        const seconds = Math.floor((new Date() - new Date(date)) / 1000);
        
        const intervals = {
            year: 31536000,
            month: 2592000,
            week: 604800,
            day: 86400,
            hour: 3600,
            minute: 60
        };
        
        for (const [unit, secondsInUnit] of Object.entries(intervals)) {
            const interval = Math.floor(seconds / secondsInUnit);
            if (interval >= 1) {
                return interval === 1 ? `1 ${unit} ago` : `${interval} ${unit}s ago`;
            }
        }
        
        return 'Just now';
    }
    
    // Apply to all time elements
    document.querySelectorAll('[data-time]').forEach(element => {
        const date = element.dataset.time;
        element.title = new Date(date).toLocaleString();
        element.textContent = formatTimeAgo(date);
    });
    
    // 9. Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img.lazy').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // 10. Print functionality enhancement
    window.printSection = function(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            const printWindow = window.open('', '', 'height=600,width=800');
            printWindow.document.write('<html><head><title>Print</title>');
            printWindow.document.write('<link rel="stylesheet" href="/css/modern-ui.css">');
            printWindow.document.write('</head><body>');
            printWindow.document.write(section.innerHTML);
            printWindow.document.write('</body></html>');
            printWindow.document.close();
            printWindow.print();
        }
    };
    
    // 11. Export table to CSV
    window.exportTableToCSV = function(tableId, filename = 'export.csv') {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const rows = table.querySelectorAll('tr');
        const csv = [];
        
        rows.forEach(row => {
            const cols = row.querySelectorAll('td, th');
            const rowData = Array.from(cols).map(col => {
                let text = col.textContent.replace(/"/g, '""');
                return `"${text}"`;
            });
            csv.push(rowData.join(','));
        });
        
        const csvContent = csv.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
        
        window.toast.success('Table exported successfully');
    };
    
    // 12. Full-text search highlighting
    window.highlightSearchTerm = function(term) {
        if (!term) return;
        
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        const nodesToHighlight = [];
        while (walker.nextNode()) {
            const node = walker.currentNode;
            if (node.nodeValue && node.nodeValue.toLowerCase().includes(term.toLowerCase())) {
                nodesToHighlight.push(node);
            }
        }
        
        nodesToHighlight.forEach(node => {
            const span = document.createElement('span');
            span.innerHTML = node.nodeValue.replace(
                new RegExp(term, 'gi'),
                match => `<mark class="highlight">${match}</mark>`
            );
            node.parentNode.replaceChild(span, node);
        });
    };
    
    // Check URL for search term
    const urlParams = new URLSearchParams(window.location.search);
    const searchTerm = urlParams.get('highlight');
    if (searchTerm) {
        highlightSearchTerm(searchTerm);
    }
});

// Add CSS for highlights
const style = document.createElement('style');
style.textContent = `
    .highlight {
        background-color: #fef3c7;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: 500;
    }
    
    .character-counter {
        font-family: 'Inter', sans-serif;
    }
    
    .sort-indicator {
        opacity: 0.3;
        font-size: 0.8em;
        margin-left: 4px;
    }
    
    th:hover .sort-indicator {
        opacity: 1;
    }
    
    @media print {
        .no-print {
            display: none !important;
        }
    }
`;
document.head.appendChild(style);