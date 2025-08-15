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
    public class SupplierRatingService
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<SupplierRatingService> _logger;
        private readonly Random _random = new Random();

        public SupplierRatingService(FdxTradingContext context, ILogger<SupplierRatingService> logger)
        {
            _context = context;
            _logger = logger;
        }

        public async Task<int> GenerateInitialRatings()
        {
            try
            {
                var suppliers = await _context.FdxUsers
                    .Where(u => u.Type == UserType.Supplier)
                    .ToListAsync();

                _logger.LogInformation($"Generating ratings for {suppliers.Count} suppliers");

                foreach (var supplier in suppliers)
                {
                    // Ensure SupplierDetails exists
                    if (supplier.SupplierDetails == null)
                    {
                        supplier.SupplierDetails = new SupplierDetails
                        {
                            UserId = supplier.Id,
                            IsVerified = true,
                            CreatedAt = DateTime.UtcNow
                        };
                    }

                    // Generate rating based on various factors
                    var rating = CalculateSupplierRating(supplier);
                    supplier.SupplierDetails.Rating = rating;
                    
                    // Generate performance metrics
                    supplier.SupplierDetails.TotalOrders = _random.Next(10, 500);
                    supplier.SupplierDetails.CompletedOrders = (int)(supplier.SupplierDetails.TotalOrders * (rating / 5m));
                    supplier.SupplierDetails.LastOrderDate = DateTime.UtcNow.AddDays(-_random.Next(1, 90));
                    
                    // Update products with quality scores
                    await UpdateProductQualityScores(supplier.Id, rating);
                }

                await _context.SaveChangesAsync();
                
                _logger.LogInformation($"Generated ratings for {suppliers.Count} suppliers");
                return suppliers.Count;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating supplier ratings");
                throw;
            }
        }

        private decimal CalculateSupplierRating(User supplier)
        {
            decimal baseRating = 3.0m; // Start with average rating
            
            // Factors that improve rating
            if (supplier.DataComplete) baseRating += 0.5m;
            if (!string.IsNullOrEmpty(supplier.Website)) baseRating += 0.3m;
            if (supplier.Verification > 0) baseRating += 0.4m;
            
            // Check product count
            var productCount = _context.SupplierProductCatalogs.Count(p => p.SupplierId == supplier.Id);
            if (productCount > 20) baseRating += 0.5m;
            else if (productCount > 10) baseRating += 0.3m;
            else if (productCount > 0) baseRating += 0.1m;
            
            // Add some randomness
            baseRating += (decimal)(_random.NextDouble() * 0.5 - 0.25); // +/- 0.25
            
            // Ensure rating is between 1 and 5
            baseRating = Math.Max(1.0m, Math.Min(5.0m, baseRating));
            
            // Round to 1 decimal place
            return Math.Round(baseRating, 1);
        }

        private async Task UpdateProductQualityScores(int supplierId, decimal supplierRating)
        {
            var products = await _context.SupplierProductCatalogs
                .Where(p => p.SupplierId == supplierId)
                .ToListAsync();

            foreach (var product in products)
            {
                // Quality score based on supplier rating with some variation
                var qualityScore = (supplierRating / 5m * 100m) + (decimal)(_random.NextDouble() * 20 - 10);
                product.QualityScore = Math.Max(0, Math.Min(100, Math.Round(qualityScore, 0)));
                
                // Customer rating (1-5 stars) similar to supplier rating
                var customerRating = (int)Math.Round(supplierRating + (decimal)(_random.NextDouble() - 0.5));
                product.CustomerRating = Math.Max(1, Math.Min(5, customerRating));
            }
        }

        public async Task<SupplierRating> RateSupplier(int supplierId, int rating, string? comment = null)
        {
            if (rating < 1 || rating > 5)
            {
                throw new ArgumentException("Rating must be between 1 and 5");
            }

            var supplierRating = new SupplierRating
            {
                SupplierId = supplierId,
                Rating = rating,
                Comment = comment,
                CreatedAt = DateTime.UtcNow
            };

            _context.SupplierRatings.Add(supplierRating);
            
            // Update supplier's average rating
            var supplier = await _context.FdxUsers
                .Include(u => u.SupplierDetails)
                .FirstOrDefaultAsync(u => u.Id == supplierId);

            if (supplier?.SupplierDetails != null)
            {
                var allRatings = await _context.SupplierRatings
                    .Where(r => r.SupplierId == supplierId)
                    .ToListAsync();
                
                allRatings.Add(supplierRating);
                supplier.SupplierDetails.Rating = (decimal)Math.Round(allRatings.Average(r => r.Rating), 1);
            }

            await _context.SaveChangesAsync();
            return supplierRating;
        }

        public async Task<object> GetRatingStatistics()
        {
            var suppliers = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier)
                .Include(u => u.SupplierDetails)
                .ToListAsync();

            var withRatings = suppliers.Where(s => s.SupplierDetails?.Rating > 0).ToList();
            var avgRating = withRatings.Any() ? withRatings.Average(s => s.SupplierDetails!.Rating ?? 0) : 0;

            var ratingDistribution = withRatings
                .GroupBy(s => Math.Floor(s.SupplierDetails!.Rating ?? 0))
                .Select(g => new { stars = g.Key, count = g.Count() })
                .OrderBy(r => r.stars);

            return new
            {
                totalSuppliers = suppliers.Count,
                suppliersWithRatings = withRatings.Count,
                suppliersWithoutRatings = suppliers.Count - withRatings.Count,
                averageRating = Math.Round(avgRating, 2),
                ratingDistribution,
                topRatedSuppliers = withRatings
                    .OrderByDescending(s => s.SupplierDetails!.Rating)
                    .Take(5)
                    .Select(s => new
                    {
                        id = s.Id,
                        name = s.CompanyName,
                        rating = s.SupplierDetails!.Rating,
                        totalOrders = s.SupplierDetails.TotalOrders
                    })
            };
        }
    }

    public class SupplierRating
    {
        public int Id { get; set; }
        public int SupplierId { get; set; }
        public int Rating { get; set; }
        public string? Comment { get; set; }
        public DateTime CreatedAt { get; set; }
        
        public virtual User Supplier { get; set; } = null!;
    }
}