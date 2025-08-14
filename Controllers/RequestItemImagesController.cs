using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Models;
using FDX.Trading.Data;
using System.IO;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class RequestItemImagesController : ControllerBase
{
    private readonly FdxTradingContext _context;
    private readonly IWebHostEnvironment _environment;
    private readonly ILogger<RequestItemImagesController> _logger;
    
    public RequestItemImagesController(
        FdxTradingContext context, 
        IWebHostEnvironment environment,
        ILogger<RequestItemImagesController> logger)
    {
        _context = context;
        _environment = environment;
        _logger = logger;
    }
    
    // GET: api/requestitemimages/{productId}
    [HttpGet("{productId}")]
    public async Task<IActionResult> GetImages(int productId)
    {
        // First check if it's a BriefProduct
        var briefProduct = await _context.BriefProducts
            .Include(bp => bp.Images)
            .FirstOrDefaultAsync(bp => bp.Id == productId);
            
        if (briefProduct != null)
        {
            var briefImages = briefProduct.Images
                .OrderBy(i => i.IsPrimary ? 0 : 1)
                .Select(i => new
                {
                    i.Id,
                    i.FileName,
                    i.FilePath,
                    ContentType = "image/jpeg",
                    FileSize = 0L,
                    Description = "",
                    i.IsPrimary,
                    UploadedAt = DateTime.Now,
                    Url = i.FilePath
                })
                .ToList();
            return Ok(briefImages);
        }
        
        // Otherwise check RequestItemImages
        var images = await _context.RequestItemImages
            .Where(i => i.RequestItemId == productId)
            .OrderBy(i => i.IsPrimary ? 0 : 1)
            .ThenBy(i => i.UploadedAt)
            .Select(i => new
            {
                i.Id,
                i.FileName,
                i.FilePath,
                i.ContentType,
                i.FileSize,
                i.Description,
                i.IsPrimary,
                i.UploadedAt,
                Url = $"/uploads/request-items/{Path.GetFileName(i.FilePath)}"
            })
            .ToListAsync();
            
        return Ok(images);
    }
    
    // POST: api/requestitemimages/upload
    [HttpPost("upload")]
    public async Task<IActionResult> UploadBriefProductImage([FromForm] IFormFile file, [FromForm] int productId)
    {
        // Check if it's a BriefProduct
        var briefProduct = await _context.BriefProducts
            .FirstOrDefaultAsync(bp => bp.Id == productId);
            
        if (briefProduct == null)
        {
            return NotFound(new { message = "Product not found" });
        }
        
        // Validate file
        if (file == null || file.Length == 0)
            return BadRequest(new { message = "No file provided" });
            
        // Check file size (limit to 10MB)
        if (file.Length > 10 * 1024 * 1024)
            return BadRequest(new { message = "File size exceeds 10MB limit" });
            
        // Check file type
        var allowedTypes = new[] { "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp" };
        if (!allowedTypes.Contains(file.ContentType.ToLower()))
            return BadRequest(new { message = "Invalid file type. Only JPEG, PNG, GIF, and WebP images are allowed" });
        
        try
        {
            // Create upload directory if it doesn't exist
            var uploadPath = Path.Combine(_environment.WebRootPath, "uploads", "brief-products");
            if (!Directory.Exists(uploadPath))
                Directory.CreateDirectory(uploadPath);
            
            // Generate unique filename
            var fileExtension = Path.GetExtension(file.FileName);
            var uniqueFileName = $"bp_{productId}_{Guid.NewGuid()}{fileExtension}";
            var filePath = Path.Combine(uploadPath, uniqueFileName);
            
            // Save file to disk
            using (var stream = new FileStream(filePath, FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }
            
            // Create image record
            var image = new BriefProductImage
            {
                BriefProductId = productId,
                FileName = file.FileName,
                FilePath = $"/uploads/brief-products/{uniqueFileName}",
                IsPrimary = false
            };
            
            _context.BriefProductImages.Add(image);
            await _context.SaveChangesAsync();
            
            return Ok(new 
            { 
                success = true, 
                message = "Image uploaded successfully",
                image = new 
                {
                    image.Id,
                    image.FileName,
                    image.FilePath
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error uploading image for product {ProductId}", productId);
            return StatusCode(500, new { message = "Failed to upload image" });
        }
    }
    
    // POST: api/requestitemimages/add-url
    [HttpPost("add-url")]
    public async Task<IActionResult> AddImageUrl([FromBody] AddImageUrlDto dto)
    {
        // Check if it's a BriefProduct
        var briefProduct = await _context.BriefProducts
            .FirstOrDefaultAsync(bp => bp.Id == dto.ProductId);
            
        if (briefProduct == null)
        {
            return NotFound(new { message = "Product not found" });
        }
        
        try
        {
            // Create image record with URL
            var image = new BriefProductImage
            {
                BriefProductId = dto.ProductId,
                FileName = Path.GetFileName(dto.ImageUrl) ?? "external-image",
                FilePath = dto.ImageUrl,
                IsPrimary = false
            };
            
            _context.BriefProductImages.Add(image);
            await _context.SaveChangesAsync();
            
            return Ok(new 
            { 
                success = true, 
                message = "Image URL added successfully",
                image = new 
                {
                    image.Id,
                    image.FileName,
                    image.FilePath
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding image URL for product {ProductId}", dto.ProductId);
            return StatusCode(500, new { message = "Failed to add image URL" });
        }
    }
}

public class AddImageUrlDto
{
    public int ProductId { get; set; }
    public string ImageUrl { get; set; } = "";
}