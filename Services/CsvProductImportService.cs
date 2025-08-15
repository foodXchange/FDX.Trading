using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using CsvHelper;
using CsvHelper.Configuration;
using FDX.Trading.Data;
using FDX.Trading.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace FDX.Trading.Services;

public class CsvProductImportService
{
    private readonly FdxTradingContext _context;
    private readonly ILogger<CsvProductImportService> _logger;

    public CsvProductImportService(FdxTradingContext context, ILogger<CsvProductImportService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<ProductImportResult> ImportProductsFromCsvAsync(string filePath)
    {
        var result = new ProductImportResult();
        var supplierCache = new Dictionary<string, User>();
        var productList = new List<Product>();

        try
        {
            using var reader = new StreamReader(filePath);
            using var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true,
                TrimOptions = CsvHelper.Configuration.TrimOptions.Trim,
                BadDataFound = null,
                MissingFieldFound = null
            });

            // Read all records
            var records = csv.GetRecords<dynamic>().ToList();
            result.TotalRows = records.Count;

            foreach (var record in records)
            {
                try
                {
                    var recordDict = record as IDictionary<string, object>;
                    if (recordDict == null) continue;

                    // Extract supplier name
                    var supplierName = GetValue(recordDict, "Supplier");
                    if (string.IsNullOrWhiteSpace(supplierName))
                    {
                        result.SkippedRows++;
                        result.Errors.Add($"Row {result.ProcessedRows + 1}: No supplier name");
                        continue;
                    }

                    // Get or create supplier
                    User supplier;
                    if (!supplierCache.ContainsKey(supplierName))
                    {
                        supplier = await GetOrCreateSupplierAsync(supplierName);
                        supplierCache[supplierName] = supplier;
                        if (supplier.Id == 0) // New supplier
                        {
                            result.SuppliersCreated++;
                        }
                    }
                    else
                    {
                        supplier = supplierCache[supplierName];
                    }

                    // Create product
                    var product = new Product
                    {
                        // Product identification
                        ProductCode = GetValue(recordDict, "Product code") ?? GetValue(recordDict, "Product ID") ?? Guid.NewGuid().ToString().Substring(0, 8),
                        ProductName = GetValue(recordDict, "Product Name") ?? "Unknown Product",
                        OriginalProductId = GetValue(recordDict, "Product ID"),
                        
                        // Supplier relationship
                        SupplierId = supplier.Id,
                        SupplierProductCode = GetValue(recordDict, "Supplier Product Code"),
                        
                        // Categories
                        Category = ParseCategory(GetValue(recordDict, "Products Category & Family")),
                        SubCategory = ParseSubCategory(GetValue(recordDict, "Products Category & Family")),
                        
                        // Pricing
                        UnitWholesalePrice = ParseDecimal(GetValue(recordDict, "Unit Wholesale Price (latest)") ?? GetValue(recordDict, "Unit Wholesale Price (Initial)")),
                        CartonWholesalePrice = ParseDecimal(GetValue(recordDict, "Price for Carton (wholesale)")),
                        Currency = GetValue(recordDict, "Currency for price") ?? "USD",
                        
                        // Terms
                        Incoterms = GetValue(recordDict, "Incoterms (Price Base)") ?? GetValue(recordDict, "Incoterms"),
                        PaymentTerms = GetValue(recordDict, "Payment Terms"),
                        PreferredPort = GetValue(recordDict, "Closest/ Prefered SeaPort"),
                        
                        // Logistics
                        MOQ = ParseInt(GetValue(recordDict, "MOQ (units)")),
                        GrossWeight = ParseDecimal(GetValue(recordDict, "Gross Weight")),
                        NetWeight = ParseDecimal(GetValue(recordDict, "Net Weight")),
                        UnitsPerCarton = ParseInt(GetValue(recordDict, "Units per carton")),
                        CartonsPerContainer20ft = ParseInt(GetValue(recordDict, "# of Cartons (20ft)")),
                        CartonsPerContainer40ft = ParseInt(GetValue(recordDict, "# of Cartons (40ft)")),
                        PalletsPerContainer20ft = ParseInt(GetValue(recordDict, "# of Pallets (20ft)")),
                        PalletsPerContainer40ft = ParseInt(GetValue(recordDict, "# of Pallets in (40ft)")),
                        
                        // Product details
                        HSCode = GetValue(recordDict, "HS/ Tariff Code"),
                        Barcode = GetValue(recordDict, "Buyer's Product code/ EAN"),
                        UnitOfMeasure = GetValue(recordDict, "Unit of Measure"),
                        ShelfLifeDays = ParseInt(GetValue(recordDict, "Shelf Life (Days)")),
                        MinTemperature = ParseDecimal(GetValue(recordDict, "Product's Min. temperature")),
                        MaxTemperature = ParseDecimal(GetValue(recordDict, "Product's Max temperature")),
                        
                        // Certifications
                        IsKosher = ParseBool(GetValue(recordDict, "Kosher?")),
                        
                        // Origin
                        CountryOfOrigin = GetValue(recordDict, "Supplier Country") ?? supplier.Country,
                        
                        // Buyer info
                        BuyerCompany = GetValue(recordDict, "Buyer Company"),
                        BuyerProductCode = GetValue(recordDict, "Buyer's Product code/ EAN"),
                        
                        // Images and descriptions
                        ProductImages = GetValue(recordDict, "Product Images"),
                        LabelImage = GetValue(recordDict, "Private- label Images"),
                        Description = GetValue(recordDict, "Supplier's Description & Products"),
                        OpenComments = GetValue(recordDict, "Open Comments"),
                        
                        // Status
                        Status = ParseProductStatus(GetValue(recordDict, "Status")),
                        
                        // Metadata
                        ImportedAt = DateTime.Now,
                        CreatedAt = DateTime.Now,
                        ImportNotes = $"Imported from CSV: {Path.GetFileName(filePath)}"
                    };

                    // Check if product already exists
                    var existingProduct = await _context.Products
                        .FirstOrDefaultAsync(p => p.ProductCode == product.ProductCode && p.SupplierId == supplier.Id);

                    if (existingProduct != null)
                    {
                        // Update existing product
                        UpdateExistingProduct(existingProduct, product);
                        result.ProductsUpdated++;
                    }
                    else
                    {
                        // Add new product
                        productList.Add(product);
                        result.ProductsCreated++;
                    }

                    result.ProcessedRows++;
                }
                catch (Exception ex)
                {
                    result.Errors.Add($"Row {result.ProcessedRows + 1}: {ex.Message}");
                    result.SkippedRows++;
                    _logger.LogError(ex, "Error processing row {RowNumber}", result.ProcessedRows + 1);
                }
            }

            // Bulk insert new products
            if (productList.Any())
            {
                await _context.Products.AddRangeAsync(productList);
                await _context.SaveChangesAsync();
            }

            result.Success = true;
            result.Message = $"Import completed: {result.ProductsCreated} products created, {result.ProductsUpdated} updated, {result.SuppliersCreated} suppliers created";
        }
        catch (Exception ex)
        {
            result.Success = false;
            result.Message = $"Import failed: {ex.Message}";
            result.Errors.Add(ex.ToString());
            _logger.LogError(ex, "CSV import failed");
        }

        return result;
    }

    private async Task<User> GetOrCreateSupplierAsync(string supplierName)
    {
        // Clean supplier name
        supplierName = supplierName.Trim();
        
        // Try to find existing supplier
        var supplier = await _context.FdxUsers
            .FirstOrDefaultAsync(u => u.Type == UserType.Supplier && 
                (u.CompanyName == supplierName || u.DisplayName == supplierName));

        if (supplier != null)
            return supplier;

        // Extract country from supplier name if present
        string country = "Unknown";
        string cleanName = supplierName;
        
        // Common patterns: "Company, Country" or "Company (Country)"
        if (supplierName.Contains(","))
        {
            var parts = supplierName.Split(',');
            if (parts.Length == 2)
            {
                cleanName = parts[0].Trim();
                country = parts[1].Trim();
            }
        }
        else if (supplierName.Contains("(") && supplierName.Contains(")"))
        {
            var startIdx = supplierName.LastIndexOf("(");
            var endIdx = supplierName.LastIndexOf(")");
            if (startIdx < endIdx)
            {
                country = supplierName.Substring(startIdx + 1, endIdx - startIdx - 1).Trim();
                cleanName = supplierName.Substring(0, startIdx).Trim();
            }
        }

        // Create username from company name
        var username = cleanName.ToLower()
            .Replace(" ", "_")
            .Replace(".", "")
            .Replace(",", "")
            .Replace("&", "and")
            .Replace("/", "_")
            .Replace("'", "")
            .Replace("\"", "");

        // Ensure username is unique
        var baseUsername = username;
        int counter = 1;
        while (await _context.FdxUsers.AnyAsync(u => u.Username == username))
        {
            username = $"{baseUsername}_{counter}";
            counter++;
        }

        // Create new supplier
        supplier = new User
        {
            Username = username,
            Password = "FDX2025!", // Default password
            Email = $"{username}@supplier.fdx",
            CompanyName = cleanName,
            DisplayName = supplierName,
            Type = UserType.Supplier,
            Country = country,
            IsActive = true,
            RequiresPasswordChange = true,
            CreatedAt = DateTime.Now,
            ImportedAt = DateTime.Now,
            ImportNotes = "Auto-created during product import",
            Verification = VerificationStatus.Pending,
            Category = "Supplier",
            BusinessType = "Product Supplier"
        };

        _context.FdxUsers.Add(supplier);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Created new supplier: {SupplierName} (ID: {SupplierId})", cleanName, supplier.Id);

        return supplier;
    }

    private void UpdateExistingProduct(Product existing, Product updated)
    {
        // Update fields if they have values in the new data
        if (updated.UnitWholesalePrice.HasValue)
            existing.UnitWholesalePrice = updated.UnitWholesalePrice;
        if (updated.CartonWholesalePrice.HasValue)
            existing.CartonWholesalePrice = updated.CartonWholesalePrice;
        if (!string.IsNullOrWhiteSpace(updated.Currency))
            existing.Currency = updated.Currency;
        if (!string.IsNullOrWhiteSpace(updated.Incoterms))
            existing.Incoterms = updated.Incoterms;
        if (!string.IsNullOrWhiteSpace(updated.PaymentTerms))
            existing.PaymentTerms = updated.PaymentTerms;
        if (updated.MOQ.HasValue)
            existing.MOQ = updated.MOQ;
        
        existing.UpdatedAt = DateTime.Now;
        existing.ImportNotes = $"Updated from CSV import on {DateTime.Now:yyyy-MM-dd HH:mm}";
    }

    private string? GetValue(IDictionary<string, object> record, string key)
    {
        if (record.TryGetValue(key, out var value) && value != null)
        {
            var strValue = value.ToString()?.Trim();
            return string.IsNullOrWhiteSpace(strValue) ? null : strValue;
        }
        return null;
    }

    private decimal? ParseDecimal(string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
            return null;
        
        // Remove currency symbols and spaces
        value = value.Replace("$", "").Replace("€", "").Replace("£", "").Replace(",", "").Trim();
        
        if (decimal.TryParse(value, NumberStyles.Any, CultureInfo.InvariantCulture, out var result))
            return result;
        
        return null;
    }

    private int? ParseInt(string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
            return null;
        
        value = value.Replace(",", "").Trim();
        
        if (int.TryParse(value, out var result))
            return result;
        
        return null;
    }

    private bool ParseBool(string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
            return false;
        
        value = value.ToLower().Trim();
        return value == "yes" || value == "true" || value == "1" || value.Contains("has certificate");
    }

    private string? ParseCategory(string? categoryFamily)
    {
        if (string.IsNullOrWhiteSpace(categoryFamily))
            return null;
        
        // Category is usually the first part before comma
        var parts = categoryFamily.Split(',');
        return parts[0].Trim();
    }

    private string? ParseSubCategory(string? categoryFamily)
    {
        if (string.IsNullOrWhiteSpace(categoryFamily))
            return null;
        
        // Subcategory is everything after the first comma
        var parts = categoryFamily.Split(',');
        if (parts.Length > 1)
        {
            return string.Join(", ", parts.Skip(1)).Trim();
        }
        return null;
    }

    private ProductStatus ParseProductStatus(string? status)
    {
        if (string.IsNullOrWhiteSpace(status))
            return ProductStatus.Active;
        
        status = status.ToLower().Trim();
        
        if (status.Contains("sourcing") || status.Contains("confirmed"))
            return ProductStatus.Active;
        if (status.Contains("inactive") || status.Contains("non-active"))
            return ProductStatus.Inactive;
        if (status.Contains("discontinued"))
            return ProductStatus.Discontinued;
        if (status.Contains("pending"))
            return ProductStatus.Pending;
        
        return ProductStatus.Active;
    }
}

public class ProductImportResult
{
    public bool Success { get; set; }
    public string Message { get; set; } = "";
    public int TotalRows { get; set; }
    public int ProcessedRows { get; set; }
    public int SkippedRows { get; set; }
    public int ProductsCreated { get; set; }
    public int ProductsUpdated { get; set; }
    public int SuppliersCreated { get; set; }
    public List<string> Errors { get; set; } = new List<string>();
}