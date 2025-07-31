/**
 * Intelligent Search JavaScript for FoodXchange Platform
 * Provides advanced search functionality with AI-powered features
 */

class IntelligentSearch {
    constructor() {
        this.searchInput = document.getElementById('intelligentSearchInput');
        this.searchBtn = document.getElementById('performSearchBtn');
        this.voiceSearchBtn = document.getElementById('voiceSearchBtn');
        this.suggestionsContainer = document.getElementById('searchSuggestions');
        this.suggestionsList = document.getElementById('suggestionsList');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsContent = document.getElementById('resultsContent');
        this.loadingState = document.getElementById('loadingState');
        this.noResultsState = document.getElementById('noResultsState');
        this.filtersSection = document.getElementById('filtersSection');
        this.searchHistorySection = document.getElementById('searchHistorySection');
        
        // Filter elements
        this.locationFilter = document.getElementById('locationFilter');
        this.certificationFilter = document.getElementById('certificationFilter');
        this.companySizeFilter = document.getElementById('companySizeFilter');
        this.categoryFilter = document.getElementById('categoryFilter');
        
        // State management
        this.currentQuery = '';
        this.activeFilters = new Map();
        this.searchHistory = [];
        this.trendingSearches = [];
        this.isSearching = false;
        this.suggestionTimeout = null;
        this.voiceRecognition = null;
        
        // Memory management
        this.eventListeners = [];
        this.timeouts = [];
        this.intervals = [];
        this.observers = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupVoiceRecognition();
        this.loadSearchHistory();
        this.loadTrendingSearches();
        this.setupKeyboardShortcuts();
        
        // Set up cleanup on page unload
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }

    setupEventListeners() {
        // Search input events
        this.addEventListener(this.searchInput, 'input', (e) => {
            this.handleSearchInput(e.target.value);
        });

        this.addEventListener(this.searchInput, 'focus', () => {
            this.showSuggestions();
        });

        this.addEventListener(this.searchInput, 'blur', () => {
            // Delay hiding suggestions to allow clicking on them
            const timeout = setTimeout(() => {
                this.hideSuggestions();
            }, 200);
            this.timeouts.push(timeout);
        });

        this.addEventListener(this.searchInput, 'keydown', (e) => {
            this.handleSearchKeydown(e);
        });

        // Mobile touch events
        this.setupMobileTouchEvents();

        // Search button
        this.addEventListener(this.searchBtn, 'click', () => {
            this.performSearch();
        });

        // Voice search button
        this.addEventListener(this.voiceSearchBtn, 'click', () => {
            this.startVoiceSearch();
        });

        // Search examples
        document.querySelectorAll('.search-example').forEach(example => {
            this.addEventListener(example, 'click', (e) => {
                const query = e.target.dataset.query;
                this.searchInput.value = query;
                this.performSearch();
            });
        });

        // Filter events
        this.addEventListener(this.locationFilter, 'change', () => this.handleFilterChange());
        this.addEventListener(this.certificationFilter, 'change', () => this.handleFilterChange());
        this.addEventListener(this.companySizeFilter, 'change', () => this.handleFilterChange());
        this.addEventListener(this.categoryFilter, 'change', () => this.handleFilterChange());

        // Clear filters
        const clearFiltersBtn = document.getElementById('clearAllFilters');
        if (clearFiltersBtn) {
            this.addEventListener(clearFiltersBtn, 'click', () => {
                this.clearAllFilters();
            });
        }

        // Toggle filters
        document.getElementById('toggleFiltersBtn').addEventListener('click', () => {
            this.toggleFilters();
        });

        // Location-based search
        this.setupLocationBasedSearch();
    }

        // Save search
        document.getElementById('saveSearchBtn').addEventListener('click', () => {
            this.saveCurrentSearch();
        });

        // Suggest alternatives
        document.getElementById('suggestAlternativesBtn').addEventListener('click', () => {
            this.suggestAlternatives();
        });

        // Advanced search
        document.getElementById('advancedSearchBtn').addEventListener('click', () => {
            this.showAdvancedSearch();
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + S to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.searchInput.focus();
            }

            // Escape to close modal
            if (e.key === 'Escape') {
                const modal = document.getElementById('intelligentSearchModal');
                if (modal.classList.contains('show')) {
                    const closeBtn = modal.querySelector('.btn-close');
                    if (closeBtn) closeBtn.click();
                }
            }
        });
    }

    setupVoiceRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.voiceRecognition = new SpeechRecognition();
            
            this.voiceRecognition.continuous = false;
            this.voiceRecognition.interimResults = false;
            this.voiceRecognition.lang = 'en-US';

            this.voiceRecognition.onstart = () => {
                this.voiceSearchBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
                this.voiceSearchBtn.classList.add('btn-danger');
                this.showNotification('Listening... Speak now', 'info');
            };

            this.voiceRecognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.searchInput.value = transcript;
                this.performSearch();
            };

            this.voiceRecognition.onerror = (event) => {
                this.showNotification('Voice recognition error: ' + event.error, 'error');
            };

            this.voiceRecognition.onend = () => {
                this.voiceSearchBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                this.voiceSearchBtn.classList.remove('btn-danger');
            };
        } else {
            this.voiceSearchBtn.style.display = 'none';
        }
    }

    setupMobileTouchEvents() {
        // Touch gestures for mobile optimization
        let touchStartX = 0;
        let touchStartY = 0;
        let touchEndX = 0;
        let touchEndY = 0;

        // Swipe gestures for search suggestions
        this.suggestionsContainer.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
            touchStartY = e.changedTouches[0].screenY;
        }, { passive: true });

        this.suggestionsContainer.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            touchEndY = e.changedTouches[0].screenY;
            this.handleSwipeGesture();
        }, { passive: true });

        // Pinch to zoom for search results
        let initialDistance = 0;
        let currentScale = 1;

        this.resultsContent.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
                initialDistance = this.getDistance(e.touches[0], e.touches[1]);
            }
        }, { passive: true });

        this.resultsContent.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2) {
                e.preventDefault();
                const currentDistance = this.getDistance(e.touches[0], e.touches[1]);
                const scale = currentDistance / initialDistance;
                currentScale = Math.min(Math.max(scale, 0.5), 2.0);
                this.resultsContent.style.transform = `scale(${currentScale})`;
            }
        });

        this.resultsContent.addEventListener('touchend', () => {
            initialDistance = 0;
        }, { passive: true });

        // Long press for quick actions
        let longPressTimer = null;
        this.resultsContent.addEventListener('touchstart', (e) => {
            longPressTimer = setTimeout(() => {
                this.handleLongPress(e);
            }, 500);
        }, { passive: true });

        this.resultsContent.addEventListener('touchend', () => {
            if (longPressTimer) {
                clearTimeout(longPressTimer);
                longPressTimer = null;
            }
        }, { passive: true });

        // Double tap to zoom
        let lastTap = 0;
        this.resultsContent.addEventListener('touchend', (e) => {
            const currentTime = new Date().getTime();
            const tapLength = currentTime - lastTap;
            if (tapLength < 500 && tapLength > 0) {
                this.handleDoubleTap(e);
            }
            lastTap = currentTime;
        }, { passive: true });
    }

    setupLocationBasedSearch() {
        // Location-based search using GPS
        if ('geolocation' in navigator) {
            const locationBtn = document.getElementById('locationSearchBtn');
            if (locationBtn) {
                locationBtn.addEventListener('click', () => {
                    this.getCurrentLocation();
                });
            }
        }
    }

    handleSwipeGesture() {
        const diffX = touchStartX - touchEndX;
        const diffY = touchStartY - touchEndY;

        // Horizontal swipe
        if (Math.abs(diffX) > Math.abs(diffY)) {
            if (diffX > 50) {
                // Swipe left - next suggestion
                this.navigateSuggestions('next');
            } else if (diffX < -50) {
                // Swipe right - previous suggestion
                this.navigateSuggestions('prev');
            }
        }
        // Vertical swipe
        else {
            if (diffY > 50) {
                // Swipe up - show more suggestions
                this.loadMoreSuggestions();
            } else if (diffY < -50) {
                // Swipe down - hide suggestions
                this.hideSuggestions();
            }
        }
    }

    getDistance(touch1, touch2) {
        const dx = touch1.clientX - touch2.clientX;
        const dy = touch1.clientY - touch2.clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    handleLongPress(e) {
        const target = e.target.closest('.search-result');
        if (target) {
            this.showQuickActions(target);
        }
    }

    handleDoubleTap(e) {
        const target = e.target.closest('.search-result');
        if (target) {
            // Zoom to fit content
            this.resultsContent.style.transform = 'scale(1)';
            currentScale = 1;
        }
    }

    async getCurrentLocation() {
        try {
            this.showNotification('Getting your location...', 'info');
            
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                });
            });

            const { latitude, longitude } = position.coords;
            
            // Add location filter
            this.addLocationFilter(latitude, longitude);
            
            this.showNotification('Location-based search enabled', 'success');
            
        } catch (error) {
            console.error('Location error:', error);
            this.showNotification('Unable to get location. Please enable location services.', 'error');
        }
    }

    addLocationFilter(latitude, longitude) {
        // Add location to active filters
        this.activeFilters.set('location', {
            type: 'location',
            value: `${latitude},${longitude}`,
            label: 'Near me'
        });

        // Update UI
        this.updateActiveFilters();
        
        // Perform search with location filter
        this.performSearch();
    }

    showQuickActions(element) {
        // Create quick actions menu
        const quickActions = document.createElement('div');
        quickActions.className = 'quick-actions-menu';
        quickActions.innerHTML = `
            <div class="quick-action" data-action="save">Save</div>
            <div class="quick-action" data-action="share">Share</div>
            <div class="quick-action" data-action="contact">Contact</div>
        `;

        // Position menu
        const rect = element.getBoundingClientRect();
        quickActions.style.position = 'fixed';
        quickActions.style.top = `${rect.top}px`;
        quickActions.style.left = `${rect.left}px`;
        quickActions.style.zIndex = '1000';

        // Add event listeners
        quickActions.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            this.handleQuickAction(action, element);
            document.body.removeChild(quickActions);
        });

        // Add to DOM
        document.body.appendChild(quickActions);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (document.body.contains(quickActions)) {
                document.body.removeChild(quickActions);
            }
        }, 3000);
    }

    handleQuickAction(action, element) {
        const resultId = element.dataset.resultId;
        
        switch (action) {
            case 'save':
                this.saveResult({ id: resultId });
                this.showNotification('Result saved', 'success');
                break;
            case 'share':
                this.shareResult(resultId);
                break;
            case 'contact':
                this.contactResult({ id: resultId });
                break;
        }
    }

    async shareResult(resultId) {
        if ('share' in navigator) {
            try {
                await navigator.share({
                    title: 'FoodXchange Search Result',
                    text: 'Check out this supplier on FoodXchange',
                    url: `${window.location.origin}/suppliers/${resultId}`
                });
            } catch (error) {
                console.error('Share failed:', error);
                this.showNotification('Share not supported', 'error');
            }
        } else {
            // Fallback: copy to clipboard
            const url = `${window.location.origin}/suppliers/${resultId}`;
            await navigator.clipboard.writeText(url);
            this.showNotification('Link copied to clipboard', 'success');
        }
    }

    loadMoreSuggestions() {
        // Load additional suggestions
        this.showNotification('Loading more suggestions...', 'info');
        // Implementation would load more suggestions from the server
    }

    async handleSearchInput(value) {
        this.currentQuery = value;
        
        // Clear previous timeout
        if (this.suggestionTimeout) {
            clearTimeout(this.suggestionTimeout);
        }

        // Show suggestions after delay
        if (value.length >= 2) {
            this.suggestionTimeout = setTimeout(() => {
                this.getSearchSuggestions(value);
            }, 300);
        } else {
            this.hideSuggestions();
        }
    }

    async getSearchSuggestions(query) {
        try {
            const response = await fetch(`/api/search/suggestions/web?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.suggestions && data.suggestions.length > 0) {
                this.displaySuggestions(data.suggestions);
            } else {
                this.hideSuggestions();
            }
        } catch (error) {
            console.error('Error getting suggestions:', error);
        }
    }

    displaySuggestions(suggestions) {
        this.suggestionsList.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const suggestionElement = this.createSuggestionElement(suggestion);
            this.suggestionsList.appendChild(suggestionElement);
        });
        
        this.showSuggestions();
    }

    createSuggestionElement(suggestion) {
        const template = document.getElementById('suggestionTemplate');
        const clone = template.content.cloneNode(true);
        
        // Set suggestion text
        clone.querySelector('.suggestion-text').textContent = suggestion.text;
        
        // Set suggestion type
        clone.querySelector('.suggestion-type').textContent = suggestion.type;
        
        // Set suggestion category
        clone.querySelector('.suggestion-category').textContent = suggestion.category;
        
        // Set icon based on type
        const iconElement = clone.querySelector('.suggestion-icon-class');
        switch (suggestion.type) {
            case 'recent_search':
                iconElement.className = 'fas fa-history text-primary';
                break;
            case 'trending':
                iconElement.className = 'fas fa-fire text-warning';
                break;
            case 'database_entity':
                iconElement.className = 'fas fa-database text-info';
                break;
            default:
                iconElement.className = 'fas fa-lightbulb text-success';
        }
        
        // Add click handler
        clone.querySelector('.use-suggestion-btn').addEventListener('click', () => {
            this.searchInput.value = suggestion.text;
            this.performSearch();
        });
        
        return clone;
    }

    showSuggestions() {
        this.suggestionsContainer.style.display = 'block';
    }

    hideSuggestions() {
        this.suggestionsContainer.style.display = 'none';
    }

    handleSearchKeydown(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.performSearch();
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.navigateSuggestions('down');
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.navigateSuggestions('up');
        }
    }

    navigateSuggestions(direction) {
        const suggestions = this.suggestionsList.querySelectorAll('.suggestion-item');
        const currentIndex = Array.from(suggestions).findIndex(item => 
            item.classList.contains('selected')
        );
        
        let newIndex;
        if (direction === 'down') {
            newIndex = currentIndex < suggestions.length - 1 ? currentIndex + 1 : 0;
        } else {
            newIndex = currentIndex > 0 ? currentIndex - 1 : suggestions.length - 1;
        }
        
        // Remove current selection
        suggestions.forEach(item => item.classList.remove('selected'));
        
        // Add new selection
        if (suggestions[newIndex]) {
            suggestions[newIndex].classList.add('selected');
        }
    }

    async performSearch() {
        if (!this.currentQuery.trim() || this.isSearching) return;
        
        this.isSearching = true;
        this.showLoadingState();
        this.hideSuggestions();
        
        try {
            const searchData = {
                query: this.currentQuery,
                categories: this.getSelectedCategories(),
                filters: this.getActiveFilters(),
                limit: 20
            };
            
            const response = await fetch('/api/search/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchData)
            });
            
            const results = await response.json();
            
            if (results.error) {
                throw new Error(results.message);
            }
            
            this.displaySearchResults(results);
            this.saveToHistory(this.currentQuery);
            
        } catch (error) {
            console.error('Search error:', error);
            this.showNotification('Search failed: ' + error.message, 'error');
            this.showNoResultsState();
        } finally {
            this.isSearching = false;
            this.hideLoadingState();
        }
    }

    displaySearchResults(results) {
        this.resultsContent.innerHTML = '';
        
        const totalResults = results.total_results || 0;
        document.getElementById('resultsCount').textContent = `${totalResults} results found`;
        
        if (totalResults === 0) {
            this.showNoResultsState();
            return;
        }
        
        // Display results by category
        Object.entries(results.results).forEach(([category, categoryResults]) => {
            if (categoryResults && categoryResults.length > 0) {
                this.displayCategoryResults(category, categoryResults);
            }
        });
        
        this.showResultsSection();
    }

    displayCategoryResults(category, results) {
        const categorySection = document.createElement('div');
        categorySection.className = 'category-section mb-4';
        
        const categoryTitle = document.createElement('h6');
        categoryTitle.className = 'category-title text-primary mb-3';
        categoryTitle.innerHTML = `<i class="fas fa-${this.getCategoryIcon(category)} me-2"></i>${this.formatCategoryName(category)} (${results.length})`;
        
        categorySection.appendChild(categoryTitle);
        
        const resultsContainer = document.createElement('div');
        resultsContainer.className = 'results-grid';
        
        results.forEach(result => {
            const resultElement = this.createResultElement(result);
            resultsContainer.appendChild(resultElement);
        });
        
        categorySection.appendChild(resultsContainer);
        this.resultsContent.appendChild(categorySection);
    }

    createResultElement(result) {
        const template = document.getElementById('searchResultTemplate');
        const clone = template.content.cloneNode(true);
        
        // Set result name
        clone.querySelector('.result-name').textContent = result.title;
        
        // Set result description
        clone.querySelector('.result-description').textContent = result.description;
        
        // Set location
        clone.querySelector('.location-text').textContent = result.metadata.location || 'N/A';
        
        // Set category
        clone.querySelector('.category-text').textContent = this.formatCategoryName(result.category);
        
        // Set rating
        clone.querySelector('.rating-text').textContent = result.metadata.rating || 'N/A';
        
        // Set relevance score
        clone.querySelector('.score-text').textContent = Math.round(result.relevance_score * 100);
        
        // Set badges
        const badgesContainer = clone.querySelector('.result-badges');
        if (result.badges && result.badges.length > 0) {
            result.badges.forEach(badge => {
                const badgeElement = document.createElement('span');
                badgeElement.className = 'badge bg-secondary me-1';
                badgeElement.textContent = badge;
                badgesContainer.appendChild(badgeElement);
            });
        }
        
        // Set view details link
        clone.querySelector('.view-details-btn').href = result.url;
        
        // Add event listeners
        clone.querySelector('.save-result-btn').addEventListener('click', () => {
            this.saveResult(result);
        });
        
        clone.querySelector('.contact-btn').addEventListener('click', () => {
            this.contactResult(result);
        });
        
        return clone;
    }

    getCategoryIcon(category) {
        const icons = {
            'suppliers': 'truck',
            'buyers': 'shopping-cart',
            'projects': 'project-diagram',
            'products': 'box',
            'certifications': 'certificate',
            'locations': 'map-marker-alt'
        };
        return icons[category] || 'tag';
    }

    formatCategoryName(category) {
        return category.charAt(0).toUpperCase() + category.slice(1);
    }

    getSelectedCategories() {
        const category = this.categoryFilter.value;
        return category ? [category] : null;
    }

    getActiveFilters() {
        const filters = [];
        
        if (this.locationFilter.value) {
            filters.push({
                type: 'location',
                value: this.locationFilter.value,
                label: this.locationFilter.options[this.locationFilter.selectedIndex].text
            });
        }
        
        if (this.certificationFilter.value) {
            filters.push({
                type: 'certification',
                value: this.certificationFilter.value,
                label: this.certificationFilter.options[this.certificationFilter.selectedIndex].text
            });
        }
        
        if (this.companySizeFilter.value) {
            filters.push({
                type: 'company_size',
                value: this.companySizeFilter.value,
                label: this.companySizeFilter.options[this.companySizeFilter.selectedIndex].text
            });
        }
        
        return filters;
    }

    handleFilterChange() {
        this.updateActiveFilters();
        if (this.currentQuery) {
            this.performSearch();
        }
    }

    updateActiveFilters() {
        const activeFilters = this.getActiveFilters();
        const filterTags = document.getElementById('filterTags');
        const activeFiltersSection = document.getElementById('activeFilters');
        
        filterTags.innerHTML = '';
        
        if (activeFilters.length > 0) {
            activeFilters.forEach(filter => {
                const tag = document.createElement('span');
                tag.className = 'badge bg-primary me-2 mb-2';
                tag.innerHTML = `${filter.label} <i class="fas fa-times ms-1" onclick="intelligentSearch.removeFilter('${filter.type}')"></i>`;
                filterTags.appendChild(tag);
            });
            activeFiltersSection.style.display = 'block';
        } else {
            activeFiltersSection.style.display = 'none';
        }
    }

    removeFilter(filterType) {
        switch (filterType) {
            case 'location':
                this.locationFilter.value = '';
                break;
            case 'certification':
                this.certificationFilter.value = '';
                break;
            case 'company_size':
                this.companySizeFilter.value = '';
                break;
        }
        this.handleFilterChange();
    }

    clearAllFilters() {
        this.locationFilter.value = '';
        this.certificationFilter.value = '';
        this.companySizeFilter.value = '';
        this.categoryFilter.value = '';
        this.handleFilterChange();
    }

    toggleFilters() {
        const isVisible = this.filtersSection.style.display !== 'none';
        this.filtersSection.style.display = isVisible ? 'none' : 'block';
    }

    startVoiceSearch() {
        if (this.voiceRecognition) {
            this.voiceRecognition.start();
        } else {
            this.showNotification('Voice recognition not supported in this browser', 'warning');
        }
    }

    showLoadingState() {
        this.loadingState.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.noResultsState.style.display = 'none';
    }

    hideLoadingState() {
        this.loadingState.style.display = 'none';
    }

    showResultsSection() {
        this.resultsSection.style.display = 'block';
        this.noResultsState.style.display = 'none';
        this.searchHistorySection.style.display = 'none';
    }

    showNoResultsState() {
        this.noResultsState.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.searchHistorySection.style.display = 'none';
    }

    async saveCurrentSearch() {
        try {
            const searchData = {
                query: this.currentQuery,
                filters: this.getActiveFilters()
            };
            
            const response = await fetch('/api/search/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Search saved successfully', 'success');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Error saving search:', error);
            this.showNotification('Failed to save search: ' + error.message, 'error');
        }
    }

    saveResult(result) {
        // This would save the result to user's favorites
        this.showNotification(`Saved: ${result.title}`, 'success');
    }

    contactResult(result) {
        // This would open contact form or email
        this.showNotification(`Contact form for: ${result.title}`, 'info');
    }

    async suggestAlternatives() {
        try {
            // This would call an API to get alternative search suggestions
            const alternatives = [
                'organic suppliers',
                'local farmers',
                'sustainable sourcing',
                'certified products'
            ];
            
            this.showNotification('Try these alternatives: ' + alternatives.join(', '), 'info');
        } catch (error) {
            console.error('Error getting alternatives:', error);
        }
    }

    showAdvancedSearch() {
        // This would open an advanced search interface
        this.showNotification('Advanced search interface coming soon', 'info');
    }

    async loadSearchHistory() {
        try {
            const response = await fetch('/api/search/recent');
            const data = await response.json();
            
            this.searchHistory = data.recent_searches || [];
            this.displaySearchHistory();
        } catch (error) {
            console.error('Error loading search history:', error);
        }
    }

    async loadTrendingSearches() {
        try {
            const response = await fetch('/api/search/trending');
            const data = await response.json();
            
            this.trendingSearches = data.trending_searches || [];
            this.displayTrendingSearches();
        } catch (error) {
            console.error('Error loading trending searches:', error);
        }
    }

    displaySearchHistory() {
        const container = document.getElementById('recentSearches');
        container.innerHTML = '';
        
        this.searchHistory.slice(0, 5).forEach(search => {
            const item = document.createElement('div');
            item.className = 'recent-search-item';
            item.innerHTML = `
                <i class="fas fa-history text-muted me-2"></i>
                <span class="search-query">${search.query}</span>
                <small class="text-muted ms-auto">${this.formatTimeAgo(search.timestamp)}</small>
            `;
            
            item.addEventListener('click', () => {
                this.searchInput.value = search.query;
                this.performSearch();
            });
            
            container.appendChild(item);
        });
    }

    displayTrendingSearches() {
        const container = document.getElementById('trendingSearches');
        container.innerHTML = '';
        
        this.trendingSearches.slice(0, 5).forEach(trend => {
            const item = document.createElement('div');
            item.className = 'trending-search-item';
            item.innerHTML = `
                <i class="fas fa-fire text-warning me-2"></i>
                <span class="search-query">${trend.query}</span>
                <small class="text-muted ms-auto">${trend.count} searches</small>
            `;
            
            item.addEventListener('click', () => {
                this.searchInput.value = trend.query;
                this.performSearch();
            });
            
            container.appendChild(item);
        });
    }

    saveToHistory(query) {
        // Add to local history
        this.searchHistory.unshift({
            query: query,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 10 searches
        this.searchHistory = this.searchHistory.slice(0, 10);
        
        this.displaySearchHistory();
    }

    formatTimeAgo(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffInMinutes = Math.floor((now - date) / (1000 * 60));
        
        if (diffInMinutes < 1) return 'Just now';
        if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
        
        const diffInHours = Math.floor(diffInMinutes / 60);
        if (diffInHours < 24) return `${diffInHours}h ago`;
        
        const diffInDays = Math.floor(diffInHours / 24);
        return `${diffInDays}d ago`;
    }

    showNotification(message, type = 'info') {
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
        const timeout = setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        this.timeouts.push(timeout);
    }

    // Memory management methods
    addEventListener(element, event, handler) {
        if (element) {
            element.addEventListener(event, handler);
            this.eventListeners.push({ element, event, handler });
        }
    }

    addTimeout(callback, delay) {
        const timeout = setTimeout(callback, delay);
        this.timeouts.push(timeout);
        return timeout;
    }

    addInterval(callback, delay) {
        const interval = setInterval(callback, delay);
        this.intervals.push(interval);
        return interval;
    }

    addObserver(target, callback, options = {}) {
        const observer = new IntersectionObserver(callback, options);
        observer.observe(target);
        this.observers.push(observer);
        return observer;
    }

    cleanup() {
        // Remove all event listeners
        this.eventListeners.forEach(({ element, event, handler }) => {
            if (element && element.removeEventListener) {
                element.removeEventListener(event, handler);
            }
        });
        
        // Clear all timeouts
        this.timeouts.forEach(timeout => clearTimeout(timeout));
        
        // Clear all intervals
        this.intervals.forEach(interval => clearInterval(interval));
        
        // Disconnect all observers
        this.observers.forEach(observer => observer.disconnect());
        
        // Clear arrays
        this.eventListeners = [];
        this.timeouts = [];
        this.intervals = [];
        this.observers = [];
        
        // Clear voice recognition
        if (this.voiceRecognition) {
            this.voiceRecognition.abort();
            this.voiceRecognition = null;
        }
        
        // Clear suggestion timeout
        if (this.suggestionTimeout) {
            clearTimeout(this.suggestionTimeout);
            this.suggestionTimeout = null;
        }
        
        console.log('IntelligentSearch: Memory cleanup completed');
    }
}

// Initialize intelligent search when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.intelligentSearch = new IntelligentSearch();
});

// Global function for filter removal
window.removeFilter = function(filterType) {
    if (window.intelligentSearch) {
        window.intelligentSearch.removeFilter(filterType);
    }
}; 