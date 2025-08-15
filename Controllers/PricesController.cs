using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using FDX.Trading.Services;
using System.Linq;
using System.Threading.Tasks;
using System.Collections.Generic;
using System;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PricesController : ControllerBase
{
    private readonly FdxTradingContext _context;
    private readonly PriceBookImportService _priceBookService;
    
    public PricesController(FdxTradingContext context, PriceBookImportService priceBookService)
    {
        _context = context;
        _priceBookService = priceBookService;
    }
    
    // GET: api/prices/history/{productId}
    [HttpGet("history/{productId}")]
    public async Task<ActionResult<List<PriceHistoryDto>>> GetPriceHistory(int productId)
    {
        var history = await _context.ProductPriceHistories
            .Where(p => p.ProductId == productId)
            .OrderByDescending(p => p.EffectiveDate)
            .ThenByDescending(p => p.CreatedAt)
            .Select(p => new PriceHistoryDto
            {
                Id = p.Id,
                ProductId = p.ProductId,
                UnitPrice = p.UnitPrice,
                Currency = p.Currency,
                EffectiveDate = p.EffectiveDate,
                CreatedBy = p.CreatedBy,
                CreatedAt = p.CreatedAt,
                ChangeReason = p.ChangeReason,
                IsActive = p.IsActive
            })
            .ToListAsync();
        
        return Ok(history);
    }
    
    // POST: api/prices/update
    [HttpPost("update")]
    public async Task<ActionResult> UpdatePrice([FromBody] UpdatePriceDto dto)
    {
        using var transaction = await _context.Database.BeginTransactionAsync();
        
        try
        {
            // Deactivate current price(s)
            var currentPrices = await _context.ProductPriceHistories
                .Where(p => p.ProductId == dto.ProductId && p.IsActive)
                .ToListAsync();
            
            foreach (var currentPrice in currentPrices)
            {
                currentPrice.IsActive = false;
            }
            
            // Add new price
            var newPrice = new ProductPriceHistory
            {
                ProductId = dto.ProductId,
                UnitPrice = dto.UnitPrice,
                Currency = dto.Currency ?? "USD",
                EffectiveDate = dto.EffectiveDate,
                CreatedBy = dto.CreatedBy ?? "System",
                CreatedAt = DateTime.Now,
                ChangeReason = dto.ChangeReason,
                IsActive = true
            };
            
            _context.ProductPriceHistories.Add(newPrice);
            
            // Also update the main product table
            var product = await _context.Products.FindAsync(dto.ProductId);
            if (product != null)
            {
                product.UnitWholesalePrice = dto.UnitPrice;
                product.Currency = dto.Currency ?? "USD";
                product.UpdatedAt = DateTime.Now;
            }
            
            await _context.SaveChangesAsync();
            await transaction.CommitAsync();
            
            return Ok(new { success = true, message = "Price updated successfully" });
        }
        catch (Exception ex)
        {
            await transaction.RollbackAsync();
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    // GET: api/prices/current
    [HttpGet("current")]
    public async Task<ActionResult<List<CurrentPriceDto>>> GetCurrentPrices()
    {
        var prices = await _context.Products
            .Include(p => p.Supplier)
            .Select(p => new CurrentPriceDto
            {
                ProductId = p.Id,
                ProductCode = p.ProductCode,
                ProductName = p.ProductName,
                SupplierName = p.Supplier != null ? p.Supplier.CompanyName : null,
                CurrentPrice = p.UnitWholesalePrice,
                Currency = p.Currency ?? "USD",
                LastUpdated = p.UpdatedAt
            })
            .OrderBy(p => p.ProductCode)
            .ToListAsync();
        
        return Ok(prices);
    }
    
    // POST: api/prices/import-csv
    [HttpPost("import-csv")]
    public async Task<ActionResult> ImportPricesFromCsv([FromBody] ImportPricesRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.FilePath))
        {
            return BadRequest("File path is required");
        }
        
        if (!System.IO.File.Exists(request.FilePath))
        {
            return BadRequest($"File not found: {request.FilePath}");
        }
        
        try
        {
            // Simple CSV format: ProductCode, Price, EffectiveDate, Reason
            var lines = System.IO.File.ReadAllLines(request.FilePath);
            var imported = 0;
            var errors = new List<string>();
            
            foreach (var line in lines.Skip(1)) // Skip header
            {
                try
                {
                    var parts = line.Split(',');
                    if (parts.Length >= 3)
                    {
                        var productCode = parts[0].Trim();
                        var price = decimal.Parse(parts[1].Trim());
                        var effectiveDate = DateTime.Parse(parts[2].Trim());
                        var reason = parts.Length > 3 ? parts[3].Trim() : "CSV Import";
                        
                        var product = await _context.Products
                            .FirstOrDefaultAsync(p => p.ProductCode == productCode);
                        
                        if (product != null)
                        {
                            // Deactivate old prices
                            var oldPrices = await _context.ProductPriceHistories
                                .Where(p => p.ProductId == product.Id && p.IsActive)
                                .ToListAsync();
                            
                            foreach (var old in oldPrices)
                            {
                                old.IsActive = false;
                            }
                            
                            // Add new price
                            _context.ProductPriceHistories.Add(new ProductPriceHistory
                            {
                                ProductId = product.Id,
                                UnitPrice = price,
                                Currency = "USD",
                                EffectiveDate = effectiveDate,
                                CreatedBy = "CSV Import",
                                ChangeReason = reason,
                                IsActive = true
                            });
                            
                            // Update product
                            product.UnitWholesalePrice = price;
                            product.UpdatedAt = DateTime.Now;
                            
                            imported++;
                        }
                        else
                        {
                            errors.Add($"Product not found: {productCode}");
                        }
                    }
                }
                catch (Exception ex)
                {
                    errors.Add($"Error processing line: {line} - {ex.Message}");
                }
            }
            
            await _context.SaveChangesAsync();
            
            return Ok(new { 
                success = true, 
                imported = imported, 
                errors = errors,
                message = $"Imported {imported} prices successfully"
            });
        }
        catch (Exception ex)
        {
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    // GET: api/prices/export-template
    [HttpGet("export-template")]
    public ActionResult GetCsvTemplate()
    {
        var csvContent = "ProductCode,Price,EffectiveDate,Reason\n";
        csvContent += "SAMPLE001,10.50,2025-01-01,Initial Price\n";
        csvContent += "SAMPLE002,25.00,2025-01-01,Market Adjustment\n";
        
        return File(System.Text.Encoding.UTF8.GetBytes(csvContent), 
                   "text/csv", 
                   "price-import-template.csv");
    }
    
    // POST: api/prices/import-pricebook
    [HttpPost("import-pricebook")]
    public async Task<ActionResult> ImportPriceBook([FromBody] ImportPriceBookRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.FilePath))
        {
            return BadRequest("File path is required");
        }
        
        if (!System.IO.File.Exists(request.FilePath))
        {
            return BadRequest($"File not found: {request.FilePath}");
        }
        
        try
        {
            var result = await _priceBookService.ImportPriceBookAsync(request.FilePath);
            
            if (result.Success)
            {
                return Ok(result);
            }
            
            return BadRequest(result);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { success = false, message = ex.Message });
        }
    }
}

// DTOs
public class PriceHistoryDto
{
    public int Id { get; set; }
    public int ProductId { get; set; }
    public decimal? UnitPrice { get; set; }
    public string Currency { get; set; } = "USD";
    public DateTime EffectiveDate { get; set; }
    public string? CreatedBy { get; set; }
    public DateTime CreatedAt { get; set; }
    public string? ChangeReason { get; set; }
    public bool IsActive { get; set; }
}

public class UpdatePriceDto
{
    public int ProductId { get; set; }
    public decimal UnitPrice { get; set; }
    public string? Currency { get; set; }
    public DateTime EffectiveDate { get; set; }
    public string? ChangeReason { get; set; }
    public string? CreatedBy { get; set; }
}

public class CurrentPriceDto
{
    public int ProductId { get; set; }
    public string ProductCode { get; set; } = "";
    public string ProductName { get; set; } = "";
    public string? SupplierName { get; set; }
    public decimal? CurrentPrice { get; set; }
    public string Currency { get; set; } = "USD";
    public DateTime? LastUpdated { get; set; }
}

public class ImportPricesRequest
{
    public string FilePath { get; set; } = "";
}

public class ImportPriceBookRequest
{
    public string FilePath { get; set; } = "";
}