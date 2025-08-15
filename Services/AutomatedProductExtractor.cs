using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Threading.Channels;
using Microsoft.Extensions.Logging;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using HtmlAgilityPack;
using System.Text.Json;

namespace FDX.Trading.Services
{
    public class AutomatedProductExtractor
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<AutomatedProductExtractor> _logger;
        private readonly HttpClient _httpClient;
        
        // Patterns for identifying products
        private readonly List<string> _productIndicators = new()
        {
            "product", "item", "sku", "catalog", "shop", "store", "buy", 
            "price", "add to cart", "in stock", "available", "specification"
        };

        private readonly List<string> _weightPatterns = new()
        {
            @"\d+\s?(kg|g|mg|l|ml|oz|lb|liter|litre|gram|kilogram)",
            @"\d+\s?x\s?\d+\s?(kg|g|mg|l|ml)",
            @"\d+[.,]\d+\s?(kg|g|l|ml)"
        };

        public AutomatedProductExtractor(
            FdxTradingContext context,
            ILogger<AutomatedProductExtractor> logger,
            HttpClient httpClient)
        {
            _context = context;
            _logger = logger;
            _httpClient = httpClient;
            _httpClient.Timeout = TimeSpan.FromSeconds(30);
        }

        // Main entry point - processes all suppliers
        public async Task<ProductExtractionReport> ExtractAllSupplierProducts(int batchSize = 10)
        {
            var report = new ProductExtractionReport { StartTime = DateTime.Now };
            
            try
            {
                // Get all suppliers with websites
                var suppliers = await _context.FdxUsers
                    .Where(u => u.Type == UserType.Supplier && 
                               !string.IsNullOrEmpty(u.Website))
                    .OrderBy(u => u.Id)
                    .ToListAsync();

                report.TotalSuppliers = suppliers.Count;
                _logger.LogInformation($"Starting extraction for {suppliers.Count} suppliers");

                // Process in batches for better performance
                var batches = suppliers.Chunk(batchSize);
                
                foreach (var batch in batches)
                {
                    var tasks = batch.Select(supplier => ProcessSupplier(supplier, report));
                    await Task.WhenAll(tasks);
                    
                    // Save after each batch
                    await _context.SaveChangesAsync();
                    
                    _logger.LogInformation($"Progress: {report.ProcessedSuppliers}/{report.TotalSuppliers} suppliers processed");
                }

                report.EndTime = DateTime.Now;
                report.Success = true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in bulk extraction");
                report.Errors.Add($"Fatal error: {ex.Message}");
                report.Success = false;
            }

            return report;
        }

        // Process individual supplier
        private async Task ProcessSupplier(User supplier, ProductExtractionReport report)
        {
            try
            {
                _logger.LogInformation($"Processing supplier: {supplier.CompanyName} ({supplier.Website})");
                
                var website = NormalizeUrl(supplier.Website);
                if (string.IsNullOrEmpty(website))
                {
                    report.SkippedSuppliers++;
                    return;
                }

                // Try multiple extraction strategies
                var products = new List<ExtractedProduct>();
                
                // Strategy 1: Look for product/catalog pages
                products.AddRange(await ExtractFromProductPages(website, supplier));
                
                // Strategy 2: Extract from homepage
                if (!products.Any())
                {
                    products.AddRange(await ExtractFromHomepage(website, supplier));
                }
                
                // Strategy 3: Use AI to analyze the site
                if (!products.Any())
                {
                    products.AddRange(await ExtractUsingAI(website, supplier));
                }

                // Save products to database
                if (products.Any())
                {
                    await SaveProducts(products, supplier);
                    report.ProcessedSuppliers++;
                    report.TotalProductsExtracted += products.Count;
                    _logger.LogInformation($"Extracted {products.Count} products from {supplier.CompanyName}");
                }
                else
                {
                    report.SuppliersWithNoProducts++;
                    _logger.LogWarning($"No products found for {supplier.CompanyName}");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error processing supplier {supplier.CompanyName}");
                report.Errors.Add($"{supplier.CompanyName}: {ex.Message}");
                report.FailedSuppliers++;
            }
        }

        // Strategy 1: Extract from dedicated product pages
        private async Task<List<ExtractedProduct>> ExtractFromProductPages(string website, User supplier)
        {
            var products = new List<ExtractedProduct>();
            var productUrls = await FindProductUrls(website);
            
            foreach (var url in productUrls.Take(50)) // Limit to 50 products per supplier
            {
                try
                {
                    var html = await FetchHtml(url);
                    if (string.IsNullOrEmpty(html)) continue;
                    
                    var doc = new HtmlDocument();
                    doc.LoadHtml(html);
                    
                    var product = ExtractProductFromHtml(doc, supplier);
                    if (product != null && !string.IsNullOrEmpty(product.Name))
                    {
                        products.Add(product);
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogDebug(ex, $"Error extracting product from {url}");
                }
            }
            
            return products;
        }

        // Strategy 2: Extract from homepage
        private async Task<List<ExtractedProduct>> ExtractFromHomepage(string website, User supplier)
        {
            var products = new List<ExtractedProduct>();
            
            try
            {
                var html = await FetchHtml(website);
                if (string.IsNullOrEmpty(html)) return products;
                
                var doc = new HtmlDocument();
                doc.LoadHtml(html);
                
                // Look for product-like elements
                var productNodes = doc.DocumentNode.SelectNodes("//div[contains(@class, 'product') or contains(@class, 'item')]");
                if (productNodes != null)
                {
                    foreach (var node in productNodes.Take(30))
                    {
                        var product = ExtractProductFromNode(node, supplier);
                        if (product != null && !string.IsNullOrEmpty(product.Name))
                        {
                            products.Add(product);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogDebug(ex, $"Error extracting from homepage {website}");
            }
            
            return products;
        }

        // Strategy 3: Use pattern-based extraction
        private async Task<List<ExtractedProduct>> ExtractUsingAI(string website, User supplier)
        {
            // For now, return empty list - can be enhanced later with actual AI integration
            return new List<ExtractedProduct>();
        }

        // Extract product from HTML document
        private ExtractedProduct? ExtractProductFromHtml(HtmlDocument doc, User supplier)
        {
            var product = new ExtractedProduct { SupplierId = supplier.Id };
            
            // Extract product name
            var titleNode = doc.DocumentNode.SelectSingleNode("//h1") ?? 
                           doc.DocumentNode.SelectSingleNode("//title") ??
                           doc.DocumentNode.SelectSingleNode("//*[contains(@class, 'product-title')]");
            
            if (titleNode != null)
            {
                product.Name = CleanText(titleNode.InnerText);
            }
            
            // Extract brand
            var brandNode = doc.DocumentNode.SelectSingleNode("//*[contains(@class, 'brand') or contains(@itemprop, 'brand')]");
            if (brandNode != null)
            {
                product.Brand = CleanText(brandNode.InnerText);
            }
            
            // Extract weight/size
            product.Weight = ExtractWeight(doc.DocumentNode.InnerHtml);
            
            // Extract price
            var priceNode = doc.DocumentNode.SelectSingleNode("//*[contains(@class, 'price') or contains(@itemprop, 'price')]");
            if (priceNode != null)
            {
                product.Price = ExtractPrice(priceNode.InnerText);
            }
            
            // Extract description
            var descNode = doc.DocumentNode.SelectSingleNode("//*[contains(@class, 'description') or contains(@itemprop, 'description')]");
            if (descNode != null)
            {
                product.Description = CleanText(descNode.InnerText).Substring(0, Math.Min(500, descNode.InnerText.Length));
            }
            
            return product;
        }

        // Extract product from HTML node
        private ExtractedProduct? ExtractProductFromNode(HtmlNode node, User supplier)
        {
            var product = new ExtractedProduct { SupplierId = supplier.Id };
            
            // Look for product name
            var nameNode = node.SelectSingleNode(".//h2 | .//h3 | .//h4 | .//*[contains(@class, 'title')]");
            if (nameNode != null)
            {
                product.Name = CleanText(nameNode.InnerText);
            }
            
            // Extract weight from text
            product.Weight = ExtractWeight(node.InnerHtml);
            
            // Extract price
            var priceNode = node.SelectSingleNode(".//*[contains(@class, 'price')]");
            if (priceNode != null)
            {
                product.Price = ExtractPrice(priceNode.InnerText);
            }
            
            return !string.IsNullOrEmpty(product.Name) ? product : null;
        }

        // Find product URLs on website
        private async Task<List<string>> FindProductUrls(string website)
        {
            var urls = new List<string>();
            
            try
            {
                var html = await FetchHtml(website);
                if (string.IsNullOrEmpty(html)) return urls;
                
                var doc = new HtmlDocument();
                doc.LoadHtml(html);
                
                // Find links that look like product pages
                var links = doc.DocumentNode.SelectNodes("//a[@href]");
                if (links != null)
                {
                    foreach (var link in links)
                    {
                        var href = link.GetAttributeValue("href", "");
                        if (IsProductUrl(href))
                        {
                            var fullUrl = MakeAbsoluteUrl(href, website);
                            if (!string.IsNullOrEmpty(fullUrl))
                            {
                                urls.Add(fullUrl);
                            }
                        }
                    }
                }
                
                // Also check for common product page patterns
                var commonPaths = new[] { "/products", "/catalog", "/shop", "/store", "/items" };
                foreach (var path in commonPaths)
                {
                    urls.Add($"{website.TrimEnd('/')}{path}");
                }
            }
            catch (Exception ex)
            {
                _logger.LogDebug(ex, $"Error finding product URLs for {website}");
            }
            
            return urls.Distinct().ToList();
        }

        // Save extracted products to database
        private async Task SaveProducts(List<ExtractedProduct> products, User supplier)
        {
            foreach (var product in products)
            {
                try
                {
                    // Check if product already exists
                    var exists = await _context.SupplierProductCatalogs
                        .AnyAsync(p => p.SupplierId == supplier.Id && 
                                      p.ProductName == product.Name);
                    
                    if (exists) continue;
                    
                    var catalogProduct = new SupplierProductCatalog
                    {
                        SupplierId = supplier.Id,
                        ProductName = product.Name ?? "Unknown Product",
                        Brand = product.Brand,
                        Category = product.Category ?? DetermineCategory(product.Name ?? "", supplier),
                        Description = product.Description,
                        Unit = product.Weight,
                        PricePerUnit = product.Price,
                        Currency = product.Currency ?? "USD",
                        IsAvailable = true,
                        CountryOfOrigin = supplier.Country,
                        SearchTags = GenerateSearchTags(product),
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    };
                    
                    _context.SupplierProductCatalogs.Add(catalogProduct);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, $"Error saving product {product.Name}");
                }
            }
        }

        // Helper methods
        private async Task<string> FetchHtml(string url)
        {
            try
            {
                var response = await _httpClient.GetAsync(url);
                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadAsStringAsync();
                }
            }
            catch (Exception ex)
            {
                _logger.LogDebug(ex, $"Error fetching {url}");
            }
            return string.Empty;
        }

        private string NormalizeUrl(string? url)
        {
            if (string.IsNullOrWhiteSpace(url)) return string.Empty;
            
            url = url.Trim().ToLower();
            if (!url.StartsWith("http://") && !url.StartsWith("https://"))
            {
                url = "https://" + url;
            }
            
            return url;
        }

        private bool IsProductUrl(string url)
        {
            if (string.IsNullOrEmpty(url)) return false;
            
            var lowerUrl = url.ToLower();
            return _productIndicators.Any(indicator => lowerUrl.Contains(indicator));
        }

        private string MakeAbsoluteUrl(string url, string baseUrl)
        {
            try
            {
                var uri = new Uri(new Uri(baseUrl), url);
                return uri.ToString();
            }
            catch
            {
                return string.Empty;
            }
        }

        private string ExtractWeight(string text)
        {
            foreach (var pattern in _weightPatterns)
            {
                var match = Regex.Match(text, pattern, RegexOptions.IgnoreCase);
                if (match.Success)
                {
                    return match.Value.Trim();
                }
            }
            return string.Empty;
        }

        private decimal? ExtractPrice(string text)
        {
            var pricePattern = @"[\d,]+\.?\d*";
            var match = Regex.Match(text, pricePattern);
            if (match.Success)
            {
                if (decimal.TryParse(match.Value.Replace(",", ""), out var price))
                {
                    return price;
                }
            }
            return null;
        }

        private string CleanText(string text)
        {
            if (string.IsNullOrEmpty(text)) return string.Empty;
            
            // Remove extra whitespace and newlines
            text = Regex.Replace(text, @"\s+", " ");
            return text.Trim();
        }

        private string CleanHtmlForAI(string html)
        {
            var doc = new HtmlDocument();
            doc.LoadHtml(html);
            
            // Remove script and style elements
            doc.DocumentNode.Descendants()
                .Where(n => n.Name == "script" || n.Name == "style")
                .ToList()
                .ForEach(n => n.Remove());
            
            return doc.DocumentNode.InnerText;
        }

        private string DetermineCategory(string productName, User supplier)
        {
            var lowerName = productName.ToLower();
            
            if (lowerName.Contains("oil")) return "Oils";
            if (lowerName.Contains("flour") || lowerName.Contains("grain")) return "Grains";
            if (lowerName.Contains("sugar") || lowerName.Contains("sweet")) return "Sweeteners";
            if (lowerName.Contains("spice") || lowerName.Contains("seasoning")) return "Spices";
            if (lowerName.Contains("dairy") || lowerName.Contains("milk") || lowerName.Contains("cheese")) return "Dairy";
            if (lowerName.Contains("meat") || lowerName.Contains("chicken") || lowerName.Contains("beef")) return "Meat";
            if (lowerName.Contains("fruit") || lowerName.Contains("vegetable")) return "Produce";
            if (lowerName.Contains("beverage") || lowerName.Contains("drink")) return "Beverages";
            if (lowerName.Contains("snack") || lowerName.Contains("cookie") || lowerName.Contains("biscuit")) return "Snacks";
            
            return supplier.Category ?? "General";
        }

        private string GenerateSearchTags(ExtractedProduct product)
        {
            var tags = new List<string>();
            
            if (!string.IsNullOrEmpty(product.Name))
                tags.AddRange(product.Name.Split(' ').Where(w => w.Length > 2));
            
            if (!string.IsNullOrEmpty(product.Brand))
                tags.Add(product.Brand);
            
            if (!string.IsNullOrEmpty(product.Category))
                tags.Add(product.Category);
            
            return string.Join(", ", tags.Distinct());
        }
    }

    // Models for extraction
    public class ExtractedProduct
    {
        public string? Name { get; set; }
        public string? Brand { get; set; }
        public string? Weight { get; set; }
        public string? Category { get; set; }
        public string? Description { get; set; }
        public decimal? Price { get; set; }
        public string? Currency { get; set; }
        public int SupplierId { get; set; }
    }

    public class AIExtractedProduct
    {
        public string name { get; set; } = "";
        public string? brand { get; set; }
        public string? weight { get; set; }
        public string? category { get; set; }
        public string? description { get; set; }
    }

    public class ProductExtractionReport
    {
        public DateTime StartTime { get; set; }
        public DateTime? EndTime { get; set; }
        public bool Success { get; set; }
        public int TotalSuppliers { get; set; }
        public int ProcessedSuppliers { get; set; }
        public int SkippedSuppliers { get; set; }
        public int FailedSuppliers { get; set; }
        public int SuppliersWithNoProducts { get; set; }
        public int TotalProductsExtracted { get; set; }
        public List<string> Errors { get; set; } = new();
        
        public TimeSpan Duration => EndTime.HasValue ? EndTime.Value - StartTime : TimeSpan.Zero;
        public double SuccessRate => TotalSuppliers > 0 ? (ProcessedSuppliers * 100.0 / TotalSuppliers) : 0;
    }
}