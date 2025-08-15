using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Services;

namespace FDX.Trading.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class IntelligentSearchController : ControllerBase
    {
        private readonly AzureCognitiveSearchService _searchService;
        private readonly FdxTradingContext _context;
        private readonly ILogger<IntelligentSearchController> _logger;

        public IntelligentSearchController(
            AzureCognitiveSearchService searchService,
            FdxTradingContext context,
            ILogger<IntelligentSearchController> logger)
        {
            _searchService = searchService;
            _context = context;
            _logger = logger;
        }

        [HttpPost("initialize")]
        public async Task<IActionResult> InitializeSearchIndex()
        {
            try
            {
                _logger.LogInformation("Initializing Azure Cognitive Search index");
                
                // Initialize the index
                var indexCreated = await _searchService.InitializeIndex();
                if (!indexCreated)
                {
                    return StatusCode(500, new { error = "Failed to create search index" });
                }

                // Get all products and index them
                var products = await _context.SupplierProductCatalogs
                    .Include(p => p.Supplier)
                    .ToListAsync();

                var indexedCount = await _searchService.IndexProducts(products);

                return Ok(new
                {
                    success = true,
                    message = "Search index initialized successfully",
                    productsIndexed = indexedCount
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error initializing search index");
                return StatusCode(500, new { error = "Failed to initialize search", details = ex.Message });
            }
        }

        [HttpPost("search")]
        public async Task<IActionResult> Search([FromBody] IntelligentSearchRequest request)
        {
            try
            {
                _logger.LogInformation($"Performing intelligent search for: {request.Query}");

                var results = await _searchService.SearchWithAI(
                    request.Query, 
                    request.Page ?? 1, 
                    request.PageSize ?? 20);

                return Ok(results);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error performing intelligent search");
                return StatusCode(500, new { error = "Search failed", details = ex.Message });
            }
        }

        [HttpPost("reindex")]
        public async Task<IActionResult> ReindexProducts()
        {
            try
            {
                _logger.LogInformation("Reindexing all products");

                var products = await _context.SupplierProductCatalogs
                    .Include(p => p.Supplier)
                    .ToListAsync();

                var indexedCount = await _searchService.IndexProducts(products);

                return Ok(new
                {
                    success = true,
                    message = "Products reindexed successfully",
                    productsIndexed = indexedCount
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error reindexing products");
                return StatusCode(500, new { error = "Reindex failed", details = ex.Message });
            }
        }

        [HttpGet("suggestions")]
        public async Task<IActionResult> GetSearchSuggestions([FromQuery] string term)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(term) || term.Length < 2)
                {
                    return Ok(new { suggestions = new List<string>() });
                }

                // For now, use the existing database for suggestions
                // In production, this would use Azure Cognitive Search suggest API
                var suggestions = await _context.SupplierProductCatalogs
                    .Where(p => p.ProductName.Contains(term))
                    .Select(p => p.ProductName)
                    .Distinct()
                    .Take(10)
                    .ToListAsync();

                return Ok(new { suggestions });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting search suggestions");
                return StatusCode(500, new { error = "Failed to get suggestions" });
            }
        }

        [HttpGet("stats")]
        public async Task<IActionResult> GetSearchStatistics()
        {
            try
            {
                var totalProducts = await _context.SupplierProductCatalogs.CountAsync();
                var categories = await _context.SupplierProductCatalogs
                    .Where(p => p.Category != null)
                    .Select(p => p.Category)
                    .Distinct()
                    .CountAsync();

                var suppliers = await _context.SupplierProductCatalogs
                    .Select(p => p.SupplierId)
                    .Distinct()
                    .CountAsync();

                return Ok(new
                {
                    totalProducts,
                    totalCategories = categories,
                    totalSuppliers = suppliers,
                    searchEngine = "Azure Cognitive Search (Simulated)",
                    aiEnabled = true,
                    openAIIntegration = true,
                    features = new[]
                    {
                        "AI-Enhanced Search",
                        "Intelligent Query Understanding",
                        "Faceted Search",
                        "Smart Recommendations",
                        "Relevance Scoring",
                        "Multi-field Search"
                    }
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting search statistics");
                return StatusCode(500, new { error = "Failed to get statistics" });
            }
        }
    }

    public class IntelligentSearchRequest
    {
        public string Query { get; set; } = "";
        public string? Category { get; set; }
        public decimal? MinPrice { get; set; }
        public decimal? MaxPrice { get; set; }
        public int? Page { get; set; }
        public int? PageSize { get; set; }
    }
}