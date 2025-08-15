using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using FDX.Trading.Data;
using FDX.Trading.Models;

namespace FDX.Trading.Services
{
    public class AdvancedSearchService
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<AdvancedSearchService> _logger;

        public AdvancedSearchService(FdxTradingContext context, ILogger<AdvancedSearchService> logger)
        {
            _context = context;
            _logger = logger;
        }

        public async Task<SearchResult> SearchProducts(SearchQuery query)
        {
            try
            {
                var stopwatch = System.Diagnostics.Stopwatch.StartNew();
                
                // Start with all products
                var productsQuery = _context.SupplierProductCatalogs
                    .Include(p => p.Supplier)
                    .AsQueryable();

                // Full-text search
                if (!string.IsNullOrWhiteSpace(query.SearchTerm))
                {
                    var searchTermLower = query.SearchTerm.ToLower();
                    var searchWords = searchTermLower.Split(' ', StringSplitOptions.RemoveEmptyEntries);

                    productsQuery = productsQuery.Where(p =>
                        p.ProductName.ToLower().Contains(searchTermLower) ||
                        (p.Description != null && p.Description.ToLower().Contains(searchTermLower)) ||
                        (p.Category != null && p.Category.ToLower().Contains(searchTermLower)) ||
                        (p.Brand != null && p.Brand.ToLower().Contains(searchTermLower)) ||
                        (p.SearchTags != null && p.SearchTags.ToLower().Contains(searchTermLower)) ||
                        searchWords.Any(word => p.ProductName.ToLower().Contains(word))
                    );
                }

                // Category filter
                if (!string.IsNullOrWhiteSpace(query.Category))
                {
                    productsQuery = productsQuery.Where(p => 
                        p.Category != null && p.Category.ToLower().Contains(query.Category.ToLower()));
                }

                // Price range filter
                if (query.MinPrice.HasValue)
                {
                    productsQuery = productsQuery.Where(p => p.PricePerUnit >= query.MinPrice.Value);
                }
                if (query.MaxPrice.HasValue)
                {
                    productsQuery = productsQuery.Where(p => p.PricePerUnit <= query.MaxPrice.Value);
                }

                // Availability filter
                if (query.InStockOnly)
                {
                    productsQuery = productsQuery.Where(p => p.IsAvailable && p.StockQuantity > 0);
                }

                // Certification filters
                if (query.IsOrganic.HasValue && query.IsOrganic.Value)
                {
                    productsQuery = productsQuery.Where(p => p.IsOrganic);
                }
                if (query.IsGlutenFree.HasValue && query.IsGlutenFree.Value)
                {
                    productsQuery = productsQuery.Where(p => p.IsGlutenFree);
                }
                if (query.IsVegan.HasValue && query.IsVegan.Value)
                {
                    productsQuery = productsQuery.Where(p => p.IsVegan);
                }

                // Supplier rating filter - simplified for now
                // (would need proper supplier details setup)

                // Country filter
                if (!string.IsNullOrWhiteSpace(query.Country))
                {
                    productsQuery = productsQuery.Where(p => 
                        p.CountryOfOrigin == query.Country || 
                        p.Supplier.Country == query.Country);
                }

                // Get total count before pagination
                var totalCount = await productsQuery.CountAsync();

                // Sorting (but not by relevance yet, as it's calculated later)
                if (query.SortBy?.ToLower() != "relevance")
                {
                    productsQuery = ApplySorting(productsQuery, query.SortBy, query.SortOrder);
                }

                // Pagination
                var pageSize = query.PageSize ?? 20;
                var page = query.Page ?? 1;
                productsQuery = productsQuery
                    .Skip((page - 1) * pageSize)
                    .Take(pageSize);

                // Execute query
                var products = await productsQuery.ToListAsync();

                // Calculate relevance scores if searching
                if (!string.IsNullOrWhiteSpace(query.SearchTerm))
                {
                    products = CalculateRelevanceScores(products, query.SearchTerm);
                }

                // Aggregations
                var aggregations = await GetAggregations(query);

                stopwatch.Stop();

                return new SearchResult
                {
                    Products = products.Select(p => new ProductSearchResult
                    {
                        Id = p.Id,
                        ProductName = p.ProductName,
                        Description = p.Description,
                        Category = p.Category,
                        Price = p.PricePerUnit,
                        Currency = p.Currency,
                        Unit = p.Unit,
                        ImageUrl = p.ImageUrl,
                        IsAvailable = p.IsAvailable,
                        StockQuantity = p.StockQuantity,
                        SupplierName = p.Supplier != null ? p.Supplier.CompanyName : "Unknown",
                        SupplierId = p.SupplierId,
                        SupplierRating = null, // Would need proper setup
                        QualityScore = p.QualityScore,
                        CustomerRating = p.CustomerRating,
                        RelevanceScore = p.RelevanceScore
                    }).ToList(),
                    TotalCount = totalCount,
                    Page = page,
                    PageSize = pageSize,
                    TotalPages = (int)Math.Ceiling((double)totalCount / pageSize),
                    SearchTime = stopwatch.ElapsedMilliseconds,
                    Aggregations = aggregations
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in advanced search");
                throw;
            }
        }

        private IQueryable<SupplierProductCatalog> ApplySorting(
            IQueryable<SupplierProductCatalog> query, 
            string? sortBy, 
            string? sortOrder)
        {
            var isDescending = sortOrder?.ToLower() == "desc";

            return (sortBy?.ToLower()) switch
            {
                "price" => isDescending ? 
                    query.OrderByDescending(p => p.PricePerUnit) : 
                    query.OrderBy(p => p.PricePerUnit),
                "name" => isDescending ? 
                    query.OrderByDescending(p => p.ProductName) : 
                    query.OrderBy(p => p.ProductName),
                "rating" => isDescending ? 
                    query.OrderByDescending(p => p.CustomerRating) : 
                    query.OrderBy(p => p.CustomerRating),
                "quality" => isDescending ? 
                    query.OrderByDescending(p => p.QualityScore) : 
                    query.OrderBy(p => p.QualityScore),
                _ => query.OrderBy(p => p.ProductName)
            };
        }

        private List<SupplierProductCatalog> CalculateRelevanceScores(
            List<SupplierProductCatalog> products, 
            string searchTerm)
        {
            var searchTermLower = searchTerm.ToLower();
            var searchWords = searchTermLower.Split(' ', StringSplitOptions.RemoveEmptyEntries);

            foreach (var product in products)
            {
                decimal score = 0;

                // Exact match in product name (highest score)
                if (product.ProductName.ToLower() == searchTermLower)
                    score += 100;
                else if (product.ProductName.ToLower().Contains(searchTermLower))
                    score += 50;

                // Word matches in product name
                foreach (var word in searchWords)
                {
                    if (product.ProductName.ToLower().Contains(word))
                        score += 20;
                }

                // Matches in description
                if (product.Description?.ToLower().Contains(searchTermLower) == true)
                    score += 30;

                // Matches in category
                if (product.Category?.ToLower().Contains(searchTermLower) == true)
                    score += 25;

                // Matches in brand
                if (product.Brand?.ToLower().Contains(searchTermLower) == true)
                    score += 15;

                // Boost for availability and quality
                if (product.IsAvailable) score += 5;
                if (product.QualityScore > 80) score += 10;
                if (product.CustomerRating >= 4) score += 10;

                product.RelevanceScore = score;
            }

            return products.OrderByDescending(p => p.RelevanceScore).ToList();
        }

        private async Task<SearchAggregations> GetAggregations(SearchQuery query)
        {
            var allProducts = _context.SupplierProductCatalogs.AsQueryable();

            // Apply basic filters but not search term for aggregations
            if (!string.IsNullOrWhiteSpace(query.Category))
            {
                allProducts = allProducts.Where(p => 
                    p.Category != null && p.Category.ToLower().Contains(query.Category.ToLower()));
            }

            var aggregations = new SearchAggregations();

            // Category counts
            aggregations.Categories = await allProducts
                .Where(p => p.Category != null)
                .GroupBy(p => p.Category)
                .Select(g => new FacetItem { Name = g.Key!, Count = g.Count() })
                .OrderByDescending(f => f.Count)
                .Take(10)
                .ToListAsync();

            // Price ranges
            var prices = await allProducts
                .Where(p => p.PricePerUnit > 0)
                .Select(p => p.PricePerUnit ?? 0)
                .ToListAsync();

            if (prices.Any())
            {
                aggregations.PriceRanges = new List<FacetItem>
                {
                    new FacetItem { Name = "Under $10", Count = prices.Count(p => p < 10) },
                    new FacetItem { Name = "$10-$25", Count = prices.Count(p => p >= 10 && p < 25) },
                    new FacetItem { Name = "$25-$50", Count = prices.Count(p => p >= 25 && p < 50) },
                    new FacetItem { Name = "$50-$100", Count = prices.Count(p => p >= 50 && p < 100) },
                    new FacetItem { Name = "Over $100", Count = prices.Count(p => p >= 100) }
                };
            }

            // Certification counts
            aggregations.Certifications = new List<FacetItem>
            {
                new FacetItem { Name = "Organic", Count = await allProducts.CountAsync(p => p.IsOrganic) },
                new FacetItem { Name = "Gluten-Free", Count = await allProducts.CountAsync(p => p.IsGlutenFree) },
                new FacetItem { Name = "Vegan", Count = await allProducts.CountAsync(p => p.IsVegan) },
                new FacetItem { Name = "Kosher", Count = await allProducts.CountAsync(p => p.IsKosher) },
                new FacetItem { Name = "Halal", Count = await allProducts.CountAsync(p => p.IsHalal) }
            };

            return aggregations;
        }

        public async Task<List<string>> GetSearchSuggestions(string term)
        {
            if (string.IsNullOrWhiteSpace(term) || term.Length < 2)
                return new List<string>();

            var termLower = term.ToLower();
            
            // Get product name suggestions
            var suggestions = await _context.SupplierProductCatalogs
                .Where(p => p.ProductName.ToLower().Contains(termLower))
                .Select(p => p.ProductName)
                .Distinct()
                .Take(10)
                .ToListAsync();

            // Add category suggestions
            var categorySuggestions = await _context.SupplierProductCatalogs
                .Where(p => p.Category != null && p.Category.ToLower().Contains(termLower))
                .Select(p => p.Category!)
                .Distinct()
                .Take(5)
                .ToListAsync();

            suggestions.AddRange(categorySuggestions);

            return suggestions.Distinct().Take(10).ToList();
        }
    }

    public class SearchQuery
    {
        public string? SearchTerm { get; set; }
        public string? Category { get; set; }
        public decimal? MinPrice { get; set; }
        public decimal? MaxPrice { get; set; }
        public bool InStockOnly { get; set; }
        public bool? IsOrganic { get; set; }
        public bool? IsGlutenFree { get; set; }
        public bool? IsVegan { get; set; }
        public decimal? MinSupplierRating { get; set; }
        public string? Country { get; set; }
        public string? SortBy { get; set; } = "relevance";
        public string? SortOrder { get; set; } = "desc";
        public int? Page { get; set; } = 1;
        public int? PageSize { get; set; } = 20;
    }

    public class SearchResult
    {
        public List<ProductSearchResult> Products { get; set; } = new();
        public int TotalCount { get; set; }
        public int Page { get; set; }
        public int PageSize { get; set; }
        public int TotalPages { get; set; }
        public long SearchTime { get; set; }
        public SearchAggregations Aggregations { get; set; } = new();
    }

    public class ProductSearchResult
    {
        public int Id { get; set; }
        public string ProductName { get; set; } = "";
        public string? Description { get; set; }
        public string? Category { get; set; }
        public decimal? Price { get; set; }
        public string? Currency { get; set; }
        public string? Unit { get; set; }
        public string? ImageUrl { get; set; }
        public bool IsAvailable { get; set; }
        public decimal? StockQuantity { get; set; }
        public string? SupplierName { get; set; }
        public int SupplierId { get; set; }
        public decimal? SupplierRating { get; set; }
        public decimal? QualityScore { get; set; }
        public int? CustomerRating { get; set; }
        public decimal RelevanceScore { get; set; }
    }

    public class SearchAggregations
    {
        public List<FacetItem> Categories { get; set; } = new();
        public List<FacetItem> PriceRanges { get; set; } = new();
        public List<FacetItem> Certifications { get; set; } = new();
    }

    public class FacetItem
    {
        public string Name { get; set; } = "";
        public int Count { get; set; }
    }
}

// Extension to add RelevanceScore property
namespace FDX.Trading.Models
{
    public partial class SupplierProductCatalog
    {
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        public decimal RelevanceScore { get; set; }
    }
}