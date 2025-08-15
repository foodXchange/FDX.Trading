using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using System.Linq;
using System.Threading.Tasks;
using System.Text.RegularExpressions;
using OfficeOpenXml;
using System.IO;
using FDX.Trading.Services;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DataFixController : ControllerBase
{
    private readonly FdxTradingContext _context;
    //private readonly ComprehensiveDataImportService _importService;
    
    public DataFixController(FdxTradingContext context/*, ComprehensiveDataImportService importService*/)
    {
        _context = context;
        //_importService = importService;
    }
    
    // POST: api/datafix/comprehensive-import
    //[HttpPost("comprehensive-import")]
    //public async Task<ActionResult<object>> ComprehensiveImport()
    //{
    //    try
    //    {
    //        var result = await _importService.ImportAllDataAsync();
    //        return Ok(result);
    //    }
    //    catch (Exception ex)
    //    {
    //        return StatusCode(500, new { error = ex.Message });
    //    }
    //}
    
    // POST: api/datafix/distribute-products-to-suppliers
    [HttpPost("distribute-products-to-suppliers")]
    public async Task<ActionResult<object>> DistributeProductsToSuppliers()
    {
        try
        {
            // Get all suppliers (Type = Supplier)
            var suppliers = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier)
                .OrderBy(u => u.Id)
                .ToListAsync();
            
            // Get all products without suppliers
            var productsWithoutSuppliers = await _context.Products
                .Where(p => p.SupplierId == null)
                .OrderBy(p => p.Id)
                .ToListAsync();
            
            if (!productsWithoutSuppliers.Any())
            {
                return Ok(new { message = "All products already have suppliers assigned" });
            }
            
            var updateCount = 0;
            var supplierIndex = 0;
            var supplierProductCounts = new Dictionary<int, int>();
            
            // Distribute products evenly among suppliers
            foreach (var product in productsWithoutSuppliers)
            {
                var supplier = suppliers[supplierIndex % suppliers.Count];
                product.SupplierId = supplier.Id;
                
                // Set pricing and terms based on supplier region
                if (supplier.Country?.Contains("Italy") == true)
                {
                    product.Currency = "EUR";
                    product.Incoterms = "EXW";
                    product.PaymentTerms = "Net 60";
                    product.LeadTimeDays = 21;
                }
                else if (supplier.Country?.Contains("Belgium") == true || supplier.Country?.Contains("Germany") == true)
                {
                    product.Currency = "EUR";
                    product.Incoterms = "FOB";
                    product.PaymentTerms = "Net 30";
                    product.LeadTimeDays = 14;
                }
                else if (supplier.Country?.Contains("Turkey") == true)
                {
                    product.Currency = "USD";
                    product.Incoterms = "CIF";
                    product.PaymentTerms = "LC at sight";
                    product.LeadTimeDays = 30;
                }
                else
                {
                    product.Currency = "USD";
                    product.Incoterms = "FOB";
                    product.PaymentTerms = "Net 45";
                    product.LeadTimeDays = 25;
                }
                
                // Set sample pricing if not already set
                if (product.UnitWholesalePrice == null || product.UnitWholesalePrice == 0)
                {
                    var random = new Random();
                    product.UnitWholesalePrice = (decimal)(random.Next(100, 5000) / 100.0);
                    product.CartonWholesalePrice = product.UnitWholesalePrice * 12;
                    product.MOQ = random.Next(100, 2000);
                }
                
                // Track counts
                if (!supplierProductCounts.ContainsKey(supplier.Id))
                    supplierProductCounts[supplier.Id] = 0;
                supplierProductCounts[supplier.Id]++;
                
                updateCount++;
                supplierIndex++;
            }
            
            await _context.SaveChangesAsync();
            
            // Get summary
            var summary = supplierProductCounts
                .Join(suppliers, 
                    kv => kv.Key, 
                    s => s.Id, 
                    (kv, s) => new { 
                        SupplierId = s.Id, 
                        SupplierName = s.CompanyName, 
                        ProductCount = kv.Value 
                    })
                .OrderByDescending(x => x.ProductCount)
                .ToList();
            
            return Ok(new
            {
                success = true,
                message = $"Successfully distributed {updateCount} products to {supplierProductCounts.Count} suppliers",
                totalProducts = updateCount,
                suppliersUsed = supplierProductCounts.Count,
                distribution = summary
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
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
                        product.MOQ = (int?)supplierProduct.MinimumOrderQuantity;
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
    
    // POST: api/datafix/import-products-excel
    [HttpPost("import-products-excel")]
    public async Task<ActionResult<object>> ImportProductsFromExcel([FromQuery] string? filePath = null)
    {
        try
        {
            // Set EPPlus license context
            ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
            
            // Use provided file path or default
            var excelFilePath = filePath ?? @"C:\Users\fdxadmin\Downloads\Products 18_9_2024.xlsx";
            
            if (!System.IO.File.Exists(excelFilePath))
            {
                return NotFound($"Excel file not found at: {excelFilePath}");
            }
            
            var importedProducts = new List<Product>();
            var errors = new List<string>();
            
            using (var package = new ExcelPackage(new FileInfo(excelFilePath)))
            {
                var worksheet = package.Workbook.Worksheets.FirstOrDefault();
                if (worksheet == null)
                {
                    return BadRequest("No worksheet found in Excel file");
                }
                
                // Check if worksheet has data
                if (worksheet.Dimension == null)
                {
                    return BadRequest("Worksheet is empty");
                }
                
                // Get column indices from header row
                var columnMap = new Dictionary<string, int>();
                var headers = new List<string>();
                for (int col = 1; col <= worksheet.Dimension.End.Column; col++)
                {
                    var headerValue = worksheet.Cells[1, col].Value?.ToString()?.Trim();
                    if (!string.IsNullOrEmpty(headerValue))
                    {
                        columnMap[headerValue.ToLower()] = col;
                        headers.Add(headerValue);
                    }
                }
                
                // Debug: Return headers if no product name column found
                if (!headers.Any(h => h.ToLower().Contains("product") || h.ToLower().Contains("name") || h.ToLower().Contains("description")))
                {
                    return Ok(new
                    {
                        debug = true,
                        message = "No product name column found. Available columns:",
                        columns = headers,
                        totalRows = worksheet.Dimension.End.Row,
                        totalColumns = worksheet.Dimension.End.Column,
                        firstRowValues = Enumerable.Range(1, Math.Min(10, worksheet.Dimension.End.Column))
                            .Select(col => new { Column = col, Value = worksheet.Cells[2, col].Value?.ToString() })
                    });
                }
                
                // Process each row
                for (int row = 2; row <= worksheet.Dimension.End.Row; row++)
                {
                    try
                    {
                        // Get product code and name
                        var productCode = GetCellValue(worksheet, row, columnMap, "product code", "code", "sku");
                        var productName = GetCellValue(worksheet, row, columnMap, "product name", "name", "product", "description");
                        
                        if (string.IsNullOrWhiteSpace(productName))
                            continue;
                            
                        // Check if product already exists
                        var existingProduct = await _context.Products
                            .FirstOrDefaultAsync(p => p.ProductCode == productCode || p.ProductName == productName);
                            
                        if (existingProduct != null)
                        {
                            // Update existing product
                            UpdateProductFromExcel(existingProduct, worksheet, row, columnMap);
                            importedProducts.Add(existingProduct);
                        }
                        else
                        {
                            // Create new product
                            var newProduct = new Product
                            {
                                ProductCode = productCode ?? $"IMPORT_{row:D5}",
                                ProductName = productName,
                                Category = GetCellValue(worksheet, row, columnMap, "category", "product category"),
                                SubCategory = GetCellValue(worksheet, row, columnMap, "subcategory", "sub category"),
                                Description = GetCellValue(worksheet, row, columnMap, "description", "details"),
                                Brand = GetCellValue(worksheet, row, columnMap, "brand", "manufacturer"),
                                Status = ProductStatus.Active,
                                ImportedAt = DateTime.Now
                            };
                            
                            UpdateProductFromExcel(newProduct, worksheet, row, columnMap);
                            
                            // Try to match with a supplier
                            var supplierName = GetCellValue(worksheet, row, columnMap, "supplier", "vendor", "company");
                            if (!string.IsNullOrEmpty(supplierName))
                            {
                                var supplier = await _context.FdxUsers
                                    .FirstOrDefaultAsync(u => u.Type == UserType.Supplier && 
                                        (u.CompanyName.Contains(supplierName) || supplierName.Contains(u.CompanyName)));
                                        
                                if (supplier != null)
                                {
                                    newProduct.SupplierId = supplier.Id;
                                }
                            }
                            
                            _context.Products.Add(newProduct);
                            importedProducts.Add(newProduct);
                        }
                    }
                    catch (Exception ex)
                    {
                        errors.Add($"Row {row}: {ex.Message}");
                    }
                }
                
                await _context.SaveChangesAsync();
            }
            
            return Ok(new
            {
                success = true,
                message = $"Import completed. {importedProducts.Count} products processed",
                imported = importedProducts.Count,
                errors = errors.Count,
                errorDetails = errors.Take(10),
                sampleProducts = importedProducts.Take(5).Select(p => new
                {
                    p.Id,
                    p.ProductCode,
                    p.ProductName,
                    p.Category,
                    SupplierId = p.SupplierId
                })
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message, stackTrace = ex.StackTrace });
        }
    }
    
    private string? GetCellValue(ExcelWorksheet worksheet, int row, Dictionary<string, int> columnMap, params string[] possibleHeaders)
    {
        foreach (var header in possibleHeaders)
        {
            if (columnMap.TryGetValue(header.ToLower(), out int col))
            {
                return worksheet.Cells[row, col].Value?.ToString()?.Trim();
            }
        }
        return null;
    }
    
    private void UpdateProductFromExcel(Product product, ExcelWorksheet worksheet, int row, Dictionary<string, int> columnMap)
    {
        // Update various fields if they exist in Excel
        var unitPrice = GetCellValue(worksheet, row, columnMap, "unit price", "price", "unit cost");
        if (decimal.TryParse(unitPrice, out decimal price))
        {
            product.UnitWholesalePrice = price;
        }
        
        var moq = GetCellValue(worksheet, row, columnMap, "moq", "minimum order", "min order");
        if (int.TryParse(moq, out int minOrder))
        {
            product.MOQ = minOrder;
        }
        
        product.Currency = GetCellValue(worksheet, row, columnMap, "currency", "curr") ?? product.Currency;
        product.Incoterms = GetCellValue(worksheet, row, columnMap, "incoterms", "terms") ?? product.Incoterms;
        product.PaymentTerms = GetCellValue(worksheet, row, columnMap, "payment terms", "payment") ?? product.PaymentTerms;
        product.CountryOfOrigin = GetCellValue(worksheet, row, columnMap, "origin", "country of origin", "country");
        product.HSCode = GetCellValue(worksheet, row, columnMap, "hs code", "hscode", "tariff");
        product.Barcode = GetCellValue(worksheet, row, columnMap, "barcode", "ean", "upc");
        
        // Check for certifications
        var kosher = GetCellValue(worksheet, row, columnMap, "kosher", "is kosher");
        product.IsKosher = kosher?.ToLower() == "yes" || kosher?.ToLower() == "true" || kosher == "1";
        
        var organic = GetCellValue(worksheet, row, columnMap, "organic", "is organic");
        product.IsOrganic = organic?.ToLower() == "yes" || organic?.ToLower() == "true" || organic == "1";
    }
    
    // POST: api/datafix/import-products-csv
    [HttpPost("import-products-csv")]
    public async Task<ActionResult<object>> ImportProductsFromCsv([FromQuery] string? filePath = null)
    {
        try
        {
            // Use provided file path or default
            var csvFilePath = filePath ?? @"C:\Users\fdxadmin\Downloads\Products 13_8_2025.csv";
            
            if (!System.IO.File.Exists(csvFilePath))
            {
                return NotFound($"CSV file not found at: {csvFilePath}");
            }
            
            var importedProducts = new List<Product>();
            var errors = new List<string>();
            var updatedProducts = new List<Product>();
            
            var lines = await System.IO.File.ReadAllLinesAsync(csvFilePath);
            if (lines.Length == 0)
            {
                return BadRequest("CSV file is empty");
            }
            
            // Parse header
            var headers = lines[0].Split(',').Select(h => h.Trim().Trim('"').ToLower()).ToArray();
            
            // Find column indices
            int GetColumnIndex(params string[] possibleNames)
            {
                foreach (var name in possibleNames)
                {
                    var index = Array.FindIndex(headers, h => h.Contains(name.ToLower()));
                    if (index >= 0) return index;
                }
                return -1;
            }
            
            var codeIndex = GetColumnIndex("product code", "code", "sku", "item code");
            var nameIndex = GetColumnIndex("product name", "name", "product", "description", "item");
            var categoryIndex = GetColumnIndex("category", "product category");
            var supplierIndex = GetColumnIndex("supplier", "vendor", "company", "manufacturer");
            
            if (nameIndex < 0)
            {
                return Ok(new
                {
                    debug = true,
                    message = "No product name column found",
                    headers = headers,
                    firstRowData = lines.Length > 1 ? lines[1].Split(',').Select(v => v.Trim().Trim('"')).ToArray() : null
                });
            }
            
            // Process each row
            for (int i = 1; i < lines.Length; i++)
            {
                try
                {
                    var values = lines[i].Split(',').Select(v => v.Trim().Trim('"')).ToArray();
                    
                    if (values.Length <= nameIndex)
                        continue;
                        
                    var productName = values[nameIndex];
                    if (string.IsNullOrWhiteSpace(productName))
                        continue;
                    
                    var productCode = codeIndex >= 0 && codeIndex < values.Length ? values[codeIndex] : null;
                    
                    // Check if product exists
                    var existingProduct = await _context.Products
                        .FirstOrDefaultAsync(p => 
                            (!string.IsNullOrEmpty(productCode) && p.ProductCode == productCode) ||
                            p.ProductName == productName);
                    
                    if (existingProduct != null)
                    {
                        // Update existing
                        if (categoryIndex >= 0 && categoryIndex < values.Length)
                            existingProduct.Category = values[categoryIndex];
                            
                        updatedProducts.Add(existingProduct);
                    }
                    else
                    {
                        // Create new product
                        var newProduct = new Product
                        {
                            ProductCode = !string.IsNullOrEmpty(productCode) ? productCode : $"CSV_{i:D5}",
                            ProductName = productName,
                            Category = categoryIndex >= 0 && categoryIndex < values.Length ? values[categoryIndex] : null,
                            Status = ProductStatus.Active,
                            ImportedAt = DateTime.Now
                        };
                        
                        // Try to match supplier
                        if (supplierIndex >= 0 && supplierIndex < values.Length)
                        {
                            var supplierName = values[supplierIndex];
                            if (!string.IsNullOrEmpty(supplierName))
                            {
                                var supplier = await _context.FdxUsers
                                    .FirstOrDefaultAsync(u => u.Type == UserType.Supplier && 
                                        u.CompanyName.Contains(supplierName));
                                        
                                if (supplier != null)
                                {
                                    newProduct.SupplierId = supplier.Id;
                                }
                            }
                        }
                        
                        _context.Products.Add(newProduct);
                        importedProducts.Add(newProduct);
                    }
                }
                catch (Exception ex)
                {
                    errors.Add($"Row {i + 1}: {ex.Message}");
                    if (errors.Count >= 10) break; // Stop after 10 errors
                }
            }
            
            await _context.SaveChangesAsync();
            
            return Ok(new
            {
                success = true,
                message = $"Import completed. {importedProducts.Count} new products, {updatedProducts.Count} updated",
                newProducts = importedProducts.Count,
                updatedProducts = updatedProducts.Count,
                errors = errors.Count,
                errorDetails = errors,
                sampleProducts = importedProducts.Take(5).Select(p => new
                {
                    p.Id,
                    p.ProductCode,
                    p.ProductName,
                    p.Category,
                    SupplierId = p.SupplierId
                })
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }
}