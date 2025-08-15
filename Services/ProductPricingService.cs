using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using FDX.Trading.Data;
using FDX.Trading.Models;

namespace FDX.Trading.Services
{
    public class ProductPricingService
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<ProductPricingService> _logger;
        private readonly Random _random = new Random();

        // Price ranges by category keywords
        private readonly Dictionary<string, (decimal min, decimal max)> _priceRanges = new()
        {
            // Oils
            { "oil", (5.99m, 45.99m) },
            { "olive", (12.99m, 89.99m) },
            { "sunflower", (3.99m, 24.99m) },
            
            // Pasta & Grains
            { "pasta", (1.99m, 12.99m) },
            { "rice", (2.99m, 19.99m) },
            { "grain", (3.99m, 24.99m) },
            
            // Dairy
            { "cheese", (4.99m, 34.99m) },
            { "milk", (2.99m, 8.99m) },
            { "yogurt", (1.99m, 7.99m) },
            
            // Meats
            { "meat", (8.99m, 49.99m) },
            { "chicken", (5.99m, 24.99m) },
            { "beef", (12.99m, 79.99m) },
            { "pork", (7.99m, 34.99m) },
            
            // Beverages
            { "juice", (2.99m, 12.99m) },
            { "water", (0.99m, 4.99m) },
            { "soda", (1.99m, 8.99m) },
            { "wine", (8.99m, 299.99m) },
            
            // Snacks
            { "cookie", (2.99m, 14.99m) },
            { "chip", (1.99m, 7.99m) },
            { "snack", (2.49m, 12.99m) },
            { "chocolate", (3.99m, 24.99m) },
            
            // Frozen
            { "frozen", (3.99m, 19.99m) },
            { "ice", (2.99m, 14.99m) },
            
            // Organic/Premium
            { "organic", (4.99m, 59.99m) },
            { "premium", (9.99m, 99.99m) },
            { "artisan", (12.99m, 149.99m) },
            
            // Default
            { "default", (2.99m, 29.99m) }
        };

        // Units by product type
        private readonly Dictionary<string, List<string>> _unitsByType = new()
        {
            { "oil", new List<string> { "L", "ml", "bottle", "case" } },
            { "pasta", new List<string> { "kg", "g", "box", "case" } },
            { "cheese", new List<string> { "kg", "g", "wheel", "block" } },
            { "liquid", new List<string> { "L", "ml", "bottle", "case" } },
            { "solid", new List<string> { "kg", "g", "unit", "case" } },
            { "frozen", new List<string> { "kg", "bag", "box", "case" } }
        };

        public ProductPricingService(FdxTradingContext context, ILogger<ProductPricingService> logger)
        {
            _context = context;
            _logger = logger;
        }

        public async Task<int> GeneratePricingForAllProducts()
        {
            try
            {
                var productsWithoutPricing = await _context.SupplierProductCatalogs
                    .Where(p => p.PricePerUnit == null || p.PricePerUnit == 0)
                    .ToListAsync();

                _logger.LogInformation($"Found {productsWithoutPricing.Count} products without pricing");

                foreach (var product in productsWithoutPricing)
                {
                    GeneratePricingForProduct(product);
                }

                await _context.SaveChangesAsync();
                
                _logger.LogInformation($"Generated pricing for {productsWithoutPricing.Count} products");
                return productsWithoutPricing.Count;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating product pricing");
                throw;
            }
        }

        private void GeneratePricingForProduct(SupplierProductCatalog product)
        {
            // Determine price range based on product name and category
            var priceRange = GetPriceRange(product);
            
            // Generate price within range
            var range = priceRange.max - priceRange.min;
            var price = priceRange.min + (decimal)(_random.NextDouble() * (double)range);
            product.PricePerUnit = Math.Round(price, 2);
            
            // Set currency
            product.Currency = "USD";
            
            // Set unit if not already set
            if (string.IsNullOrEmpty(product.Unit))
            {
                product.Unit = DetermineUnit(product);
            }
            
            // Set minimum order quantity
            if (product.MinOrderQuantity == null || product.MinOrderQuantity == 0)
            {
                product.MinOrderQuantity = DetermineMinOrderQuantity(product);
            }
            
            // Set lead time
            if (product.LeadTimeDays == null || product.LeadTimeDays == 0)
            {
                product.LeadTimeDays = _random.Next(3, 21); // 3 to 21 days
            }
            
            // Set stock quantity
            if (product.StockQuantity == null || product.StockQuantity == 0)
            {
                product.StockQuantity = _random.Next(100, 10000);
            }
            
            // Set incoterms
            if (string.IsNullOrEmpty(product.Incoterms))
            {
                var incoterms = new[] { "EXW", "FOB", "CIF", "DDP", "FCA" };
                product.Incoterms = incoterms[_random.Next(incoterms.Length)];
            }
        }

        private (decimal min, decimal max) GetPriceRange(SupplierProductCatalog product)
        {
            var productName = product.ProductName.ToLower();
            var category = (product.Category ?? "").ToLower();
            var description = (product.Description ?? "").ToLower();
            
            // Check for specific keywords
            foreach (var kvp in _priceRanges)
            {
                if (kvp.Key == "default") continue;
                
                if (productName.Contains(kvp.Key) || 
                    category.Contains(kvp.Key) || 
                    description.Contains(kvp.Key))
                {
                    // Adjust for organic/premium
                    if (productName.Contains("organic") || productName.Contains("premium"))
                    {
                        return (kvp.Value.min * 1.5m, kvp.Value.max * 1.5m);
                    }
                    return kvp.Value;
                }
            }
            
            return _priceRanges["default"];
        }

        private string DetermineUnit(SupplierProductCatalog product)
        {
            var productName = product.ProductName.ToLower();
            
            if (productName.Contains("oil") || productName.Contains("juice") || 
                productName.Contains("milk") || productName.Contains("water"))
            {
                var units = _unitsByType["liquid"];
                return units[_random.Next(units.Count)];
            }
            
            if (productName.Contains("pasta") || productName.Contains("rice") || 
                productName.Contains("grain"))
            {
                var units = _unitsByType["solid"];
                return units[_random.Next(units.Count)];
            }
            
            if (productName.Contains("frozen"))
            {
                var units = _unitsByType["frozen"];
                return units[_random.Next(units.Count)];
            }
            
            // Default
            return "unit";
        }

        private decimal DetermineMinOrderQuantity(SupplierProductCatalog product)
        {
            var unit = product.Unit?.ToLower() ?? "unit";
            
            return unit switch
            {
                "case" => _random.Next(1, 10),
                "kg" => _random.Next(10, 100),
                "g" => _random.Next(500, 5000),
                "l" => _random.Next(5, 50),
                "ml" => _random.Next(500, 5000),
                "box" => _random.Next(5, 20),
                _ => _random.Next(10, 100)
            };
        }

        public async Task<object> GetPricingStatistics()
        {
            var products = await _context.SupplierProductCatalogs.ToListAsync();
            
            var withPricing = products.Where(p => p.PricePerUnit > 0).ToList();
            var avgPrice = withPricing.Any() ? withPricing.Average(p => p.PricePerUnit ?? 0) : 0;
            var minPrice = withPricing.Any() ? withPricing.Min(p => p.PricePerUnit ?? 0) : 0;
            var maxPrice = withPricing.Any() ? withPricing.Max(p => p.PricePerUnit ?? 0) : 0;
            
            return new
            {
                totalProducts = products.Count,
                productsWithPricing = withPricing.Count,
                productsWithoutPricing = products.Count - withPricing.Count,
                percentageWithPricing = products.Count > 0 ? 
                    Math.Round((decimal)withPricing.Count / products.Count * 100, 2) : 0,
                averagePrice = Math.Round(avgPrice, 2),
                minPrice = Math.Round(minPrice, 2),
                maxPrice = Math.Round(maxPrice, 2),
                currencies = products.Where(p => !string.IsNullOrEmpty(p.Currency))
                    .GroupBy(p => p.Currency)
                    .Select(g => new { currency = g.Key, count = g.Count() })
            };
        }
    }
}