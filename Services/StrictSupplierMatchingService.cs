using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using Microsoft.Extensions.Logging;

namespace FDX.Trading.Services;

public class StrictSupplierMatchingService
{
    private readonly FdxTradingContext _context;
    private readonly ILogger<StrictSupplierMatchingService> _logger;

    public StrictSupplierMatchingService(FdxTradingContext context, ILogger<StrictSupplierMatchingService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<List<MatchedSupplierDto>> GetStrictMatchedSuppliers(int briefId)
    {
        var brief = await _context.SourcingBriefs
            .Include(b => b.Products)
            .FirstOrDefaultAsync(b => b.Id == briefId);

        if (brief == null)
        {
            _logger.LogWarning($"Brief {briefId} not found");
            return new List<MatchedSupplierDto>();
        }

        var matchedSuppliers = new Dictionary<int, MatchedSupplierDto>();

        foreach (var briefProduct in brief.Products)
        {
            // Extract search terms from the product name and description
            var searchTerms = ExtractSearchTerms(briefProduct.ProductName, briefProduct.Description);
            
            _logger.LogInformation($"Searching for product: {briefProduct.ProductName} with terms: {string.Join(", ", searchTerms)}");

            // Search in SupplierProductCatalogs with strict matching
            var supplierProducts = await _context.SupplierProductCatalogs
                .Include(sp => sp.Supplier)
                .Where(sp => sp.IsAvailable)
                .ToListAsync();

            foreach (var supplierProduct in supplierProducts)
            {
                var productMatchScore = CalculateStrictMatchScore(
                    searchTerms,
                    supplierProduct.ProductName,
                    supplierProduct.Description,
                    supplierProduct.Category,
                    supplierProduct.SearchTags
                );

                // Only include if match score is significant (>95% for strict matching)
                if (productMatchScore < 95) continue;

                _logger.LogInformation($"Found match: {supplierProduct.ProductName} from supplier {supplierProduct.SupplierId} with score {productMatchScore}");

                if (!matchedSuppliers.ContainsKey(supplierProduct.SupplierId))
                {
                    var supplier = supplierProduct.Supplier;
                    matchedSuppliers[supplierProduct.SupplierId] = new MatchedSupplierDto
                    {
                        SupplierId = supplier.Id,
                        SupplierName = supplier.CompanyName ?? $"{supplier.FirstName} {supplier.LastName}",
                        CompanyName = supplier.CompanyName,
                        Email = supplier.Email,
                        Phone = supplier.PhoneNumber,
                        Country = supplier.Country,
                        MatchScore = productMatchScore,
                        MatchedProducts = new List<MatchedProductInfo>()
                    };
                }

                // Update max score if this product has a higher score
                if (productMatchScore > matchedSuppliers[supplierProduct.SupplierId].MatchScore)
                {
                    matchedSuppliers[supplierProduct.SupplierId].MatchScore = productMatchScore;
                }

                matchedSuppliers[supplierProduct.SupplierId].MatchedProducts.Add(new MatchedProductInfo
                {
                    BriefProductName = briefProduct.ProductName,
                    SupplierProductName = supplierProduct.ProductName,
                    SupplierProductCode = supplierProduct.ProductCode,
                    Category = supplierProduct.Category,
                    Price = supplierProduct.PricePerUnit,
                    Currency = supplierProduct.Currency,
                    MinOrderQuantity = supplierProduct.MinOrderQuantity,
                    Unit = supplierProduct.Unit,
                    MatchScore = productMatchScore
                });
            }
        }

        var result = matchedSuppliers.Values
            .OrderByDescending(s => s.MatchScore)
            .ThenBy(s => s.SupplierName)
            .Take(20)
            .ToList();

        _logger.LogInformation($"Found {result.Count} strictly matched suppliers for brief {briefId}");
        return result;
    }

    private List<string> ExtractSearchTerms(string productName, string? description)
    {
        var terms = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        
        // Add the full product name
        if (!string.IsNullOrWhiteSpace(productName))
        {
            terms.Add(productName.Trim());
            
            // Split and add individual words (excluding common words)
            var words = productName.Split(new[] { ' ', ',', '-', '/', '\\' }, StringSplitOptions.RemoveEmptyEntries);
            foreach (var word in words)
            {
                if (word.Length > 2 && !IsCommonWord(word))
                {
                    terms.Add(word.Trim());
                }
            }
        }
        
        // Extract key terms from description if available
        if (!string.IsNullOrWhiteSpace(description))
        {
            var descWords = description.Split(new[] { ' ', ',', '-', '/', '\\', '.', ';' }, StringSplitOptions.RemoveEmptyEntries);
            foreach (var word in descWords.Take(10)) // Only take first 10 words from description
            {
                if (word.Length > 3 && !IsCommonWord(word))
                {
                    terms.Add(word.Trim());
                }
            }
        }
        
        return terms.ToList();
    }

    private bool IsCommonWord(string word)
    {
        var commonWords = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "the", "and", "or", "for", "with", "from", "to", "in", "on", "at", 
            "of", "a", "an", "is", "are", "was", "were", "been", "be"
        };
        return commonWords.Contains(word);
    }

    private decimal CalculateStrictMatchScore(
        List<string> searchTerms,
        string productName,
        string? description,
        string? category,
        string? searchTags)
    {
        if (!searchTerms.Any()) return 0;

        var matchedTerms = 0;
        var totalWeight = 0m;
        
        var combinedText = $"{productName} {description} {category} {searchTags}".ToLower();

        foreach (var term in searchTerms)
        {
            var lowerTerm = term.ToLower();
            var weight = 1.0m;
            
            // Give more weight to full product name matches
            if (term.Split(' ').Length > 1)
            {
                weight = 2.0m;
            }
            
            // Check for exact match in product name (highest priority)
            if (productName?.ToLower().Contains(lowerTerm) == true)
            {
                matchedTerms++;
                totalWeight += weight * 2; // Double weight for product name matches
            }
            // Check in other fields
            else if (combinedText.Contains(lowerTerm))
            {
                matchedTerms++;
                totalWeight += weight;
            }
        }

        if (matchedTerms == 0) return 0;

        // Calculate percentage based on matched terms
        var matchPercentage = (matchedTerms * 100m) / searchTerms.Count;
        
        // For strict matching, require at least 90% of terms to match
        if (matchPercentage < 90) return 0;
        
        // Boost score if all terms match
        if (matchedTerms == searchTerms.Count)
        {
            matchPercentage = 100;
        }
        
        return Math.Min(100, matchPercentage);
    }
}

public class MatchedSupplierDto
{
    public int SupplierId { get; set; }
    public string SupplierName { get; set; } = "";
    public string? CompanyName { get; set; }
    public string? Email { get; set; }
    public string? Phone { get; set; }
    public string? Country { get; set; }
    public decimal MatchScore { get; set; }
    public List<MatchedProductInfo> MatchedProducts { get; set; } = new();
}

public class MatchedProductInfo
{
    public string BriefProductName { get; set; } = "";
    public string SupplierProductName { get; set; } = "";
    public string? SupplierProductCode { get; set; }
    public string? Category { get; set; }
    public decimal? Price { get; set; }
    public string? Currency { get; set; }
    public decimal? MinOrderQuantity { get; set; }
    public string? Unit { get; set; }
    public decimal MatchScore { get; set; }
}