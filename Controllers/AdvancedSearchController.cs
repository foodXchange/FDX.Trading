using Microsoft.AspNetCore.Mvc;
using FDX.Trading.Services;

namespace FDX.Trading.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AdvancedSearchController : ControllerBase
    {
        private readonly AdvancedSearchService _searchService;
        private readonly ILogger<AdvancedSearchController> _logger;

        public AdvancedSearchController(AdvancedSearchService searchService, ILogger<AdvancedSearchController> logger)
        {
            _searchService = searchService;
            _logger = logger;
        }

        [HttpPost("search")]
        public async Task<IActionResult> SearchProducts([FromBody] SearchQuery query)
        {
            try
            {
                _logger.LogInformation($"Searching for: {query.SearchTerm}");
                var results = await _searchService.SearchProducts(query);
                
                return Ok(results);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in product search");
                return StatusCode(500, new { error = "Search failed", message = ex.Message });
            }
        }

        [HttpGet("suggestions")]
        public async Task<IActionResult> GetSearchSuggestions([FromQuery] string term)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(term))
                {
                    return Ok(new List<string>());
                }

                var suggestions = await _searchService.GetSearchSuggestions(term);
                return Ok(suggestions);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting search suggestions");
                return StatusCode(500, new { error = "Failed to get suggestions", message = ex.Message });
            }
        }

        [HttpGet("demo")]
        public IActionResult GetDemoSearches()
        {
            return Ok(new
            {
                message = "Try these search examples:",
                examples = new object[]
                {
                    new { query = "oil", description = "Search for all oil products" },
                    new { query = "organic pasta", description = "Find organic pasta products" },
                    new { query = "chocolate", filters = new { minPrice = 5, maxPrice = 25 }, description = "Chocolate within price range" },
                    new { query = "frozen", filters = new { inStockOnly = true }, description = "Available frozen products" },
                    new { query = "cheese", filters = new { minSupplierRating = 4 }, description = "Cheese from highly-rated suppliers" }
                },
                availableFilters = new
                {
                    category = "string",
                    minPrice = "decimal",
                    maxPrice = "decimal",
                    inStockOnly = "boolean",
                    isOrganic = "boolean",
                    isGlutenFree = "boolean",
                    isVegan = "boolean",
                    minSupplierRating = "decimal (1-5)",
                    country = "string",
                    sortBy = "relevance|price|name|rating|quality",
                    sortOrder = "asc|desc",
                    page = "integer",
                    pageSize = "integer"
                }
            });
        }
    }
}