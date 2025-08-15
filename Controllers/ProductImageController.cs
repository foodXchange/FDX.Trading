using Microsoft.AspNetCore.Mvc;
using FDX.Trading.Services;

namespace FDX.Trading.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ProductImageController : ControllerBase
    {
        private readonly ProductImageService _imageService;
        private readonly ILogger<ProductImageController> _logger;

        public ProductImageController(ProductImageService imageService, ILogger<ProductImageController> logger)
        {
            _imageService = imageService;
            _logger = logger;
        }

        [HttpPost("generate-all")]
        public async Task<IActionResult> GenerateImagesForAll()
        {
            try
            {
                _logger.LogInformation("Starting image generation for all products");
                var count = await _imageService.GenerateImagesForAllProducts();
                
                return Ok(new
                {
                    success = true,
                    message = $"Generated images for {count} products",
                    productsUpdated = count
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating images");
                return StatusCode(500, new { error = "Failed to generate images", message = ex.Message });
            }
        }

        [HttpGet("statistics")]
        public async Task<IActionResult> GetImageStatistics()
        {
            try
            {
                var stats = await _imageService.GetImageStatistics();
                return Ok(stats);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting image statistics");
                return StatusCode(500, new { error = "Failed to get statistics", message = ex.Message });
            }
        }
    }
}