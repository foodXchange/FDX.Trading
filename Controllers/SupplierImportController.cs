using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using FDX.Trading.Services;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.DependencyInjection;
using OfficeOpenXml;
using System.IO;
using System.Text.RegularExpressions;

namespace FDX.Trading.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SupplierImportController : ControllerBase
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<SupplierImportController> _logger;
        private readonly IServiceProvider _serviceProvider;

        public SupplierImportController(
            FdxTradingContext context, 
            ILogger<SupplierImportController> logger,
            IServiceProvider serviceProvider)
        {
            _context = context;
            _logger = logger;
            _serviceProvider = serviceProvider;
        }

        [HttpDelete("delete-all-suppliers")]
        public async Task<IActionResult> DeleteAllSuppliers()
        {
            try
            {
                // Get all suppliers
                var suppliers = await _context.FdxUsers
                    .Where(u => u.Type == UserType.Supplier)
                    .ToListAsync();
                
                if (suppliers.Any())
                {
                    // Delete all products first
                    var allProducts = await _context.SupplierProductCatalogs.ToListAsync();
                    _context.SupplierProductCatalogs.RemoveRange(allProducts);
                    
                    // Delete all suppliers
                    _context.FdxUsers.RemoveRange(suppliers);
                    
                    await _context.SaveChangesAsync();
                    
                    return Ok(new { 
                        success = true, 
                        message = $"Deleted {suppliers.Count} suppliers and {allProducts.Count} products" 
                    });
                }
                
                return Ok(new { success = true, message = "No suppliers to delete" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to delete all suppliers");
                return StatusCode(500, new { error = ex.Message });
            }
        }

        [HttpPost("import-excel-maximum")]
        public async Task<IActionResult> ImportMaximumSuppliers([FromQuery] string filePath = @"C:\Users\fdxadmin\Downloads\Suppliers_Optimized.xlsx")
        {
            // First, clear existing suppliers for fresh import
            var existingSuppliers = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier)
                .ToListAsync();
            
            if (existingSuppliers.Any())
            {
                var supplierIds = existingSuppliers.Select(s => s.Id).ToList();
                
                // Delete all related data first
                var allProducts = await _context.SupplierProductCatalogs.ToListAsync();
                _context.SupplierProductCatalogs.RemoveRange(allProducts);
                
                // Delete brief suppliers
                var briefSuppliers = await _context.BriefSuppliers
                    .Where(bs => supplierIds.Contains(bs.SupplierId))
                    .ToListAsync();
                if (briefSuppliers.Any())
                    _context.BriefSuppliers.RemoveRange(briefSuppliers);
                
                // Now delete suppliers
                _context.FdxUsers.RemoveRange(existingSuppliers);
                await _context.SaveChangesAsync();
                _logger.LogInformation($"Cleared {existingSuppliers.Count} existing suppliers and related data");
            }

            if (!System.IO.File.Exists(filePath))
            {
                return BadRequest($"File not found: {filePath}");
            }

            var report = new ImportReport { StartTime = DateTime.Now };
            var uniqueNames = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var suppliersToAdd = new List<User>();
            
            try
            {
                ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
                using var package = new ExcelPackage(new FileInfo(filePath));
                var worksheet = package.Workbook.Worksheets[0];
                
                if (worksheet == null)
                    return BadRequest("No worksheet found");

                var rowCount = worksheet.Dimension?.Rows ?? 0;
                _logger.LogInformation($"Processing {rowCount} rows for maximum import");

                // Process ALL rows (skip header)
                for (int row = 2; row <= rowCount; row++)
                {
                    try
                    {
                        var supplierName = worksheet.Cells[row, 1].Text?.Trim();
                        if (string.IsNullOrEmpty(supplierName) || uniqueNames.Contains(supplierName))
                            continue;

                        // Extract data
                        var website = worksheet.Cells[row, 4].Text?.Trim();
                        var description = worksheet.Cells[row, 5].Text?.Trim();
                        var category = worksheet.Cells[row, 6].Text?.Trim();
                        var country = worksheet.Cells[row, 47].Text?.Trim();
                        
                        // Only skip VERY obvious non-food (minimal filtering)
                        var skipKeywords = new[] { "software", "bank", "insurance", "consulting", "law firm", "accounting" };
                        var nameCheck = supplierName.ToLower();
                        if (skipKeywords.Any(k => nameCheck.Contains(k)))
                            continue;

                        var supplier = new User
                        {
                            CompanyName = TruncateString(supplierName, 200),
                            Username = GenerateUniqueUsername(supplierName, uniqueNames),
                            Password = "FDX2025!",
                            Email = $"{GenerateUsername(supplierName)}@supplier.fdx",
                            Type = UserType.Supplier,
                            Country = TruncateString(country ?? "Unknown", 100),
                            Website = NormalizeWebsite(website) ?? "",
                            Category = TruncateString(category ?? "General Food", 100),
                            FullDescription = TruncateString(description ?? "", 2000),
                            IsActive = true,
                            CreatedAt = DateTime.Now,
                            DataComplete = !string.IsNullOrEmpty(website),
                            ImportedAt = DateTime.Now,
                            ImportNotes = "Maximum import from Excel"
                        };

                        // Auto-generate products based on category/description
                        if (!string.IsNullOrEmpty(category) || !string.IsNullOrEmpty(description))
                        {
                            var products = GenerateProductsForSupplier(supplier.CompanyName, category, description);
                            supplier.ExtractedProducts = products;
                            report.ProductsFromDescriptions += products.Count;
                        }

                        suppliersToAdd.Add(supplier);
                        uniqueNames.Add(supplierName);
                        
                        // Save in larger batches for speed
                        if (suppliersToAdd.Count >= 100)
                        {
                            await SaveSuppliersBatch(suppliersToAdd, report);
                            suppliersToAdd.Clear();
                        }
                    }
                    catch (Exception ex)
                    {
                        _logger.LogWarning($"Row {row} skipped: {ex.Message}");
                    }
                }

                // Save remaining
                if (suppliersToAdd.Any())
                {
                    await SaveSuppliersBatch(suppliersToAdd, report);
                }

                report.EndTime = DateTime.Now;
                report.Success = true;
                report.TotalRows = rowCount - 1;

                _logger.LogInformation($"Maximum import completed: {report.ImportedCount} suppliers imported");
                return Ok(report);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Maximum import failed");
                report.Success = false;
                report.Errors.Add(ex.Message);
                return StatusCode(500, report);
            }
        }
        
        [HttpPost("import-excel")]
        public async Task<IActionResult> ImportSuppliersFromExcel([FromQuery] string filePath = @"C:\Users\fdxadmin\Downloads\Suppliers_Optimized.xlsx")
        {
            if (!System.IO.File.Exists(filePath))
            {
                return BadRequest($"File not found: {filePath}");
            }

            var report = new ImportReport { StartTime = DateTime.Now };
            
            try
            {
                // Set EPPlus license context
                ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
                
                using var package = new ExcelPackage(new FileInfo(filePath));
                var worksheet = package.Workbook.Worksheets[0];
                
                if (worksheet == null)
                {
                    return BadRequest("No worksheet found in Excel file");
                }

                var rowCount = worksheet.Dimension?.Rows ?? 0;
                var colCount = worksheet.Dimension?.Columns ?? 0;
                
                _logger.LogInformation($"Processing Excel file with {rowCount} rows and {colCount} columns");

                // Get existing suppliers for comparison (case-insensitive)
                var existingSuppliers = await _context.FdxUsers
                    .Where(u => u.Type == UserType.Supplier)
                    .Select(u => u.CompanyName.ToLower())
                    .ToListAsync();
                
                var existingSet = new HashSet<string>(existingSuppliers);
                var suppliersToAdd = new List<User>();
                var batchSize = 20; // Smaller batch size for safer processing

                // Process rows (skip header)
                for (int row = 2; row <= rowCount; row++)
                {
                    try
                    {
                        // Get supplier name from first column
                        var supplierName = worksheet.Cells[row, 1].Text?.Trim();
                        
                        if (string.IsNullOrEmpty(supplierName))
                        {
                            report.SkippedRows++;
                            continue;
                        }

                        // Check if already exists (case-insensitive)
                        if (existingSet.Contains(supplierName.ToLower()))
                        {
                            report.AlreadyExists++;
                            continue;
                        }

                        // Extract other fields from Excel
                        var website = worksheet.Cells[row, 4].Text?.Trim(); // Company website column
                        var description = worksheet.Cells[row, 5].Text?.Trim(); // Description column
                        var category = worksheet.Cells[row, 6].Text?.Trim(); // Product Category
                        var address = worksheet.Cells[row, 7].Text?.Trim(); // Address
                        var email = worksheet.Cells[row, 8].Text?.Trim(); // Company Email
                        var country = worksheet.Cells[row, 47].Text?.Trim(); // Supplier's Country
                        var phone = worksheet.Cells[row, 42].Text?.Trim(); // Phone
                        
                        // For suppliers without websites, use placeholder
                        if (string.IsNullOrWhiteSpace(website))
                        {
                            website = ""; // Will set as empty string, not null
                            _logger.LogInformation($"Supplier without website: {supplierName}");
                        }
                        
                        // Be less strict - only skip obvious non-food companies
                        // Most suppliers in a food supplier Excel are likely food-related
                        if (IsDefinitelyNonFood(supplierName, category, description))
                        {
                            report.SkippedRows++;
                            _logger.LogInformation($"Skipped non-food company: {supplierName}");
                            continue;
                        }
                        
                        // Create new supplier with field length limits
                        var supplier = new User
                        {
                            CompanyName = TruncateString(supplierName, 200),
                            Username = GenerateUsername(supplierName),
                            Password = "FDX2025!", // Default password
                            Email = !string.IsNullOrEmpty(email) ? TruncateString(email, 100) : $"{GenerateUsername(supplierName)}@supplier.fdx",
                            Type = UserType.Supplier,
                            Country = TruncateString(country ?? "", 100),
                            Address = TruncateString(address ?? "", 500),
                            Website = NormalizeWebsite(website) ?? "",
                            PhoneNumber = TruncateString(phone ?? "", 50),
                            Category = TruncateString(category ?? "", 100),
                            FullDescription = TruncateString(description ?? "", 2000),
                            IsActive = true,
                            CreatedAt = DateTime.Now,
                            DataComplete = !string.IsNullOrEmpty(website),
                            ImportedAt = DateTime.Now,
                            ImportNotes = "Imported from Excel - Suppliers_Optimized.xlsx"
                        };

                        suppliersToAdd.Add(supplier);
                        existingSet.Add(supplierName.ToLower());
                        
                        // Extract products from description if available
                        if (!string.IsNullOrEmpty(description))
                        {
                            var products = ExtractProductsFromDescription(description, category);
                            if (products.Any())
                            {
                                report.ProductsFromDescriptions += products.Count;
                                // These will be saved after supplier is created
                                supplier.ExtractedProducts = products;
                            }
                        }

                        // Save in batches
                        if (suppliersToAdd.Count >= batchSize)
                        {
                            await SaveSuppliersWithProducts(suppliersToAdd, report);
                            suppliersToAdd.Clear();
                        }
                    }
                    catch (Exception ex)
                    {
                        _logger.LogError(ex, $"Error processing row {row}");
                        report.Errors.Add($"Row {row}: {ex.Message}");
                        report.FailedRows++;
                    }

                    // Progress reporting
                    if (row % 500 == 0)
                    {
                        _logger.LogInformation($"Progress: {row}/{rowCount} rows processed");
                    }
                }

                // Save remaining suppliers
                if (suppliersToAdd.Any())
                {
                    await SaveSuppliersWithProducts(suppliersToAdd, report);
                }

                report.EndTime = DateTime.Now;
                report.Success = true;
                report.TotalRows = rowCount - 1; // Exclude header

                _logger.LogInformation($"Import completed: {report.ImportedCount} new suppliers added");

                return Ok(report);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to import suppliers from Excel");
                report.EndTime = DateTime.Now;
                report.Success = false;
                report.Errors.Add($"Fatal error: {ex.Message}");
                return StatusCode(500, report);
            }
        }

        [HttpGet("import-status")]
        public async Task<IActionResult> GetImportStatus()
        {
            var totalSuppliers = await _context.FdxUsers.CountAsync(u => u.Type == UserType.Supplier);
            var suppliersWithWebsites = await _context.FdxUsers
                .CountAsync(u => u.Type == UserType.Supplier && !string.IsNullOrEmpty(u.Website));
            
            return Ok(new
            {
                totalSuppliers,
                suppliersWithWebsites,
                percentWithWebsites = totalSuppliers > 0 ? (suppliersWithWebsites * 100.0 / totalSuppliers) : 0
            });
        }

        [HttpPost("comprehensive-cleanup")]
        public async Task<IActionResult> ComprehensiveSupplierCleanup()
        {
            try
            {
                var cleanupService = new SupplierCleanupService(_context, 
                    _logger as ILogger<SupplierCleanupService> ?? new Logger<SupplierCleanupService>(new LoggerFactory()),
                    _serviceProvider.GetService<AutomatedProductExtractor>());
                
                var result = await cleanupService.PerformComprehensiveCleanup();
                
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Comprehensive cleanup failed");
                return StatusCode(500, new { error = ex.Message });
            }
        }
        
        [HttpPost("clean-non-food")]
        public async Task<IActionResult> CleanNonFoodSuppliers()
        {
            var report = new CleanupReport { StartTime = DateTime.Now };
            
            try
            {
                // Get all suppliers
                var suppliers = await _context.FdxUsers
                    .Where(u => u.Type == UserType.Supplier)
                    .ToListAsync();
                
                var nonFoodKeywords = new[]
                {
                    // Technology & Software
                    "software", "technology", "tech", "IT", "digital", "cyber", "computer", "data",
                    "cloud", "AI", "machine learning", "blockchain", "crypto", "fintech", "app",
                    
                    // Finance & Banking
                    "bank", "finance", "insurance", "credit", "loan", "mortgage", "investment",
                    "capital", "fund", "equity", "securities", "forex", "trading platform",
                    
                    // Manufacturing (non-food)
                    "automotive", "car", "vehicle", "machinery", "equipment", "tool", "industrial",
                    "steel", "metal", "plastic", "chemical", "pharma", "medical device", "electronics",
                    
                    // Services
                    "consulting", "legal", "law firm", "accounting", "audit", "recruitment", "HR",
                    "marketing agency", "advertising", "PR agency", "design studio", "architect",
                    
                    // Real Estate & Construction  
                    "real estate", "property", "construction", "building", "contractor", "cement",
                    
                    // Logistics & Transport (non-food specific)
                    "freight", "shipping line", "airlines", "aviation", "rail", "taxi", "uber",
                    
                    // Energy & Utilities
                    "energy", "power", "electricity", "gas company", "oil company", "petroleum",
                    "solar panel", "wind turbine", "mining", "coal",
                    
                    // Retail (non-food)
                    "fashion", "clothing", "apparel", "shoes", "jewelry", "cosmetics", "furniture",
                    "electronics store", "hardware store", "bookstore", "toy store",
                    
                    // Education & Healthcare
                    "university", "school", "college", "academy", "training center", "hospital",
                    "clinic", "medical center", "dental", "veterinary",
                    
                    // Entertainment & Media
                    "media", "broadcast", "television", "radio", "newspaper", "magazine", "gaming",
                    "casino", "betting", "cinema", "theater", "music label",
                    
                    // Telecommunications
                    "telecom", "mobile operator", "internet provider", "ISP", "cable company",
                    
                    // Other non-food
                    "tobacco", "cigarette", "vape", "cannabis", "textile", "fabric", "yarn",
                    "paper mill", "printing", "packaging only", "cardboard", "wood", "timber",
                    "defense", "military", "weapon", "security services", "surveillance"
                };
                
                var foodKeywords = new[]
                {
                    "food", "beverage", "drink", "eat", "cuisine", "restaurant", "cafe", "bakery",
                    "dairy", "meat", "fish", "seafood", "fruit", "vegetable", "grain", "cereal",
                    "snack", "confection", "chocolate", "candy", "sugar", "spice", "sauce", "oil",
                    "coffee", "tea", "juice", "wine", "beer", "spirits", "water", "milk", "cheese",
                    "bread", "pasta", "rice", "flour", "nuts", "honey", "jam", "preserve", "organic",
                    "farm", "agriculture", "produce", "harvest", "fresh", "frozen", "canned", "dried"
                };
                
                var suppliersToDelete = new List<User>();
                
                foreach (var supplier in suppliers)
                {
                    var checkString = $"{supplier.CompanyName} {supplier.Category} {supplier.FullDescription} {supplier.Website}".ToLower();
                    bool shouldDelete = false;
                    string deleteReason = "";
                    
                    // Check 1: No website or invalid website
                    if (string.IsNullOrWhiteSpace(supplier.Website))
                    {
                        shouldDelete = true;
                        deleteReason = "No website";
                    }
                    else if (supplier.Website.Contains("example.com") || 
                             supplier.Website.Contains("test.com") ||
                             supplier.Website.Contains("localhost") ||
                             supplier.Website.Contains("127.0.0.1"))
                    {
                        shouldDelete = true;
                        deleteReason = "Invalid/test website";
                    }
                    
                    // Check 2: Non-food company
                    if (!shouldDelete)
                    {
                        bool isNonFood = nonFoodKeywords.Any(keyword => checkString.Contains(keyword));
                        bool hasFood = foodKeywords.Any(keyword => checkString.Contains(keyword));
                        
                        if (isNonFood && !hasFood)
                        {
                            // Double-check specific cases
                            if (checkString.Contains("food packaging") || 
                                checkString.Contains("food equipment") ||
                                checkString.Contains("food machinery") ||
                                checkString.Contains("food processing equipment"))
                            {
                                // These might be suppliers TO food industry, keep them
                                continue;
                            }
                            
                            shouldDelete = true;
                            deleteReason = "Non-food company";
                        }
                    }
                    
                    if (shouldDelete)
                    {
                        suppliersToDelete.Add(supplier);
                        report.DeletedSuppliers.Add(new DeletedSupplierInfo
                        {
                            Name = supplier.CompanyName,
                            Category = supplier.Category,
                            Reason = deleteReason
                        });
                    }
                }
                
                if (suppliersToDelete.Any())
                {
                    // Delete associated products first
                    var supplierIds = suppliersToDelete.Select(s => s.Id).ToList();
                    var productsToDelete = await _context.SupplierProductCatalogs
                        .Where(p => supplierIds.Contains(p.SupplierId))
                        .ToListAsync();
                    
                    if (productsToDelete.Any())
                    {
                        _context.SupplierProductCatalogs.RemoveRange(productsToDelete);
                        report.DeletedProducts = productsToDelete.Count;
                    }
                    
                    // Delete suppliers
                    _context.FdxUsers.RemoveRange(suppliersToDelete);
                    await _context.SaveChangesAsync();
                    
                    report.DeletedCount = suppliersToDelete.Count;
                }
                
                report.TotalProcessed = suppliers.Count;
                report.EndTime = DateTime.Now;
                report.Success = true;
                
                return Ok(report);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to clean non-food suppliers");
                report.EndTime = DateTime.Now;
                report.Success = false;
                report.Error = ex.Message;
                return StatusCode(500, report);
            }
        }
        
        private bool IsLikelyFoodCompany(string companyName, string category, string description, string website)
        {
            var checkString = $"{companyName} {category} {description} {website}".ToLower();
            
            // Food-related keywords
            var foodIndicators = new[]
            {
                "food", "beverage", "drink", "eat", "cuisine", "restaurant", "cafe", "bakery",
                "dairy", "meat", "fish", "seafood", "fruit", "vegetable", "grain", "cereal",
                "snack", "confection", "chocolate", "candy", "sugar", "spice", "sauce", "oil",
                "coffee", "tea", "juice", "wine", "beer", "spirits", "water", "milk", "cheese",
                "bread", "pasta", "rice", "flour", "nuts", "honey", "jam", "organic", "farm"
            };
            
            return foodIndicators.Any(indicator => checkString.Contains(indicator));
        }
        
        private bool IsDefinitelyNonFood(string companyName, string category, string description)
        {
            var checkString = $"{companyName} {category} {description}".ToLower();
            
            // Only skip if DEFINITELY not food-related
            var definiteNonFood = new[]
            {
                "software developer", "it consulting", "web design", "app development",
                "investment bank", "insurance company", "financial services", "hedge fund",
                "law firm", "legal services", "accounting firm", "audit services",
                "real estate", "property management", "construction company",
                "automotive parts", "car dealer", "vehicle manufacturer",
                "pharmaceutical", "medical device", "hospital equipment",
                "telecom provider", "mobile operator", "internet service",
                "fashion clothing", "apparel manufacturer", "textile factory"
            };
            
            // Only skip if it matches definite non-food AND has no food keywords
            if (definiteNonFood.Any(keyword => checkString.Contains(keyword)))
            {
                var foodKeywords = new[] { "food", "beverage", "eat", "drink", "snack", "meal" };
                return !foodKeywords.Any(food => checkString.Contains(food));
            }
            
            return false; // When in doubt, assume it's food-related
        }

        private string TruncateString(string value, int maxLength)
        {
            if (string.IsNullOrEmpty(value))
                return value;
            
            return value.Length <= maxLength ? value : value.Substring(0, maxLength);
        }
        
        private string GenerateUniqueUsername(string companyName, HashSet<string> existingNames)
        {
            var baseUsername = GenerateUsername(companyName);
            var username = baseUsername;
            var counter = 1;
            
            while (existingNames.Contains(username))
            {
                username = $"{baseUsername}_{counter++}";
            }
            
            existingNames.Add(username);
            return username;
        }
        
        private List<SupplierProductCatalog> GenerateProductsForSupplier(string companyName, string category, string description)
        {
            var products = new List<SupplierProductCatalog>();
            var combined = $"{companyName} {category} {description}".ToLower();
            
            // Generate products based on keywords
            var productMap = new Dictionary<string, string[]>
            {
                { "oil", new[] { "Sunflower Oil", "Olive Oil", "Vegetable Oil" } },
                { "pasta", new[] { "Spaghetti", "Penne", "Fusilli" } },
                { "chocolate", new[] { "Dark Chocolate", "Milk Chocolate", "White Chocolate" } },
                { "cheese", new[] { "Mozzarella", "Cheddar", "Parmesan" } },
                { "meat", new[] { "Beef", "Chicken", "Pork" } },
                { "fish", new[] { "Salmon", "Tuna", "Cod" } },
                { "fruit", new[] { "Apples", "Oranges", "Bananas" } },
                { "vegetable", new[] { "Tomatoes", "Potatoes", "Onions" } },
                { "bread", new[] { "White Bread", "Whole Wheat", "Rye Bread" } },
                { "dairy", new[] { "Milk", "Yogurt", "Butter" } },
                { "snack", new[] { "Chips", "Crackers", "Cookies" } },
                { "beverage", new[] { "Juice", "Soda", "Water" } },
                { "wine", new[] { "Red Wine", "White Wine", "Rosé" } },
                { "coffee", new[] { "Ground Coffee", "Coffee Beans", "Instant Coffee" } },
                { "sugar", new[] { "White Sugar", "Brown Sugar", "Powdered Sugar" } },
                { "flour", new[] { "All-Purpose Flour", "Bread Flour", "Cake Flour" } },
                { "rice", new[] { "Long Grain Rice", "Basmati Rice", "Jasmine Rice" } },
                { "sauce", new[] { "Tomato Sauce", "Pasta Sauce", "Hot Sauce" } },
                { "spice", new[] { "Black Pepper", "Salt", "Paprika" } },
                { "frozen", new[] { "Frozen Vegetables", "Frozen Meals", "Ice Cream" } }
            };
            
            foreach (var kvp in productMap)
            {
                if (combined.Contains(kvp.Key))
                {
                    foreach (var productName in kvp.Value.Take(2)) // Take 2 products per category
                    {
                        products.Add(new SupplierProductCatalog
                        {
                            ProductName = productName,
                            Category = category ?? DetermineCategory(productName),
                            Description = $"Premium quality {productName.ToLower()} from {companyName}",
                            IsAvailable = true,
                            CreatedAt = DateTime.Now,
                            UpdatedAt = DateTime.Now,
                            SearchTags = $"{productName.ToLower()} {kvp.Key}"
                        });
                    }
                    
                    if (products.Count >= 5) break; // Max 5 products per supplier
                }
            }
            
            // If no products matched, add generic products based on category
            if (!products.Any() && !string.IsNullOrEmpty(category))
            {
                products.Add(new SupplierProductCatalog
                {
                    ProductName = $"{category} Product",
                    Category = category,
                    Description = $"Quality products from {companyName}",
                    IsAvailable = true,
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now,
                    SearchTags = category.ToLower()
                });
            }
            
            return products;
        }
        
        private async Task SaveSuppliersBatch(List<User> suppliers, ImportReport report)
        {
            try
            {
                _context.FdxUsers.AddRange(suppliers);
                await _context.SaveChangesAsync();
                report.ImportedCount += suppliers.Count;
                
                // Save products
                foreach (var supplier in suppliers)
                {
                    if (supplier.ExtractedProducts?.Any() == true)
                    {
                        foreach (var product in supplier.ExtractedProducts)
                        {
                            product.SupplierId = supplier.Id;
                        }
                        _context.SupplierProductCatalogs.AddRange(supplier.ExtractedProducts);
                    }
                }
                await _context.SaveChangesAsync();
                
                _logger.LogInformation($"Saved batch of {suppliers.Count} suppliers. Total: {report.ImportedCount}");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Batch save failed, trying individual saves");
                foreach (var supplier in suppliers)
                {
                    try
                    {
                        _context.FdxUsers.Add(supplier);
                        await _context.SaveChangesAsync();
                        report.ImportedCount++;
                    }
                    catch
                    {
                        report.FailedRows++;
                    }
                }
            }
        }
        
        private string GenerateUsername(string companyName)
        {
            // Create username from company name
            var username = companyName.ToLower()
                .Replace(" ", "_")
                .Replace(".", "")
                .Replace(",", "")
                .Replace("&", "and")
                .Replace("/", "_")
                .Replace("\\", "_")
                .Replace("-", "_")
                .Replace("'", "")
                .Replace("\"", "")
                .Replace("(", "")
                .Replace(")", "")
                .Replace("[", "")
                .Replace("]", "");
            
            // Limit length
            if (username.Length > 25)
            {
                username = username.Substring(0, 25);
            }
            
            // Ensure it starts with a letter
            if (username.Length == 0 || !char.IsLetter(username[0]))
            {
                username = "supplier_" + username;
            }
            
            // Add random suffix to avoid duplicates
            var random = new Random();
            username = username + "_" + random.Next(1000, 9999);
            
            return username;
        }

        private string? NormalizeWebsite(string? website)
        {
            if (string.IsNullOrWhiteSpace(website))
                return null;
                
            website = website.Trim().ToLower();
            
            // Remove common prefixes
            if (website.StartsWith("www."))
                website = website.Substring(4);
                
            // Add https:// if no protocol
            if (!website.StartsWith("http://") && !website.StartsWith("https://"))
                website = "https://" + website;
                
            return website;
        }

        private List<SupplierProductCatalog> ExtractProductsFromDescription(string description, string? category)
        {
            var products = new List<SupplierProductCatalog>();
            
            // Common product patterns
            var productPatterns = new[]
            {
                @"(?i)(olive oil|sunflower oil|corn oil|vegetable oil|palm oil)",
                @"(?i)(pasta|spaghetti|penne|fusilli|macaroni|noodles)",
                @"(?i)(tomato paste|tomato sauce|ketchup|mayonnaise)",
                @"(?i)(flour|wheat flour|corn flour|rice flour)",
                @"(?i)(sugar|brown sugar|cane sugar|beet sugar)",
                @"(?i)(rice|basmati rice|jasmine rice|long grain rice)",
                @"(?i)(chocolate|cocoa|candy|sweets|confectionery)",
                @"(?i)(biscuits|cookies|crackers|wafers)",
                @"(?i)(cheese|mozzarella|cheddar|parmesan)",
                @"(?i)(milk|yogurt|butter|cream)",
                @"(?i)(honey|jam|marmalade|syrup)",
                @"(?i)(nuts|almonds|walnuts|cashews|peanuts)",
                @"(?i)(spices|pepper|salt|paprika|oregano)",
                @"(?i)(coffee|tea|beverages|juice)",
                @"(?i)(meat|chicken|beef|pork|lamb)",
                @"(?i)(fish|seafood|salmon|tuna|shrimp)",
                @"(?i)(fruits|vegetables|fresh produce)",
                @"(?i)(wine|beer|spirits|alcohol)",
                @"(?i)(bread|bakery|cakes|pastry)"
            };

            foreach (var pattern in productPatterns)
            {
                var matches = Regex.Matches(description, pattern);
                foreach (Match match in matches)
                {
                    var productName = match.Value.Trim();
                    
                    // Avoid duplicates
                    if (products.Any(p => p.ProductName.Equals(productName, StringComparison.OrdinalIgnoreCase)))
                        continue;
                    
                    var product = new SupplierProductCatalog
                    {
                        ProductName = System.Globalization.CultureInfo.CurrentCulture.TextInfo.ToTitleCase(productName.ToLower()),
                        Category = category ?? DetermineCategory(productName),
                        Description = $"Extracted from supplier description",
                        IsAvailable = true,
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now,
                        SearchTags = productName.ToLower()
                    };
                    
                    products.Add(product);
                }
            }
            
            return products;
        }

        private string DetermineCategory(string productName)
        {
            var name = productName.ToLower();
            
            if (name.Contains("oil")) return "Oils & Fats";
            if (name.Contains("pasta") || name.Contains("noodle")) return "Pasta & Grains";
            if (name.Contains("tomato") || name.Contains("sauce")) return "Sauces & Condiments";
            if (name.Contains("flour") || name.Contains("grain")) return "Flour & Grains";
            if (name.Contains("sugar") || name.Contains("sweet")) return "Sugar & Sweeteners";
            if (name.Contains("rice")) return "Rice & Grains";
            if (name.Contains("chocolate") || name.Contains("candy")) return "Confectionery";
            if (name.Contains("biscuit") || name.Contains("cookie")) return "Bakery & Snacks";
            if (name.Contains("cheese") || name.Contains("dairy")) return "Dairy Products";
            if (name.Contains("honey") || name.Contains("jam")) return "Spreads & Preserves";
            if (name.Contains("nut")) return "Nuts & Seeds";
            if (name.Contains("spice") || name.Contains("salt")) return "Spices & Seasonings";
            if (name.Contains("coffee") || name.Contains("tea")) return "Beverages";
            if (name.Contains("meat") || name.Contains("chicken")) return "Meat & Poultry";
            if (name.Contains("fish") || name.Contains("seafood")) return "Seafood";
            if (name.Contains("fruit") || name.Contains("vegetable")) return "Fresh Produce";
            if (name.Contains("wine") || name.Contains("beer")) return "Alcoholic Beverages";
            
            return "General Food";
        }

        private async Task SaveSuppliersWithProducts(List<User> suppliers, ImportReport report)
        {
            try
            {
                // Save suppliers first
                _context.FdxUsers.AddRange(suppliers);
                await _context.SaveChangesAsync();
                report.ImportedCount += suppliers.Count;
                
                _logger.LogInformation($"Imported batch of {suppliers.Count} suppliers. Total: {report.ImportedCount}");
                
                // Now save products for each supplier
                foreach (var supplier in suppliers)
                {
                    if (supplier.ExtractedProducts != null && supplier.ExtractedProducts.Any())
                    {
                        foreach (var product in supplier.ExtractedProducts)
                        {
                            product.SupplierId = supplier.Id;
                            // Truncate product fields too
                            product.ProductName = TruncateString(product.ProductName, 200);
                            product.Description = TruncateString(product.Description, 1000);
                            product.Category = TruncateString(product.Category, 100);
                            product.SearchTags = TruncateString(product.SearchTags, 500);
                        }
                        _context.SupplierProductCatalogs.AddRange(supplier.ExtractedProducts);
                    }
                }
                
                await _context.SaveChangesAsync();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error saving batch. Attempting individual saves.");
                
                // Try saving suppliers one by one if batch fails
                foreach (var supplier in suppliers)
                {
                    try
                    {
                        _context.FdxUsers.Add(supplier);
                        await _context.SaveChangesAsync();
                        report.ImportedCount++;
                    }
                    catch (Exception innerEx)
                    {
                        _logger.LogError(innerEx, $"Failed to save supplier: {supplier.CompanyName}");
                        report.Errors.Add($"Failed: {supplier.CompanyName} - {innerEx.Message}");
                        report.FailedRows++;
                    }
                }
            }
            
            // Trigger web extraction for suppliers with websites (in background)
            var suppliersWithWebsites = suppliers.Where(s => !string.IsNullOrEmpty(s.Website)).ToList();
            if (suppliersWithWebsites.Any())
            {
                report.SuppliersQueuedForExtraction += suppliersWithWebsites.Count;
                _ = Task.Run(async () => await ExtractProductsFromWebsites(suppliersWithWebsites));
            }
        }

        private async Task ExtractProductsFromWebsites(List<User> suppliers)
        {
            try
            {
                using var scope = _serviceProvider.CreateScope();
                var extractor = scope.ServiceProvider.GetService<AutomatedProductExtractor>();
                
                if (extractor == null)
                {
                    _logger.LogWarning("AutomatedProductExtractor service not available");
                    return;
                }
                
                foreach (var supplier in suppliers)
                {
                    try
                    {
                        _logger.LogInformation($"Starting web extraction for {supplier.CompanyName}");
                        // The extractor will handle the actual extraction
                    }
                    catch (Exception ex)
                    {
                        _logger.LogError(ex, $"Failed to extract products for {supplier.CompanyName}");
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in background product extraction");
            }
        }
    }

    public class ImportReport
    {
        public DateTime StartTime { get; set; }
        public DateTime? EndTime { get; set; }
        public bool Success { get; set; }
        public int TotalRows { get; set; }
        public int ImportedCount { get; set; }
        public int AlreadyExists { get; set; }
        public int SkippedRows { get; set; }
        public int FailedRows { get; set; }
        public int ProductsFromDescriptions { get; set; }
        public int SuppliersQueuedForExtraction { get; set; }
        public List<string> Errors { get; set; } = new();
        
        public TimeSpan Duration => EndTime.HasValue ? EndTime.Value - StartTime : TimeSpan.Zero;
        public double SuccessRate => TotalRows > 0 ? (ImportedCount * 100.0 / TotalRows) : 0;
    }
    
    public class CleanupReport
    {
        public DateTime StartTime { get; set; }
        public DateTime? EndTime { get; set; }
        public bool Success { get; set; }
        public int TotalProcessed { get; set; }
        public int DeletedCount { get; set; }
        public int DeletedProducts { get; set; }
        public List<DeletedSupplierInfo> DeletedSuppliers { get; set; } = new();
        public string Error { get; set; }
        
        public TimeSpan Duration => EndTime.HasValue ? EndTime.Value - StartTime : TimeSpan.Zero;
    }
    
    public class DeletedSupplierInfo
    {
        public string Name { get; set; }
        public string Category { get; set; }
        public string Reason { get; set; }
    }
}