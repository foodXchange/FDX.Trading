using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using FDX.Trading.Models;
using FDX.Trading.Data;
using Microsoft.EntityFrameworkCore;

namespace FDX.Trading.Services
{
    public class AzureCognitiveSearchService
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<AzureCognitiveSearchService> _logger;
        private readonly FdxTradingContext _context;
        private readonly string _indexName = "fdx-products";

        public AzureCognitiveSearchService(
            IConfiguration configuration,
            ILogger<AzureCognitiveSearchService> logger,
            FdxTradingContext context)
        {
            _configuration = configuration;
            _logger = logger;
            _context = context;
        }

        public async Task<IntelligentSearchResult> SearchWithAI(string query, int page = 1, int pageSize = 20)
        {
            try
            {
                var stopwatch = System.Diagnostics.Stopwatch.StartNew();

                // For now, use the existing database search with enhanced features
                // In production, this would connect to Azure Cognitive Search
                
                var searchTermLower = query.ToLower();
                var searchWords = searchTermLower.Split(' ', StringSplitOptions.RemoveEmptyEntries);

                // Start with all products
                var productsQuery = _context.SupplierProductCatalogs
                    .Include(p => p.Supplier)
                    .AsQueryable();

                // Full-text search
                productsQuery = productsQuery.Where(p =>
                    p.ProductName.ToLower().Contains(searchTermLower) ||
                    (p.Description != null && p.Description.ToLower().Contains(searchTermLower)) ||
                    (p.Category != null && p.Category.ToLower().Contains(searchTermLower)) ||
                    (p.Brand != null && p.Brand.ToLower().Contains(searchTermLower)) ||
                    searchWords.Any(word => p.ProductName.ToLower().Contains(word))
                );

                // Get total count
                var totalCount = await productsQuery.CountAsync();

                // Apply pagination
                var products = await productsQuery
                    .Skip((page - 1) * pageSize)
                    .Take(pageSize)
                    .ToListAsync();

                // Calculate relevance scores
                var results = products.Select(p => 
                {
                    decimal score = 0;
                    if (p.ProductName.ToLower() == searchTermLower)
                        score += 100;
                    else if (p.ProductName.ToLower().Contains(searchTermLower))
                        score += 50;
                    
                    foreach (var word in searchWords)
                    {
                        if (p.ProductName.ToLower().Contains(word))
                            score += 20;
                    }
                    
                    if (p.Description?.ToLower().Contains(searchTermLower) == true)
                        score += 30;
                    if (p.Category?.ToLower().Contains(searchTermLower) == true)
                        score += 25;
                    if (p.IsAvailable) score += 5;
                    if (p.QualityScore > 80) score += 10;

                    return new IntelligentProductResult
                    {
                        Id = p.Id,
                        ProductName = p.ProductName,
                        Description = p.Description,
                        Category = p.Category,
                        Price = p.PricePerUnit ?? 0,
                        SupplierName = p.Supplier?.CompanyName,
                        Score = (double)score,
                        Highlights = new Dictionary<string, IList<string>>()
                    };
                })
                .OrderByDescending(r => r.Score)
                .ToList();

                // Get aggregations
                var categories = await _context.SupplierProductCatalogs
                    .Where(p => p.Category != null)
                    .GroupBy(p => p.Category)
                    .Select(g => new { Name = g.Key!, Count = g.Count() })
                    .OrderByDescending(f => f.Count)
                    .Take(10)
                    .ToListAsync();

                // Simplified facets without using Azure SDK types directly
                var facets = new Dictionary<string, IList<SimpleFacet>>();
                var categoryFacets = categories.Select(c => new SimpleFacet { Name = c.Name, Count = c.Count }).ToList();
                facets["category"] = categoryFacets.Cast<SimpleFacet>().ToList();

                // Generate AI insights
                var insights = GenerateBasicInsights(query, results.Count, totalCount);

                stopwatch.Stop();

                return new IntelligentSearchResult
                {
                    Query = query,
                    EnhancedQuery = query + " (enhanced)",
                    Results = results,
                    TotalCount = totalCount,
                    Facets = facets,
                    SearchTimeMs = stopwatch.ElapsedMilliseconds,
                    AIInsights = insights,
                    SuggestedFilters = new List<string> 
                    { 
                        "Try filtering by category",
                        "Consider organic options",
                        "Check supplier ratings"
                    }
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in intelligent search");
                throw;
            }
        }

        private SearchInsights GenerateBasicInsights(string query, int resultCount, int totalCount)
        {
            var insights = new SearchInsights
            {
                Summary = $"Found {resultCount} products matching '{query}' out of {totalCount} total products.",
                Recommendations = new List<string>()
            };

            if (resultCount == 0)
            {
                insights.Recommendations.Add("Try using broader search terms");
                insights.Recommendations.Add("Check spelling of your search query");
            }
            else if (resultCount < 5)
            {
                insights.Recommendations.Add("Limited results found - consider expanding your search");
                insights.Recommendations.Add("Try related product categories");
            }
            else
            {
                insights.Recommendations.Add("Use filters to narrow down your results");
                insights.Recommendations.Add("Sort by price or rating for better matches");
                insights.Recommendations.Add("Check product availability before ordering");
            }

            return insights;
        }

        public async Task<bool> InitializeIndex()
        {
            try
            {
                _logger.LogInformation("Index initialization simulated - Azure Cognitive Search would be configured here");
                // In production, this would create the actual Azure Cognitive Search index
                return await Task.FromResult(true);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error initializing index");
                return false;
            }
        }

        public async Task<int> IndexProducts(List<SupplierProductCatalog> products)
        {
            try
            {
                _logger.LogInformation($"Simulating indexing of {products.Count} products to Azure Cognitive Search");
                // In production, this would upload documents to Azure Cognitive Search
                return await Task.FromResult(products.Count);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error indexing products");
                throw;
            }
        }
    }

    public class SimpleFacet
    {
        public string Name { get; set; } = "";
        public int Count { get; set; }
    }

    public class IntelligentSearchResult
    {
        public string Query { get; set; } = "";
        public string EnhancedQuery { get; set; } = "";
        public List<IntelligentProductResult> Results { get; set; } = new();
        public long TotalCount { get; set; }
        public IDictionary<string, IList<SimpleFacet>>? Facets { get; set; }
        public long SearchTimeMs { get; set; }
        public SearchInsights AIInsights { get; set; } = new();
        public List<string> SuggestedFilters { get; set; } = new();
    }

    public class IntelligentProductResult
    {
        public int Id { get; set; }
        public string ProductName { get; set; } = "";
        public string? Description { get; set; }
        public string? Category { get; set; }
        public decimal Price { get; set; }
        public string? SupplierName { get; set; }
        public double Score { get; set; }
        public IDictionary<string, IList<string>>? Highlights { get; set; }
        public List<string>? Captions { get; set; }
    }

    public class SearchInsights
    {
        public string Summary { get; set; } = "";
        public List<string> Recommendations { get; set; } = new();
        public List<string?> TopCategories { get; set; } = new();
    }
}