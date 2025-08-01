# FoodXchange Social Media Configuration

## Overview
The social media links in the footer are configured in the `foodxchange/routes/footer_routes.py` file.

## Current Configuration

```python
SOCIAL_MEDIA_LINKS = {
    "linkedin": "https://www.linkedin.com/company/foodxchange",
    "facebook": "https://www.facebook.com/foodxchange",
    "twitter": "https://x.com/foodxchange",
    "instagram": "https://www.instagram.com/foodxchange",
    "youtube": "https://www.youtube.com/@foodxchange"
}
```

## How to Update Social Media Links

1. Open the file: `foodxchange/routes/footer_routes.py`
2. Find the `SOCIAL_MEDIA_LINKS` dictionary (around line 20-27)
3. Update the URLs with your actual social media profiles
4. Save the file and restart the server

## Features Implemented

✅ **5 Social Media Platforms**
- LinkedIn
- Facebook
- X (Twitter)
- Instagram
- YouTube

✅ **Professional Design**
- Hover effects with brand colors
- Circular icons with smooth transitions
- Opens in new tabs with `target="_blank"`
- Accessibility labels for screen readers

✅ **Brand-Specific Hover Colors**
- LinkedIn: #0077B5
- Facebook: #1877F2
- X (Twitter): #000000
- Instagram: Gradient (orange to purple)
- YouTube: #FF0000

✅ **Mobile Responsive**
- Icons scale appropriately on all devices
- Touch-friendly size (40x40px)

## File Locations

- **Configuration**: `foodxchange/routes/footer_routes.py`
- **HTML Template**: `foodxchange/templates/components/footer.html`
- **CSS Styles**: `foodxchange/static/css/style.css` (lines 518-564)

## Next Steps

1. Create your social media accounts if you haven't already
2. Update the URLs in the configuration
3. Test all links to ensure they work correctly
4. Consider adding additional platforms if needed (TikTok, Pinterest, etc.)

## Adding New Social Media Platforms

To add a new platform:

1. Add the URL to `SOCIAL_MEDIA_LINKS` in `footer_routes.py`
2. Add the icon HTML in `footer.html`:
   ```html
   <a href="URL" target="_blank" rel="noopener noreferrer" aria-label="Platform Name">
       <i class="fab fa-icon-name"></i>
   </a>
   ```
3. Add hover color in `style.css`:
   ```css
   .social-links a[aria-label="Platform Name"]:hover {
       background-color: #BRANDCOLOR;
   }
   ```

## Notes

- All links use Font Awesome icons (already included in the project)
- The current URLs are placeholders - replace with your actual social media profiles
- The configuration is centralized for easy management