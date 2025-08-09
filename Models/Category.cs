namespace FDX.Trading.Models;

public enum CategoryType
{
    // Contractor/Expert Categories (1-99)
    CourierLogistics = 1,          // UPS, DHL, FedEx, TNT, EMS
    KosherCertification = 2,        // Kosher certification agencies
    FoodManufacturing = 3,          // Food producers and processors
    PackagingSupplies = 4,          // Packaging and containers
    ITServices = 5,                 // Technology and software
    QualityControl = 6,             // QC and testing services
    ImportExport = 7,               // Import/Export services
    ConsultingServices = 8,         // Business consulting
    MarketingServices = 9,          // Marketing and advertising
    LegalServices = 10,             // Legal and compliance
    
    // Buyer Categories (101-199)  
    SupermarketChain = 101,         // Carrefour, Shufersal, etc.
    ConvenienceStore = 102,         // Dor Alon, am:pm, Alonit
    WholesaleDistributor = 103,     // H. Cohen, wholesale companies
    OnlineRetailer = 104,           // E-commerce platforms
    HotelRestaurant = 105,          // HORECA sector
    InstitutionalBuyer = 106,       // Schools, hospitals, government
    SpecialtyStore = 107,           // Organic, kosher, health stores
    GroceryStore = 108,             // Local grocery stores
    FoodServiceProvider = 109,      // Catering, meal services
    RetailChain = 110,              // General retail chains
    
    // General/Unknown
    Other = 999
}

public class CategoryInfo
{
    public CategoryType Type { get; set; }
    public string Name { get; set; } = "";
    public string DisplayName { get; set; } = "";
    public string Description { get; set; } = "";
    public string Icon { get; set; } = "";
    public string ColorCode { get; set; } = "";
    public bool IsContractor { get; set; }
    public string[] Keywords { get; set; } = Array.Empty<string>();
}

public static class CategoryData
{
    public static readonly Dictionary<CategoryType, CategoryInfo> Categories = new()
    {
        // Contractor Categories
        [CategoryType.CourierLogistics] = new CategoryInfo
        {
            Type = CategoryType.CourierLogistics,
            Name = "Courier & Logistics",
            DisplayName = "Courier/Logistics",
            Description = "Shipping, delivery, and logistics services",
            Icon = "📦",
            ColorCode = "#FF6B6B",
            IsContractor = true,
            Keywords = new[] { "courier", "delivery", "shipping", "logistics", "postal", "express", "freight" }
        },
        [CategoryType.KosherCertification] = new CategoryInfo
        {
            Type = CategoryType.KosherCertification,
            Name = "Kosher Certification",
            DisplayName = "Kosher",
            Description = "Kosher certification and supervision services",
            Icon = "✡️",
            ColorCode = "#4ECDC4",
            IsContractor = true,
            Keywords = new[] { "kosher", "rabbi", "certification", "hashgacha", "badatz", "religious" }
        },
        [CategoryType.FoodManufacturing] = new CategoryInfo
        {
            Type = CategoryType.FoodManufacturing,
            Name = "Food Manufacturing",
            DisplayName = "Manufacturing",
            Description = "Food production and processing",
            Icon = "🏭",
            ColorCode = "#95E77E",
            IsContractor = true,
            Keywords = new[] { "manufacturing", "production", "processing", "factory", "producer", "maker" }
        },
        
        // Buyer Categories
        [CategoryType.SupermarketChain] = new CategoryInfo
        {
            Type = CategoryType.SupermarketChain,
            Name = "Supermarket Chain",
            DisplayName = "Supermarket",
            Description = "Large supermarket chains",
            Icon = "🛒",
            ColorCode = "#6C5CE7",
            IsContractor = false,
            Keywords = new[] { "supermarket", "hypermarket", "grocery chain", "retail chain" }
        },
        [CategoryType.ConvenienceStore] = new CategoryInfo
        {
            Type = CategoryType.ConvenienceStore,
            Name = "Convenience Store",
            DisplayName = "Convenience",
            Description = "Convenience stores and gas stations",
            Icon = "🏪",
            ColorCode = "#00B894",
            IsContractor = false,
            Keywords = new[] { "convenience", "gas station", "fuel", "kiosk", "minimarket", "alonit", "am:pm" }
        },
        [CategoryType.WholesaleDistributor] = new CategoryInfo
        {
            Type = CategoryType.WholesaleDistributor,
            Name = "Wholesale Distributor",
            DisplayName = "Wholesale",
            Description = "Wholesale and distribution companies",
            Icon = "📊",
            ColorCode = "#FDCB6E",
            IsContractor = false,
            Keywords = new[] { "wholesale", "distributor", "distribution", "import", "marketing", "supplier" }
        },
        [CategoryType.SpecialtyStore] = new CategoryInfo
        {
            Type = CategoryType.SpecialtyStore,
            Name = "Specialty Store",
            DisplayName = "Specialty",
            Description = "Specialty food stores (organic, kosher, etc.)",
            Icon = "🌿",
            ColorCode = "#55EFC4",
            IsContractor = false,
            Keywords = new[] { "organic", "natural", "health", "specialty", "gourmet", "boutique" }
        },
        [CategoryType.Other] = new CategoryInfo
        {
            Type = CategoryType.Other,
            Name = "Other",
            DisplayName = "Other",
            Description = "Uncategorized",
            Icon = "📋",
            ColorCode = "#B2BEC3",
            IsContractor = false,
            Keywords = Array.Empty<string>()
        }
    };
    
    public static CategoryInfo GetCategory(CategoryType type)
    {
        return Categories.TryGetValue(type, out var category) 
            ? category 
            : Categories[CategoryType.Other];
    }
    
    public static string GetDisplayName(CategoryType type)
    {
        return GetCategory(type).DisplayName;
    }
    
    public static string GetColorCode(CategoryType type)
    {
        return GetCategory(type).ColorCode;
    }
}