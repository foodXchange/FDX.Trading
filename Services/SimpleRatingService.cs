using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using FDX.Trading.Data;
using FDX.Trading.Models;

namespace FDX.Trading.Services
{
    public class SimpleRatingService
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<SimpleRatingService> _logger;
        private readonly Random _random = new Random();

        public SimpleRatingService(FdxTradingContext context, ILogger<SimpleRatingService> logger)
        {
            _context = context;
            _logger = logger;
        }

        public async Task<int> GenerateRatingsForProducts()
        {
            try
            {
                var products = await _context.SupplierProductCatalogs
                    .Where(p => p.QualityScore == null || p.CustomerRating == null)
                    .ToListAsync();

                _logger.LogInformation($"Generating ratings for {products.Count} products");

                foreach (var product in products)
                {
                    // Generate quality score (0-100)
                    product.QualityScore = _random.Next(60, 100);
                    
                    // Generate customer rating (1-5 stars)
                    product.CustomerRating = _random.Next(3, 6); // 3 to 5 stars
                }

                await _context.SaveChangesAsync();
                
                _logger.LogInformation($"Generated ratings for {products.Count} products");
                return products.Count;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating ratings");
                throw;
            }
        }

        public async Task<object> GetRatingStatistics()
        {
            var products = await _context.SupplierProductCatalogs.ToListAsync();
            
            var withRatings = products.Where(p => p.CustomerRating > 0).ToList();
            var avgRating = withRatings.Any() ? withRatings.Average(p => p.CustomerRating ?? 0) : 0;
            var avgQuality = withRatings.Any() ? withRatings.Average(p => (double)(p.QualityScore ?? 0)) : 0;

            return new
            {
                totalProducts = products.Count,
                productsWithRatings = withRatings.Count,
                averageCustomerRating = Math.Round(avgRating, 2),
                averageQualityScore = Math.Round(avgQuality, 2),
                ratingDistribution = withRatings
                    .GroupBy(p => p.CustomerRating)
                    .Select(g => new { stars = g.Key, count = g.Count() })
                    .OrderBy(r => r.stars)
            };
        }
    }
}