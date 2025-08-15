using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using FDX.Trading.Data;
using FDX.Trading.Models;

namespace FDX.Trading.Services
{
    public class SupplierCleanupService
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<SupplierCleanupService> _logger;
        private readonly AutomatedProductExtractor _productExtractor;

        public SupplierCleanupService(
            FdxTradingContext context,
            ILogger<SupplierCleanupService> logger,
            AutomatedProductExtractor productExtractor)
        {
            _context = context;
            _logger = logger;
            _productExtractor = productExtractor;
        }

        public async Task<CleanupResult> PerformComprehensiveCleanup()
        {
            var result = new CleanupResult { StartTime = DateTime.Now };
            
            try
            {
                _logger.LogInformation("Starting comprehensive supplier cleanup");
                
                // Step 1: Remove suppliers without websites
                await RemoveSuppliersWithoutWebsites(result);
                
                // Step 2: Remove non-food companies
                await RemoveNonFoodCompanies(result);
                
                // Step 3: Extract products for suppliers without products
                await EnsureAllSuppliersHaveProducts(result);
                
                // Step 4: Final cleanup - remove suppliers that still have no products after extraction
                await RemoveSuppliersWithoutProducts(result);
                
                result.EndTime = DateTime.Now;
                result.Success = true;
                
                _logger.LogInformation($"Cleanup completed. Removed {result.TotalDeleted} suppliers");
                
                return result;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Comprehensive cleanup failed");
                result.EndTime = DateTime.Now;
                result.Success = false;
                result.Error = ex.Message;
                return result;
            }
        }

        private async Task RemoveSuppliersWithoutWebsites(CleanupResult result)
        {
            var suppliersWithoutWebsites = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier && 
                           (string.IsNullOrEmpty(u.Website) || 
                            u.Website.Contains("example.com") ||
                            u.Website.Contains("test.com")))
                .ToListAsync();
            
            if (suppliersWithoutWebsites.Any())
            {
                var supplierIds = suppliersWithoutWebsites.Select(s => s.Id).ToList();
                
                // Delete products first
                var products = await _context.SupplierProductCatalogs
                    .Where(p => supplierIds.Contains(p.SupplierId))
                    .ToListAsync();
                
                _context.SupplierProductCatalogs.RemoveRange(products);
                _context.FdxUsers.RemoveRange(suppliersWithoutWebsites);
                
                await _context.SaveChangesAsync();
                
                result.DeletedNoWebsite = suppliersWithoutWebsites.Count;
                result.TotalDeleted += suppliersWithoutWebsites.Count;
                
                _logger.LogInformation($"Removed {suppliersWithoutWebsites.Count} suppliers without valid websites");
            }
        }

        private async Task RemoveNonFoodCompanies(CleanupResult result)
        {
            var nonFoodKeywords = GetNonFoodKeywords();
            var foodKeywords = GetFoodKeywords();
            
            var allSuppliers = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier)
                .ToListAsync();
            
            var nonFoodSuppliers = new List<User>();
            
            foreach (var supplier in allSuppliers)
            {
                var checkString = $"{supplier.CompanyName} {supplier.Category} {supplier.FullDescription}".ToLower();
                
                bool isNonFood = nonFoodKeywords.Any(keyword => checkString.Contains(keyword));
                bool hasFood = foodKeywords.Any(keyword => checkString.Contains(keyword));
                
                // Special cases for food-related equipment/packaging suppliers
                if (checkString.Contains("food packaging") || 
                    checkString.Contains("food equipment") ||
                    checkString.Contains("food machinery"))
                {
                    continue; // Keep these as they serve food industry
                }
                
                if (isNonFood && !hasFood)
                {
                    nonFoodSuppliers.Add(supplier);
                }
            }
            
            if (nonFoodSuppliers.Any())
            {
                var supplierIds = nonFoodSuppliers.Select(s => s.Id).ToList();
                
                // Delete products first
                var products = await _context.SupplierProductCatalogs
                    .Where(p => supplierIds.Contains(p.SupplierId))
                    .ToListAsync();
                
                _context.SupplierProductCatalogs.RemoveRange(products);
                _context.FdxUsers.RemoveRange(nonFoodSuppliers);
                
                await _context.SaveChangesAsync();
                
                result.DeletedNonFood = nonFoodSuppliers.Count;
                result.TotalDeleted += nonFoodSuppliers.Count;
                
                _logger.LogInformation($"Removed {nonFoodSuppliers.Count} non-food companies");
            }
        }

        private async Task EnsureAllSuppliersHaveProducts(CleanupResult result)
        {
            // Get suppliers with websites but no products
            var suppliersWithoutProducts = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier && 
                           !string.IsNullOrEmpty(u.Website))
                .Where(u => !_context.SupplierProductCatalogs.Any(p => p.SupplierId == u.Id))
                .ToListAsync();
            
            _logger.LogInformation($"Found {suppliersWithoutProducts.Count} suppliers without products. Starting extraction...");
            
            int extractionSuccess = 0;
            int extractionFailed = 0;
            
            foreach (var supplier in suppliersWithoutProducts)
            {
                try
                {
                    _logger.LogInformation($"Extracting products for {supplier.CompanyName}");
                    
                    // Try to extract from description first
                    if (!string.IsNullOrEmpty(supplier.FullDescription))
                    {
                        var extractedProducts = ExtractProductsFromDescription(
                            supplier.FullDescription, 
                            supplier.Category);
                        
                        if (extractedProducts.Any())
                        {
                            foreach (var product in extractedProducts)
                            {
                                product.SupplierId = supplier.Id;
                            }
                            
                            _context.SupplierProductCatalogs.AddRange(extractedProducts);
                            await _context.SaveChangesAsync();
                            
                            extractionSuccess++;
                            continue;
                        }
                    }
                    
                    // If no products from description, try web extraction
                    if (!string.IsNullOrEmpty(supplier.Website))
                    {
                        // This would normally call the web extraction service
                        // For now, marking for future extraction
                        supplier.ImportNotes = "Pending web extraction";
                        extractionFailed++;
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, $"Failed to extract products for {supplier.CompanyName}");
                    extractionFailed++;
                }
            }
            
            result.ProductsExtracted = extractionSuccess;
            result.ExtractionFailed = extractionFailed;
            
            _logger.LogInformation($"Product extraction: {extractionSuccess} successful, {extractionFailed} failed");
        }

        private async Task RemoveSuppliersWithoutProducts(CleanupResult result)
        {
            // Final cleanup: Remove suppliers that still have no products
            var suppliersWithoutProducts = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier)
                .Where(u => !_context.SupplierProductCatalogs.Any(p => p.SupplierId == u.Id))
                .ToListAsync();
            
            if (suppliersWithoutProducts.Any())
            {
                _context.FdxUsers.RemoveRange(suppliersWithoutProducts);
                await _context.SaveChangesAsync();
                
                result.DeletedNoProducts = suppliersWithoutProducts.Count;
                result.TotalDeleted += suppliersWithoutProducts.Count;
                
                _logger.LogInformation($"Removed {suppliersWithoutProducts.Count} suppliers without products");
            }
        }

        private List<SupplierProductCatalog> ExtractProductsFromDescription(string description, string category)
        {
            var products = new List<SupplierProductCatalog>();
            
            var productPatterns = new[]
            {
                @"(?i)(olive oil|sunflower oil|corn oil|vegetable oil|palm oil|coconut oil|sesame oil)",
                @"(?i)(pasta|spaghetti|penne|fusilli|macaroni|noodles|lasagna|ravioli)",
                @"(?i)(tomato paste|tomato sauce|ketchup|mayonnaise|mustard|hot sauce)",
                @"(?i)(flour|wheat flour|corn flour|rice flour|bread flour|cake flour)",
                @"(?i)(sugar|brown sugar|cane sugar|beet sugar|powdered sugar)",
                @"(?i)(rice|basmati rice|jasmine rice|long grain rice|short grain rice)",
                @"(?i)(chocolate|cocoa|candy|sweets|confectionery|pralines)",
                @"(?i)(biscuits|cookies|crackers|wafers|digestives)",
                @"(?i)(cheese|mozzarella|cheddar|parmesan|gouda|brie|feta)",
                @"(?i)(milk|yogurt|butter|cream|ice cream|dairy)",
                @"(?i)(honey|jam|marmalade|syrup|molasses|preserves)",
                @"(?i)(nuts|almonds|walnuts|cashews|peanuts|pistachios|hazelnuts)",
                @"(?i)(spices|pepper|salt|paprika|oregano|basil|thyme|rosemary)",
                @"(?i)(coffee|tea|green tea|black tea|herbal tea)",
                @"(?i)(juice|orange juice|apple juice|grape juice)",
                @"(?i)(wine|beer|spirits|vodka|whiskey|rum|gin)",
                @"(?i)(meat|chicken|beef|pork|lamb|turkey|fish|seafood)",
                @"(?i)(bread|rolls|baguette|croissant|bagel|muffin)",
                @"(?i)(canned goods|preserves|pickles|olives)",
                @"(?i)(snacks|chips|popcorn|pretzels|nachos)"
            };

            foreach (var pattern in productPatterns)
            {
                var matches = Regex.Matches(description, pattern);
                foreach (Match match in matches)
                {
                    var productName = match.Value.Trim();
                    
                    if (products.Any(p => p.ProductName.Equals(productName, StringComparison.OrdinalIgnoreCase)))
                        continue;
                    
                    var product = new SupplierProductCatalog
                    {
                        ProductName = System.Globalization.CultureInfo.CurrentCulture.TextInfo.ToTitleCase(productName.ToLower()),
                        Category = category ?? DetermineCategory(productName),
                        Description = "Extracted from supplier description",
                        IsAvailable = true,
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now,
                        SearchTags = productName.ToLower(),
                        // Source = "Description extraction" // Commented out as field doesn't exist yet
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
            if (name.Contains("sauce") || name.Contains("ketchup")) return "Sauces & Condiments";
            if (name.Contains("flour")) return "Flour & Baking";
            if (name.Contains("sugar") || name.Contains("sweet")) return "Sugar & Sweeteners";
            if (name.Contains("rice")) return "Rice & Grains";
            if (name.Contains("chocolate") || name.Contains("candy")) return "Confectionery";
            if (name.Contains("biscuit") || name.Contains("cookie")) return "Bakery & Snacks";
            if (name.Contains("cheese") || name.Contains("dairy") || name.Contains("milk")) return "Dairy Products";
            if (name.Contains("honey") || name.Contains("jam")) return "Spreads & Preserves";
            if (name.Contains("nut")) return "Nuts & Seeds";
            if (name.Contains("spice") || name.Contains("salt")) return "Spices & Seasonings";
            if (name.Contains("coffee") || name.Contains("tea")) return "Beverages";
            if (name.Contains("juice")) return "Juices & Drinks";
            if (name.Contains("meat") || name.Contains("chicken") || name.Contains("beef")) return "Meat & Poultry";
            if (name.Contains("fish") || name.Contains("seafood")) return "Seafood";
            if (name.Contains("wine") || name.Contains("beer")) return "Alcoholic Beverages";
            if (name.Contains("bread") || name.Contains("bagel")) return "Bakery";
            if (name.Contains("snack") || name.Contains("chip")) return "Snacks";
            
            return "General Food";
        }

        private string[] GetNonFoodKeywords()
        {
            return new[]
            {
                "software", "technology", "IT services", "digital", "cyber", "blockchain",
                "bank", "finance", "insurance", "credit", "loan", "investment",
                "automotive", "vehicle", "machinery", "industrial equipment",
                "consulting", "legal", "accounting", "recruitment", "marketing agency",
                "real estate", "construction", "cement", "building materials",
                "airline", "shipping line", "logistics only", "freight",
                "energy", "petroleum", "gas company", "mining",
                "fashion", "clothing", "apparel", "textile", "fabric",
                "electronics", "hardware", "telecom", "mobile operator",
                "pharmaceutical", "medical device", "hospital", "clinic",
                "education", "university", "school", "training",
                "media", "broadcast", "gaming", "entertainment",
                "tobacco", "cigarette", "vape"
            };
        }

        private string[] GetFoodKeywords()
        {
            return new[]
            {
                "food", "beverage", "drink", "edible", "cuisine", "culinary",
                "bakery", "dairy", "meat", "fish", "seafood", "poultry",
                "fruit", "vegetable", "produce", "organic", "fresh",
                "grain", "cereal", "flour", "bread", "pasta", "rice",
                "snack", "confection", "chocolate", "candy", "sweet",
                "sugar", "honey", "jam", "preserve", "spread",
                "spice", "sauce", "condiment", "seasoning", "herb",
                "oil", "butter", "cheese", "milk", "yogurt", "cream",
                "coffee", "tea", "juice", "water", "soda", "beverage",
                "wine", "beer", "spirits", "alcohol",
                "nuts", "seeds", "dried fruit", "frozen", "canned",
                "restaurant", "catering", "kitchen", "cooking",
                "nutrition", "diet", "meal", "ingredient"
            };
        }
    }

    public class CleanupResult
    {
        public DateTime StartTime { get; set; }
        public DateTime? EndTime { get; set; }
        public bool Success { get; set; }
        public int TotalDeleted { get; set; }
        public int DeletedNoWebsite { get; set; }
        public int DeletedNonFood { get; set; }
        public int DeletedNoProducts { get; set; }
        public int ProductsExtracted { get; set; }
        public int ExtractionFailed { get; set; }
        public string Error { get; set; }
        
        public TimeSpan Duration => EndTime.HasValue ? EndTime.Value - StartTime : TimeSpan.Zero;
    }
}