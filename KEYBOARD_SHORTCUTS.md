# FDX Trading - Keyboard Shortcuts Guide

## 🚀 Quick Reference

Press `Ctrl + /` (or `Cmd + /` on Mac) anywhere in the application to see the keyboard shortcuts help popup.

## 🌐 Global Navigation Shortcuts

These shortcuts work from any page in the application:

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Alt + H` | Go to Dashboard | Navigate to the main dashboard |
| `Alt + R` | Go to Requests | Open the requests page |
| `Alt + P` | Go to Products | Open the products catalog |
| `Alt + S` | Go to Suppliers | Open the supplier catalog |
| `Alt + U` | Go to Users | Open user management |
| `Alt + M` | Go to Price Management | Open pricing management |

## 📝 Form Shortcuts

Available on all form pages (Create/Edit Request, Add Product, etc.):

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl/Cmd + S` | Save | Save the current form as draft |
| `Ctrl/Cmd + Enter` | Save & Submit | Save and publish/submit the form |
| `Escape` | Cancel | Cancel current operation and go back |
| `Alt + A` | Add Item | Add a new item to the current form |
| `Alt + D` | Duplicate Item | Duplicate the last item in the list |

## 🔍 Search & Filter Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl/Cmd + K` | Focus Search | Jump to the search box on the current page |
| `1` | Filter: Draft | Quick filter for draft status (on list pages) |
| `2` | Filter: Active | Quick filter for active status (on list pages) |
| `3` | Filter: Closed | Quick filter for closed status (on list pages) |

## ➕ Quick Actions

Context-aware shortcuts that adapt to the current page:

| Shortcut | Action | Context |
|----------|--------|---------|
| `Ctrl/Cmd + N` | New Item | Creates new request/product based on current page |
| `Alt + A` | Add Item | Adds item in forms, focuses product name field |
| `Alt + D` | Duplicate | Duplicates items in forms or records in lists |

## 📄 Page-Specific Shortcuts

### Request Create/Edit Page
- `Ctrl/Cmd + S` - Save as draft
- `Ctrl/Cmd + Enter` - Save and publish request
- `Alt + A` - Add new product item
- `Alt + D` - Duplicate last item
- `F1` - Show form-specific help

### Request Detail Page
- `E` - Edit request
- `D` - Duplicate request
- `Delete` - Delete request (with confirmation)
- `Escape` - Go back to requests list

### Products Page
- `Ctrl/Cmd + N` - Add new product
- `/` - Focus on search
- `F` - Open filters panel

### Dashboard
- `1-6` - Quick navigate to dashboard cards
- `R` - Refresh dashboard data
- `N` - View notifications

## ❓ Help Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl/Cmd + /` | Show Help | Display keyboard shortcuts help popup |
| `F1` | Context Help | Show help relevant to the current page |

## 💡 Pro Tips

1. **Mac Users**: Use `Cmd` instead of `Ctrl` for all control-based shortcuts
2. **Escape Key**: Press `Escape` to close any modal or popup dialog
3. **Tab Navigation**: Use `Tab` and `Shift+Tab` to navigate between form fields
4. **Number Keys**: On list pages, use number keys for quick status filtering
5. **Search Focus**: `Ctrl/Cmd + K` works on any page with a search box

## 🔧 Implementation

To add keyboard shortcuts to any page, include the global shortcuts script:

```html
<script src="/js/keyboard-shortcuts.js"></script>
```

This will automatically enable all global navigation shortcuts and common patterns.

## 📱 Accessibility Notes

- All shortcuts are designed to not conflict with browser defaults
- Screen reader users can disable shortcuts if needed
- All actions available via shortcuts are also accessible through UI buttons
- Shortcuts respect form field focus (won't trigger when typing in inputs)

## 🎯 Recommended Workflow Shortcuts

### Creating a New Request (Speed Workflow)
1. `Alt + R` - Go to Requests
2. `Ctrl + N` - New Request
3. Fill in details
4. `Alt + A` - Add items quickly
5. `Ctrl + S` - Save draft
6. `Ctrl + Enter` - When ready to publish

### Quick Navigation Flow
1. `Alt + H` - Dashboard
2. `1-6` - Select card
3. `Alt + R/P/S` - Jump to specific section
4. `Ctrl + K` - Search immediately

---

**Note**: These shortcuts are designed to enhance productivity while maintaining accessibility. All actions remain available through the standard UI for users who prefer mouse navigation.