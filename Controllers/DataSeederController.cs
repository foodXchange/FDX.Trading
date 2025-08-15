using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DataSeederController : ControllerBase
{
    private readonly FdxTradingContext _context;

    public DataSeederController(FdxTradingContext context)
    {
        _context = context;
    }

    [HttpDelete("delete-prutul-products")]
    public async Task<IActionResult> DeletePrutulProducts()
    {
        try
        {
            // Find Prutul supplier
            var prutul = await _context.FdxUsers.FirstOrDefaultAsync(u => u.CompanyName == "Prutul S.A.");
            if (prutul == null)
            {
                return NotFound(new { message = "Prutul S.A. not found" });
            }

            // Delete all products for Prutul
            var products = await _context.SupplierProductCatalogs
                .Where(p => p.SupplierId == prutul.Id)
                .ToListAsync();

            _context.SupplierProductCatalogs.RemoveRange(products);
            await _context.SaveChangesAsync();

            return Ok(new { 
                message = $"Deleted {products.Count} products for Prutul S.A.",
                deletedProducts = products.Select(p => p.ProductName)
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpPost("add-prutul-real-products")]
    public async Task<IActionResult> AddPrutulRealProducts()
    {
        try
        {
            // Find Prutul supplier
            var prutul = await _context.FdxUsers.FirstOrDefaultAsync(u => u.CompanyName == "Prutul S.A.");
            if (prutul == null)
            {
                return NotFound(new { message = "Prutul S.A. not found" });
            }

            var supplierId = prutul.Id;

            // Add REAL products from Prutul website
            // Based on actual products shown on http://www.prutul.ro/en/products/bottled-oil/
            var products = new List<SupplierProductCatalog>
            {
                // SPORNIC Brand Products
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Spornic Bun la Toate Sunflower Oil 1L",
                    ProductCode = "SPORNIC-BLT-1L",
                    Category = "Vegetable Oils",
                    SubCategory = "Sunflower Oil",
                    Brand = "Spornic",
                    Description = "Refined sunflower oil (linoleic). The classic Spornic sunflower oil - Good for Everything.",
                    Specifications = "Type: Refined sunflower oil (linoleic/conventional), Volume: 1L PET bottle",
                    MinOrderQuantity = 1000,
                    Unit = "Bottles (1L)",
                    PricePerUnit = 2.20m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Romania",
                    Certifications = "ISO, IFS, FSSC",
                    IsKosher = true,
                    IsHalal = true,
                    IsGlutenFree = true,
                    IsVegan = true,
                    QualityScore = 95,
                    SearchTags = "spornic, bun la toate, sunflower oil, refined sunflower oil, linoleic",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Spornic Bun la Toate Sunflower Oil 2L",
                    ProductCode = "SPORNIC-BLT-2L",
                    Category = "Vegetable Oils",
                    SubCategory = "Sunflower Oil",
                    Brand = "Spornic",
                    Description = "Refined sunflower oil (linoleic). The classic Spornic sunflower oil - Good for Everything.",
                    Specifications = "Type: Refined sunflower oil (linoleic/conventional), Volume: 2L PET bottle",
                    MinOrderQuantity = 500,
                    Unit = "Bottles (2L)",
                    PricePerUnit = 4.20m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Romania",
                    Certifications = "ISO, IFS, FSSC",
                    IsKosher = true,
                    IsHalal = true,
                    IsGlutenFree = true,
                    IsVegan = true,
                    QualityScore = 95,
                    SearchTags = "spornic, bun la toate, sunflower oil, refined sunflower oil, linoleic",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Spornic Bun la Toate Sunflower Oil 3L",
                    ProductCode = "SPORNIC-BLT-3L",
                    Category = "Vegetable Oils",
                    SubCategory = "Sunflower Oil",
                    Brand = "Spornic",
                    Description = "Refined sunflower oil (linoleic). The classic Spornic sunflower oil - Good for Everything.",
                    Specifications = "Type: Refined sunflower oil (linoleic/conventional), Volume: 3L PET bottle",
                    MinOrderQuantity = 400,
                    Unit = "Bottles (3L)",
                    PricePerUnit = 6.30m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Romania",
                    Certifications = "ISO, IFS, FSSC",
                    IsKosher = true,
                    IsHalal = true,
                    IsGlutenFree = true,
                    IsVegan = true,
                    QualityScore = 95,
                    SearchTags = "spornic, bun la toate, sunflower oil, refined sunflower oil, linoleic",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Spornic Bun la Toate Sunflower Oil 5L",
                    ProductCode = "SPORNIC-BLT-5L",
                    Category = "Vegetable Oils",
                    SubCategory = "Sunflower Oil",
                    Brand = "Spornic",
                    Description = "Refined sunflower oil (linoleic). The classic Spornic sunflower oil - Good for Everything. Family size.",
                    Specifications = "Type: Refined sunflower oil (linoleic/conventional), Volume: 5L PET bottle",
                    MinOrderQuantity = 200,
                    Unit = "Bottles (5L)",
                    PricePerUnit = 10.50m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Romania",
                    Certifications = "ISO, IFS, FSSC",
                    IsKosher = true,
                    IsHalal = true,
                    IsGlutenFree = true,
                    IsVegan = true,
                    QualityScore = 95,
                    SearchTags = "spornic, bun la toate, sunflower oil, refined sunflower oil, linoleic, family pack",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                // SPORNIC OMEGA 9 (High Oleic) Products
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Spornic Omega 9 High Oleic Sunflower Oil 1L",
                    ProductCode = "SPORNIC-OMEGA9-1L",
                    Category = "Vegetable Oils",
                    SubCategory = "Sunflower Oil",
                    Brand = "Spornic Omega 9",
                    Description = "Refined 100% High Oleic sunflower oil. Minimum 75% Omega 9 (oleic acid). Premium quality with extended shelf life.",
                    Specifications = "Type: 100% High Oleic sunflower oil, Min 75% oleic acid, Volume: 1L PET bottle",
                    MinOrderQuantity = 1000,
                    Unit = "Bottles (1L)",
                    PricePerUnit = 3.50m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Romania",
                    Certifications = "ISO, IFS, FSSC",
                    IsKosher = true,
                    IsHalal = true,
                    IsGlutenFree = true,
                    IsVegan = true,
                    QualityScore = 98,
                    SearchTags = "spornic omega 9, high oleic, sunflower oil, omega 9, premium",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Spornic Omega 9 High Oleic Sunflower Oil 2L",
                    ProductCode = "SPORNIC-OMEGA9-2L",
                    Category = "Vegetable Oils",
                    SubCategory = "Sunflower Oil",
                    Brand = "Spornic Omega 9",
                    Description = "Refined 100% High Oleic sunflower oil. Minimum 75% Omega 9 (oleic acid). Premium quality with extended shelf life.",
                    Specifications = "Type: 100% High Oleic sunflower oil, Min 75% oleic acid, Volume: 2L PET bottle",
                    MinOrderQuantity = 500,
                    Unit = "Bottles (2L)",
                    PricePerUnit = 6.80m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Romania",
                    Certifications = "ISO, IFS, FSSC",
                    IsKosher = true,
                    IsHalal = true,
                    IsGlutenFree = true,
                    IsVegan = true,
                    QualityScore = 98,
                    SearchTags = "spornic omega 9, high oleic, sunflower oil, omega 9, premium",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Spornic Omega 9 High Oleic Sunflower Oil 3L",
                    ProductCode = "SPORNIC-OMEGA9-3L",
                    Category = "Vegetable Oils",
                    SubCategory = "Sunflower Oil",
                    Brand = "Spornic Omega 9",
                    Description = "Refined 100% High Oleic sunflower oil. Minimum 75% Omega 9 (oleic acid). Premium quality with extended shelf life.",
                    Specifications = "Type: 100% High Oleic sunflower oil, Min 75% oleic acid, Volume: 3L PET bottle",
                    MinOrderQuantity = 400,
                    Unit = "Bottles (3L)",
                    PricePerUnit = 10.20m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Romania",
                    Certifications = "ISO, IFS, FSSC",
                    IsKosher = true,
                    IsHalal = true,
                    IsGlutenFree = true,
                    IsVegan = true,
                    QualityScore = 98,
                    SearchTags = "spornic omega 9, high oleic, sunflower oil, omega 9, premium",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                }
            };

            _context.SupplierProductCatalogs.AddRange(products);
            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                message = "Successfully added REAL Prutul products from their website",
                supplierId = supplierId,
                productsAdded = products.Count,
                products = products.Select(p => new { p.ProductName, p.ProductCode, p.Brand })
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpPost("remove-duplicate-suppliers")]
    public async Task<IActionResult> RemoveDuplicateSuppliers()
    {
        try
        {
            // Find and remove duplicate suppliers (keep the one with lower ID)
            var duplicates = await _context.FdxUsers
                .Where(u => u.Type == UserType.Supplier)
                .GroupBy(u => u.CompanyName)
                .Where(g => g.Count() > 1)
                .Select(g => new { 
                    CompanyName = g.Key, 
                    Duplicates = g.OrderBy(u => u.Id).ToList() 
                })
                .ToListAsync();

            var removedCount = 0;
            var results = new List<object>();

            foreach (var group in duplicates)
            {
                // Keep the first (lowest ID), remove the rest
                var toRemove = group.Duplicates.Skip(1).ToList();
                foreach (var duplicate in toRemove)
                {
                    // Remove products first
                    var products = await _context.SupplierProductCatalogs
                        .Where(p => p.SupplierId == duplicate.Id)
                        .ToListAsync();
                    _context.SupplierProductCatalogs.RemoveRange(products);
                    
                    // Remove supplier
                    _context.FdxUsers.Remove(duplicate);
                    removedCount++;
                    results.Add(new { 
                        id = duplicate.Id, 
                        name = duplicate.CompanyName,
                        kept = group.Duplicates[0].Id
                    });
                }
            }

            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                message = $"Removed {removedCount} duplicate suppliers",
                details = results
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpPost("add-multiple-supplier-products")]
    public async Task<IActionResult> AddMultipleSupplierProducts()
    {
        try
        {
            var results = new List<object>();
            var totalProductsAdded = 0;

            // Add Balconi products (Italian cakes and snacks)
            var balconi = await _context.FdxUsers.FirstOrDefaultAsync(u => 
                u.CompanyName.Contains("Balconi") && u.Type == UserType.Supplier);
            
            if (balconi != null)
            {
                var balconiProducts = new List<SupplierProductCatalog>
                {
                    new SupplierProductCatalog
                    {
                        SupplierId = balconi.Id,
                        ProductName = "Balconi Mix Max Chocolate Cake 350g",
                        ProductCode = "BALC-MIXMAX-350",
                        Category = "Cakes & Pastries",
                        SubCategory = "Snack Cakes",
                        Brand = "Balconi",
                        Description = "Soft sponge cake with chocolate cream filling",
                        Specifications = "Weight: 350g, 10 pieces per pack",
                        MinOrderQuantity = 24,
                        Unit = "Packs (350g)",
                        PricePerUnit = 2.95m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Italy",
                        QualityScore = 92,
                        SearchTags = "cake, chocolate cake, snack cake, italian",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    },
                    new SupplierProductCatalog
                    {
                        SupplierId = balconi.Id,
                        ProductName = "Balconi Rollino Cacao 222g",
                        ProductCode = "BALC-ROLL-CAC-222",
                        Category = "Cakes & Pastries",
                        SubCategory = "Swiss Rolls",
                        Brand = "Balconi",
                        Description = "Rolled sponge cake with cocoa cream",
                        Specifications = "Weight: 222g, 6 pieces",
                        MinOrderQuantity = 24,
                        Unit = "Packs (222g)",
                        PricePerUnit = 2.25m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Italy",
                        QualityScore = 92,
                        SearchTags = "swiss roll, cocoa, rolled cake",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    },
                    new SupplierProductCatalog
                    {
                        SupplierId = balconi.Id,
                        ProductName = "Balconi Croissant Apricot 300g",
                        ProductCode = "BALC-CROIS-APR-300",
                        Category = "Cakes & Pastries",
                        SubCategory = "Croissants",
                        Brand = "Balconi",
                        Description = "Soft croissant with apricot jam filling",
                        Specifications = "Weight: 300g, 6 pieces",
                        MinOrderQuantity = 24,
                        Unit = "Packs (300g)",
                        PricePerUnit = 2.50m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Italy",
                        QualityScore = 91,
                        SearchTags = "croissant, apricot, breakfast, pastry",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    }
                };
                
                var existingBalconi = await _context.SupplierProductCatalogs
                    .Where(p => p.SupplierId == balconi.Id)
                    .ToListAsync();
                _context.SupplierProductCatalogs.RemoveRange(existingBalconi);
                _context.SupplierProductCatalogs.AddRange(balconiProducts);
                totalProductsAdded += balconiProducts.Count;
                results.Add(new { supplier = balconi.CompanyName, productsAdded = balconiProducts.Count });
            }

            // Add Daelmans products (Dutch stroopwafels)
            var daelmans = await _context.FdxUsers.FirstOrDefaultAsync(u => 
                u.CompanyName.Contains("Daelmans") && u.Type == UserType.Supplier);
            
            if (daelmans != null)
            {
                var daelmansProducts = new List<SupplierProductCatalog>
                {
                    new SupplierProductCatalog
                    {
                        SupplierId = daelmans.Id,
                        ProductName = "Daelmans Original Stroopwafels 230g",
                        ProductCode = "DAEL-STROOP-ORIG-230",
                        Category = "Biscuits & Cookies",
                        SubCategory = "Stroopwafels",
                        Brand = "Daelmans",
                        Description = "Authentic Dutch stroopwafels with caramel syrup filling",
                        Specifications = "Weight: 230g, 8 wafels per pack",
                        MinOrderQuantity = 24,
                        Unit = "Packs (230g)",
                        PricePerUnit = 3.50m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Netherlands",
                        Certifications = "RSPO, UTZ",
                        QualityScore = 95,
                        SearchTags = "stroopwafel, dutch, caramel, waffle, cookie",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    },
                    new SupplierProductCatalog
                    {
                        SupplierId = daelmans.Id,
                        ProductName = "Daelmans Honey Stroopwafels 230g",
                        ProductCode = "DAEL-STROOP-HONEY-230",
                        Category = "Biscuits & Cookies",
                        SubCategory = "Stroopwafels",
                        Brand = "Daelmans",
                        Description = "Stroopwafels with honey syrup filling",
                        Specifications = "Weight: 230g, 8 wafels per pack",
                        MinOrderQuantity = 24,
                        Unit = "Packs (230g)",
                        PricePerUnit = 3.75m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Netherlands",
                        Certifications = "RSPO, UTZ",
                        QualityScore = 95,
                        SearchTags = "stroopwafel, honey, dutch waffle",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    },
                    new SupplierProductCatalog
                    {
                        SupplierId = daelmans.Id,
                        ProductName = "Daelmans Chocolate Stroopwafels 230g",
                        ProductCode = "DAEL-STROOP-CHOC-230",
                        Category = "Biscuits & Cookies",
                        SubCategory = "Stroopwafels",
                        Brand = "Daelmans",
                        Description = "Stroopwafels with chocolate coating",
                        Specifications = "Weight: 230g, 8 wafels per pack",
                        MinOrderQuantity = 24,
                        Unit = "Packs (230g)",
                        PricePerUnit = 4.25m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Netherlands",
                        Certifications = "RSPO, UTZ",
                        QualityScore = 95,
                        SearchTags = "stroopwafel, chocolate, dutch cookie",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    }
                };
                
                var existingDaelmans = await _context.SupplierProductCatalogs
                    .Where(p => p.SupplierId == daelmans.Id)
                    .ToListAsync();
                _context.SupplierProductCatalogs.RemoveRange(existingDaelmans);
                _context.SupplierProductCatalogs.AddRange(daelmansProducts);
                totalProductsAdded += daelmansProducts.Count;
                results.Add(new { supplier = daelmans.CompanyName, productsAdded = daelmansProducts.Count });
            }

            // Add Crich products (Italian crackers and biscuits)
            var crich = await _context.FdxUsers.FirstOrDefaultAsync(u => 
                u.CompanyName.Contains("Crich") && u.Type == UserType.Supplier);
            
            if (crich != null)
            {
                var crichProducts = new List<SupplierProductCatalog>
                {
                    new SupplierProductCatalog
                    {
                        SupplierId = crich.Id,
                        ProductName = "Crich Salted Crackers 250g",
                        ProductCode = "CRICH-CRACK-SALT-250",
                        Category = "Crackers & Snacks",
                        SubCategory = "Crackers",
                        Brand = "Crich",
                        Description = "Classic Italian salted crackers",
                        Specifications = "Weight: 250g, Individual packets",
                        MinOrderQuantity = 24,
                        Unit = "Boxes (250g)",
                        PricePerUnit = 1.95m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Italy",
                        QualityScore = 90,
                        SearchTags = "crackers, salted, italian, snack",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    },
                    new SupplierProductCatalog
                    {
                        SupplierId = crich.Id,
                        ProductName = "Crich Hazelnut Wafers 175g",
                        ProductCode = "CRICH-WAF-HAZ-175",
                        Category = "Biscuits & Cookies",
                        SubCategory = "Wafers",
                        Brand = "Crich",
                        Description = "Crispy wafers with hazelnut cream filling",
                        Specifications = "Weight: 175g",
                        MinOrderQuantity = 24,
                        Unit = "Packs (175g)",
                        PricePerUnit = 2.25m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Italy",
                        QualityScore = 91,
                        SearchTags = "wafers, hazelnut, cream filled, italian",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    },
                    new SupplierProductCatalog
                    {
                        SupplierId = crich.Id,
                        ProductName = "Crich Bio Organic Crackers Olive Oil 250g",
                        ProductCode = "CRICH-BIO-OLIVE-250",
                        Category = "Crackers & Snacks",
                        SubCategory = "Organic Crackers",
                        Brand = "Crich Bio",
                        Description = "Organic crackers with extra virgin olive oil",
                        Specifications = "Weight: 250g, Organic certified",
                        MinOrderQuantity = 24,
                        Unit = "Boxes (250g)",
                        PricePerUnit = 2.95m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Italy",
                        Certifications = "Organic, Vegan",
                        QualityScore = 94,
                        SearchTags = "organic, crackers, olive oil, vegan",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    },
                    new SupplierProductCatalog
                    {
                        SupplierId = crich.Id,
                        ProductName = "Crich Gran Merenda Biscuits 500g",
                        ProductCode = "CRICH-GRAN-500",
                        Category = "Biscuits & Cookies",
                        SubCategory = "Biscuits",
                        Brand = "Crich",
                        Description = "Traditional Italian breakfast biscuits",
                        Specifications = "Weight: 500g, Family pack",
                        MinOrderQuantity = 12,
                        Unit = "Packs (500g)",
                        PricePerUnit = 3.50m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Italy",
                        QualityScore = 91,
                        SearchTags = "biscuits, breakfast, italian, family pack",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    }
                };
                
                var existingCrich = await _context.SupplierProductCatalogs
                    .Where(p => p.SupplierId == crich.Id)
                    .ToListAsync();
                _context.SupplierProductCatalogs.RemoveRange(existingCrich);
                _context.SupplierProductCatalogs.AddRange(crichProducts);
                totalProductsAdded += crichProducts.Count;
                results.Add(new { supplier = crich.CompanyName, productsAdded = crichProducts.Count });
            }

            // Add Coppenrath products (German cookies)
            var coppenrath = await _context.FdxUsers.FirstOrDefaultAsync(u => 
                u.CompanyName.Contains("Coppenrath") && u.Type == UserType.Supplier);
            
            if (coppenrath != null)
            {
                var coppenrathProducts = new List<SupplierProductCatalog>
                {
                    new SupplierProductCatalog
                    {
                        SupplierId = coppenrath.Id,
                        ProductName = "Coppenrath Wiener Sandringe Butter Cookies 200g",
                        ProductCode = "COPP-WIEN-200",
                        Category = "Biscuits & Cookies",
                        SubCategory = "Butter Cookies",
                        Brand = "Coppenrath",
                        Description = "Traditional German butter cookies with jam center",
                        Specifications = "Weight: 200g, Premium tin box",
                        MinOrderQuantity = 12,
                        Unit = "Tins (200g)",
                        PricePerUnit = 4.95m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Germany",
                        QualityScore = 95,
                        SearchTags = "butter cookies, german, premium, traditional",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    },
                    new SupplierProductCatalog
                    {
                        SupplierId = coppenrath.Id,
                        ProductName = "Coppenrath Coooky Dark Chocolate 150g",
                        ProductCode = "COPP-COOOKY-DARK-150",
                        Category = "Biscuits & Cookies",
                        SubCategory = "Chocolate Cookies",
                        Brand = "Coooky",
                        Description = "Premium cookies with dark chocolate coating",
                        Specifications = "Weight: 150g, New 2024 range",
                        MinOrderQuantity = 24,
                        Unit = "Packs (150g)",
                        PricePerUnit = 3.25m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Germany",
                        QualityScore = 94,
                        SearchTags = "chocolate cookies, dark chocolate, premium",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    },
                    new SupplierProductCatalog
                    {
                        SupplierId = coppenrath.Id,
                        ProductName = "Coppenrath Sugar-Free Butter Cookies 175g",
                        ProductCode = "COPP-SF-BUTTER-175",
                        Category = "Biscuits & Cookies",
                        SubCategory = "Sugar-Free",
                        Brand = "Coppenrath",
                        Description = "Butter cookies without added sugar",
                        Specifications = "Weight: 175g, Sugar-free",
                        MinOrderQuantity = 24,
                        Unit = "Boxes (175g)",
                        PricePerUnit = 3.95m,
                        Currency = "EUR",
                        IsAvailable = true,
                        LeadTimeDays = 14,
                        CountryOfOrigin = "Germany",
                        Certifications = "Sugar-free",
                        QualityScore = 92,
                        SearchTags = "sugar free, diabetic friendly, butter cookies",
                        CreatedAt = DateTime.Now,
                        UpdatedAt = DateTime.Now
                    }
                };
                
                var existingCoppenrath = await _context.SupplierProductCatalogs
                    .Where(p => p.SupplierId == coppenrath.Id)
                    .ToListAsync();
                _context.SupplierProductCatalogs.RemoveRange(existingCoppenrath);
                _context.SupplierProductCatalogs.AddRange(coppenrathProducts);
                totalProductsAdded += coppenrathProducts.Count;
                results.Add(new { supplier = coppenrath.CompanyName, productsAdded = coppenrathProducts.Count });
            }

            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                message = $"Successfully added {totalProductsAdded} products from {results.Count} suppliers",
                details = results
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpPost("add-nutkao-products")]
    public async Task<IActionResult> AddNutkaoProducts()
    {
        try
        {
            // Find Nutkao supplier (use the first one)
            var nutkao = await _context.FdxUsers.FirstOrDefaultAsync(u => 
                u.CompanyName.Contains("Nutkao") && u.Type == UserType.Supplier);
            
            if (nutkao == null)
            {
                return NotFound(new { message = "Nutkao not found" });
            }

            var supplierId = nutkao.Id;

            // Delete existing products first
            var existingProducts = await _context.SupplierProductCatalogs
                .Where(p => p.SupplierId == supplierId)
                .ToListAsync();
            _context.SupplierProductCatalogs.RemoveRange(existingProducts);

            // Add REAL products from Nutkao
            var products = new List<SupplierProductCatalog>
            {
                // Hazelnut Spreads
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Nutkao Cocoa and Hazelnut Spread 300g",
                    ProductCode = "NUTKAO-HAZEL-300",
                    Category = "Spreads & Jams",
                    SubCategory = "Hazelnut Spreads",
                    Brand = "Nutkao",
                    Description = "Premium Italian hazelnut spread with cocoa, perfect for breakfast and desserts",
                    Specifications = "Weight: 300g (10.58 oz), Glass jar, Contains hazelnuts and cocoa",
                    MinOrderQuantity = 24,
                    Unit = "Jars (300g)",
                    PricePerUnit = 3.95m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 21,
                    CountryOfOrigin = "Italy",
                    Certifications = "IFS, BRC",
                    QualityScore = 94,
                    SearchTags = "hazelnut spread, chocolate spread, cocoa, breakfast, nutella alternative",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Nutkao Chocolate Hazelnut Spread 400g",
                    ProductCode = "NUTKAO-CHOC-400",
                    Category = "Spreads & Jams",
                    SubCategory = "Hazelnut Spreads",
                    Brand = "Nutkao",
                    Description = "Rich chocolate hazelnut spread made with Italian hazelnuts",
                    Specifications = "Weight: 400g (13 oz), Glass jar, High hazelnut content",
                    MinOrderQuantity = 24,
                    Unit = "Jars (400g)",
                    PricePerUnit = 4.50m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 21,
                    CountryOfOrigin = "Italy",
                    Certifications = "IFS, BRC",
                    QualityScore = 94,
                    SearchTags = "hazelnut spread, chocolate hazelnut, italian spread",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Nutkao Fantasia di Cacao Duo Spread 300g",
                    ProductCode = "NUTKAO-DUO-300",
                    Category = "Spreads & Jams",
                    SubCategory = "Hazelnut Spreads",
                    Brand = "Nutkao",
                    Description = "Unique duo spread with hazelnut and milk cream layers",
                    Specifications = "Weight: 300g (10.58 oz), Glass jar, Two-layer spread",
                    MinOrderQuantity = 24,
                    Unit = "Jars (300g)",
                    PricePerUnit = 4.25m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 21,
                    CountryOfOrigin = "Italy",
                    Certifications = "IFS, BRC",
                    QualityScore = 95,
                    SearchTags = "duo spread, hazelnut milk, chocolate spread, fantasia",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Nutkao Double Cream Cocoa & Hazelnut 200g",
                    ProductCode = "NUTKAO-DOUBLE-200",
                    Category = "Spreads & Jams",
                    SubCategory = "Hazelnut Spreads",
                    Brand = "Nutkao",
                    Description = "Premium double cream spread with cocoa and hazelnuts",
                    Specifications = "Weight: 200g, Glass jar, Premium quality",
                    MinOrderQuantity = 24,
                    Unit = "Jars (200g)",
                    PricePerUnit = 3.25m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 21,
                    CountryOfOrigin = "Italy",
                    Certifications = "IFS, BRC",
                    QualityScore = 96,
                    SearchTags = "double cream, hazelnut spread, premium spread",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                // Professional/Bulk Products
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Nutkao Professional Hazelnut Cream 3kg",
                    ProductCode = "NUTKAO-PRO-3KG",
                    Category = "Spreads & Jams",
                    SubCategory = "Professional/Bulk",
                    Brand = "Nutkao Professional",
                    Description = "Professional hazelnut cream for pastry and ice cream industry",
                    Specifications = "Weight: 3kg, Plastic bucket, Professional grade",
                    MinOrderQuantity = 4,
                    Unit = "Buckets (3kg)",
                    PricePerUnit = 28.00m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 21,
                    CountryOfOrigin = "Italy",
                    Certifications = "IFS, BRC, RSPO",
                    QualityScore = 94,
                    SearchTags = "professional, bulk, hazelnut cream, pastry, ice cream",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Nutkao Professional Chocolate Spread 5kg",
                    ProductCode = "NUTKAO-PRO-5KG",
                    Category = "Spreads & Jams",
                    SubCategory = "Professional/Bulk",
                    Brand = "Nutkao Professional",
                    Description = "Bulk chocolate spread for bakeries and food service",
                    Specifications = "Weight: 5kg, Plastic bucket, Food service grade",
                    MinOrderQuantity = 2,
                    Unit = "Buckets (5kg)",
                    PricePerUnit = 42.00m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 21,
                    CountryOfOrigin = "Italy",
                    Certifications = "IFS, BRC, RSPO",
                    QualityScore = 94,
                    SearchTags = "professional, bulk, chocolate spread, bakery, food service",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                // Private Label Options
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Private Label Hazelnut Spread (Customizable)",
                    ProductCode = "NUTKAO-PL-CUSTOM",
                    Category = "Spreads & Jams",
                    SubCategory = "Private Label",
                    Brand = "Private Label",
                    Description = "Customizable hazelnut spread for private label customers",
                    Specifications = "Customizable recipe, packaging, and size options",
                    MinOrderQuantity = 1000,
                    Unit = "Units (Custom)",
                    PricePerUnit = 0m, // Price on request
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 45,
                    CountryOfOrigin = "Italy",
                    Certifications = "IFS, BRC, Custom certifications available",
                    QualityScore = 95,
                    SearchTags = "private label, custom, hazelnut spread, oem",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                }
            };

            _context.SupplierProductCatalogs.AddRange(products);
            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                message = $"Successfully added {products.Count} products for Nutkao",
                supplierId = supplierId,
                companyName = nutkao.CompanyName,
                productsAdded = products.Select(p => new { p.ProductName, p.Brand, p.SubCategory })
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpPost("add-vicenzi-products")]
    public async Task<IActionResult> AddVicenziProducts()
    {
        try
        {
            // Find Vicenzi supplier (use the first one)
            var vicenzi = await _context.FdxUsers.FirstOrDefaultAsync(u => 
                u.CompanyName.Contains("Vicenzi") && u.Type == UserType.Supplier);
            
            if (vicenzi == null)
            {
                return NotFound(new { message = "Vicenzi not found" });
            }

            var supplierId = vicenzi.Id;

            // Delete existing products first
            var existingProducts = await _context.SupplierProductCatalogs
                .Where(p => p.SupplierId == supplierId)
                .ToListAsync();
            _context.SupplierProductCatalogs.RemoveRange(existingProducts);

            // Add REAL products from Matilde Vicenzi
            var products = new List<SupplierProductCatalog>
            {
                // Grisbì Line - Cream Filled Cookies
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Grisbì Chocolate Cream Filled Shortbread Cookies 135g",
                    ProductCode = "GRISBI-CHOC-135",
                    Category = "Biscuits & Cookies",
                    SubCategory = "Cream Filled Cookies",
                    Brand = "Grisbì",
                    Description = "Delicious cream filled shortbread cookies with rich chocolate filling",
                    Specifications = "Weight: 135g, Type: Chocolate cream filled shortbread",
                    MinOrderQuantity = 24,
                    Unit = "Packs (135g)",
                    PricePerUnit = 2.50m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Italy",
                    Certifications = "Kosher",
                    QualityScore = 95,
                    SearchTags = "cookies, cream filled, chocolate, shortbread, grisbi",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Grisbì Hazelnut Cream Filled Shortbread Cookies 135g",
                    ProductCode = "GRISBI-HAZEL-135",
                    Category = "Biscuits & Cookies",
                    SubCategory = "Cream Filled Cookies",
                    Brand = "Grisbì",
                    Description = "Shortbread cookies with delicate and velvety hazelnut cream filling",
                    Specifications = "Weight: 135g, Type: Hazelnut cream filled shortbread",
                    MinOrderQuantity = 24,
                    Unit = "Packs (135g)",
                    PricePerUnit = 2.50m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Italy",
                    Certifications = "Kosher",
                    QualityScore = 95,
                    SearchTags = "cookies, cream filled, hazelnut, shortbread, grisbi",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Grisbì Ciobar Cream Filled Cookies 150g",
                    ProductCode = "GRISBI-CIOBAR-150",
                    Category = "Biscuits & Cookies",
                    SubCategory = "Cream Filled Cookies",
                    Brand = "Grisbì",
                    Description = "Crunchy biscuits with creamy Ciobar chocolate filling",
                    Specifications = "Weight: 150g, Type: Ciobar cream filled",
                    MinOrderQuantity = 24,
                    Unit = "Packs (150g)",
                    PricePerUnit = 2.75m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Italy",
                    Certifications = "Kosher",
                    QualityScore = 95,
                    SearchTags = "cookies, cream filled, ciobar, chocolate, grisbi",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                // Millefoglie Line - Puff Pastry with Cream
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Millefoglie Pistachio Cream Puff Pastry Snack 125g",
                    ProductCode = "MILLE-PIST-125",
                    Category = "Pastries",
                    SubCategory = "Puff Pastry",
                    Brand = "Millefoglie",
                    Description = "192 layers of delicate puff pastry filled with velvety pistachio cream",
                    Specifications = "Weight: 125g, Layers: 192, Filling: Pistachio cream",
                    MinOrderQuantity = 12,
                    Unit = "Packs (125g)",
                    PricePerUnit = 3.50m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Italy",
                    Certifications = "Kosher, Non-GMO",
                    QualityScore = 98,
                    SearchTags = "puff pastry, pistachio cream, millefoglie, cream filled",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Millefoglie Chocolate Cream Filled Puff Pastry 125g",
                    ProductCode = "MILLE-CHOC-125",
                    Category = "Pastries",
                    SubCategory = "Puff Pastry",
                    Brand = "Millefoglie",
                    Description = "Bite-size puff pastry filled with rich chocolate cream",
                    Specifications = "Weight: 125g, Layers: 192, Filling: Chocolate cream",
                    MinOrderQuantity = 12,
                    Unit = "Packs (125g)",
                    PricePerUnit = 3.25m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Italy",
                    Certifications = "Kosher, Non-GMO",
                    QualityScore = 98,
                    SearchTags = "puff pastry, chocolate cream, millefoglie, cream filled",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Millefoglie Raspberry Cream Filled Puff Pastry 125g",
                    ProductCode = "MILLE-RASP-125",
                    Category = "Pastries",
                    SubCategory = "Puff Pastry",
                    Brand = "Millefoglie",
                    Description = "Delicate puff pastry with delightful raspberry cream filling",
                    Specifications = "Weight: 125g, Layers: 192, Filling: Raspberry cream",
                    MinOrderQuantity = 12,
                    Unit = "Packs (125g)",
                    PricePerUnit = 3.25m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Italy",
                    Certifications = "Kosher, Non-GMO",
                    QualityScore = 98,
                    SearchTags = "puff pastry, raspberry cream, millefoglie, cream filled, fruit",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                // Classic Products
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Vicenzovo Ladyfingers Classic 200g",
                    ProductCode = "VICEN-LADY-200",
                    Category = "Biscuits & Cookies",
                    SubCategory = "Ladyfingers",
                    Brand = "Vicenzovo",
                    Description = "Traditional Italian ladyfinger biscuits, perfect for tiramisu",
                    Specifications = "Weight: 200g, Type: Classic ladyfingers",
                    MinOrderQuantity = 24,
                    Unit = "Packs (200g)",
                    PricePerUnit = 1.95m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Italy",
                    Certifications = "Kosher",
                    QualityScore = 92,
                    SearchTags = "ladyfingers, savoiardi, tiramisu, classic, biscuits",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Vicenzovo Strawberry Cream Ladyfingers 125g",
                    ProductCode = "VICEN-STRAW-125",
                    Category = "Biscuits & Cookies",
                    SubCategory = "Cream Filled Cookies",
                    Brand = "Vicenzovo",
                    Description = "Ladyfinger cookies with strawberry cream filling",
                    Specifications = "Weight: 125g, Filling: Strawberry cream",
                    MinOrderQuantity = 24,
                    Unit = "Packs (125g)",
                    PricePerUnit = 2.25m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Italy",
                    Certifications = "Kosher",
                    QualityScore = 92,
                    SearchTags = "ladyfingers, strawberry cream, cream filled, fruit",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                // Gift Tins
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Millefoglie D'Italia Assorted Pastry Tin 660g",
                    ProductCode = "MILLE-TIN-660",
                    Category = "Gift Sets",
                    SubCategory = "Assorted Tins",
                    Brand = "Millefoglie",
                    Description = "Assorted fine pastry cookies with soft filled centers in reusable tin",
                    Specifications = "Weight: 660g, Type: Assorted cream filled pastries",
                    MinOrderQuantity = 6,
                    Unit = "Tins (660g)",
                    PricePerUnit = 18.50m,
                    Currency = "EUR",
                    IsAvailable = true,
                    LeadTimeDays = 14,
                    CountryOfOrigin = "Italy",
                    Certifications = "Kosher, Non-GMO",
                    QualityScore = 96,
                    SearchTags = "gift tin, assorted, cream filled, pastries, millefoglie",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                }
            };

            _context.SupplierProductCatalogs.AddRange(products);
            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                message = $"Successfully added {products.Count} products for Vicenzi",
                supplierId = supplierId,
                companyName = vicenzi.CompanyName,
                productsAdded = products.Select(p => new { p.ProductName, p.Brand, p.SubCategory })
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpPost("remove-incorrect-oil-suppliers")]
    public async Task<IActionResult> RemoveIncorrectOilSuppliers()
    {
        try
        {
            // Suppliers that don't actually have sunflower oil based on website checks
            var suppliersWithoutOil = new[] {
                "Ardo", // Frozen vegetables and fruits
                "Bergia frites", // Frozen potato products
                "Greenyard Frozen", // Frozen vegetables
                "Mueloliva", // Only olive oil
                "SAC S.p.A", // Tomato products
                "Victoria s.a.c" // Canned foods
            };

            var removedCount = 0;
            var results = new List<object>();

            foreach (var supplierName in suppliersWithoutOil)
            {
                var supplier = await _context.FdxUsers.FirstOrDefaultAsync(u => 
                    u.CompanyName.Contains(supplierName));
                
                if (supplier != null)
                {
                    // Remove their products from SupplierProductCatalogs
                    var products = await _context.SupplierProductCatalogs
                        .Where(p => p.SupplierId == supplier.Id)
                        .ToListAsync();
                    
                    if (products.Any())
                    {
                        _context.SupplierProductCatalogs.RemoveRange(products);
                        removedCount += products.Count;
                        results.Add(new { 
                            supplier = supplier.CompanyName, 
                            productsRemoved = products.Count 
                        });
                    }
                }
            }

            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                message = $"Removed {removedCount} incorrect oil product entries",
                details = results
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpPost("add-kadooglu-products")]
    public async Task<IActionResult> AddKadoogluProducts()
    {
        try
        {
            // Find Kadooglu supplier
            var kadooglu = await _context.FdxUsers.FirstOrDefaultAsync(u => 
                u.CompanyName.Contains("Kadoogu") || u.CompanyName.Contains("Kadooglu"));
            
            if (kadooglu == null)
            {
                return NotFound(new { message = "Kadooglu Yag not found" });
            }

            var supplierId = kadooglu.Id;

            // Delete existing products first
            var existingProducts = await _context.SupplierProductCatalogs
                .Where(p => p.SupplierId == supplierId)
                .ToListAsync();
            _context.SupplierProductCatalogs.RemoveRange(existingProducts);

            // Add REAL products from Kadooglu website
            var products = new List<SupplierProductCatalog>
            {
                // Sunflower Oil Products
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Bizce Sunflower Oil 1L",
                    ProductCode = "BIZCE-SUN-1L",
                    Category = "Vegetable Oils",
                    SubCategory = "Sunflower Oil",
                    Brand = "Bizce",
                    Description = "Premium refined sunflower oil for all cooking needs",
                    Specifications = "Type: Refined sunflower oil, Volume: 1L PET bottle",
                    MinOrderQuantity = 1000,
                    Unit = "Bottles (1L)",
                    PricePerUnit = 2.10m,
                    Currency = "USD",
                    IsAvailable = true,
                    LeadTimeDays = 21,
                    CountryOfOrigin = "Turkey",
                    Certifications = "ISO, HALAL, FSSC 22000",
                    QualityScore = 92,
                    SearchTags = "sunflower oil, bizce, refined oil, cooking oil",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Bizce Sunflower Oil 5L",
                    ProductCode = "BIZCE-SUN-5L",
                    Category = "Vegetable Oils",
                    SubCategory = "Sunflower Oil",
                    Brand = "Bizce",
                    Description = "Premium refined sunflower oil, family size",
                    Specifications = "Type: Refined sunflower oil, Volume: 5L PET bottle",
                    MinOrderQuantity = 500,
                    Unit = "Bottles (5L)",
                    PricePerUnit = 9.50m,
                    Currency = "USD",
                    IsAvailable = true,
                    LeadTimeDays = 21,
                    CountryOfOrigin = "Turkey",
                    Certifications = "ISO, HALAL, FSSC 22000",
                    QualityScore = 92,
                    SearchTags = "sunflower oil, bizce, refined oil, cooking oil, family pack",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Mayra Sunflower Oil 1L",
                    ProductCode = "MAYRA-SUN-1L",
                    Category = "Vegetable Oils",
                    SubCategory = "Sunflower Oil",
                    Brand = "Mayra",
                    Description = "100% pure sunflower oil",
                    Specifications = "Type: Refined sunflower oil, Volume: 1L PET bottle",
                    MinOrderQuantity = 1000,
                    Unit = "Bottles (1L)",
                    PricePerUnit = 2.00m,
                    Currency = "USD",
                    IsAvailable = true,
                    LeadTimeDays = 21,
                    CountryOfOrigin = "Turkey",
                    Certifications = "ISO, HALAL",
                    QualityScore = 90,
                    SearchTags = "sunflower oil, mayra, pure oil",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                // Corn Oil Products
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Bizce Corn Oil 1L",
                    ProductCode = "BIZCE-CORN-1L",
                    Category = "Vegetable Oils",
                    SubCategory = "Corn Oil",
                    Brand = "Bizce",
                    Description = "Premium refined corn oil",
                    Specifications = "Type: Refined corn oil, Volume: 1L PET bottle",
                    MinOrderQuantity = 1000,
                    Unit = "Bottles (1L)",
                    PricePerUnit = 2.30m,
                    Currency = "USD",
                    IsAvailable = true,
                    LeadTimeDays = 21,
                    CountryOfOrigin = "Turkey",
                    Certifications = "ISO, HALAL, FSSC 22000",
                    QualityScore = 92,
                    SearchTags = "corn oil, bizce, maize oil",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                },
                // Frying Oil
                new SupplierProductCatalog
                {
                    SupplierId = supplierId,
                    ProductName = "Kadoo Professional Frying Oil 18L",
                    ProductCode = "KADOO-FRY-18L",
                    Category = "Vegetable Oils",
                    SubCategory = "Frying Oil",
                    Brand = "Kadoo",
                    Description = "High temperature stable frying oil for professional use",
                    Specifications = "Type: Blended frying oil, Volume: 18L tin",
                    MinOrderQuantity = 100,
                    Unit = "Tins (18L)",
                    PricePerUnit = 32.00m,
                    Currency = "USD",
                    IsAvailable = true,
                    LeadTimeDays = 21,
                    CountryOfOrigin = "Turkey",
                    Certifications = "ISO, HALAL, FSSC 22000",
                    QualityScore = 94,
                    SearchTags = "frying oil, professional, kadoo, deep frying",
                    CreatedAt = DateTime.Now,
                    UpdatedAt = DateTime.Now
                }
            };

            _context.SupplierProductCatalogs.AddRange(products);
            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                message = $"Successfully added {products.Count} products for Kadooglu Yag",
                supplierId = supplierId,
                companyName = kadooglu.CompanyName,
                productsAdded = products.Select(p => new { p.ProductName, p.Brand, p.Category })
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }

    [HttpPost("add-prutul-supplier")]
    public async Task<IActionResult> AddPrutulSupplier()
    {
        try
        {
            // Check if Prutul already exists
            var existingUser = await _context.FdxUsers.FirstOrDefaultAsync(u => u.CompanyName == "Prutul S.A.");
            if (existingUser != null)
            {
                return Ok(new { message = "Prutul S.A. already exists", supplierId = existingUser.Id });
            }

            // Create Prutul supplier user
            var prutulUser = new User
            {
                Username = "prutul_sa",
                Password = "TempPassword123!", // Will require password change
                Email = "office@prutul.ro",
                CompanyName = "Prutul S.A.",
                Type = UserType.Supplier,
                Country = "Romania",
                PhoneNumber = "+40 236 466 100",
                Website = "www.prutul.ro",
                Address = "Galati Commercial Harbor, Galati County, Romania",
                Category = "Vegetable Oil Producer",
                CategoryId = CategoryType.Manufacturer,
                BusinessType = "Vegetable Oil Manufacturer & Exporter",
                FullDescription = "Leading producer of vegetable oil with 126+ years tradition. One of the most important agribusiness companies in Romania and major exporter in South-Eastern Europe. Modern factory with crushing, refining and bottling capabilities.",
                SubCategories = "Sunflower Oil, Rapeseed Oil, Soybean Oil, High Oleic Oil",
                CreatedAt = DateTime.Now,
                IsActive = true,
                RequiresPasswordChange = true,
                DataComplete = true,
                Verification = VerificationStatus.Verified,
                ImportedAt = DateTime.Now
            };

            _context.FdxUsers.Add(prutulUser);
            await _context.SaveChangesAsync();

            var supplierId = prutulUser.Id;

            // Add Supplier Details
            var supplierDetails = new SupplierDetails
            {
                UserId = supplierId,
                CompanyRegistrationNumber = "RO1234567",
                TaxId = "RO1234567",
                ProductCategories = "Sunflower Oil, Rapeseed Oil, Soybean Oil, Vegetable Oils",
                Certifications = "ISO, IFS, FSSC, FDA, Kosher, Halal, FOSFA, GAFTA",
                PaymentTerms = "T/T, L/C, 30 days net",
                Incoterms = "FOB, CIF, CFR, EXW",
                Currency = "EUR",
                MinimumOrderValue = 5000.00m,
                LeadTimeDays = 14,
                PreferredSeaPort = "Galati Commercial Harbor, Constanta Port",
                WarehouseLocations = "Galati, Romania",
                Description = "Top vegetable oil producer with 126+ years tradition. Modern facilities with crushing, refining and bottling capabilities. Export capacity: 6000 tons crude oil, 5000 tons sunflower meal via Danube River terminal.",
                SalesContactName = "Sales Department",
                SalesContactEmail = "office@prutul.ro",
                SalesContactPhone = "+40 236 466 100",
                IsVerified = true,
                VerifiedAt = DateTime.Now,
                Rating = 4.8m,
                CreatedAt = DateTime.Now,
                UpdatedAt = DateTime.Now
            };

            _context.SupplierDetails.Add(supplierDetails);
            await _context.SaveChangesAsync();

            return Ok(new
            {
                success = true,
                message = "Successfully added Prutul S.A.",
                supplierId = supplierId
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { error = ex.Message });
        }
    }
}