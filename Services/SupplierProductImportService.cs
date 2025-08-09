using System.Text;
using FDX.Trading.Models;
using FDX.Trading.Data;
using Microsoft.EntityFrameworkCore;
using System.Globalization;
using CsvHelper;
using CsvHelper.Configuration;

namespace FDX.Trading.Services;

public class SupplierProductImportService
{
    private const string DEFAULT_PASSWORD = "FDX2025!";
    private readonly FdxTradingContext _context;
    
    public SupplierProductImportService(FdxTradingContext context)
    {
        _context = context;
    }
    
    public class ProductCsvRow
    {
        public string ProductID { get; set; } = "";
        public string ProductCode { get; set; } = "";
        public string Supplier { get; set; } = "";
        public string BuyerCompany { get; set; } = "";
        public string ProductName { get; set; } = "";
        public string ProductsCategory { get; set; } = "";
        public string UnitWholesalePrice { get; set; } = "";
        public string GrossWeight { get; set; } = "";
        public string UnitsPerCarton { get; set; } = "";
        public string HSCode { get; set; } = "";
        public string MOQ { get; set; } = "";
        public string MaxTemperature { get; set; } = "";
        public string MinTemperature { get; set; } = "";
        public string Cartons20ft { get; set; } = "";
        public string Cartons40ft { get; set; } = "";
        public string Kosher { get; set; } = "";
        public string Pallets20ft { get; set; } = "";
        public string Pallets40ft { get; set; } = "";
        public string UnitOfMeasure { get; set; } = "";
        public string NetWeight { get; set; } = "";
        public string SupplierCountry { get; set; } = "";
        public string ShelfLife { get; set; } = "";
        public string SeaPort { get; set; } = "";
        public string Currency { get; set; } = "";
        public string Incoterms { get; set; } = "";
        public string PaymentTerms { get; set; } = "";
        public string PriceForCarton { get; set; } = "";
        public string SupplierProductCode { get; set; } = "";
        public string SuppliersDescription { get; set; } = "";
        public string SuppliersWebsite { get; set; } = "";
        public string ProductImage { get; set; } = "";
    }
    
    public async Task<ImportSummary> ImportFromCsvAsync(string csvFilePath)
    {
        var summary = new ImportSummary();
        var suppliers = new Dictionary<string, User>();
        var supplierDetails = new Dictionary<int, SupplierDetails>();
        var products = new Dictionary<string, Product>();
        
        try
        {
            var config = new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HeaderValidated = null,
                MissingFieldFound = null,
                BadDataFound = null
            };
            
            using var reader = new StreamReader(csvFilePath);
            using var csv = new CsvReader(reader, config);
            
            // Map CSV columns to our model
            csv.Context.RegisterClassMap<ProductCsvMap>();
            
            var records = csv.GetRecords<ProductCsvRow>().ToList();
            summary.TotalRows = records.Count;
            
            // Phase 1: Extract and create unique suppliers
            var uniqueSuppliers = records
                .Where(r => !string.IsNullOrWhiteSpace(r.Supplier))
                .Select(r => new { 
                    Name = CleanSupplierName(r.Supplier), 
                    Country = r.SupplierCountry,
                    Website = r.SuppliersWebsite
                })
                .GroupBy(s => s.Name)
                .Select(g => g.First())
                .ToList();
            
            foreach (var supplier in uniqueSuppliers)
            {
                try
                {
                    var username = GenerateUsername(supplier.Name);
                    
                    // Check if supplier user already exists
                    var existingUser = await _context.FdxUsers
                        .FirstOrDefaultAsync(u => u.Username == username);
                    
                    if (existingUser == null)
                    {
                        var user = new User
                        {
                            Username = username,
                            Password = DEFAULT_PASSWORD,
                            Email = $"{username}@supplier.fdx",
                            CompanyName = supplier.Name,
                            Type = UserType.Supplier,
                            Country = supplier.Country ?? "",
                            Website = supplier.Website ?? "",
                            IsActive = true,
                            RequiresPasswordChange = true,
                            DataComplete = false,
                            Verification = VerificationStatus.Pending,
                            CreatedAt = DateTime.Now,
                            ImportedAt = DateTime.Now
                        };
                        
                        _context.FdxUsers.Add(user);
                        await _context.SaveChangesAsync();
                        suppliers[supplier.Name] = user;
                        
                        // Create SupplierDetails
                        var details = new SupplierDetails
                        {
                            UserId = user.Id,
                            Description = $"Supplier from {supplier.Country}",
                            Currency = "USD",
                            IsVerified = false,
                            CreatedAt = DateTime.Now
                        };
                        
                        _context.SupplierDetails.Add(details);
                        await _context.SaveChangesAsync();
                        supplierDetails[user.Id] = details;
                        
                        summary.SuppliersCreated++;
                    }
                    else
                    {
                        suppliers[supplier.Name] = existingUser;
                        var existingDetails = await _context.SupplierDetails
                            .FirstOrDefaultAsync(sd => sd.UserId == existingUser.Id);
                        if (existingDetails != null)
                            supplierDetails[existingUser.Id] = existingDetails;
                    }
                }
                catch (Exception ex)
                {
                    summary.Errors.Add($"Error creating supplier {supplier.Name}: {ex.Message}");
                }
            }
            
            // Phase 2: Import products
            foreach (var row in records)
            {
                try
                {
                    if (string.IsNullOrWhiteSpace(row.ProductCode))
                        continue;
                    
                    var productCode = row.ProductCode.Trim();
                    
                    if (!products.ContainsKey(productCode))
                    {
                        // Check if product already exists
                        var existingProduct = await _context.Products
                            .FirstOrDefaultAsync(p => p.ProductCode == productCode);
                        
                        if (existingProduct == null)
                        {
                            var product = new Product
                            {
                                ProductCode = productCode,
                                ProductName = row.ProductName ?? "",
                                Category = ParseCategory(row.ProductsCategory),
                                SubCategory = ParseSubCategory(row.ProductsCategory),
                                HSCode = row.HSCode,
                                UnitOfMeasure = row.UnitOfMeasure ?? "unit",
                                NetWeight = ParseDecimal(row.NetWeight),
                                GrossWeight = ParseDecimal(row.GrossWeight),
                                UnitsPerCarton = ParseInt(row.UnitsPerCarton),
                                MinTemperature = ParseDecimal(row.MinTemperature),
                                MaxTemperature = ParseDecimal(row.MaxTemperature),
                                ShelfLifeDays = ParseInt(row.ShelfLife),
                                IsKosher = ParseBool(row.Kosher),
                                CountryOfOrigin = row.SupplierCountry,
                                ProductImage = row.ProductImage,
                                Status = ProductStatus.Active,
                                CreatedAt = DateTime.Now,
                                ImportedAt = DateTime.Now,
                                OriginalProductId = row.ProductID
                            };
                            
                            _context.Products.Add(product);
                            await _context.SaveChangesAsync();
                            products[productCode] = product;
                            summary.ProductsCreated++;
                        }
                        else
                        {
                            products[productCode] = existingProduct;
                        }
                    }
                    
                    // Phase 3: Create supplier-product association
                    if (!string.IsNullOrWhiteSpace(row.Supplier))
                    {
                        var supplierName = CleanSupplierName(row.Supplier);
                        if (suppliers.ContainsKey(supplierName) && products.ContainsKey(productCode))
                        {
                            var supplier = suppliers[supplierName];
                            var product = products[productCode];
                            
                            if (supplierDetails.ContainsKey(supplier.Id))
                            {
                                var supplierDetail = supplierDetails[supplier.Id];
                                
                                // Check if association already exists
                                var existingAssoc = await _context.SupplierProducts
                                    .FirstOrDefaultAsync(sp => sp.SupplierDetailsId == supplierDetail.Id 
                                        && sp.ProductId == product.Id);
                                
                                if (existingAssoc == null)
                                {
                                    var supplierProduct = new SupplierProduct
                                    {
                                        SupplierDetailsId = supplierDetail.Id,
                                        ProductId = product.Id,
                                        SupplierProductCode = row.SupplierProductCode,
                                        UnitWholesalePrice = ParseDecimal(row.UnitWholesalePrice),
                                        CartonWholesalePrice = ParseDecimal(row.PriceForCarton),
                                        Currency = string.IsNullOrWhiteSpace(row.Currency) ? "USD" : row.Currency,
                                        MinimumOrderQuantity = ParseInt(row.MOQ),
                                        CartonsPerContainer20ft = ParseInt(row.Cartons20ft),
                                        CartonsPerContainer40ft = ParseInt(row.Cartons40ft),
                                        PalletsPerContainer20ft = ParseInt(row.Pallets20ft),
                                        PalletsPerContainer40ft = ParseInt(row.Pallets40ft),
                                        Incoterms = row.Incoterms,
                                        PaymentTerms = row.PaymentTerms,
                                        ShippingPort = row.SeaPort,
                                        Status = SupplierProductStatus.Available,
                                        CreatedAt = DateTime.Now,
                                        ImportedAt = DateTime.Now,
                                        ImportSource = "Products 9_8_2025.csv"
                                    };
                                    
                                    _context.SupplierProducts.Add(supplierProduct);
                                    await _context.SaveChangesAsync();
                                    summary.AssociationsCreated++;
                                }
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    summary.Errors.Add($"Error processing row {row.ProductID}: {ex.Message}");
                }
            }
            
            summary.Success = true;
            summary.Message = $"Import completed: {summary.SuppliersCreated} suppliers, {summary.ProductsCreated} products, {summary.AssociationsCreated} associations created";
        }
        catch (Exception ex)
        {
            summary.Success = false;
            summary.Message = $"Import failed: {ex.Message}";
            summary.Errors.Add(ex.ToString());
        }
        
        return summary;
    }
    
    private string CleanSupplierName(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            return "";
        
        // Remove country suffix if present
        var parts = name.Split(',');
        return parts[0].Trim();
    }
    
    private string GenerateUsername(string companyName)
    {
        if (string.IsNullOrWhiteSpace(companyName))
            return "supplier_" + Guid.NewGuid().ToString("N").Substring(0, 8);
        
        // Remove special characters and spaces
        var username = companyName.ToLower()
            .Replace(" ", "_")
            .Replace(".", "")
            .Replace(",", "")
            .Replace("/", "_")
            .Replace("&", "and")
            .Replace("-", "_");
        
        // Remove any remaining non-alphanumeric characters except underscore
        username = System.Text.RegularExpressions.Regex.Replace(username, @"[^a-z0-9_]", "");
        
        // Ensure it starts with a letter
        if (username.Length > 0 && char.IsDigit(username[0]))
            username = "s_" + username;
        
        // Limit length
        if (username.Length > 50)
            username = username.Substring(0, 50);
        
        return string.IsNullOrWhiteSpace(username) ? "supplier_" + Guid.NewGuid().ToString("N").Substring(0, 8) : username;
    }
    
    private string? ParseCategory(string? category)
    {
        if (string.IsNullOrWhiteSpace(category))
            return null;
        
        var parts = category.Split(',');
        return parts.Length > 0 ? parts[0].Trim() : category.Trim();
    }
    
    private string? ParseSubCategory(string? category)
    {
        if (string.IsNullOrWhiteSpace(category))
            return null;
        
        var parts = category.Split(',');
        return parts.Length > 1 ? parts[1].Trim() : null;
    }
    
    private decimal? ParseDecimal(string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
            return null;
        
        value = value.Replace(",", "").Trim();
        
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
        
        value = value.Trim().ToLower();
        return value == "yes" || value == "true" || value == "1" || value.Contains("has certificate");
    }
}

public class ImportSummary
{
    public bool Success { get; set; }
    public string Message { get; set; } = "";
    public int TotalRows { get; set; }
    public int SuppliersCreated { get; set; }
    public int ProductsCreated { get; set; }
    public int AssociationsCreated { get; set; }
    public List<string> Errors { get; set; } = new();
}

public class ProductCsvMap : ClassMap<SupplierProductImportService.ProductCsvRow>
{
    public ProductCsvMap()
    {
        Map(m => m.ProductID).Name("Product ID");
        Map(m => m.ProductCode).Name("Product code");
        Map(m => m.Supplier).Name("Supplier");
        Map(m => m.BuyerCompany).Name("Buyer Company");
        Map(m => m.ProductName).Name("Product Name");
        Map(m => m.ProductsCategory).Name("Products Category & Family");
        Map(m => m.UnitWholesalePrice).Name("Unit Wholesale Price (latest)");
        Map(m => m.GrossWeight).Name("Gross Weight");
        Map(m => m.UnitsPerCarton).Name("Units per carton");
        Map(m => m.HSCode).Name("HS/ Tariff Code");
        Map(m => m.MOQ).Name("MOQ (units)");
        Map(m => m.MaxTemperature).Name("Product's Max temperature");
        Map(m => m.MinTemperature).Name("Product's Min. temperature");
        Map(m => m.Cartons20ft).Name("# of Cartons (20ft)");
        Map(m => m.Cartons40ft).Name("# of Cartons (40ft)");
        Map(m => m.Kosher).Name("Kosher?");
        Map(m => m.Pallets20ft).Name("# of Pallets (20ft)");
        Map(m => m.Pallets40ft).Name("# of Pallets in (40ft)");
        Map(m => m.UnitOfMeasure).Name("Unit of Measure");
        Map(m => m.NetWeight).Name("Net Weight");
        Map(m => m.SupplierCountry).Name("Supplier Country");
        Map(m => m.ShelfLife).Name("Shelf Life (Days)");
        Map(m => m.SeaPort).Name("Closest/ Prefered SeaPort");
        Map(m => m.Currency).Name("Currency for price");
        Map(m => m.Incoterms).Name("Incoterms (Price Base)");
        Map(m => m.PaymentTerms).Name("Payment Terms");
        Map(m => m.PriceForCarton).Name("Price for Carton (wholesale)");
        Map(m => m.SupplierProductCode).Name("Supplier Product Code");
        Map(m => m.SuppliersDescription).Name("Supplier's Description & Products");
        Map(m => m.SuppliersWebsite).Name("Supplier's Website");
        Map(m => m.ProductImage).Name("Product Images");
    }
}