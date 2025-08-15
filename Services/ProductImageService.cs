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
    public class ProductImageService
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<ProductImageService> _logger;
        private readonly Random _random = new Random();

        // Sample image URLs by product type (using placeholder images)
        private readonly Dictionary<string, List<string>> _imageUrlsByType = new()
        {
            { "oil", new List<string> 
                { 
                    "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400", // Olive oil
                    "https://images.unsplash.com/photo-1612203985729-70726954388c?w=400", // Oil bottles
                    "https://images.unsplash.com/photo-1608303588026-884930af2559?w=400"  // Cooking oil
                }
            },
            { "pasta", new List<string> 
                { 
                    "https://images.unsplash.com/photo-1551462147-ff29053bfc14?w=400", // Pasta varieties
                    "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400", // Pasta dish
                    "https://images.unsplash.com/photo-1612892010343-983bfd063dc5?w=400"  // Raw pasta
                }
            },
            { "cheese", new List<string> 
                { 
                    "https://images.unsplash.com/photo-1552767059-ce182ead6c1b?w=400", // Cheese board
                    "https://images.unsplash.com/photo-1486297678162-eb2e5faf3db5?w=400", // Cheese variety
                    "https://images.unsplash.com/photo-1589881133825-bbb3b9471b1b?w=400"  // Cheese wheel
                }
            },
            { "bread", new List<string> 
                { 
                    "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=400", // Bread loaf
                    "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400", // Bakery bread
                    "https://images.unsplash.com/photo-1558303420-f814d8a590f5?w=400"  // Artisan bread
                }
            },
            { "chocolate", new List<string> 
                { 
                    "https://images.unsplash.com/photo-1511381939415-e44015466834?w=400", // Chocolate bars
                    "https://images.unsplash.com/photo-1575377427642-087cf684f29d?w=400", // Dark chocolate
                    "https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=400"  // Chocolate pieces
                }
            },
            { "juice", new List<string> 
                { 
                    "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400", // Orange juice
                    "https://images.unsplash.com/photo-1546173159-315724a31696?w=400", // Juice bottles
                    "https://images.unsplash.com/photo-1613478223719-2ab802602423?w=400"  // Fresh juice
                }
            },
            { "meat", new List<string> 
                { 
                    "https://images.unsplash.com/photo-1602473812169-361320e20f6e?w=400", // Meat cuts
                    "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400", // Packaged meat
                    "https://images.unsplash.com/photo-1551028150-64b9f398f678?w=400"  // Fresh meat
                }
            },
            { "frozen", new List<string> 
                { 
                    "https://images.unsplash.com/photo-1584385002340-d886f3a0f097?w=400", // Frozen vegetables
                    "https://images.unsplash.com/photo-1619221882062-f11ba6c9c7ab?w=400", // Frozen food
                    "https://images.unsplash.com/photo-1625943556566-623905d70e18?w=400"  // Ice cream
                }
            },
            { "snack", new List<string> 
                { 
                    "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400", // Chips
                    "https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=400", // Popcorn
                    "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"  // Cookies
                }
            },
            { "default", new List<string> 
                { 
                    "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400", // Grocery
                    "https://images.unsplash.com/photo-1584473457406-6240486418e9?w=400", // Food products
                    "https://images.unsplash.com/photo-1543168256-418811576931?w=400"  // General food
                }
            }
        };

        public ProductImageService(FdxTradingContext context, ILogger<ProductImageService> logger)
        {
            _context = context;
            _logger = logger;
        }

        public async Task<int> GenerateImagesForAllProducts()
        {
            try
            {
                var productsWithoutImages = await _context.SupplierProductCatalogs
                    .Where(p => string.IsNullOrEmpty(p.ImageUrl))
                    .ToListAsync();

                _logger.LogInformation($"Found {productsWithoutImages.Count} products without images");

                foreach (var product in productsWithoutImages)
                {
                    product.ImageUrl = GenerateImageUrl(product);
                }

                await _context.SaveChangesAsync();
                
                _logger.LogInformation($"Generated images for {productsWithoutImages.Count} products");
                return productsWithoutImages.Count;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating product images");
                throw;
            }
        }

        private string GenerateImageUrl(SupplierProductCatalog product)
        {
            var productName = product.ProductName.ToLower();
            var category = (product.Category ?? "").ToLower();
            
            // Find matching image category
            foreach (var kvp in _imageUrlsByType)
            {
                if (kvp.Key == "default") continue;
                
                if (productName.Contains(kvp.Key) || category.Contains(kvp.Key))
                {
                    var images = kvp.Value;
                    return images[_random.Next(images.Count)];
                }
            }
            
            // Default images
            var defaultImages = _imageUrlsByType["default"];
            return defaultImages[_random.Next(defaultImages.Count)];
        }

        public async Task<object> GetImageStatistics()
        {
            var products = await _context.SupplierProductCatalogs.ToListAsync();
            
            var withImages = products.Where(p => !string.IsNullOrEmpty(p.ImageUrl)).ToList();
            
            return new
            {
                totalProducts = products.Count,
                productsWithImages = withImages.Count,
                productsWithoutImages = products.Count - withImages.Count,
                percentageWithImages = products.Count > 0 ? 
                    Math.Round((decimal)withImages.Count / products.Count * 100, 2) : 0
            };
        }
    }
}