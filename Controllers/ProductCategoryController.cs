using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using FDX.Trading.Data;
using FDX.Trading.Models;
using FDX.Trading.Services;
using CsvHelper;
using System.Globalization;
using CsvHelper.Configuration;

namespace FDX.Trading.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ProductCategoryController : ControllerBase
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<ProductCategoryController> _logger;
        private readonly ImprovedCategoryMatchingService? _matchingService;

        public ProductCategoryController(
            FdxTradingContext context, 
            ILogger<ProductCategoryController> logger,
            ImprovedCategoryMatchingService? matchingService = null)
        {
            _context = context;
            _logger = logger;
            _matchingService = matchingService;
        }

        // GET: api/ProductCategory/hierarchy
        [HttpGet("hierarchy")]
        public async Task<ActionResult<IEnumerable<CategoryHierarchyDto>>> GetCategoryHierarchy()
        {
            var categories = await _context.ProductCategories
                .OrderBy(c => c.Category)
                .ThenBy(c => c.SubCategory)
                .ThenBy(c => c.Family)
                .ToListAsync();

            var hierarchy = categories
                .GroupBy(c => c.Category)
                .Select(categoryGroup => new CategoryHierarchyDto
                {
                    Category = categoryGroup.Key,
                    SubCategories = categoryGroup
                        .GroupBy(c => c.SubCategory)
                        .Select(subCategoryGroup => new SubCategoryDto
                        {
                            Name = subCategoryGroup.Key,
                            Families = subCategoryGroup
                                .GroupBy(c => c.Family)
                                .Select(familyGroup => new FamilyDto
                                {
                                    Name = familyGroup.Key,
                                    SubFamilies = familyGroup
                                        .Where(c => !string.IsNullOrWhiteSpace(c.SubFamily))
                                        .Select(c => c.SubFamily!)
                                        .Distinct()
                                        .OrderBy(s => s)
                                        .ToList()
                                })
                                .OrderBy(f => f.Name)
                                .ToList()
                        })
                        .OrderBy(s => s.Name)
                        .ToList()
                })
                .OrderBy(c => c.Category)
                .ToList();

            return Ok(hierarchy);
        }

        // GET: api/ProductCategory/search?q=sunflower
        [HttpGet("search")]
        public async Task<ActionResult<IEnumerable<ProductCategory>>> SearchCategories([FromQuery] string q)
        {
            if (string.IsNullOrWhiteSpace(q))
                return BadRequest("Search query is required");

            var query = q.ToLower();
            var categories = await _context.ProductCategories
                .Where(c => c.FullPath.ToLower().Contains(query) ||
                           c.Category.ToLower().Contains(query) ||
                           c.SubCategory.ToLower().Contains(query) ||
                           c.Family.ToLower().Contains(query) ||
                           (c.SubFamily != null && c.SubFamily.ToLower().Contains(query)))
                .Take(20)
                .ToListAsync();

            return Ok(categories);
        }

        // POST: api/ProductCategory/import-csv
        [HttpPost("import-csv")]
        public async Task<IActionResult> ImportCategoriesFromCsv()
        {
            var csvFilePath = @"C:\Users\fdxadmin\Downloads\Products Category 9_8_2025.csv";
            
            if (!System.IO.File.Exists(csvFilePath))
            {
                return NotFound($"CSV file not found at {csvFilePath}");
            }

            var imported = 0;
            var skipped = 0;
            var errors = new List<string>();

            try
            {
                using (var reader = new StreamReader(csvFilePath, Encoding.UTF8))
                {
                    // Skip header
                    await reader.ReadLineAsync();
                    
                    string? line;
                    var lineNumber = 1;
                    
                    while ((line = await reader.ReadLineAsync()) != null)
                    {
                        lineNumber++;
                        try
                        {
                            var values = ParseCsvLine(line);
                            
                            if (values.Length < 11) // Must have at least 11 columns
                                continue;

                            var category = values[1].Trim();
                            var subCategory = values[2].Trim();
                            var family = values[3].Trim();
                            var subFamily = values[4].Trim();
                            var productFamilyId = values[10].Trim();

                            // Skip if main fields are empty
                            if (string.IsNullOrWhiteSpace(category) || 
                                string.IsNullOrWhiteSpace(subCategory) || 
                                string.IsNullOrWhiteSpace(family))
                            {
                                skipped++;
                                continue;
                            }

                            // Check if already exists
                            var exists = await _context.ProductCategories.AnyAsync(pc =>
                                pc.Category == category &&
                                pc.SubCategory == subCategory &&
                                pc.Family == family &&
                                (string.IsNullOrWhiteSpace(subFamily) ? pc.SubFamily == null : pc.SubFamily == subFamily));

                            if (exists)
                            {
                                skipped++;
                                continue;
                            }

                            var productCategory = new ProductCategory
                            {
                                Category = category,
                                SubCategory = subCategory,
                                Family = family,
                                SubFamily = string.IsNullOrWhiteSpace(subFamily) ? null : subFamily,
                                ProductFamilyId = string.IsNullOrWhiteSpace(productFamilyId) ? null : productFamilyId,
                                CreatedBy = "CSV Import",
                                UpdatedBy = "CSV Import",
                                CreatedAt = DateTime.Now,
                                UpdatedAt = DateTime.Now
                            };

                            productCategory.BuildFullPath();
                            
                            _context.ProductCategories.Add(productCategory);
                            imported++;

                            // Save in batches
                            if (imported % 50 == 0)
                            {
                                await _context.SaveChangesAsync();
                                _logger.LogInformation($"Imported {imported} categories so far...");
                            }
                        }
                        catch (Exception ex)
                        {
                            errors.Add($"Line {lineNumber}: {ex.Message}");
                        }
                    }
                }

                // Save remaining
                await _context.SaveChangesAsync();

                _logger.LogInformation($"Category import completed: {imported} imported, {skipped} skipped");

                return Ok(new
                {
                    success = true,
                    message = $"Successfully imported {imported} product categories",
                    imported,
                    skipped,
                    errors = errors.Take(10) // Show first 10 errors only
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error importing product categories");
                return StatusCode(500, new { error = "Failed to import categories", message = ex.Message });
            }
        }

        // POST: api/ProductCategory/link-products
        [HttpPost("link-products")]
        public async Task<IActionResult> LinkProductsToCategories()
        {
            try
            {
                var products = await _context.SupplierProductCatalogs
                    .Where(p => p.ProductCategoryId == null && !string.IsNullOrWhiteSpace(p.Category))
                    .ToListAsync();

                var linked = 0;
                var notFound = 0;

                foreach (var product in products)
                {
                    // Try to find matching category
                    var category = await _context.ProductCategories
                        .FirstOrDefaultAsync(c => 
                            c.Category.ToLower() == product.Category!.ToLower() ||
                            c.SubCategory.ToLower() == product.Category!.ToLower() ||
                            c.Family.ToLower() == product.Category!.ToLower() ||
                            c.FullPath.ToLower().Contains(product.Category!.ToLower()));

                    if (category != null)
                    {
                        product.ProductCategoryId = category.Id;
                        linked++;
                    }
                    else
                    {
                        // Try to match by product name keywords
                        var productNameLower = product.ProductName.ToLower();
                        
                        if (productNameLower.Contains("oil"))
                        {
                            category = await _context.ProductCategories
                                .FirstOrDefaultAsync(c => c.Family.ToLower().Contains("oil"));
                        }
                        else if (productNameLower.Contains("cookie") || productNameLower.Contains("biscuit"))
                        {
                            category = await _context.ProductCategories
                                .FirstOrDefaultAsync(c => c.Family.ToLower().Contains("cookie") || 
                                                         c.Family.ToLower().Contains("biscuit"));
                        }
                        else if (productNameLower.Contains("chocolate"))
                        {
                            category = await _context.ProductCategories
                                .FirstOrDefaultAsync(c => c.Family.ToLower().Contains("chocolate"));
                        }
                        else if (productNameLower.Contains("pasta"))
                        {
                            category = await _context.ProductCategories
                                .FirstOrDefaultAsync(c => c.Family.ToLower().Contains("pasta"));
                        }
                        else if (productNameLower.Contains("spread"))
                        {
                            category = await _context.ProductCategories
                                .FirstOrDefaultAsync(c => c.Family.ToLower().Contains("spread"));
                        }

                        if (category != null)
                        {
                            product.ProductCategoryId = category.Id;
                            linked++;
                        }
                        else
                        {
                            notFound++;
                        }
                    }
                }

                await _context.SaveChangesAsync();

                return Ok(new
                {
                    success = true,
                    message = $"Linked {linked} products to categories",
                    linked,
                    notFound,
                    totalProducts = products.Count
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error linking products to categories");
                return StatusCode(500, new { error = "Failed to link products", message = ex.Message });
            }
        }

        // POST: api/ProductCategory/improved-match
        [HttpPost("improved-match")]
        public async Task<IActionResult> ImprovedCategoryMatch()
        {
            if (_matchingService == null)
            {
                return StatusCode(500, new { error = "Matching service not available" });
            }

            try
            {
                var result = await _matchingService.MatchAllProducts();
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in improved category matching");
                return StatusCode(500, new { error = "Failed to match categories", message = ex.Message });
            }
        }

        // GET: api/ProductCategory/stats
        [HttpGet("stats")]
        public async Task<IActionResult> GetCategoryStats()
        {
            var totalCategories = await _context.ProductCategories.CountAsync();
            var totalProducts = await _context.SupplierProductCatalogs.CountAsync();
            var linkedProducts = await _context.SupplierProductCatalogs
                .CountAsync(p => p.ProductCategoryId != null);

            var topCategories = await _context.ProductCategories
                .Select(c => new
                {
                    Category = c.Category,
                    ProductCount = c.Products.Count
                })
                .GroupBy(x => x.Category)
                .Select(g => new
                {
                    Category = g.Key,
                    ProductCount = g.Sum(x => x.ProductCount)
                })
                .OrderByDescending(x => x.ProductCount)
                .Take(10)
                .ToListAsync();

            return Ok(new
            {
                totalCategories,
                totalProducts,
                linkedProducts,
                unlinkedProducts = totalProducts - linkedProducts,
                linkagePercentage = totalProducts > 0 ? (linkedProducts * 100.0 / totalProducts) : 0,
                topCategories
            });
        }

        private string[] ParseCsvLine(string line)
        {
            var values = new List<string>();
            var currentValue = new StringBuilder();
            var inQuotes = false;

            for (int i = 0; i < line.Length; i++)
            {
                var ch = line[i];

                if (ch == '"')
                {
                    if (inQuotes && i + 1 < line.Length && line[i + 1] == '"')
                    {
                        currentValue.Append('"');
                        i++; // Skip next quote
                    }
                    else
                    {
                        inQuotes = !inQuotes;
                    }
                }
                else if (ch == ',' && !inQuotes)
                {
                    values.Add(currentValue.ToString());
                    currentValue.Clear();
                }
                else
                {
                    currentValue.Append(ch);
                }
            }

            values.Add(currentValue.ToString());
            return values.ToArray();
        }
    }
}