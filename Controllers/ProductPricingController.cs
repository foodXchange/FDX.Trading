using Microsoft.AspNetCore.Mvc;
using FDX.Trading.Services;

namespace FDX.Trading.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ProductPricingController : ControllerBase
    {
        private readonly ProductPricingService _pricingService;
        private readonly ILogger<ProductPricingController> _logger;

        public ProductPricingController(ProductPricingService pricingService, ILogger<ProductPricingController> logger)
        {
            _pricingService = pricingService;
            _logger = logger;
        }

        [HttpPost("generate-all")]
        public async Task<IActionResult> GeneratePricingForAll()
        {
            try
            {
                _logger.LogInformation("Starting pricing generation for all products");
                var count = await _pricingService.GeneratePricingForAllProducts();
                
                return Ok(new
                {
                    success = true,
                    message = $"Generated pricing for {count} products",
                    productsUpdated = count
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating pricing");
                return StatusCode(500, new { error = "Failed to generate pricing", message = ex.Message });
            }
        }

        [HttpGet("statistics")]
        public async Task<IActionResult> GetPricingStatistics()
        {
            try
            {
                var stats = await _pricingService.GetPricingStatistics();
                return Ok(stats);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting pricing statistics");
                return StatusCode(500, new { error = "Failed to get statistics", message = ex.Message });
            }
        }
    }
}