using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using System.Linq;

namespace FDX.Trading.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class DataCleanupController : ControllerBase
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<DataCleanupController> _logger;

        public DataCleanupController(FdxTradingContext context, ILogger<DataCleanupController> logger)
        {
            _context = context;
            _logger = logger;
        }

        [HttpPost("remove-duplicate-products")]
        public async Task<IActionResult> RemoveDuplicateProducts()
        {
            try
            {
                // Find duplicates by SupplierId and ProductName
                var allProducts = await _context.SupplierProductCatalogs.ToListAsync();
                var duplicateGroups = allProducts
                    .GroupBy(p => new { p.SupplierId, ProductNameLower = p.ProductName.ToLower() })
                    .Where(g => g.Count() > 1)
                    .ToList();

                var totalDuplicates = 0;
                var removedCount = 0;

                foreach (var group in duplicateGroups)
                {
                    var products = group.OrderByDescending(p => p.UpdatedAt)
                                       .ThenByDescending(p => p.Description != null)
                                       .ThenByDescending(p => p.PricePerUnit != null)
                                       .ThenByDescending(p => p.ImageUrl != null)
                                       .ToList();

                    // Keep the best record (first one after ordering)
                    var toKeep = products.First();
                    var toRemove = products.Skip(1).ToList();

                    // Merge data from duplicates into the one we're keeping
                    foreach (var duplicate in toRemove)
                    {
                        // Keep the best data from each duplicate
                        if (string.IsNullOrEmpty(toKeep.Description) && !string.IsNullOrEmpty(duplicate.Description))
                            toKeep.Description = duplicate.Description;
                        
                        if (toKeep.PricePerUnit == null && duplicate.PricePerUnit != null)
                            toKeep.PricePerUnit = duplicate.PricePerUnit;
                        
                        if (string.IsNullOrEmpty(toKeep.ImageUrl) && !string.IsNullOrEmpty(duplicate.ImageUrl))
                            toKeep.ImageUrl = duplicate.ImageUrl;
                        
                        if (string.IsNullOrEmpty(toKeep.Category) && !string.IsNullOrEmpty(duplicate.Category))
                            toKeep.Category = duplicate.Category;
                        
                        if (toKeep.ProductCategoryId == null && duplicate.ProductCategoryId != null)
                            toKeep.ProductCategoryId = duplicate.ProductCategoryId;
                    }

                    _context.SupplierProductCatalogs.RemoveRange(toRemove);
                    totalDuplicates += group.Count() - 1;
                    removedCount += toRemove.Count;
                }

                await _context.SaveChangesAsync();

                _logger.LogInformation($"Removed {removedCount} duplicate products from {duplicateGroups.Count} groups");

                return Ok(new
                {
                    success = true,
                    message = $"Successfully removed {removedCount} duplicate products",
                    duplicateGroups = duplicateGroups.Count,
                    totalDuplicatesRemoved = removedCount
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error removing duplicate products");
                return StatusCode(500, new { error = "Failed to remove duplicates", message = ex.Message });
            }
        }

        [HttpGet("duplicate-stats")]
        public async Task<IActionResult> GetDuplicateStats()
        {
            try
            {
                var allProds = await _context.SupplierProductCatalogs.ToListAsync();
                var duplicates = allProds
                    .GroupBy(p => new { p.SupplierId, ProductNameLower = p.ProductName.ToLower() })
                    .Where(g => g.Count() > 1)
                    .Select(g => new
                    {
                        SupplierId = g.Key.SupplierId,
                        ProductName = g.First().ProductName,
                        Count = g.Count()
                    })
                    .ToList();

                var totalProducts = allProds.Count;
                var uniqueProducts = allProds
                    .Select(p => new { p.SupplierId, ProductNameLower = p.ProductName.ToLower() })
                    .Distinct()
                    .Count();

                return Ok(new
                {
                    totalProducts,
                    uniqueProducts,
                    duplicateCount = totalProducts - uniqueProducts,
                    duplicateGroups = duplicates.Count(),
                    topDuplicates = duplicates.OrderByDescending(d => d.Count).Take(10)
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting duplicate stats");
                return StatusCode(500, new { error = "Failed to get stats", message = ex.Message });
            }
        }
    }
}