# FDX Trading Design System & Standards

## Overview
This document defines the design standards, layout patterns, and component specifications for all FDX Trading web pages to ensure consistency across the application.

## Core Principles
- **Dashboard-style alignment** - All pages use consistent container spacing
- **Modern UI with gradients** - Purple gradient backgrounds and card-based layouts
- **SVG Icons only** - No emoji icons, all icons are inline SVG
- **Dark mode support** - All pages must support dark mode
- **Responsive design** - Mobile-first approach with proper breakpoints

## Page Structure

### 1. Base HTML Template
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title - FDX Trading</title>
    
    <!-- Theme Initialization (must be first) -->
    <script src="/js/theme-init.js"></script>
    
    <!-- Modern UI System -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/smart-navigation.css?v=3">
    <link rel="stylesheet" href="/css/modern-ui.css">
</head>
<body>
    <div class="page-container">
        <!-- Page content here -->
    </div>
    
    <!-- Load Smart Navigation -->
    <script src="/js/smart-navigation.js"></script>
    <script src="/js/universal-dark-mode.js"></script>
</body>
</html>
```

### 2. Container Alignment (CRITICAL)
```css
/* Dashboard-style container - MUST be used on all pages */
.page-container {
    padding: 24px;
    max-width: 1600px;
    margin: 0 auto;
}
```

### 3. Page Header Component
```html
<div class="page-header">
    <div class="header-content">
        <div>
            <h1 class="page-title">Page Title</h1>
            <p class="page-subtitle">Brief description of the page</p>
        </div>
        <div class="header-actions">
            <!-- Action buttons here -->
        </div>
    </div>
</div>
```

```css
.page-header {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    border-radius: 20px;
    padding: 32px;
    color: white;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.page-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 60%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    transform: rotate(30deg);
}
```

## Color Palette

### CSS Variables (Required in all pages)
```css
:root {
    /* Primary Brand Colors */
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --primary-light: #818cf8;
    --secondary: #ec4899;
    --secondary-light: #f472b6;
    
    /* Status Colors */
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --info: #3b82f6;
    
    /* Gray Scale */
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    
    /* Backgrounds */
    --bg-primary: #ffffff;
    --bg-secondary: #f9fafb;
    --bg-tertiary: #f3f4f6;
    
    /* Text Colors */
    --text-primary: #1f2937;
    --text-secondary: #4b5563;
    --text-tertiary: #6b7280;
    --text-on-primary: #ffffff;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
```

## Component Standards

### 1. Statistics Cards
```html
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-icon">
            <svg><!-- SVG icon here --></svg>
        </div>
        <div class="stat-content">
            <div class="stat-value">123</div>
            <div class="stat-label">Label</div>
        </div>
    </div>
</div>
```

### 2. Content Cards
```html
<div class="content-card">
    <div class="card-header">
        <h2 class="card-title">
            <svg><!-- Icon --></svg>
            Card Title
        </h2>
        <div class="card-actions">
            <!-- Action buttons -->
        </div>
    </div>
    <div class="card-content">
        <!-- Content here -->
    </div>
</div>
```

### 3. Buttons
```html
<!-- Primary Button -->
<button class="btn btn-primary">
    <svg><!-- Icon --></svg>
    Button Text
</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">
    <svg><!-- Icon --></svg>
    Button Text
</button>

<!-- Success Button -->
<button class="btn btn-success">
    <svg><!-- Icon --></svg>
    Button Text
</button>

<!-- Danger Button -->
<button class="btn btn-danger">
    <svg><!-- Icon --></svg>
    Button Text
</button>
```

### 4. SVG Icons (NEVER use emoji)
```html
<!-- Standard icon sizes -->
<svg class="icon-svg" width="20" height="20">...</svg>
<svg class="icon-svg-small" width="16" height="16">...</svg>
<svg class="icon-svg-large" width="24" height="24">...</svg>
<svg class="icon-svg-xlarge" width="32" height="32">...</svg>
```

Common icons to use:
- **Add/Create**: `<path d="M12 4v16m8-8H4"/>`
- **Edit**: `<path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>`
- **Delete**: `<path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>`
- **Search**: `<path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>`
- **Filter**: `<path d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>`
- **Calendar**: `<path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>`
- **User**: `<path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>`
- **Check**: `<path d="M5 13l4 4L19 7"/>`
- **Close**: `<path d="M6 18L18 6M6 6l12 12"/>`

## Dark Mode Requirements

### Body Styles
```css
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

body.dark-mode {
    background: linear-gradient(135deg, #0f1419 0%, #1a1d24 100%);
}
```

### Component Dark Mode
```css
/* Card dark mode */
.content-card {
    background: white;
}

body.dark-mode .content-card {
    background: #1e2028;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Table hover dark mode */
tbody tr:hover {
    background: #f3f4f6;
}

body.dark-mode tbody tr:hover {
    background: rgba(99, 102, 241, 0.08);
}
```

## Layout Patterns

### 1. Grid Layouts
```css
/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
}

/* Content Grid */
.content-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
}
```

### 2. Responsive Breakpoints
```css
/* Mobile */
@media (max-width: 768px) {
    .page-container {
        padding: 16px;
    }
    
    .page-header {
        padding: 24px;
    }
    
    .page-title {
        font-size: 28px;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
```

## Typography

### Font Stack
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Font Sizes
- **Page Title**: 36px, weight 800
- **Section Title**: 24px, weight 700
- **Card Title**: 20px, weight 700
- **Body Text**: 14px, weight 400
- **Small Text**: 12px, weight 500
- **Labels**: 13px, weight 600, uppercase

## Animation Standards

### Transitions
```css
/* Standard transition */
transition: all 0.3s ease;

/* Fast transition */
transition: all 0.2s ease;

/* Hover lift effect */
.card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}
```

### Page Load Animation
```css
@keyframes fadeIn {
    from { 
        opacity: 0; 
        transform: translateY(10px); 
    }
    to { 
        opacity: 1; 
        transform: translateY(0); 
    }
}

.animate-fade-in {
    animation: fadeIn 0.3s ease-out;
}
```

## Navigation Integration

### Smart Navigation
- All pages automatically include `/js/smart-navigation.js`
- No custom navbar components needed
- Navigation is handled by the smart navigation system

### Command Palette
- Accessible via Cmd/Ctrl + K
- No need to add command palette HTML to pages
- Handled by smart navigation

## File Naming Conventions

### HTML Files
- Use kebab-case: `user-profile.html`, `request-detail.html`
- No version suffixes in production: avoid `-v2.html`, `-old.html`
- Test files should be in a separate test directory

### CSS/JS Files
- System files: `smart-navigation.css`, `modern-ui.css`
- Page-specific styles should be inline in `<style>` tags
- Shared utilities: `universal-dark-mode.js`

## Checklist for New Pages

When creating a new page, ensure:

- [ ] Uses the standard HTML template structure
- [ ] Includes theme initialization script first
- [ ] Has `.page-container` wrapper with correct padding/max-width
- [ ] Includes all CSS variables in `:root`
- [ ] Has gradient page header with title and subtitle
- [ ] Uses SVG icons only (no emojis)
- [ ] Supports dark mode with proper contrast
- [ ] Content cards have proper shadows and borders
- [ ] Buttons follow the design system
- [ ] Responsive breakpoints are implemented
- [ ] Smart navigation is loaded
- [ ] Universal dark mode script is included
- [ ] Follows the Inter font family
- [ ] Has proper hover states and transitions
- [ ] Tables have alternating row colors on hover
- [ ] Forms use consistent styling
- [ ] Loading states use spinners or skeletons

## Common Mistakes to Avoid

1. **DON'T use emoji icons** - Always use SVG
2. **DON'T create custom navbars** - Use smart navigation
3. **DON'T forget dark mode** - Test all components in dark mode
4. **DON'T use inline styles for layout** - Use the design system classes
5. **DON'T forget the page container** - Always wrap content properly
6. **DON'T use pixels for responsive design** - Use rem/em units
7. **DON'T skip hover states** - All interactive elements need feedback
8. **DON'T use harsh blacks** - Use the gray scale for better contrast

## Implementation Priority

When updating existing pages:

1. **First**: Add container alignment (padding: 24px, max-width: 1600px)
2. **Second**: Replace emoji icons with SVG
3. **Third**: Add gradient page header
4. **Fourth**: Update color scheme to use CSS variables
5. **Fifth**: Ensure dark mode support
6. **Sixth**: Add responsive breakpoints
7. **Last**: Polish animations and transitions

## Reference Implementation

The best reference for implementation is:
- `template-design.html` - Complete design system template
- `dashboard.html` - Production implementation
- `users.html` - Table and data display patterns
- `analytics.html` - Charts and KPI cards
- `settings.html` - Forms and settings patterns

---

*Last Updated: December 2024*
*Version: 1.0*