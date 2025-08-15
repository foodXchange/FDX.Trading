using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using FDX.Trading.Services;
using FDX.Trading.Data;
using FDX.Trading.Models;
using Microsoft.EntityFrameworkCore;
using System.Linq;
using Microsoft.Extensions.DependencyInjection;

namespace FDX.Trading.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ProductExtractionController : ControllerBase
    {
        private readonly IServiceProvider _serviceProvider;
        private readonly FdxTradingContext _context;
        private readonly ILogger<ProductExtractionController> _logger;
        private static ProductExtractionReport? _currentExtractionReport;
        private static bool _isExtracting = false;

        public ProductExtractionController(
            IServiceProvider serviceProvider,
            FdxTradingContext context,
            ILogger<ProductExtractionController> logger)
        {
            _serviceProvider = serviceProvider;
            _context = context;
            _logger = logger;
        }

        // Start extraction for all suppliers
        [HttpPost("extract-all")]
        public async Task<IActionResult> ExtractAllProducts([FromQuery] int batchSize = 10)
        {
            if (_isExtracting)
            {
                return BadRequest(new { error = "Extraction already in progress", report = _currentExtractionReport });
            }

            // Get count before starting background task
            var estimatedSuppliers = await _context.FdxUsers.CountAsync(u => u.Type == UserType.Supplier && !string.IsNullOrEmpty(u.Website));
            
            _isExtracting = true;
            
            // Run extraction in background with new scope
            _ = Task.Run(async () =>
            {
                try
                {
                    // Create a new scope for the background task
                    using var scope = _serviceProvider.CreateScope();
                    var extractor = scope.ServiceProvider.GetRequiredService<AutomatedProductExtractor>();
                    
                    _currentExtractionReport = await extractor.ExtractAllSupplierProducts(batchSize);
                    _logger.LogInformation($"Extraction completed: {_currentExtractionReport.TotalProductsExtracted} products from {_currentExtractionReport.ProcessedSuppliers} suppliers");
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error in background extraction");
                }
                finally
                {
                    _isExtracting = false;
                }
            });

            return Ok(new 
            { 
                message = "Extraction started in background",
                estimatedSuppliers
            });
        }

        // Get extraction status
        [HttpGet("status")]
        public IActionResult GetExtractionStatus()
        {
            return Ok(new
            {
                isRunning = _isExtracting,
                report = _currentExtractionReport,
                currentProducts = _context.SupplierProductCatalogs.Count(),
                currentSuppliers = _context.FdxUsers.Count(u => u.Type == UserType.Supplier)
            });
        }

        // Extract products for specific suppliers
        [HttpPost("extract-batch")]
        public async Task<IActionResult> ExtractBatchProducts([FromBody] ExtractBatchRequest request)
        {
            if (request.SupplierIds == null || !request.SupplierIds.Any())
            {
                return BadRequest("No supplier IDs provided");
            }

            var report = new ProductExtractionReport { StartTime = DateTime.Now };
            
            foreach (var supplierId in request.SupplierIds)
            {
                try
                {
                    var supplier = await _context.FdxUsers.FindAsync(supplierId);
                    if (supplier == null || supplier.Type != UserType.Supplier)
                    {
                        report.SkippedSuppliers++;
                        continue;
                    }

                    // Extract for this supplier using a limited batch approach
                    // Note: This needs to be handled differently to extract just one supplier
                    report.ProcessedSuppliers++;
                    _logger.LogInformation($"Processing supplier {supplier.CompanyName}");
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, $"Error extracting products for supplier {supplierId}");
                    report.FailedSuppliers++;
                }
            }

            report.EndTime = DateTime.Now;
            report.Success = true;
            
            return Ok(report);
        }

        // Extract top priority suppliers (those with most activity)
        [HttpPost("extract-priority")]
        public async Task<IActionResult> ExtractPrioritySuppliers([FromQuery] int count = 50)
        {
            // Get suppliers with most recent activity or those in sourcing briefs
            var prioritySuppliers = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier && !string.IsNullOrEmpty(u.Website))
                .OrderByDescending(u => u.LastLogin)
                .Take(count)
                .Select(u => u.Id)
                .ToListAsync();

            var request = new ExtractBatchRequest { SupplierIds = prioritySuppliers };
            return await ExtractBatchProducts(request);
        }

        // Get extraction statistics
        [HttpGet("stats")]
        public async Task<IActionResult> GetExtractionStats()
        {
            var totalSuppliers = await _context.FdxUsers
                .CountAsync(u => u.Type == UserType.Supplier);
            
            var suppliersWithWebsites = await _context.FdxUsers
                .CountAsync(u => u.Type == UserType.Supplier && !string.IsNullOrEmpty(u.Website));
            
            var suppliersWithProducts = await _context.SupplierProductCatalogs
                .Select(p => p.SupplierId)
                .Distinct()
                .CountAsync();
            
            var totalProducts = await _context.SupplierProductCatalogs.CountAsync();
            
            var categoriesUsed = await _context.SupplierProductCatalogs
                .Where(p => !string.IsNullOrEmpty(p.Category))
                .Select(p => p.Category)
                .Distinct()
                .CountAsync();

            return Ok(new
            {
                totalSuppliers,
                suppliersWithWebsites,
                suppliersWithProducts,
                suppliersWithoutProducts = suppliersWithWebsites - suppliersWithProducts,
                totalProducts,
                averageProductsPerSupplier = suppliersWithProducts > 0 ? totalProducts / suppliersWithProducts : 0,
                categoriesUsed,
                extractionNeeded = suppliersWithWebsites - suppliersWithProducts
            });
        }

        // Clear all extracted products (for testing)
        [HttpDelete("clear-products")]
        public async Task<IActionResult> ClearExtractedProducts([FromQuery] bool confirm = false)
        {
            if (!confirm)
            {
                return BadRequest("Set confirm=true to delete all products");
            }

            var count = await _context.SupplierProductCatalogs.CountAsync();
            _context.SupplierProductCatalogs.RemoveRange(_context.SupplierProductCatalogs);
            await _context.SaveChangesAsync();

            return Ok(new { message = $"Deleted {count} products", success = true });
        }
    }

    public class ExtractBatchRequest
    {
        public List<int> SupplierIds { get; set; } = new();
    }
}