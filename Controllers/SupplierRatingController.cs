using Microsoft.AspNetCore.Mvc;
using FDX.Trading.Services;

namespace FDX.Trading.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SupplierRatingController : ControllerBase
    {
        private readonly SimpleRatingService _ratingService;
        private readonly ILogger<SupplierRatingController> _logger;

        public SupplierRatingController(SimpleRatingService ratingService, ILogger<SupplierRatingController> logger)
        {
            _ratingService = ratingService;
            _logger = logger;
        }

        [HttpPost("generate-initial")]
        public async Task<IActionResult> GenerateInitialRatings()
        {
            try
            {
                _logger.LogInformation("Generating initial supplier ratings");
                var count = await _ratingService.GenerateRatingsForProducts();
                
                return Ok(new
                {
                    success = true,
                    message = $"Generated ratings for {count} suppliers",
                    suppliersUpdated = count
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating ratings");
                return StatusCode(500, new { error = "Failed to generate ratings", message = ex.Message });
            }
        }


        [HttpGet("statistics")]
        public async Task<IActionResult> GetRatingStatistics()
        {
            try
            {
                var stats = await _ratingService.GetRatingStatistics();
                return Ok(stats);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting rating statistics");
                return StatusCode(500, new { error = "Failed to get statistics", message = ex.Message });
            }
        }
    }

    public class RateSupplierRequest
    {
        public int Rating { get; set; }
        public string? Comment { get; set; }
    }
}