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
    public class ImprovedCategoryMatchingService
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<ImprovedCategoryMatchingService> _logger;

        // Enhanced keyword mappings for better matching
        private readonly Dictionary<string, List<string>> _categoryKeywords = new()
        {
            // Bakery
            { "bakery", new List<string> { "bread", "cake", "pastry", "croissant", "baguette", "roll", "muffin", "donut", "bagel", "biscuit", "cookie", "cracker" } },
            
            // Dairy
            { "dairy", new List<string> { "milk", "cheese", "yogurt", "butter", "cream", "cottage", "mozzarella", "cheddar", "parmesan", "ricotta", "feta" } },
            
            // Meat & Poultry
            { "meat", new List<string> { "beef", "pork", "lamb", "chicken", "turkey", "duck", "sausage", "ham", "bacon", "salami", "prosciutto", "meat" } },
            
            // Seafood
            { "seafood", new List<string> { "fish", "salmon", "tuna", "shrimp", "lobster", "crab", "oyster", "squid", "octopus", "anchovy", "sardine", "seafood" } },
            
            // Beverages
            { "beverages", new List<string> { "juice", "water", "soda", "tea", "coffee", "drink", "beverage", "cola", "lemonade", "smoothie", "milkshake" } },
            
            // Alcoholic Beverages
            { "alcohol", new List<string> { "wine", "beer", "vodka", "whiskey", "rum", "gin", "tequila", "brandy", "champagne", "prosecco", "liqueur" } },
            
            // Oils & Fats
            { "oils", new List<string> { "oil", "olive", "sunflower", "canola", "coconut", "palm", "avocado", "sesame", "peanut", "corn", "vegetable" } },
            
            // Pasta & Grains
            { "grains", new List<string> { "pasta", "rice", "wheat", "barley", "oats", "quinoa", "couscous", "bulgur", "spaghetti", "penne", "fusilli", "grain" } },
            
            // Snacks
            { "snacks", new List<string> { "chip", "pretzel", "popcorn", "nut", "trail", "snack", "crisp", "puff", "stick", "bite" } },
            
            // Sweets & Confectionery
            { "sweets", new List<string> { "chocolate", "candy", "sweet", "sugar", "honey", "jam", "jelly", "marmalade", "syrup", "caramel", "toffee", "marshmallow" } },
            
            // Frozen Foods
            { "frozen", new List<string> { "frozen", "ice", "freeze", "frost" } },
            
            // Vegetables
            { "vegetables", new List<string> { "vegetable", "tomato", "potato", "carrot", "onion", "garlic", "pepper", "lettuce", "spinach", "broccoli", "corn", "pea" } },
            
            // Fruits
            { "fruits", new List<string> { "fruit", "apple", "banana", "orange", "grape", "strawberry", "mango", "pineapple", "peach", "pear", "cherry", "berry" } },
            
            // Sauces & Condiments
            { "sauces", new List<string> { "sauce", "ketchup", "mayo", "mustard", "vinegar", "dressing", "pesto", "salsa", "chutney", "relish", "marinade" } },
            
            // Organic & Health
            { "organic", new List<string> { "organic", "bio", "natural", "gluten-free", "vegan", "vegetarian", "kosher", "halal", "sugar-free", "lactose-free" } }
        };

        public ImprovedCategoryMatchingService(FdxTradingContext context, ILogger<ImprovedCategoryMatchingService> logger)
        {
            _context = context;
            _logger = logger;
        }

        public async Task<CategoryMatchResult> MatchAllProducts()
        {
            try
            {
                var result = new CategoryMatchResult();
                
                // Get all products without categories
                var unlinkedProducts = await _context.SupplierProductCatalogs
                    .Where(p => p.ProductCategoryId == null)
                    .ToListAsync();
                
                result.TotalProducts = unlinkedProducts.Count;
                
                // Get all categories
                var categories = await _context.ProductCategories.ToListAsync();
                
                foreach (var product in unlinkedProducts)
                {
                    var match = await FindBestCategoryMatch(product, categories);
                    
                    if (match != null)
                    {
                        product.ProductCategoryId = match.CategoryId;
                        product.Category = match.CategoryPath;
                        result.Matched++;
                        result.Matches.Add(new ProductMatch
                        {
                            ProductId = product.Id,
                            ProductName = product.ProductName,
                            CategoryId = match.CategoryId,
                            CategoryPath = match.CategoryPath,
                            MatchScore = match.Score,
                            MatchReason = match.Reason
                        });
                    }
                    else
                    {
                        result.Unmatched++;
                        result.UnmatchedProducts.Add(product.ProductName);
                    }
                }
                
                await _context.SaveChangesAsync();
                
                _logger.LogInformation($"Category matching complete: {result.Matched} matched, {result.Unmatched} unmatched");
                
                return result;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in category matching");
                throw;
            }
        }

        private async Task<CategoryMatch?> FindBestCategoryMatch(SupplierProductCatalog product, List<ProductCategory> categories)
        {
            var matches = new List<CategoryMatch>();
            
            foreach (var category in categories)
            {
                var score = CalculateMatchScore(product, category);
                if (score > 0)
                {
                    matches.Add(new CategoryMatch
                    {
                        CategoryId = category.Id,
                        CategoryPath = category.FullPath,
                        Score = score,
                        Reason = DetermineMatchReason(product, category, score)
                    });
                }
            }
            
            // Return the best match (highest score)
            return matches.OrderByDescending(m => m.Score).FirstOrDefault();
        }

        private decimal CalculateMatchScore(SupplierProductCatalog product, ProductCategory category)
        {
            decimal score = 0;
            var productNameLower = product.ProductName.ToLower();
            var productDescLower = (product.Description ?? "").ToLower();
            var productCatLower = (product.Category ?? "").ToLower();
            
            var categoryLower = category.Category.ToLower();
            var subCategoryLower = category.SubCategory.ToLower();
            var familyLower = category.Family.ToLower();
            var subFamilyLower = (category.SubFamily ?? "").ToLower();
            
            // Exact matches (highest scores)
            if (productCatLower == categoryLower) score += 100;
            if (productCatLower == subCategoryLower) score += 90;
            if (productCatLower == familyLower) score += 80;
            if (productCatLower == subFamilyLower) score += 70;
            
            // Partial matches in product name
            if (productNameLower.Contains(categoryLower)) score += 60;
            if (productNameLower.Contains(subCategoryLower)) score += 50;
            if (productNameLower.Contains(familyLower)) score += 40;
            if (productNameLower.Contains(subFamilyLower)) score += 30;
            
            // Keyword-based matching
            foreach (var kvp in _categoryKeywords)
            {
                var categoryKeyword = kvp.Key;
                var keywords = kvp.Value;
                
                // Check if category matches keyword group
                if (categoryLower.Contains(categoryKeyword) || 
                    subCategoryLower.Contains(categoryKeyword) || 
                    familyLower.Contains(categoryKeyword))
                {
                    // Check if product contains any of the keywords
                    foreach (var keyword in keywords)
                    {
                        if (productNameLower.Contains(keyword))
                        {
                            score += 25;
                            break;
                        }
                        if (productDescLower.Contains(keyword))
                        {
                            score += 15;
                            break;
                        }
                    }
                }
            }
            
            // Check for word boundary matches
            var productWords = Regex.Split(productNameLower, @"\W+");
            var categoryWords = Regex.Split($"{categoryLower} {subCategoryLower} {familyLower}", @"\W+");
            
            var commonWords = productWords.Intersect(categoryWords).Count();
            score += commonWords * 10;
            
            return score;
        }

        private string DetermineMatchReason(SupplierProductCatalog product, ProductCategory category, decimal score)
        {
            var reasons = new List<string>();
            
            if (product.Category?.ToLower() == category.Category.ToLower())
                reasons.Add("Exact category match");
            else if (product.ProductName.ToLower().Contains(category.Family.ToLower()))
                reasons.Add($"Product name contains '{category.Family}'");
            else if (score >= 50)
                reasons.Add("High keyword similarity");
            else if (score >= 25)
                reasons.Add("Moderate keyword match");
            else
                reasons.Add("Partial keyword match");
            
            return string.Join(", ", reasons);
        }

        public async Task<object> GetMatchingStatistics()
        {
            var totalProducts = await _context.SupplierProductCatalogs.CountAsync();
            var linkedProducts = await _context.SupplierProductCatalogs
                .CountAsync(p => p.ProductCategoryId != null);
            var categories = await _context.ProductCategories.CountAsync();
            
            var topCategories = await _context.SupplierProductCatalogs
                .Where(p => p.ProductCategoryId != null)
                .GroupBy(p => p.ProductCategoryId)
                .Select(g => new
                {
                    CategoryId = g.Key,
                    ProductCount = g.Count()
                })
                .OrderByDescending(x => x.ProductCount)
                .Take(10)
                .ToListAsync();
            
            return new
            {
                totalProducts,
                linkedProducts,
                unlinkedProducts = totalProducts - linkedProducts,
                linkPercentage = totalProducts > 0 ? 
                    Math.Round((decimal)linkedProducts / totalProducts * 100, 2) : 0,
                totalCategories = categories,
                topCategories
            };
        }
    }

    public class CategoryMatch
    {
        public int CategoryId { get; set; }
        public string CategoryPath { get; set; } = "";
        public decimal Score { get; set; }
        public string Reason { get; set; } = "";
    }

    public class CategoryMatchResult
    {
        public int TotalProducts { get; set; }
        public int Matched { get; set; }
        public int Unmatched { get; set; }
        public List<ProductMatch> Matches { get; set; } = new();
        public List<string> UnmatchedProducts { get; set; } = new();
    }

    public class ProductMatch
    {
        public int ProductId { get; set; }
        public string ProductName { get; set; } = "";
        public int CategoryId { get; set; }
        public string CategoryPath { get; set; } = "";
        public decimal MatchScore { get; set; }
        public string MatchReason { get; set; } = "";
    }
}