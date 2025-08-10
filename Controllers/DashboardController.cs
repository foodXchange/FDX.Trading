using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using System.Linq;
using System.Threading.Tasks;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DashboardController : ControllerBase
{
    private readonly FdxTradingContext _context;
    
    public DashboardController(FdxTradingContext context)
    {
        _context = context;
    }
    
    // GET: api/dashboard/stats
    [HttpGet("stats")]
    public async Task<ActionResult<DashboardStats>> GetDashboardStats([FromQuery] int? userId = null)
    {
        var stats = new DashboardStats();
        
        // Product Statistics
        stats.TotalProducts = await _context.Products.CountAsync();
        stats.ActiveProducts = await _context.Products.CountAsync(p => p.Status == ProductStatus.Active);
        stats.NewProductsThisWeek = await _context.Products
            .CountAsync(p => p.CreatedAt >= DateTime.Now.AddDays(-7));
        
        // Supplier Statistics
        stats.TotalSuppliers = await _context.FdxUsers.CountAsync(u => u.Type == UserType.Supplier);
        stats.ActiveSuppliers = await _context.FdxUsers
            .CountAsync(u => u.Type == UserType.Supplier && u.IsActive);
        stats.SuppliersWithProducts = await _context.Products
            .Where(p => p.SupplierId != null)
            .Select(p => p.SupplierId)
            .Distinct()
            .CountAsync();
        
        // User Statistics
        stats.TotalUsers = await _context.FdxUsers.CountAsync();
        stats.UsersByType = await _context.FdxUsers
            .GroupBy(u => u.Type)
            .Select(g => new UserTypeCount 
            { 
                Type = g.Key.ToString(), 
                Count = g.Count() 
            })
            .ToListAsync();
        stats.PendingVerifications = await _context.FdxUsers
            .CountAsync(u => u.Verification == VerificationStatus.Pending);
        
        // Category Statistics
        stats.TotalCategories = await _context.Products
            .Where(p => p.Category != null)
            .Select(p => p.Category)
            .Distinct()
            .CountAsync();
        
        // Price Proposal Statistics
        if (_context.PriceProposals != null)
        {
            stats.ActiveProposals = await _context.PriceProposals
                .CountAsync(pp => pp.Status == ProposalStatus.SourcingStage || pp.Status == ProposalStatus.PriceProposed);
            stats.PendingApprovals = await _context.PriceProposals
                .CountAsync(pp => pp.Status == ProposalStatus.PriceProposed);
        }
        
        // Purchase Request Statistics
        if (_context.ProductRequests != null)
        {
            stats.ActiveRequests = await _context.ProductRequests
                .CountAsync(pr => pr.Status == RequestStatus.Active);
            stats.PendingRequests = await _context.ProductRequests
                .CountAsync(pr => pr.Status == RequestStatus.Draft);
        }
        
        // Recent Activity
        stats.RecentImportDate = await _context.Products
            .Where(p => p.ImportedAt != null)
            .MaxAsync(p => p.ImportedAt);
        
        // Certification Statistics
        stats.KosherProducts = await _context.Products.CountAsync(p => p.IsKosher);
        stats.OrganicProducts = await _context.Products.CountAsync(p => p.IsOrganic);
        
        return Ok(stats);
    }
    
    // GET: api/dashboard/modules
    [HttpGet("modules")]
    public ActionResult<List<DashboardModule>> GetAvailableModules([FromQuery] string userRole = "Admin")
    {
        var modules = new List<DashboardModule>();
        
        // Define all modules
        var allModules = new List<DashboardModule>
        {
            new DashboardModule
            {
                Id = "products",
                Title = "Product Catalog",
                Description = "Browse and manage all products in the system",
                Icon = "📦",
                Color = "#667eea",
                Url = "/product-catalog.html",
                QuickActions = new List<QuickAction>
                {
                    new() { Label = "View Catalog", Url = "/product-catalog.html" },
                    new() { Label = "Add Product", Url = "/products.html#add" },
                    new() { Label = "Import CSV", Url = "/products.html#import" }
                },
                RequiredRole = "All"
            },
            new DashboardModule
            {
                Id = "suppliers",
                Title = "Supplier Management",
                Description = "Manage suppliers and their product catalogs",
                Icon = "🏭",
                Color = "#764ba2",
                Url = "/supplier-catalog.html",
                QuickActions = new List<QuickAction>
                {
                    new() { Label = "View Suppliers", Url = "/supplier-catalog.html" },
                    new() { Label = "Add Supplier", Url = "/users.html#add-supplier" },
                    new() { Label = "View Catalogs", Url = "/supplier-catalog.html" }
                },
                RequiredRole = "Admin,Buyer"
            },
            new DashboardModule
            {
                Id = "users",
                Title = "User Management",
                Description = "Manage system users and permissions",
                Icon = "👥",
                Color = "#f093fb",
                Url = "/users.html",
                QuickActions = new List<QuickAction>
                {
                    new() { Label = "View Users", Url = "/users.html" },
                    new() { Label = "Add User", Url = "/users.html#add" },
                    new() { Label = "Pending Verifications", Url = "/users.html#pending" }
                },
                RequiredRole = "Admin"
            },
            new DashboardModule
            {
                Id = "requests",
                Title = "Purchase Requests",
                Description = "Create and manage purchase requests",
                Icon = "🛒",
                Color = "#4facfe",
                Url = "/requests.html",
                QuickActions = new List<QuickAction>
                {
                    new() { Label = "New Request", Url = "/requests.html#new" },
                    new() { Label = "View Active", Url = "/requests.html" },
                    new() { Label = "Pending Review", Url = "/requests.html#pending" }
                },
                RequiredRole = "Admin,Buyer"
            },
            new DashboardModule
            {
                Id = "import",
                Title = "Import Center",
                Description = "Import products and data from CSV files",
                Icon = "📥",
                Color = "#00f2fe",
                Url = "/import.html",
                QuickActions = new List<QuickAction>
                {
                    new() { Label = "Import Products", Url = "/supplier-catalog.html#import" },
                    new() { Label = "Import Users", Url = "/users.html#import" },
                    new() { Label = "View History", Url = "/import.html#history" }
                },
                RequiredRole = "Admin"
            },
            new DashboardModule
            {
                Id = "reports",
                Title = "Reports & Analytics",
                Description = "View business insights and analytics",
                Icon = "📊",
                Color = "#30cfd0",
                Url = "/reports.html",
                QuickActions = new List<QuickAction>
                {
                    new() { Label = "Product Report", Url = "/reports.html#products" },
                    new() { Label = "Supplier Report", Url = "/reports.html#suppliers" },
                    new() { Label = "Export Data", Url = "/reports.html#export" }
                },
                RequiredRole = "All"
            },
            new DashboardModule
            {
                Id = "pricing",
                Title = "Price Management",
                Description = "Manage product prices and view price history",
                Icon = "💲",
                Color = "#4CAF50",
                Url = "/price-management.html",
                QuickActions = new List<QuickAction>
                {
                    new() { Label = "Update Prices", Url = "/price-management.html" },
                    new() { Label = "Price History", Url = "/price-management.html" },
                    new() { Label = "Import Prices", Url = "/price-management.html#import" }
                },
                RequiredRole = "Admin,Supplier"
            },
            new DashboardModule
            {
                Id = "proposals",
                Title = "Price Proposals",
                Description = "Manage price negotiations and proposals",
                Icon = "💰",
                Color = "#a8edea",
                Url = "/proposals.html",
                QuickActions = new List<QuickAction>
                {
                    new() { Label = "View Proposals", Url = "/proposals.html" },
                    new() { Label = "Create New", Url = "/proposals.html#new" },
                    new() { Label = "Pending Approval", Url = "/proposals.html#pending" }
                },
                RequiredRole = "Admin,Buyer,Supplier"
            },
            new DashboardModule
            {
                Id = "categories",
                Title = "Category Management",
                Description = "Organize products by categories",
                Icon = "🏷️",
                Color = "#fed6e3",
                Url = "/categories.html",
                QuickActions = new List<QuickAction>
                {
                    new() { Label = "View Categories", Url = "/categories.html" },
                    new() { Label = "Add Category", Url = "/categories.html#add" },
                    new() { Label = "Uncategorized", Url = "/categories.html#uncategorized" }
                },
                RequiredRole = "Admin"
            },
            new DashboardModule
            {
                Id = "settings",
                Title = "Settings & Profile",
                Description = "Manage your profile and system settings",
                Icon = "⚙️",
                Color = "#ffdee9",
                Url = "/settings.html",
                QuickActions = new List<QuickAction>
                {
                    new() { Label = "Edit Profile", Url = "/settings.html#profile" },
                    new() { Label = "System Settings", Url = "/settings.html#system" },
                    new() { Label = "Change Password", Url = "/settings.html#password" }
                },
                RequiredRole = "All"
            }
        };
        
        // Filter modules based on role
        foreach (var module in allModules)
        {
            if (module.RequiredRole == "All" || 
                module.RequiredRole.Contains(userRole))
            {
                modules.Add(module);
            }
        }
        
        return Ok(modules);
    }
    
    // GET: api/dashboard/activity
    [HttpGet("activity")]
    public async Task<ActionResult<List<ActivityItem>>> GetRecentActivity([FromQuery] int limit = 10)
    {
        var activities = new List<ActivityItem>();
        
        // Recent products
        var recentProducts = await _context.Products
            .OrderByDescending(p => p.CreatedAt)
            .Take(5)
            .Select(p => new ActivityItem
            {
                Type = "product_added",
                Title = $"New product added: {p.ProductName}",
                Description = $"SKU: {p.ProductCode}",
                Timestamp = p.CreatedAt,
                Icon = "📦",
                Color = "#667eea"
            })
            .ToListAsync();
        activities.AddRange(recentProducts);
        
        // Recent users
        var recentUsers = await _context.FdxUsers
            .OrderByDescending(u => u.CreatedAt)
            .Take(5)
            .Select(u => new ActivityItem
            {
                Type = "user_added",
                Title = $"New user registered: {u.CompanyName}",
                Description = $"Type: {u.Type}",
                Timestamp = u.CreatedAt,
                Icon = "👤",
                Color = "#764ba2"
            })
            .ToListAsync();
        activities.AddRange(recentUsers);
        
        // Sort by timestamp and take the requested limit
        activities = activities
            .OrderByDescending(a => a.Timestamp)
            .Take(limit)
            .ToList();
        
        return Ok(activities);
    }
    
    // GET: api/dashboard/notifications
    [HttpGet("notifications")]
    public async Task<ActionResult<List<NotificationItem>>> GetNotifications([FromQuery] int? userId = null)
    {
        var notifications = new List<NotificationItem>();
        
        // Check for pending verifications
        var pendingUsers = await _context.FdxUsers
            .CountAsync(u => u.Verification == VerificationStatus.Pending);
        if (pendingUsers > 0)
        {
            notifications.Add(new NotificationItem
            {
                Id = 1,
                Type = "warning",
                Title = "Pending User Verifications",
                Message = $"{pendingUsers} users require verification",
                Url = "/users.html#pending",
                IsRead = false,
                CreatedAt = DateTime.Now
            });
        }
        
        // Check for products without suppliers
        var orphanProducts = await _context.Products
            .CountAsync(p => p.SupplierId == null);
        if (orphanProducts > 0)
        {
            notifications.Add(new NotificationItem
            {
                Id = 2,
                Type = "info",
                Title = "Products Without Suppliers",
                Message = $"{orphanProducts} products need supplier assignment",
                Url = "/products.html#no-supplier",
                IsRead = false,
                CreatedAt = DateTime.Now
            });
        }
        
        // Check for low activity suppliers
        var inactiveSuppliers = await _context.FdxUsers
            .CountAsync(u => u.Type == UserType.Supplier && 
                           u.LastLogin < DateTime.Now.AddDays(-30));
        if (inactiveSuppliers > 0)
        {
            notifications.Add(new NotificationItem
            {
                Id = 3,
                Type = "info",
                Title = "Inactive Suppliers",
                Message = $"{inactiveSuppliers} suppliers haven't logged in for 30+ days",
                Url = "/suppliers.html#inactive",
                IsRead = false,
                CreatedAt = DateTime.Now
            });
        }
        
        return Ok(notifications);
    }
}

// DTOs
public class DashboardStats
{
    // Products
    public int TotalProducts { get; set; }
    public int ActiveProducts { get; set; }
    public int NewProductsThisWeek { get; set; }
    
    // Suppliers
    public int TotalSuppliers { get; set; }
    public int ActiveSuppliers { get; set; }
    public int SuppliersWithProducts { get; set; }
    
    // Users
    public int TotalUsers { get; set; }
    public List<UserTypeCount> UsersByType { get; set; } = new();
    public int PendingVerifications { get; set; }
    
    // Categories
    public int TotalCategories { get; set; }
    
    // Proposals
    public int ActiveProposals { get; set; }
    public int PendingApprovals { get; set; }
    
    // Requests
    public int ActiveRequests { get; set; }
    public int PendingRequests { get; set; }
    
    // Other
    public DateTime? RecentImportDate { get; set; }
    public int KosherProducts { get; set; }
    public int OrganicProducts { get; set; }
}

public class UserTypeCount
{
    public string Type { get; set; } = "";
    public int Count { get; set; }
}

public class DashboardModule
{
    public string Id { get; set; } = "";
    public string Title { get; set; } = "";
    public string Description { get; set; } = "";
    public string Icon { get; set; } = "";
    public string Color { get; set; } = "";
    public string Url { get; set; } = "";
    public List<QuickAction> QuickActions { get; set; } = new();
    public string RequiredRole { get; set; } = "";
}

public class QuickAction
{
    public string Label { get; set; } = "";
    public string Url { get; set; } = "";
}

public class ActivityItem
{
    public string Type { get; set; } = "";
    public string Title { get; set; } = "";
    public string Description { get; set; } = "";
    public DateTime Timestamp { get; set; }
    public string Icon { get; set; } = "";
    public string Color { get; set; } = "";
}

public class NotificationItem
{
    public int Id { get; set; }
    public string Type { get; set; } = "";
    public string Title { get; set; } = "";
    public string Message { get; set; } = "";
    public string Url { get; set; } = "";
    public bool IsRead { get; set; }
    public DateTime CreatedAt { get; set; }
}