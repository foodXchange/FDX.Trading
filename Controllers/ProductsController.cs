using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using FDX.Trading.Services;
using System.Linq;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    private readonly FdxTradingContext _context;
    private readonly CsvProductImportService _importService;
    
    public ProductsController(FdxTradingContext context, CsvProductImportService importService)
    {
        _context = context;
        _importService = importService;
    }
    
    // GET: api/products/catalog - Optimized catalog endpoint with advanced filtering
    [HttpGet("catalog")]
    public async Task<ActionResult<ProductCatalogResponse>> GetProductCatalog(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 50,
        [FromQuery] string? search = null,
        [FromQuery] string? categories = null, // comma-separated
        [FromQuery] string? suppliers = null, // comma-separated IDs
        [FromQuery] decimal? priceMin = null,
        [FromQuery] decimal? priceMax = null,
        [FromQuery] string? certifications = null, // comma-separated: kosher,organic,vegan,glutenfree
        [FromQuery] string? status = null,
        [FromQuery] string? countries = null, // comma-separated
        [FromQuery] int? shelfLifeMin = null,
        [FromQuery] int? shelfLifeMax = null,
        [FromQuery] string? sortBy = "name",
        [FromQuery] string? sortOrder = "asc")
    {
        var query = _context.Products
            .Include(p => p.Supplier)
            .AsQueryable();

        // Apply search filter
        if (!string.IsNullOrWhiteSpace(search))
        {
            search = search.ToLower();
            query = query.Where(p => 
                p.ProductName.ToLower().Contains(search) ||
                p.ProductCode.ToLower().Contains(search) ||
                (p.Description != null && p.Description.ToLower().Contains(search)) ||
                (p.Barcode != null && p.Barcode.Contains(search)));
        }

        // Apply category filter
        if (!string.IsNullOrWhiteSpace(categories))
        {
            var categoryList = categories.Split(',').Select(c => c.Trim()).ToList();
            query = query.Where(p => categoryList.Contains(p.Category));
        }

        // Apply supplier filter
        if (!string.IsNullOrWhiteSpace(suppliers))
        {
            var supplierIds = suppliers.Split(',').Select(s => int.Parse(s.Trim())).ToList();
            query = query.Where(p => p.SupplierId.HasValue && supplierIds.Contains(p.SupplierId.Value));
        }

        // Apply price range filter
        if (priceMin.HasValue)
            query = query.Where(p => p.UnitWholesalePrice >= priceMin);
        if (priceMax.HasValue)
            query = query.Where(p => p.UnitWholesalePrice <= priceMax);

        // Apply certification filters
        if (!string.IsNullOrWhiteSpace(certifications))
        {
            var certs = certifications.ToLower().Split(',');
            if (certs.Contains("kosher"))
                query = query.Where(p => p.IsKosher);
            if (certs.Contains("organic"))
                query = query.Where(p => p.IsOrganic);
            if (certs.Contains("vegan"))
                query = query.Where(p => p.IsVegan);
            if (certs.Contains("glutenfree"))
                query = query.Where(p => p.IsGlutenFree);
        }

        // Apply status filter
        if (!string.IsNullOrWhiteSpace(status) && Enum.TryParse<ProductStatus>(status, out var productStatus))
        {
            query = query.Where(p => p.Status == productStatus);
        }

        // Apply country filter
        if (!string.IsNullOrWhiteSpace(countries))
        {
            var countryList = countries.Split(',').Select(c => c.Trim()).ToList();
            query = query.Where(p => countryList.Contains(p.CountryOfOrigin) || 
                (p.Supplier != null && countryList.Contains(p.Supplier.Country)));
        }

        // Apply shelf life filter
        if (shelfLifeMin.HasValue)
            query = query.Where(p => p.ShelfLifeDays >= shelfLifeMin);
        if (shelfLifeMax.HasValue)
            query = query.Where(p => p.ShelfLifeDays <= shelfLifeMax);

        // Get total count before pagination
        var totalCount = await query.CountAsync();

        // Apply sorting
        query = sortBy?.ToLower() switch
        {
            "price" => sortOrder?.ToLower() == "desc" 
                ? query.OrderByDescending(p => p.UnitWholesalePrice)
                : query.OrderBy(p => p.UnitWholesalePrice),
            "newest" => query.OrderByDescending(p => p.CreatedAt),
            "supplier" => sortOrder?.ToLower() == "desc"
                ? query.OrderByDescending(p => p.Supplier.CompanyName)
                : query.OrderBy(p => p.Supplier.CompanyName),
            _ => sortOrder?.ToLower() == "desc"
                ? query.OrderByDescending(p => p.ProductName)
                : query.OrderBy(p => p.ProductName)
        };

        // Apply pagination
        var products = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(p => new ProductCatalogItem
            {
                Id = p.Id,
                ProductCode = p.ProductCode,
                ProductName = p.ProductName,
                Category = p.Category,
                SubCategory = p.SubCategory,
                SupplierId = p.SupplierId,
                SupplierName = p.Supplier != null ? p.Supplier.CompanyName : null,
                SupplierCountry = p.Supplier != null ? p.Supplier.Country : null,
                UnitPrice = p.UnitWholesalePrice,
                Currency = p.Currency ?? "USD",
                MOQ = p.MOQ,
                UnitsPerCarton = p.UnitsPerCarton,
                Incoterms = p.Incoterms,
                PaymentTerms = p.PaymentTerms,
                LeadTimeDays = p.LeadTimeDays,
                IsKosher = p.IsKosher,
                IsOrganic = p.IsOrganic,
                IsVegan = p.IsVegan,
                IsGlutenFree = p.IsGlutenFree,
                CountryOfOrigin = p.CountryOfOrigin,
                ShelfLifeDays = p.ShelfLifeDays,
                Status = p.Status.ToString(),
                ProductImage = p.ProductImage,
                CreatedAt = p.CreatedAt
            })
            .ToListAsync();

        return Ok(new ProductCatalogResponse
        {
            Products = products,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)pageSize)
        });
    }

    // GET: api/products/catalog/filters - Get available filter options with counts
    [HttpGet("catalog/filters")]
    public async Task<ActionResult<ProductFiltersResponse>> GetProductFilters()
    {
        var filters = new ProductFiltersResponse();

        // Get categories with counts
        filters.Categories = await _context.Products
            .Where(p => p.Category != null)
            .GroupBy(p => p.Category)
            .Select(g => new FilterOption { Value = g.Key!, Count = g.Count() })
            .OrderBy(f => f.Value)
            .ToListAsync();

        // Get suppliers with counts
        filters.Suppliers = await _context.Products
            .Where(p => p.SupplierId != null)
            .GroupBy(p => new { p.SupplierId, p.Supplier.CompanyName })
            .Select(g => new SupplierFilterOption 
            { 
                Id = g.Key.SupplierId!.Value, 
                Name = g.Key.CompanyName, 
                Count = g.Count() 
            })
            .OrderBy(f => f.Name)
            .ToListAsync();

        // Get countries with counts
        filters.Countries = await _context.Products
            .Where(p => p.CountryOfOrigin != null || p.Supplier.Country != null)
            .Select(p => p.CountryOfOrigin ?? p.Supplier.Country)
            .Where(c => c != null)
            .GroupBy(c => c)
            .Select(g => new FilterOption { Value = g.Key!, Count = g.Count() })
            .OrderBy(f => f.Value)
            .ToListAsync();

        // Get price range
        var priceStats = await _context.Products
            .Where(p => p.UnitWholesalePrice.HasValue)
            .GroupBy(p => 1)
            .Select(g => new
            {
                Min = g.Min(p => p.UnitWholesalePrice),
                Max = g.Max(p => p.UnitWholesalePrice)
            })
            .FirstOrDefaultAsync();

        filters.PriceRange = new PriceRange
        {
            Min = priceStats?.Min ?? 0,
            Max = priceStats?.Max ?? 1000
        };

        // Get certification counts
        filters.Certifications = new List<CertificationOption>
        {
            new() { Type = "kosher", Label = "Kosher", Count = await _context.Products.CountAsync(p => p.IsKosher) },
            new() { Type = "organic", Label = "Organic", Count = await _context.Products.CountAsync(p => p.IsOrganic) },
            new() { Type = "vegan", Label = "Vegan", Count = await _context.Products.CountAsync(p => p.IsVegan) },
            new() { Type = "glutenfree", Label = "Gluten Free", Count = await _context.Products.CountAsync(p => p.IsGlutenFree) }
        };

        return Ok(filters);
    }

    // GET: api/products
    [HttpGet]
    public async Task<ActionResult<IEnumerable<object>>> GetProducts(
        [FromQuery] string? category = null,
        [FromQuery] int? supplierId = null,
        [FromQuery] int? buyerId = null,
        [FromQuery] string? status = null,
        [FromQuery] string? search = null,
        [FromQuery] bool? isKosher = null,
        [FromQuery] bool? isOrganic = null)
    {
        var query = _context.Products
            .Include(p => p.Supplier)
            .Include(p => p.PriceProposals)
                .ThenInclude(pp => pp.Supplier)
            .Include(p => p.InitialBuyer)
            .AsQueryable();
        
        // Apply filters
        if (!string.IsNullOrWhiteSpace(category))
            query = query.Where(p => p.Category == category);
        
        if (supplierId.HasValue)
            query = query.Where(p => p.SupplierId == supplierId);
        
        if (buyerId.HasValue)
            query = query.Where(p => p.InitialBuyerId == buyerId || 
                p.PriceProposals.Any(pp => pp.ProductRequest.BuyerId == buyerId));
        
        if (!string.IsNullOrWhiteSpace(status))
        {
            if (Enum.TryParse<ProductStatus>(status, out var productStatus))
                query = query.Where(p => p.Status == productStatus);
        }
        
        if (!string.IsNullOrWhiteSpace(search))
        {
            search = search.ToLower();
            query = query.Where(p => 
                p.ProductName.ToLower().Contains(search) ||
                p.ProductCode.ToLower().Contains(search) ||
                (p.Description != null && p.Description.ToLower().Contains(search)));
        }
        
        if (isKosher.HasValue)
            query = query.Where(p => p.IsKosher == isKosher.Value);
        
        if (isOrganic.HasValue)
            query = query.Where(p => p.IsOrganic == isOrganic.Value);
        
        var products = await query.Select(p => new
        {
            id = p.Id,
            productCode = p.ProductCode,
            productName = p.ProductName,
            category = p.Category,
            subCategory = p.SubCategory,
            description = p.Description,
            status = p.Status.ToString(),
            isKosher = p.IsKosher,
            isOrganic = p.IsOrganic,
            isVegan = p.IsVegan,
            isGlutenFree = p.IsGlutenFree,
            unitOfMeasure = p.UnitOfMeasure,
            netWeight = p.NetWeight,
            grossWeight = p.GrossWeight,
            unitsPerCarton = p.UnitsPerCarton,
            shelfLifeDays = p.ShelfLifeDays,
            productImages = p.ProductImages,
            hsCode = p.HSCode,
            buyerCompany = p.BuyerCompany,
            supplier = p.Supplier != null ? new
            {
                supplierId = p.SupplierId,
                supplierName = p.Supplier.CompanyName,
                country = p.Supplier.Country,
                unitPrice = p.UnitWholesalePrice,
                currency = p.Currency,
                moq = p.MOQ,
                incoterms = p.Incoterms,
                paymentTerms = p.PaymentTerms
            } : null,
            proposals = p.PriceProposals.Select(pp => new
            {
                proposalId = pp.Id,
                supplierId = pp.SupplierId,
                supplierName = pp.Supplier.CompanyName,
                currentPrice = pp.CurrentPrice,
                currency = pp.Currency,
                status = pp.Status.ToString(),
                moq = pp.MinimumOrderQuantity,
                incoterms = pp.Incoterms,
                leadTimeDays = pp.LeadTimeDays
            }).ToList(),
            lowestPrice = p.PriceProposals.Any() ? 
                p.PriceProposals.Where(pp => pp.Status == ProposalStatus.PriceConfirmed)
                    .Min(pp => (decimal?)pp.CurrentPrice) : null
        }).ToListAsync();
        
        return Ok(products);
    }
    
    // GET: api/products/{id}
    [HttpGet("{id}")]
    public async Task<ActionResult<object>> GetProduct(int id)
    {
        var product = await _context.Products
            .Include(p => p.Supplier)
            .Include(p => p.PriceProposals)
                .ThenInclude(pp => pp.Supplier)
            .Include(p => p.PriceProposals)
                .ThenInclude(pp => pp.PriceHistories)
            .Include(p => p.InitialBuyer)
            .FirstOrDefaultAsync(p => p.Id == id);
        
        if (product == null)
            return NotFound();
        
        return Ok(new
        {
            id = product.Id,
            productCode = product.ProductCode,
            productName = product.ProductName,
            category = product.Category,
            subCategory = product.SubCategory,
            productFamily = product.ProductFamily,
            description = product.Description,
            status = product.Status.ToString(),
            
            // Certifications
            isKosher = product.IsKosher,
            kosherCertificate = product.KosherCertificate,
            isOrganic = product.IsOrganic,
            organicCertificate = product.OrganicCertificate,
            isVegan = product.IsVegan,
            isGlutenFree = product.IsGlutenFree,
            otherCertifications = product.OtherCertifications,
            
            // Measurements
            unitOfMeasure = product.UnitOfMeasure,
            netWeight = product.NetWeight,
            grossWeight = product.GrossWeight,
            unitsPerCarton = product.UnitsPerCarton,
            cartonsPerPallet = product.CartonsPerPallet,
            
            // Storage
            minTemperature = product.MinTemperature,
            maxTemperature = product.MaxTemperature,
            shelfLifeDays = product.ShelfLifeDays,
            storageConditions = product.StorageConditions,
            
            // Identification
            hsCode = product.HSCode,
            barcode = product.Barcode,
            productImages = product.ProductImages,
            openComments = product.OpenComments,
            
            // Origin
            countryOfOrigin = product.CountryOfOrigin,
            manufacturer = product.Manufacturer,
            brand = product.Brand,
            
            // Buyer info
            initialBuyerId = product.InitialBuyerId,
            initialBuyer = product.InitialBuyer != null ? new
            {
                id = product.InitialBuyer.Id,
                companyName = product.InitialBuyer.CompanyName,
                country = product.InitialBuyer.Country
            } : null,
            buyerCompany = product.BuyerCompany,
            buyerProductCode = product.BuyerProductCode,
            
            // Supplier
            supplier = product.Supplier != null ? new
            {
                supplierId = product.SupplierId,
                supplierName = product.Supplier.CompanyName,
                country = product.Supplier.Country,
                website = product.Supplier.Website,
                unitPrice = product.UnitWholesalePrice,
                cartonPrice = product.CartonWholesalePrice,
                currency = product.Currency,
                moq = product.MOQ,
                leadTimeDays = product.LeadTimeDays,
                paymentTerms = product.PaymentTerms,
                incoterms = product.Incoterms,
                preferredPort = product.PreferredPort
            } : null,
            
            // Price Proposals
            proposals = product.PriceProposals.OrderByDescending(pp => pp.UpdatedAt).Select(pp => new
            {
                proposalId = pp.Id,
                supplierId = pp.SupplierId,
                supplierName = pp.Supplier.CompanyName,
                initialPrice = pp.InitialPrice,
                currentPrice = pp.CurrentPrice,
                currency = pp.Currency,
                pricePerCarton = pp.PricePerCarton,
                status = pp.Status.ToString(),
                moq = pp.MinimumOrderQuantity,
                unit = pp.Unit,
                incoterms = pp.Incoterms,
                paymentTerms = pp.PaymentTerms,
                preferredPort = pp.PreferredPort,
                leadTimeDays = pp.LeadTimeDays,
                unitsPerCarton = pp.UnitsPerCarton,
                cartonsPerContainer20ft = pp.CartonsPerContainer20ft,
                cartonsPerContainer40ft = pp.CartonsPerContainer40ft,
                notes = pp.Notes,
                createdAt = pp.CreatedAt,
                updatedAt = pp.UpdatedAt,
                confirmedAt = pp.ConfirmedAt,
                priceHistory = pp.PriceHistories.OrderByDescending(ph => ph.ChangedAt).Select(ph => new
                {
                    oldPrice = ph.OldPrice,
                    newPrice = ph.NewPrice,
                    changeReason = ph.ChangeReason,
                    changedBy = ph.ChangedBy,
                    changedAt = ph.ChangedAt
                }).ToList()
            }).ToList(),
            
            // Metadata
            createdAt = product.CreatedAt,
            updatedAt = product.UpdatedAt,
            importedAt = product.ImportedAt
        });
    }
    
    // GET: api/products/categories
    [HttpGet("categories")]
    public async Task<ActionResult<IEnumerable<string>>> GetCategories()
    {
        var categories = await _context.Products
            .Where(p => p.Category != null)
            .Select(p => p.Category)
            .Distinct()
            .OrderBy(c => c)
            .ToListAsync();
        
        return Ok(categories);
    }
    
    // GET: api/products/proposals
    [HttpGet("proposals")]
    public async Task<ActionResult<IEnumerable<object>>> GetProductsWithProposals(
        [FromQuery] ProposalStatus? status = null,
        [FromQuery] int? buyerId = null,
        [FromQuery] int? supplierId = null)
    {
        var query = _context.PriceProposals
            .Include(pp => pp.Product)
            .Include(pp => pp.Supplier)
            .Include(pp => pp.ProductRequest)
                .ThenInclude(pr => pr.Buyer)
            .AsQueryable();
        
        if (status.HasValue)
            query = query.Where(pp => pp.Status == status.Value);
        
        if (buyerId.HasValue)
            query = query.Where(pp => pp.ProductRequest.BuyerId == buyerId.Value);
        
        if (supplierId.HasValue)
            query = query.Where(pp => pp.SupplierId == supplierId.Value);
        
        var proposals = await query.Select(pp => new
        {
            proposalId = pp.Id,
            productId = pp.ProductId,
            productCode = pp.Product.ProductCode,
            productName = pp.Product.ProductName,
            category = pp.Product.Category,
            productImage = pp.Product.ProductImages,
            supplierId = pp.SupplierId,
            supplierName = pp.Supplier.CompanyName,
            supplierCountry = pp.Supplier.Country,
            buyerId = pp.ProductRequest.BuyerId,
            buyerName = pp.ProductRequest.Buyer.CompanyName,
            requestTitle = pp.ProductRequest.Title,
            currentPrice = pp.CurrentPrice,
            currency = pp.Currency,
            moq = pp.MinimumOrderQuantity,
            unit = pp.Unit,
            status = pp.Status.ToString(),
            incoterms = pp.Incoterms,
            paymentTerms = pp.PaymentTerms,
            leadTimeDays = pp.LeadTimeDays,
            createdAt = pp.CreatedAt,
            updatedAt = pp.UpdatedAt,
            confirmedAt = pp.ConfirmedAt
        }).ToListAsync();
        
        return Ok(proposals);
    }
    
    // POST: api/products
    [HttpPost]
    public async Task<ActionResult<Product>> CreateProduct([FromBody] ProductCreateDto dto)
    {
        var product = new Product
        {
            ProductCode = dto.ProductCode,
            ProductName = dto.ProductName,
            Category = dto.Category,
            SubCategory = dto.SubCategory,
            Description = dto.Description,
            UnitOfMeasure = dto.UnitOfMeasure,
            NetWeight = dto.NetWeight,
            GrossWeight = dto.GrossWeight,
            UnitsPerCarton = dto.UnitsPerCarton,
            IsKosher = dto.IsKosher,
            IsOrganic = dto.IsOrganic,
            IsVegan = dto.IsVegan,
            IsGlutenFree = dto.IsGlutenFree,
            ShelfLifeDays = dto.ShelfLifeDays,
            HSCode = dto.HSCode,
            CountryOfOrigin = dto.CountryOfOrigin,
            Manufacturer = dto.Manufacturer,
            Brand = dto.Brand,
            InitialBuyerId = dto.InitialBuyerId,
            BuyerCompany = dto.BuyerCompany,
            ProductImages = dto.ProductImages,
            Status = ProductStatus.Active,
            CreatedAt = DateTime.Now
        };
        
        _context.Products.Add(product);
        await _context.SaveChangesAsync();
        
        return CreatedAtAction(nameof(GetProduct), new { id = product.Id }, product);
    }
    
    // PUT: api/products/{id}
    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateProduct(int id, [FromBody] ProductUpdateDto dto)
    {
        var product = await _context.Products.FindAsync(id);
        
        if (product == null)
            return NotFound();
        
        // Update fields
        product.ProductName = dto.ProductName ?? product.ProductName;
        product.Category = dto.Category ?? product.Category;
        product.SubCategory = dto.SubCategory ?? product.SubCategory;
        product.Description = dto.Description ?? product.Description;
        product.Status = dto.Status ?? product.Status;
        product.IsKosher = dto.IsKosher ?? product.IsKosher;
        product.IsOrganic = dto.IsOrganic ?? product.IsOrganic;
        product.IsVegan = dto.IsVegan ?? product.IsVegan;
        product.IsGlutenFree = dto.IsGlutenFree ?? product.IsGlutenFree;
        product.ShelfLifeDays = dto.ShelfLifeDays ?? product.ShelfLifeDays;
        product.ProductImages = dto.ProductImages ?? product.ProductImages;
        product.UpdatedAt = DateTime.Now;
        
        await _context.SaveChangesAsync();
        
        return Ok(new { success = true, message = "Product updated successfully" });
    }
    
    // GET: api/products/stats
    [HttpGet("stats")]
    public async Task<ActionResult<object>> GetStats()
    {
        var stats = new
        {
            totalProducts = await _context.Products.CountAsync(),
            activeProducts = await _context.Products.CountAsync(p => p.Status == ProductStatus.Active),
            totalCategories = await _context.Products.Select(p => p.Category).Distinct().CountAsync(),
            kosherProducts = await _context.Products.CountAsync(p => p.IsKosher),
            organicProducts = await _context.Products.CountAsync(p => p.IsOrganic),
            totalProposals = await _context.PriceProposals.CountAsync(),
            confirmedProposals = await _context.PriceProposals.CountAsync(pp => pp.Status == ProposalStatus.PriceConfirmed),
            activeRequests = await _context.ProductRequests.CountAsync(pr => pr.Status == RequestStatus.Active),
            suppliersWithProducts = await _context.SupplierProducts.Select(sp => sp.SupplierDetailsId).Distinct().CountAsync(),
            averageLeadTime = await _context.PriceProposals
                .Where(pp => pp.LeadTimeDays > 0)
                .AverageAsync(pp => (double?)pp.LeadTimeDays) ?? 0
        };
        
        return Ok(stats);
    }
    
    // POST: api/products/import-csv
    [HttpPost("import-csv")]
    public async Task<ActionResult<ProductImportResult>> ImportProductsFromCsv([FromBody] ImportCsvRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.FilePath))
        {
            return BadRequest("File path is required");
        }
        
        if (!System.IO.File.Exists(request.FilePath))
        {
            return BadRequest($"File not found: {request.FilePath}");
        }
        
        var result = await _importService.ImportProductsFromCsvAsync(request.FilePath);
        
        if (result.Success)
        {
            return Ok(result);
        }
        
        return BadRequest(result);
    }
    
    // GET: api/products/supplier/{supplierId}
    [HttpGet("supplier/{supplierId}")]
    public async Task<ActionResult<IEnumerable<object>>> GetSupplierProducts(int supplierId)
    {
        var supplier = await _context.FdxUsers
            .FirstOrDefaultAsync(u => u.Id == supplierId && u.Type == UserType.Supplier);
        
        if (supplier == null)
        {
            return NotFound("Supplier not found");
        }
        
        var products = await _context.Products
            .Where(p => p.SupplierId == supplierId)
            .Select(p => new
            {
                id = p.Id,
                productCode = p.ProductCode,
                productName = p.ProductName,
                category = p.Category,
                subCategory = p.SubCategory,
                unitPrice = p.UnitWholesalePrice,
                cartonPrice = p.CartonWholesalePrice,
                currency = p.Currency,
                moq = p.MOQ,
                incoterms = p.Incoterms,
                paymentTerms = p.PaymentTerms,
                leadTimeDays = p.LeadTimeDays,
                isKosher = p.IsKosher,
                isOrganic = p.IsOrganic,
                status = p.Status.ToString(),
                countryOfOrigin = p.CountryOfOrigin,
                shelfLifeDays = p.ShelfLifeDays,
                unitsPerCarton = p.UnitsPerCarton
            })
            .ToListAsync();
        
        return Ok(new
        {
            supplier = new
            {
                id = supplier.Id,
                companyName = supplier.CompanyName,
                country = supplier.Country,
                email = supplier.Email,
                website = supplier.Website
            },
            productCount = products.Count,
            products = products
        });
    }
    
    // GET: api/products/suppliers/catalog-summary
    [HttpGet("suppliers/catalog-summary")]
    public async Task<ActionResult<IEnumerable<object>>> GetSuppliersCatalogSummary()
    {
        var suppliers = await _context.FdxUsers
            .Where(u => u.Type == UserType.Supplier)
            .Select(s => new
            {
                supplierId = s.Id,
                companyName = s.CompanyName,
                country = s.Country,
                productCount = s.Products.Count(),
                categories = s.Products.Select(p => p.Category).Distinct().Count(),
                totalValue = s.Products.Sum(p => p.UnitWholesalePrice ?? 0),
                hasKosherProducts = s.Products.Any(p => p.IsKosher),
                hasOrganicProducts = s.Products.Any(p => p.IsOrganic),
                latestProduct = s.Products.OrderByDescending(p => p.CreatedAt).Select(p => p.ProductName).FirstOrDefault()
            })
            .OrderByDescending(s => s.productCount)
            .ToListAsync();
        
        return Ok(suppliers);
    }
}

// DTOs
public class ImportCsvRequest
{
    public string FilePath { get; set; } = "";
}

public class ProductCatalogResponse
{
    public List<ProductCatalogItem> Products { get; set; } = new();
    public int TotalCount { get; set; }
    public int Page { get; set; }
    public int PageSize { get; set; }
    public int TotalPages { get; set; }
}

public class ProductCatalogItem
{
    public int Id { get; set; }
    public string ProductCode { get; set; } = "";
    public string ProductName { get; set; } = "";
    public string? Category { get; set; }
    public string? SubCategory { get; set; }
    public int? SupplierId { get; set; }
    public string? SupplierName { get; set; }
    public string? SupplierCountry { get; set; }
    public decimal? UnitPrice { get; set; }
    public string Currency { get; set; } = "USD";
    public int? MOQ { get; set; }
    public int? UnitsPerCarton { get; set; }
    public string? Incoterms { get; set; }
    public string? PaymentTerms { get; set; }
    public int? LeadTimeDays { get; set; }
    public bool IsKosher { get; set; }
    public bool IsOrganic { get; set; }
    public bool IsVegan { get; set; }
    public bool IsGlutenFree { get; set; }
    public string? CountryOfOrigin { get; set; }
    public int? ShelfLifeDays { get; set; }
    public string Status { get; set; } = "";
    public string? ProductImage { get; set; }
    public DateTime CreatedAt { get; set; }
}

public class ProductFiltersResponse
{
    public List<FilterOption> Categories { get; set; } = new();
    public List<SupplierFilterOption> Suppliers { get; set; } = new();
    public List<FilterOption> Countries { get; set; } = new();
    public PriceRange PriceRange { get; set; } = new();
    public List<CertificationOption> Certifications { get; set; } = new();
}

public class FilterOption
{
    public string Value { get; set; } = "";
    public int Count { get; set; }
}

public class SupplierFilterOption
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public int Count { get; set; }
}

public class PriceRange
{
    public decimal? Min { get; set; }
    public decimal? Max { get; set; }
}

public class CertificationOption
{
    public string Type { get; set; } = "";
    public string Label { get; set; } = "";
    public int Count { get; set; }
}

public class ProductCreateDto
{
    public string ProductCode { get; set; } = "";
    public string ProductName { get; set; } = "";
    public string? Category { get; set; }
    public string? SubCategory { get; set; }
    public string? Description { get; set; }
    public string? UnitOfMeasure { get; set; }
    public decimal? NetWeight { get; set; }
    public decimal? GrossWeight { get; set; }
    public int? UnitsPerCarton { get; set; }
    public bool IsKosher { get; set; }
    public bool IsOrganic { get; set; }
    public bool IsVegan { get; set; }
    public bool IsGlutenFree { get; set; }
    public int? ShelfLifeDays { get; set; }
    public string? HSCode { get; set; }
    public string? CountryOfOrigin { get; set; }
    public string? Manufacturer { get; set; }
    public string? Brand { get; set; }
    public int? InitialBuyerId { get; set; }
    public string? BuyerCompany { get; set; }
    public string? ProductImages { get; set; }
}

public class ProductUpdateDto
{
    public string? ProductName { get; set; }
    public string? Category { get; set; }
    public string? SubCategory { get; set; }
    public string? Description { get; set; }
    public ProductStatus? Status { get; set; }
    public bool? IsKosher { get; set; }
    public bool? IsOrganic { get; set; }
    public bool? IsVegan { get; set; }
    public bool? IsGlutenFree { get; set; }
    public int? ShelfLifeDays { get; set; }
    public string? ProductImages { get; set; }
}