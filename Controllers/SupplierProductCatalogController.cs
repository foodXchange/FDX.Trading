using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using FDX.Trading.Services;
using System.Text.Json;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class SupplierProductCatalogController : ControllerBase
{
    private readonly FdxTradingContext _context;
    private readonly ILogger<SupplierProductCatalogController> _logger;
    //private readonly SupplierDataEnrichmentService? _enrichmentService;

    public SupplierProductCatalogController(
        FdxTradingContext context, 
        ILogger<SupplierProductCatalogController> logger/*,
        SupplierDataEnrichmentService? enrichmentService = null*/)
    {
        _context = context;
        _logger = logger;
        //_enrichmentService = enrichmentService;
    }

    // GET: api/SupplierProductCatalog
    [HttpGet]
    public async Task<ActionResult<IEnumerable<SupplierProductDto>>> GetProducts()
    {
        var products = await _context.SupplierProductCatalogs
            .Include(p => p.Supplier)
            .Where(p => p.IsAvailable)
            .Select(p => new SupplierProductDto
            {
                Id = p.Id,
                SupplierId = p.SupplierId,
                SupplierName = p.Supplier.FirstName + " " + p.Supplier.LastName,
                ProductName = p.ProductName,
                ProductCode = p.ProductCode,
                Category = p.Category,
                SubCategory = p.SubCategory,
                Brand = p.Brand,
                Description = p.Description,
                MinOrderQuantity = p.MinOrderQuantity,
                Unit = p.Unit,
                PricePerUnit = p.PricePerUnit,
                Currency = p.Currency,
                IsAvailable = p.IsAvailable,
                LeadTimeDays = p.LeadTimeDays,
                CountryOfOrigin = p.CountryOfOrigin,
                QualityScore = p.QualityScore
            })
            .ToListAsync();

        return Ok(products);
    }

    // GET: api/SupplierProductCatalog/supplier/5
    [HttpGet("supplier/{supplierId}")]
    public async Task<ActionResult<IEnumerable<SupplierProductDto>>> GetSupplierProducts(int supplierId)
    {
        var products = await _context.SupplierProductCatalogs
            .Where(p => p.SupplierId == supplierId)
            .Select(p => new SupplierProductDto
            {
                Id = p.Id,
                SupplierId = p.SupplierId,
                ProductName = p.ProductName,
                ProductCode = p.ProductCode,
                Category = p.Category,
                SubCategory = p.SubCategory,
                Brand = p.Brand,
                Description = p.Description,
                MinOrderQuantity = p.MinOrderQuantity,
                Unit = p.Unit,
                PricePerUnit = p.PricePerUnit,
                Currency = p.Currency,
                IsAvailable = p.IsAvailable,
                LeadTimeDays = p.LeadTimeDays,
                CountryOfOrigin = p.CountryOfOrigin,
                QualityScore = p.QualityScore
            })
            .ToListAsync();

        return Ok(products);
    }

    // GET: api/SupplierProductCatalog/{id}/images
    [HttpGet("{id}/images")]
    public async Task<ActionResult> GetProductImages(int id)
    {
        var product = await _context.SupplierProductCatalogs
            .FirstOrDefaultAsync(p => p.Id == id);
            
        if (product == null)
        {
            return NotFound();
        }
        
        var images = new List<object>();
        
        // Check if product has an image URL
        if (!string.IsNullOrEmpty(product.ImageUrl))
        {
            images.Add(new { id = 1, imageUrl = product.ImageUrl });
        }
        
        return Ok(images);
    }
    
    // POST: api/SupplierProductCatalog/upload-image
    [HttpPost("upload-image")]
    public async Task<ActionResult> UploadProductImage([FromForm] IFormFile file, [FromForm] int productId)
    {
        var product = await _context.SupplierProductCatalogs
            .FirstOrDefaultAsync(p => p.Id == productId);
            
        if (product == null)
        {
            return NotFound(new { message = "Product not found" });
        }
        
        if (file == null || file.Length == 0)
        {
            return BadRequest(new { message = "No file provided" });
        }
        
        // Check file size (limit to 5MB)
        if (file.Length > 5 * 1024 * 1024)
        {
            return BadRequest(new { message = "File size exceeds 5MB limit" });
        }
        
        try
        {
            // Create upload directory if it doesn't exist
            var uploadPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "uploads", "supplier-products");
            if (!Directory.Exists(uploadPath))
            {
                Directory.CreateDirectory(uploadPath);
            }
            
            // Generate unique filename
            var fileExtension = Path.GetExtension(file.FileName);
            var uniqueFileName = $"sp_{productId}_{Guid.NewGuid()}{fileExtension}";
            var filePath = Path.Combine(uploadPath, uniqueFileName);
            
            // Save file to disk
            using (var stream = new FileStream(filePath, FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }
            
            // Update product with image URL
            product.ImageUrl = $"/uploads/supplier-products/{uniqueFileName}";
            await _context.SaveChangesAsync();
            
            return Ok(new 
            { 
                success = true, 
                message = "Image uploaded successfully",
                imageUrl = product.ImageUrl
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error uploading image for product {ProductId}", productId);
            return StatusCode(500, new { message = "Failed to upload image" });
        }
    }
    
    // POST: api/SupplierProductCatalog/add-image-url
    [HttpPost("add-image-url")]
    public async Task<ActionResult> AddImageUrl([FromBody] AddProductImageUrlDto dto)
    {
        var product = await _context.SupplierProductCatalogs
            .FirstOrDefaultAsync(p => p.Id == dto.ProductId);
            
        if (product == null)
        {
            return NotFound(new { message = "Product not found" });
        }
        
        if (string.IsNullOrWhiteSpace(dto.ImageUrl))
        {
            return BadRequest(new { message = "Image URL is required" });
        }
        
        try
        {
            // Update product with image URL
            product.ImageUrl = dto.ImageUrl;
            await _context.SaveChangesAsync();
            
            return Ok(new 
            { 
                success = true, 
                message = "Image URL added successfully",
                imageUrl = product.ImageUrl
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding image URL for product {ProductId}", dto.ProductId);
            return StatusCode(500, new { message = "Failed to add image URL" });
        }
    }

    private bool ProductExists(int id)
    {
        return _context.SupplierProductCatalogs.Any(e => e.Id == id);
    }
}

public class AddProductImageUrlDto
{
    public int ProductId { get; set; }
    public string ImageUrl { get; set; } = "";
}