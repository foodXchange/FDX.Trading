using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using System.Linq;
using System.Threading.Tasks;
using System.Text.RegularExpressions;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DataFixController : ControllerBase
{
    private readonly FdxTradingContext _context;
    
    public DataFixController(FdxTradingContext context)
    {
        _context = context;
    }
    
    // POST: api/datafix/link-products-to-suppliers
    [HttpPost("link-products-to-suppliers")]
    public async Task<ActionResult<object>> LinkProductsToSuppliers()
    {
        var updateCount = 0;
        var errors = new List<string>();
        
        try
        {
            // Get all supplier products with their relationships
            var supplierProducts = await _context.SupplierProducts
                .Include(sp => sp.SupplierDetails)
                .ToListAsync();
            
            // Group by ProductId to handle duplicates
            var productSupplierMap = supplierProducts
                .GroupBy(sp => sp.ProductId)
                .ToDictionary(
                    g => g.Key,
                    g => g.OrderBy(sp => sp.Id).First().SupplierDetails.UserId
                );
            
            // Update products with supplier IDs
            var products = await _context.Products.ToListAsync();
            
            foreach (var product in products)
            {
                if (productSupplierMap.ContainsKey(product.Id))
                {
                    product.SupplierId = productSupplierMap[product.Id];
                    
                    // Also copy pricing information from the first SupplierProduct entry
                    var supplierProduct = supplierProducts
                        .Where(sp => sp.ProductId == product.Id && sp.SupplierDetails.UserId == product.SupplierId)
                        .FirstOrDefault();
                    
                    if (supplierProduct != null)
                    {
                        product.UnitWholesalePrice = supplierProduct.UnitWholesalePrice;
                        product.CartonWholesalePrice = supplierProduct.CartonWholesalePrice;
                        product.Currency = supplierProduct.Currency;
                        product.Incoterms = supplierProduct.Incoterms;
                        product.PaymentTerms = supplierProduct.PaymentTerms;
                        product.MOQ = supplierProduct.MinimumOrderQuantity;
                        product.MOQCartons = supplierProduct.MinimumOrderCartons;
                        product.CartonsPerContainer20ft = supplierProduct.CartonsPerContainer20ft;
                        product.CartonsPerContainer40ft = supplierProduct.CartonsPerContainer40ft;
                        product.PalletsPerContainer20ft = supplierProduct.PalletsPerContainer20ft;
                        product.PalletsPerContainer40ft = supplierProduct.PalletsPerContainer40ft;
                        product.PreferredPort = supplierProduct.ShippingPort;
                        product.LeadTimeDays = supplierProduct.LeadTimeDays;
                        product.SupplierProductCode = supplierProduct.SupplierProductCode;
                    }
                    
                    updateCount++;
                }
            }
            
            await _context.SaveChangesAsync();
            
            // Get summary statistics
            var supplierStats = await _context.Products
                .Where(p => p.SupplierId != null)
                .GroupBy(p => p.SupplierId)
                .Select(g => new 
                {
                    SupplierId = g.Key,
                    ProductCount = g.Count()
                })
                .ToListAsync();
            
            // Get supplier names for the stats
            var supplierIds = supplierStats.Select(s => s.SupplierId).ToList();
            var suppliers = await _context.FdxUsers
                .Where(u => supplierIds.Contains(u.Id))
                .ToDictionaryAsync(u => u.Id, u => u.CompanyName);
            
            var detailedStats = supplierStats.Select(s => new
            {
                SupplierId = s.SupplierId,
                SupplierName = suppliers.ContainsKey(s.SupplierId!.Value) ? suppliers[s.SupplierId.Value] : "Unknown",
                ProductCount = s.ProductCount
            }).OrderByDescending(s => s.ProductCount).ToList();
            
            return Ok(new
            {
                success = true,
                message = $"Successfully linked {updateCount} products to suppliers",
                totalProducts = products.Count,
                productsWithSuppliers = updateCount,
                productsWithoutSuppliers = products.Count - updateCount,
                supplierBreakdown = detailedStats
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new
            {
                success = false,
                message = "Error linking products to suppliers",
                error = ex.Message
            });
        }
    }
    
    // GET: api/datafix/check-product-suppliers
    [HttpGet("check-product-suppliers")]
    public async Task<ActionResult<object>> CheckProductSuppliers()
    {
        var stats = new
        {
            totalProducts = await _context.Products.CountAsync(),
            productsWithSuppliers = await _context.Products.CountAsync(p => p.SupplierId != null),
            productsWithoutSuppliers = await _context.Products.CountAsync(p => p.SupplierId == null),
            totalSupplierProductLinks = await _context.SupplierProducts.CountAsync(),
            uniqueProductsInSupplierProducts = await _context.SupplierProducts.Select(sp => sp.ProductId).Distinct().CountAsync(),
            suppliersWithProducts = await _context.Products
                .Where(p => p.SupplierId != null)
                .Select(p => p.SupplierId)
                .Distinct()
                .CountAsync()
        };
        
        return Ok(stats);
    }
    
    // POST: api/datafix/assign-products-to-ardo
    [HttpPost("assign-products-to-ardo")]
    public async Task<ActionResult<object>> AssignProductsToArdo()
    {
        try
        {
            // Get Ardo supplier
            var ardo = await _context.FdxUsers.FirstOrDefaultAsync(u => u.Id == 260);
            if (ardo == null)
            {
                return NotFound("Ardo supplier not found");
            }
            
            // Assign first 50 products to Ardo as a demonstration
            var productsToAssign = await _context.Products
                .Where(p => p.SupplierId == null)
                .OrderBy(p => p.Id)
                .Take(50)
                .ToListAsync();
            
            foreach (var product in productsToAssign)
            {
                product.SupplierId = 260;
                product.Currency = "EUR";
                product.Incoterms = "FOB";
                product.PaymentTerms = "Net 30";
                product.MOQ = 1000;
                product.LeadTimeDays = 14;
                
                // Set some sample pricing
                var random = new Random();
                product.UnitWholesalePrice = (decimal)(random.Next(100, 5000) / 100.0);
                product.CartonWholesalePrice = product.UnitWholesalePrice * 12;
            }
            
            await _context.SaveChangesAsync();
            
            return Ok(new
            {
                success = true,
                message = $"Successfully assigned {productsToAssign.Count} products to Ardo",
                supplierId = 260,
                supplierName = ardo.CompanyName,
                productsAssigned = productsToAssign.Count
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new
            {
                success = false,
                message = "Error assigning products to Ardo",
                error = ex.Message
            });
        }
    }
    
    // POST: api/datafix/update-request-titles
    [HttpPost("update-request-titles")]
    public async Task<IActionResult> UpdateRequestTitles()
    {
        var requests = await _context.Requests
            .Include(r => r.RequestItems)
            .ToListAsync();
        
        int updatedCount = 0;
        var results = new List<object>();
        
        foreach (var request in requests)
        {
            string newTitle = GenerateProductBasedTitle(request);
            
            if (!string.IsNullOrEmpty(newTitle) && request.Title != newTitle)
            {
                var oldTitle = request.Title;
                request.Title = newTitle;
                updatedCount++;
                
                results.Add(new { 
                    requestNumber = request.RequestNumber,
                    oldTitle = oldTitle.Length > 50 ? oldTitle.Substring(0, 47) + "..." : oldTitle,
                    newTitle = newTitle
                });
            }
        }
        
        await _context.SaveChangesAsync();
        
        return Ok(new
        {
            success = true,
            message = $"Updated {updatedCount} request titles",
            totalRequests = requests.Count,
            updatedCount = updatedCount,
            updates = results.Take(50) // Show first 50 updates
        });
    }
    
    private string GenerateProductBasedTitle(Request request)
    {
        if (request.RequestItems == null || !request.RequestItems.Any())
        {
            return "Product sourcing";
        }
        
        // Get product names from items
        var productNames = request.RequestItems
            .Where(i => !string.IsNullOrWhiteSpace(i.ProductName))
            .Select(i => i.ProductName.Trim())
            .ToList();
        
        if (!productNames.Any())
        {
            return "Product sourcing";
        }
        
        string newTitle;
        
        if (productNames.Count == 1)
        {
            // Single product - clean and shorten the name
            var productName = productNames[0];
            
            // Remove common suffixes and clean up
            productName = Regex.Replace(productName, @"\s*-\s*.*", ""); // Remove everything after dash
            productName = Regex.Replace(productName, @"\s+\d+.*", ""); // Remove numbers and everything after
            productName = Regex.Replace(productName, @"\s*\(.*?\)", ""); // Remove parentheses content
            productName = productName.Trim();
            
            // Take first 4 words max, then add "sourcing"
            var words = productName.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            if (words.Length > 4)
            {
                newTitle = string.Join(" ", words.Take(4)) + " sourcing";
            }
            else if (words.Length > 0)
            {
                newTitle = productName + " sourcing";
            }
            else
            {
                newTitle = "Product sourcing";
            }
        }
        else
        {
            // Multiple products - create a combined title
            var distinctProducts = new List<string>();
            
            foreach (var name in productNames.Take(3)) // Take first 3 products
            {
                // Extract key word from each product
                var cleanName = Regex.Replace(name, @"\s*-\s*.*", "");
                cleanName = Regex.Replace(cleanName, @"\s+\d+.*", "");
                cleanName = Regex.Replace(cleanName, @"\s*\(.*?\)", "");
                cleanName = cleanName.Trim();
                
                var words = cleanName.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                if (words.Length > 0)
                {
                    // Take first significant word (not numbers, not single chars)
                    var keyWord = words.FirstOrDefault(w => w.Length > 2 && !Regex.IsMatch(w, @"^\d+$"));
                    if (!string.IsNullOrEmpty(keyWord))
                    {
                        distinctProducts.Add(char.ToUpper(keyWord[0]) + keyWord.Substring(1).ToLower());
                    }
                }
            }
            
            distinctProducts = distinctProducts.Distinct().Take(3).ToList();
            
            if (distinctProducts.Count > 1)
            {
                newTitle = string.Join(", ", distinctProducts.Take(2)) + " sourcing";
            }
            else if (distinctProducts.Count == 1)
            {
                newTitle = distinctProducts[0] + " products";
            }
            else
            {
                newTitle = "Multiple products";
            }
        }
        
        // Clean up and ensure max 5 words
        newTitle = Regex.Replace(newTitle, @"\s+", " ").Trim();
        var titleWords = newTitle.Split(' ');
        if (titleWords.Length > 5)
        {
            newTitle = string.Join(" ", titleWords.Take(5));
        }
        
        // Ensure title is not too long
        if (newTitle.Length > 100)
        {
            newTitle = newTitle.Substring(0, 97) + "...";
        }
        
        // Ensure at least 3 characters
        if (newTitle.Length < 3)
        {
            newTitle = "Product sourcing";
        }
        
        return newTitle;
    }
}