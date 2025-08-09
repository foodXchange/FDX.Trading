using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using FDX.Trading.Services;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class SuppliersController : ControllerBase
{
    private readonly FdxTradingContext _context;
    
    public SuppliersController(FdxTradingContext context)
    {
        _context = context;
    }
    
    [HttpGet]
    public async Task<ActionResult<IEnumerable<object>>> GetSuppliers()
    {
        var suppliers = await _context.FdxUsers
            .Where(u => u.Type == UserType.Supplier)
            .Select(u => new
            {
                u.Id,
                u.Username,
                u.Email,
                u.CompanyName,
                u.Country,
                u.Website,
                u.IsActive,
                u.CreatedAt,
                ProductCount = _context.SupplierDetails
                    .Where(sd => sd.UserId == u.Id)
                    .SelectMany(sd => sd.SupplierProducts)
                    .Count()
            })
            .ToListAsync();
        
        return Ok(suppliers);
    }
    
    [HttpGet("{id}")]
    public async Task<ActionResult<object>> GetSupplier(int id)
    {
        var supplier = await _context.FdxUsers
            .Where(u => u.Id == id && u.Type == UserType.Supplier)
            .Select(u => new
            {
                u.Id,
                u.Username,
                u.Email,
                u.CompanyName,
                u.Country,
                u.Website,
                u.PhoneNumber,
                u.Address,
                u.IsActive,
                u.CreatedAt,
                Details = _context.SupplierDetails
                    .Where(sd => sd.UserId == u.Id)
                    .Select(sd => new
                    {
                        sd.Description,
                        sd.ProductCategories,
                        sd.Certifications,
                        sd.PreferredSeaPort,
                        sd.PaymentTerms,
                        sd.Incoterms,
                        sd.Currency,
                        sd.MinimumOrderValue,
                        sd.LeadTimeDays,
                        sd.IsVerified
                    })
                    .FirstOrDefault(),
                Products = _context.SupplierDetails
                    .Where(sd => sd.UserId == u.Id)
                    .SelectMany(sd => sd.SupplierProducts)
                    .Select(sp => new
                    {
                        sp.Product.Id,
                        sp.Product.ProductCode,
                        sp.Product.ProductName,
                        sp.Product.Category,
                        sp.UnitWholesalePrice,
                        sp.Currency,
                        sp.MinimumOrderQuantity,
                        sp.Status
                    })
                    .ToList()
            })
            .FirstOrDefaultAsync();
        
        if (supplier == null)
        {
            return NotFound();
        }
        
        return Ok(supplier);
    }
    
    [HttpGet("products")]
    public async Task<ActionResult<IEnumerable<object>>> GetSupplierProducts()
    {
        var products = await _context.Products
            .Select(p => new
            {
                p.Id,
                p.ProductCode,
                p.ProductName,
                p.Category,
                p.SubCategory,
                p.IsKosher,
                p.IsOrganic,
                p.CountryOfOrigin,
                p.Status,
                Suppliers = p.SupplierProducts.Select(sp => new
                {
                    sp.SupplierDetails.User.CompanyName,
                    sp.SupplierDetails.User.Country,
                    sp.UnitWholesalePrice,
                    sp.Currency,
                    sp.MinimumOrderQuantity
                }).ToList()
            })
            .ToListAsync();
        
        return Ok(products);
    }
    
    [HttpPost("import")]
    public async Task<ActionResult<ImportSummary>> ImportFromCsv([FromBody] ImportRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.FilePath))
        {
            return BadRequest("File path is required");
        }
        
        if (!System.IO.File.Exists(request.FilePath))
        {
            return BadRequest($"File not found: {request.FilePath}");
        }
        
        var importService = new SupplierProductImportService(_context);
        var result = await importService.ImportFromCsvAsync(request.FilePath);
        
        if (result.Success)
        {
            return Ok(result);
        }
        else
        {
            return StatusCode(500, result);
        }
    }
    
    [HttpGet("stats")]
    public async Task<ActionResult<object>> GetStats()
    {
        var stats = new
        {
            TotalSuppliers = await _context.FdxUsers.CountAsync(u => u.Type == UserType.Supplier),
            ActiveSuppliers = await _context.FdxUsers.CountAsync(u => u.Type == UserType.Supplier && u.IsActive),
            TotalProducts = await _context.Products.CountAsync(),
            ActiveProducts = await _context.Products.CountAsync(p => p.Status == ProductStatus.Active),
            TotalAssociations = await _context.SupplierProducts.CountAsync(),
            KosherProducts = await _context.Products.CountAsync(p => p.IsKosher),
            OrganicProducts = await _context.Products.CountAsync(p => p.IsOrganic),
            CountriesRepresented = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier)
                .Select(u => u.Country)
                .Distinct()
                .CountAsync()
        };
        
        return Ok(stats);
    }
}

public class ImportRequest
{
    public string FilePath { get; set; } = "";
}