// Theme Initialization - Must run before page renders
(function() {
    // Check multiple storage keys for compatibility
    const dashboardTheme = localStorage.getItem('dashboardTheme');
    const themeKey = localStorage.getItem('theme');
    const darkMode = localStorage.getItem('darkMode');
    
    // Determine the theme (priority: dashboardTheme > theme > darkMode)
    let savedTheme = 'light';
    if (dashboardTheme) {
        savedTheme = dashboardTheme;
    } else if (themeKey) {
        savedTheme = themeKey;
    } else if (darkMode === 'true') {
        savedTheme = 'dark';
    }
    
    // Apply theme immediately to prevent flash
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Also add dark-mode class for compatibility
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        // Add to body when it's available
        if (document.body) {
            document.body.classList.add('dark-mode');
        } else {
            document.addEventListener('DOMContentLoaded', function() {
                document.body.classList.add('dark-mode');
            });
        }
    }
    
    // Also add a theme class for better CSS targeting
    document.documentElement.classList.add('theme-' + savedTheme);
    
    console.log('Theme initialized:', savedTheme);
})();

// Global theme toggle function that can be called from anywhere
window.toggleGlobalTheme = function() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    // Update data attribute
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Update class
    document.documentElement.classList.remove('theme-' + currentTheme);
    document.documentElement.classList.add('theme-' + newTheme);
    
    // Save preference
    localStorage.setItem('theme', newTheme);
    
    // Update any theme toggle icons
    const icons = document.querySelectorAll('#navThemeIcon, .theme-icon');
    icons.forEach(icon => {
        if (icon) {
            icon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
        }
    });
    
    // Dispatch event
    window.dispatchEvent(new CustomEvent('themechange', { detail: newTheme }));
    
    console.log('Theme changed to:', newTheme);
    
    return newTheme;
};