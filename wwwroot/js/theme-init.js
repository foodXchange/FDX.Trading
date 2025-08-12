// Theme Initialization - Must run before page renders
(function() {
    // Apply theme immediately to prevent flash
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Also add a class for better CSS targeting
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