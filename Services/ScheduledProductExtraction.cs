using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using FDX.Trading.Data;
using FDX.Trading.Models;

namespace FDX.Trading.Services
{
    public class ScheduledProductExtraction : BackgroundService
    {
        private readonly ILogger<ScheduledProductExtraction> _logger;
        private readonly IServiceProvider _serviceProvider;
        private Timer? _timer;

        public ScheduledProductExtraction(
            ILogger<ScheduledProductExtraction> logger,
            IServiceProvider serviceProvider)
        {
            _logger = logger;
            _serviceProvider = serviceProvider;
        }

        protected override Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("Scheduled Product Extraction Service started");
            
            // Schedule extraction to run daily at 2 AM
            var now = DateTime.Now;
            var scheduledTime = new DateTime(now.Year, now.Month, now.Day, 2, 0, 0);
            
            if (now > scheduledTime)
            {
                scheduledTime = scheduledTime.AddDays(1);
            }
            
            var initialDelay = scheduledTime - now;
            var period = TimeSpan.FromDays(1);
            
            _timer = new Timer(
                DoWork,
                null,
                initialDelay,
                period
            );
            
            _logger.LogInformation($"Next extraction scheduled for: {scheduledTime}");
            
            return Task.CompletedTask;
        }

        private async void DoWork(object? state)
        {
            _logger.LogInformation("Starting scheduled product extraction");
            
            try
            {
                using (var scope = _serviceProvider.CreateScope())
                {
                    var context = scope.ServiceProvider.GetRequiredService<FdxTradingContext>();
                    var extractor = scope.ServiceProvider.GetRequiredService<AutomatedProductExtractor>();
                    
                    // Get suppliers that need extraction
                    var suppliersNeedingExtraction = await context.FdxUsers
                        .Where(u => u.Type == UserType.Supplier)
                        .Where(u => !string.IsNullOrEmpty(u.Website))
                        .Where(u => !context.SupplierProductCatalogs.Any(p => p.SupplierId == u.Id) ||
                                   context.SupplierProductCatalogs
                                       .Where(p => p.SupplierId == u.Id)
                                       .Max(p => p.UpdatedAt) < DateTime.UtcNow.AddDays(-7))
                        .ToListAsync();
                    
                    if (suppliersNeedingExtraction.Any())
                    {
                        _logger.LogInformation($"Found {suppliersNeedingExtraction.Count} suppliers needing extraction");
                        
                        // Extract products in batches
                        var report = await extractor.ExtractAllSupplierProducts(10);
                        
                        _logger.LogInformation($"Extraction completed: {report.TotalProductsExtracted} products from {report.ProcessedSuppliers} suppliers");
                        
                        // Clean up duplicates
                        await CleanupDuplicateProducts(context);
                        
                        // Link to categories
                        await LinkProductsToCategories(context);
                    }
                    else
                    {
                        _logger.LogInformation("No suppliers need extraction at this time");
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during scheduled product extraction");
            }
        }
        
        private async Task CleanupDuplicateProducts(FdxTradingContext context)
        {
            try
            {
                var duplicates = await context.SupplierProductCatalogs
                    .GroupBy(p => new { p.SupplierId, p.ProductName })
                    .Where(g => g.Count() > 1)
                    .SelectMany(g => g.OrderByDescending(p => p.UpdatedAt).Skip(1))
                    .ToListAsync();
                
                if (duplicates.Any())
                {
                    context.SupplierProductCatalogs.RemoveRange(duplicates);
                    await context.SaveChangesAsync();
                    _logger.LogInformation($"Removed {duplicates.Count} duplicate products");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error cleaning up duplicate products");
            }
        }
        
        private async Task LinkProductsToCategories(FdxTradingContext context)
        {
            try
            {
                var unlinkedProducts = await context.SupplierProductCatalogs
                    .Where(p => p.ProductCategoryId == null && !string.IsNullOrWhiteSpace(p.Category))
                    .ToListAsync();
                
                var linked = 0;
                foreach (var product in unlinkedProducts)
                {
                    var category = await context.ProductCategories
                        .FirstOrDefaultAsync(c => 
                            c.Category.ToLower() == product.Category!.ToLower() ||
                            c.SubCategory.ToLower() == product.Category!.ToLower() ||
                            c.Family.ToLower() == product.Category!.ToLower());
                    
                    if (category != null)
                    {
                        product.ProductCategoryId = category.Id;
                        linked++;
                    }
                }
                
                if (linked > 0)
                {
                    await context.SaveChangesAsync();
                    _logger.LogInformation($"Linked {linked} products to categories");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error linking products to categories");
            }
        }

        public override void Dispose()
        {
            _timer?.Dispose();
            base.Dispose();
        }
    }
}