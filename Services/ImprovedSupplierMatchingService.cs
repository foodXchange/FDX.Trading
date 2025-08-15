using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using FDX.Trading.Data;
using FDX.Trading.Models;

namespace FDX.Trading.Services
{
    public class ImprovedSupplierMatchingService
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<ImprovedSupplierMatchingService> _logger;

        public ImprovedSupplierMatchingService(FdxTradingContext context, ILogger<ImprovedSupplierMatchingService> logger)
        {
            _context = context;
            _logger = logger;
        }

        public async Task<List<SupplierMatch>> MatchSuppliersForBrief(int briefId, SupplierMatchingOptions? options = null)
        {
            options ??= new SupplierMatchingOptions();
            
            // Get brief with products
            var brief = await _context.SourcingBriefs
                .Include(sb => sb.Products)
                .FirstOrDefaultAsync(sb => sb.Id == briefId);
                
            if (brief == null || !brief.Products.Any())
                return new List<SupplierMatch>();
                
            // Convert brief products to requirements
            var requirements = brief.Products
                .Select(p => ProductRequirement.FromBriefProduct(p))
                .ToList();
                
            return await MatchSuppliersForRequirements(requirements, options);
        }

        public async Task<List<SupplierMatch>> MatchSuppliersForRequirements(
            List<ProductRequirement> requirements, 
            SupplierMatchingOptions options)
        {
            var allMatches = new Dictionary<int, SupplierMatch>();
            
            foreach (var requirement in requirements)
            {
                var matches = await MatchSuppliersForProduct(requirement, options);
                
                // Aggregate matches across all requirements
                foreach (var match in matches)
                {
                    if (allMatches.ContainsKey(match.SupplierId))
                    {
                        // Combine scores for suppliers matching multiple products
                        var before = allMatches[match.SupplierId].AvailableProducts.Count;
                        allMatches[match.SupplierId].MatchScore += match.MatchScore;
                        allMatches[match.SupplierId].MatchReasons.AddRange(match.MatchReasons);
                        allMatches[match.SupplierId].AvailableProducts.AddRange(match.AvailableProducts);
                        var after = allMatches[match.SupplierId].AvailableProducts.Count;
                        _logger.LogInformation($"Merged {match.CompanyName}: products {before} -> {after}");
                    }
                    else
                    {
                        allMatches[match.SupplierId] = match;
                        _logger.LogInformation($"Added {match.CompanyName} with {match.AvailableProducts.Count} products");
                    }
                }
            }
            
            // Normalize scores and apply final filtering
            var finalMatches = allMatches.Values
                .Select(m => {
                    // Calculate normalized score (max 100%)
                    // Take the highest match level score, not sum
                    var highestScore = m.MatchReasons.Any() ? m.MatchReasons.Max(r => r.Score) : 0;
                    m.NormalizedScore = Math.Min(100, highestScore);
                    m.MatchScore = m.NormalizedScore / 100m; // Convert to 0-1 range for compatibility
                    return m;
                })
                .Where(m => m.NormalizedScore >= options.MinimumScore)
                .OrderByDescending(m => m.NormalizedScore)
                .Take(options.MaxResults)
                .ToList();
                
            return finalMatches;
        }

        private async Task<List<SupplierMatch>> MatchSuppliersForProduct(
            ProductRequirement requirement, 
            SupplierMatchingOptions options)
        {
            var matches = new List<SupplierMatch>();
            
            // If RequireExactMatch is true, ONLY use exact product matching
            if (options.RequireExactMatch)
            {
                // Only Level 1: Exact Product Match - must have the actual product
                matches.AddRange(await MatchExactProducts(requirement, strictMode: true));
            }
            else
            {
                // Level 1: Exact Product Match
                matches.AddRange(await MatchExactProducts(requirement, strictMode: false));
                
                // Level 2: Category Match
                matches.AddRange(await MatchByCategory(requirement));
                
                // Level 3: Business Type Match
                matches.AddRange(await MatchByBusinessType(requirement));
                
                // Level 4: Product Family Match
                matches.AddRange(await MatchByProductFamily(requirement));
                
                // Level 5: Keyword Match (if not enough results)
                if (matches.Count < 10)
                {
                    matches.AddRange(await MatchByKeywords(requirement));
                }
            }
            
            // Deduplicate and merge matches for same supplier
            var mergedMatches = matches
                .GroupBy(m => m.SupplierId)
                .Select(g => MergeSupplierMatches(g.ToList()))
                .ToList();
                
            return mergedMatches;
        }

        private async Task<List<SupplierMatch>> MatchExactProducts(ProductRequirement requirement, bool strictMode = false)
        {
            var matches = new List<SupplierMatch>();
            
            // For strict mode, require BOTH words "sunflower" AND "oil" to be present
            // Check Products table
            var productQuery = _context.Products
                .Where(p => p.SupplierId != null && p.ProductName != null);
            
            if (strictMode)
            {
                // For sunflower oil, must contain both "sunflower" AND "oil"
                var keywords = requirement.ProductName.ToLower().Split(' ');
                foreach (var keyword in keywords.Where(k => k.Length > 2))
                {
                    productQuery = productQuery.Where(p => p.ProductName!.ToLower().Contains(keyword));
                }
            }
            else
            {
                productQuery = productQuery.Where(p => p.ProductName!.ToLower().Contains(requirement.ProductName.ToLower()));
            }
            
            var exactProducts = await productQuery
                .Include(p => p.Supplier)
                .ToListAsync();
                
            foreach (var product in exactProducts)
            {
                if (product.Supplier == null) continue;
                
                var match = await CreateSupplierMatch(product.SupplierId!.Value);
                if (match == null) continue;
                
                match.MatchReasons.Add(new MatchReason
                {
                    Level = MatchLevel.ExactProduct,
                    Type = "Exact Product",
                    Detail = $"Has '{product.ProductName}' in catalog",
                    Score = 100m // 100% confidence for exact match
                });
                
                match.AvailableProducts.Add(product.ProductName!);
                match.MatchScore = 100m; // 100% match score
                
                matches.Add(match);
            }
            
            // Check SupplierProductCatalog table
            var catalogQuery = _context.SupplierProductCatalogs.AsQueryable();
            
            // Extract key product words, ignoring packaging details
            var productKeywords = ExtractProductKeywords(requirement.ProductName);
            _logger.LogInformation($"Searching for products with keywords: {string.Join(", ", productKeywords)}");
            
            if (strictMode && productKeywords.Count >= 2)
            {
                // For sunflower oil, must contain both "sunflower" AND "oil"
                foreach (var keyword in productKeywords)
                {
                    catalogQuery = catalogQuery.Where(spc => spc.ProductName.ToLower().Contains(keyword));
                }
            }
            else if (productKeywords.Any())
            {
                // Match any product containing at least one keyword
                var firstKeyword = productKeywords.First();
                catalogQuery = catalogQuery.Where(spc => spc.ProductName.ToLower().Contains(firstKeyword));
                
                // For oil products specifically, also require "oil" to be present
                if (firstKeyword != "oil" && requirement.ProductName.ToLower().Contains("oil"))
                {
                    catalogQuery = catalogQuery.Where(spc => spc.ProductName.ToLower().Contains("oil"));
                }
            }
            
            var catalogProducts = await catalogQuery.ToListAsync();
            
            _logger.LogInformation($"Found {catalogProducts.Count} catalog products matching '{requirement.ProductName}'");
                
            foreach (var catalogProduct in catalogProducts)
            {
                _logger.LogInformation($"Processing catalog product: {catalogProduct.ProductName} from supplier {catalogProduct.SupplierId}");
                
                var match = await CreateSupplierMatch(catalogProduct.SupplierId);
                if (match == null)
                {
                    _logger.LogWarning($"Could not create supplier match for supplier {catalogProduct.SupplierId}");
                    continue;
                }
                
                match.MatchReasons.Add(new MatchReason
                {
                    Level = MatchLevel.ExactProduct,
                    Type = "Catalog Product",
                    Detail = $"Has '{catalogProduct.ProductName}' in product catalog",
                    Score = 95m // 95% confidence for catalog product
                });
                
                match.AvailableProducts.Add(catalogProduct.ProductName);
                match.MatchScore = 95m; // 95% match score for catalog items
                
                _logger.LogInformation($"Added product '{catalogProduct.ProductName}' to supplier {match.CompanyName}");
                
                matches.Add(match);
            }
            
            return matches;
        }

        private async Task<List<SupplierMatch>> MatchByCategory(ProductRequirement requirement)
        {
            var matches = new List<SupplierMatch>();
            
            // Determine category keywords based on product
            var categoryKeywords = DetermineCategoryKeywords(requirement);
            
            // Check SupplierDetails.ProductCategories
            var supplierDetails = await _context.SupplierDetails
                .Where(sd => sd.ProductCategories != null)
                .ToListAsync();
                
            foreach (var detail in supplierDetails)
            {
                if (string.IsNullOrWhiteSpace(detail.ProductCategories)) continue;
                
                var categories = detail.ProductCategories.ToLower();
                var matchedKeywords = categoryKeywords.Where(k => categories.Contains(k.ToLower())).ToList();
                
                if (matchedKeywords.Any())
                {
                    // For sunflower oil specifically, verify they have actual products
                    if (requirement.ProductName.ToLower().Contains("sunflower") && 
                        requirement.ProductName.ToLower().Contains("oil"))
                    {
                        var hasActualProducts = await _context.SupplierProductCatalogs
                            .AnyAsync(p => p.SupplierId == detail.UserId && 
                                          p.ProductName.ToLower().Contains("sunflower") &&
                                          p.ProductName.ToLower().Contains("oil"));
                        
                        if (!hasActualProducts)
                        {
                            _logger.LogInformation($"Skipping {detail.UserId} - claims oil category but no actual sunflower oil products");
                            continue;
                        }
                    }
                    
                    var match = await CreateSupplierMatch(detail.UserId);
                    if (match == null) continue;
                    
                    match.MatchReasons.Add(new MatchReason
                    {
                        Level = MatchLevel.CategoryMatch,
                        Type = "Category Match",
                        Detail = $"Supplier categories include: {string.Join(", ", matchedKeywords)}",
                        Score = (decimal)MatchLevel.CategoryMatch
                    });
                    
                    match.ProductCategories = detail.ProductCategories;
                    match.MatchScore = (decimal)MatchLevel.CategoryMatch;
                    
                    matches.Add(match);
                }
            }
            
            // Check Suppliers table (CompanySuppliers) categories
            var suppliers = await _context.SupplierDetails
                .Where(s => s.ProductCategories != null)
                .ToListAsync();
                
            foreach (var supplier in suppliers)
            {
                if (string.IsNullOrWhiteSpace(supplier.ProductCategories)) continue;
                
                var categories = supplier.ProductCategories.ToLower();
                var matchedKeywords = categoryKeywords.Where(k => categories.Contains(k.ToLower())).ToList();
                
                if (matchedKeywords.Any())
                {
                    // Get the user associated with this supplier
                    var user = await _context.FdxUsers
                        .FirstOrDefaultAsync(u => u.Id == supplier.UserId);
                        
                    if (user != null)
                    {
                        var match = await CreateSupplierMatch(user.Id);
                        if (match == null) continue;
                        
                        match.MatchReasons.Add(new MatchReason
                        {
                            Level = MatchLevel.CategoryMatch,
                            Type = "Company Category",
                            Detail = $"Company categories include: {string.Join(", ", matchedKeywords)}",
                            Score = (decimal)MatchLevel.CategoryMatch * 0.95m
                        });
                        
                        match.ProductCategories = supplier.ProductCategories;
                        match.MatchScore = (decimal)MatchLevel.CategoryMatch * 0.95m;
                        
                        matches.Add(match);
                    }
                }
            }
            
            return matches;
        }

        private async Task<List<SupplierMatch>> MatchByBusinessType(ProductRequirement requirement)
        {
            var matches = new List<SupplierMatch>();
            var businessKeywords = DetermineBusinessKeywords(requirement);
            
            var users = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier && u.BusinessType != null)
                .ToListAsync();
                
            foreach (var user in users)
            {
                if (string.IsNullOrWhiteSpace(user.BusinessType)) continue;
                
                var businessType = user.BusinessType.ToLower();
                var matchedKeywords = businessKeywords.Where(k => businessType.Contains(k.ToLower())).ToList();
                
                if (matchedKeywords.Any())
                {
                    var match = await CreateSupplierMatch(user.Id);
                    if (match == null) continue;
                    
                    match.MatchReasons.Add(new MatchReason
                    {
                        Level = MatchLevel.BusinessType,
                        Type = "Business Type",
                        Detail = $"Business type matches: {string.Join(", ", matchedKeywords)}",
                        Score = (decimal)MatchLevel.BusinessType
                    });
                    
                    match.BusinessType = user.BusinessType;
                    match.MatchScore = (decimal)MatchLevel.BusinessType;
                    
                    matches.Add(match);
                }
            }
            
            return matches;
        }

        private async Task<List<SupplierMatch>> MatchByProductFamily(ProductRequirement requirement)
        {
            var matches = new List<SupplierMatch>();
            var familyKeywords = DetermineFamilyKeywords(requirement);
            
            // Find suppliers with related products
            var relatedProducts = await _context.Products
                .Where(p => p.SupplierId != null && p.ProductName != null)
                .ToListAsync();
                
            var supplierGroups = relatedProducts
                .Where(p => familyKeywords.Any(k => p.ProductName!.ToLower().Contains(k.ToLower())))
                .GroupBy(p => p.SupplierId);
                
            foreach (var group in supplierGroups)
            {
                var match = await CreateSupplierMatch(group.Key!.Value);
                if (match == null) continue;
                
                var relatedProductNames = group.Select(p => p.ProductName).Take(3).ToList();
                
                match.MatchReasons.Add(new MatchReason
                {
                    Level = MatchLevel.ProductFamily,
                    Type = "Product Family",
                    Detail = $"Has related products: {string.Join(", ", relatedProductNames)}",
                    Score = (decimal)MatchLevel.ProductFamily
                });
                
                match.AvailableProducts.AddRange(relatedProductNames!);
                match.MatchScore = (decimal)MatchLevel.ProductFamily;
                
                matches.Add(match);
            }
            
            return matches;
        }

        private async Task<List<SupplierMatch>> MatchByKeywords(ProductRequirement requirement)
        {
            var matches = new List<SupplierMatch>();
            
            var users = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier)
                .ToListAsync();
                
            foreach (var user in users)
            {
                var matchedIn = new List<string>();
                
                foreach (var keyword in requirement.Keywords)
                {
                    if (user.CompanyName?.ToLower().Contains(keyword) == true)
                        matchedIn.Add($"company name");
                    
                    if (user.FullDescription?.ToLower().Contains(keyword) == true)
                        matchedIn.Add($"description");
                }
                
                if (matchedIn.Any())
                {
                    var match = await CreateSupplierMatch(user.Id);
                    if (match == null) continue;
                    
                    match.MatchReasons.Add(new MatchReason
                    {
                        Level = MatchLevel.KeywordMatch,
                        Type = "Keyword Match",
                        Detail = $"Keywords found in: {string.Join(", ", matchedIn.Distinct())}",
                        Score = (decimal)MatchLevel.KeywordMatch
                    });
                    
                    match.MatchScore = (decimal)MatchLevel.KeywordMatch;
                    matches.Add(match);
                }
            }
            
            return matches;
        }

        private async Task<SupplierMatch?> CreateSupplierMatch(int userId)
        {
            var user = await _context.FdxUsers.FindAsync(userId);
            if (user == null) return null;
            
            var supplierDetails = await _context.SupplierDetails
                .FirstOrDefaultAsync(sd => sd.UserId == userId);
                
            // Find supplier by matching company name
            var company = await _context.FdxUsers
                .FirstOrDefaultAsync(c => c.CompanyName == user.CompanyName);
            var supplier = company != null ? await _context.SupplierDetails
                .FirstOrDefaultAsync(s => s.UserId == company.Id) : null;
            
            var match = new SupplierMatch
            {
                SupplierId = userId,
                CompanyName = user.CompanyName ?? user.Username,
                Country = user.Country,
                ContactEmail = user.Email,
                ContactPhone = user.PhoneNumber,
                IsVerified = supplierDetails?.IsVerified ?? false,
                TotalOrders = supplierDetails?.TotalOrders,
                Rating = supplierDetails?.Rating,
                ProductCategories = supplierDetails?.ProductCategories ?? supplier?.ProductCategories,
                BusinessType = user.BusinessType,
                Certifications = supplierDetails?.Certifications, // ?? supplier?.QualityCertifications,
                PaymentTerms = supplierDetails?.PaymentTerms ?? supplier?.PaymentTerms,
                Incoterms = supplierDetails?.Incoterms ?? supplier?.Incoterms,
                CanManufacture = user.BusinessType?.ToLower().Contains("manufactur") ?? false,
                CanTrade = user.BusinessType?.ToLower().Contains("trad") ?? false,
                CanExport = false // supplier?.CanShipDirect ?? false
            };
            
            return match;
        }

        private SupplierMatch MergeSupplierMatches(List<SupplierMatch> matches)
        {
            var primary = matches.First();
            
            foreach (var match in matches.Skip(1))
            {
                primary.MatchReasons.AddRange(match.MatchReasons);
                primary.AvailableProducts.AddRange(match.AvailableProducts);
                primary.MatchScore = Math.Max(primary.MatchScore, match.MatchScore);
            }
            
            // Remove duplicate products and reasons
            primary.AvailableProducts = primary.AvailableProducts.Distinct().ToList();
            
            // Consolidate similar reasons
            primary.MatchReasons = primary.MatchReasons
                .GroupBy(r => new { r.Level, r.Type })
                .Select(g => g.First())
                .OrderByDescending(r => r.Score)
                .ToList();
            
            return primary;
        }

        private List<string> DetermineCategoryKeywords(ProductRequirement requirement)
        {
            var keywords = new List<string>();
            var productLower = requirement.ProductName.ToLower();
            
            // Oil-specific categories
            if (productLower.Contains("oil"))
            {
                keywords.AddRange(new[] { "oil", "oils", "edible oil", "cooking oil", "vegetable oil" });
                
                if (productLower.Contains("sunflower"))
                    keywords.AddRange(new[] { "sunflower", "sunflower oil", "seed oil" });
                else if (productLower.Contains("olive"))
                    keywords.AddRange(new[] { "olive", "olive oil" });
                else if (productLower.Contains("palm"))
                    keywords.AddRange(new[] { "palm", "palm oil" });
                else if (productLower.Contains("soybean") || productLower.Contains("soya"))
                    keywords.AddRange(new[] { "soybean", "soya", "soybean oil" });
            }
            
            // Add general category if specified
            if (!string.IsNullOrWhiteSpace(requirement.Category))
                keywords.Add(requirement.Category.ToLower());
            
            // Add keywords from requirement
            keywords.AddRange(requirement.Keywords);
            
            return keywords.Distinct().ToList();
        }

        private List<string> DetermineBusinessKeywords(ProductRequirement requirement)
        {
            var keywords = new List<string>();
            var productLower = requirement.ProductName.ToLower();
            
            if (productLower.Contains("oil"))
            {
                keywords.AddRange(new[] { 
                    "oil", "oils", "edible", "refinery", "refining", 
                    "oil mill", "oil processing", "oil manufacturer",
                    "oil trader", "oil supplier", "oil exporter"
                });
            }
            
            // General manufacturing/trading keywords
            keywords.AddRange(new[] { "manufacturer", "producer", "trader", "supplier", "exporter" });
            
            return keywords.Distinct().ToList();
        }

        private List<string> DetermineFamilyKeywords(ProductRequirement requirement)
        {
            var keywords = new List<string>();
            var productLower = requirement.ProductName.ToLower();
            
            if (productLower.Contains("oil"))
            {
                // All types of oils are in the same family
                keywords.AddRange(new[] { 
                    "oil", "vegetable oil", "cooking oil", "edible oil",
                    "seed oil", "refined oil", "crude oil"
                });
            }
            
            return keywords.Distinct().ToList();
        }
        
        private List<string> ExtractProductKeywords(string productName)
        {
            var keywords = new List<string>();
            var lowerName = productName.ToLower();
            
            // Remove common packaging/quantity terms
            var cleanedName = lowerName
                .Replace("-liter", "")
                .Replace("liter", "")
                .Replace("litre", "")
                .Replace("pet bottles", "")
                .Replace("pet bottle", "")
                .Replace("bottles", "")
                .Replace("bottle", "")
                .Replace("5l", "")
                .Replace("1l", "")
                .Replace("2l", "")
                .Replace("3l", "");
            
            // Split and filter words
            var words = cleanedName
                .Split(new[] { ' ', '-', ',', '/', '\\', '(', ')', '[', ']' }, StringSplitOptions.RemoveEmptyEntries)
                .Where(w => w.Length > 2 && !IsNumber(w))
                .ToList();
            
            // For oil products, ensure we get the oil type
            if (lowerName.Contains("sunflower") && lowerName.Contains("oil"))
            {
                keywords.Add("sunflower");
                keywords.Add("oil");
            }
            else if (lowerName.Contains("oil"))
            {
                keywords.AddRange(words);
                if (!keywords.Contains("oil"))
                    keywords.Add("oil");
            }
            else
            {
                keywords.AddRange(words);
            }
            
            return keywords.Distinct().ToList();
        }
        
        private bool IsNumber(string word)
        {
            return double.TryParse(word, out _);
        }
    }
}