using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using FDX.Trading.Data;
using FDX.Trading.Models;
using System.Text.Json;

namespace FDX.Trading.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SuppliersController : ControllerBase
    {
        private readonly FdxTradingContext _context;
        private readonly ILogger<SuppliersController> _logger;

        public SuppliersController(FdxTradingContext context, ILogger<SuppliersController> logger)
        {
            _context = context;
            _logger = logger;
        }

        // GET: api/suppliers
        [HttpGet]
        public async Task<ActionResult<IEnumerable<SupplierDto>>> GetSuppliers(
            [FromQuery] bool? hasKosher = null,
            [FromQuery] bool? hasHalal = null,
            [FromQuery] bool? hasOrganic = null,
            [FromQuery] bool? offersPrivateLabel = null,
            [FromQuery] string? incoterms = null,
            [FromQuery] string? country = null,
            [FromQuery] string? search = null)
        {
            var query = _context.Suppliers
                .Include(s => s.Company)
                .Where(s => s.Company.IsActive);

            // Apply filters
            if (hasKosher.HasValue)
                query = query.Where(s => s.HasKosherCertification == hasKosher.Value);
            
            if (hasHalal.HasValue)
                query = query.Where(s => s.HasHalalCertification == hasHalal.Value);
            
            if (hasOrganic.HasValue)
                query = query.Where(s => s.HasOrganicCertification == hasOrganic.Value);
            
            if (offersPrivateLabel.HasValue)
                query = query.Where(s => s.OffersPrivateLabel == offersPrivateLabel.Value);
            
            if (!string.IsNullOrEmpty(incoterms))
                query = query.Where(s => s.Incoterms == incoterms);
            
            if (!string.IsNullOrEmpty(country))
                query = query.Where(s => s.Company.Country == country);
            
            if (!string.IsNullOrEmpty(search))
            {
                var searchLower = search.ToLower();
                query = query.Where(s => 
                    s.Company.CompanyName.ToLower().Contains(searchLower) ||
                    (s.Company.Email != null && s.Company.Email.ToLower().Contains(searchLower)) ||
                    (s.BrandNames != null && s.BrandNames.ToLower().Contains(searchLower)));
            }

            var suppliers = await query
                .OrderBy(s => s.Company.CompanyName)
                .ToListAsync();

            return Ok(suppliers.Select(s => MapToDto(s)));
        }

        // GET: api/suppliers/5
        [HttpGet("{id}")]
        public async Task<ActionResult<SupplierDetailDto>> GetSupplier(int id)
        {
            var supplier = await _context.Suppliers
                .Include(s => s.Company)
                    .ThenInclude(c => c.UserRoles)
                    .ThenInclude(ur => ur.User)
                .FirstOrDefaultAsync(s => s.Id == id);

            if (supplier == null)
            {
                return NotFound();
            }

            return Ok(MapToDetailDto(supplier));
        }

        // GET: api/suppliers/company/5
        [HttpGet("company/{companyId}")]
        public async Task<ActionResult<SupplierDetailDto>> GetSupplierByCompany(int companyId)
        {
            var supplier = await _context.Suppliers
                .Include(s => s.Company)
                .FirstOrDefaultAsync(s => s.CompanyId == companyId);

            if (supplier == null)
            {
                return NotFound();
            }

            return Ok(MapToDetailDto(supplier));
        }

        // POST: api/suppliers
        [HttpPost]
        public async Task<ActionResult<SupplierDto>> CreateSupplier([FromBody] CreateSupplierDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            // Check if company exists
            var company = await _context.Companies.FindAsync(dto.CompanyId);
            if (company == null)
            {
                return NotFound("Company not found");
            }

            // Check if supplier profile already exists for this company
            var existingSupplier = await _context.Suppliers
                .FirstOrDefaultAsync(s => s.CompanyId == dto.CompanyId);
            
            if (existingSupplier != null)
            {
                return Conflict(new { message = "Supplier profile already exists for this company" });
            }

            var supplier = new Supplier
            {
                CompanyId = dto.CompanyId,
                BrandNames = dto.BrandNames,
                ProductCatalogUrl = dto.ProductCatalogUrl,
                ManufacturingCapacity = dto.ManufacturingCapacity,
                MinOrderQuantity = dto.MinOrderQuantity,
                MinOrderUnit = dto.MinOrderUnit,
                LeadTime = dto.LeadTime,
                Incoterms = dto.Incoterms,
                CanShipDirect = dto.CanShipDirect,
                PortOfLoading = dto.PortOfLoading,
                HasKosherCertification = dto.HasKosherCertification,
                KosherCertifier = dto.KosherCertifier,
                HasHalalCertification = dto.HasHalalCertification,
                HalalCertifier = dto.HalalCertifier,
                HasOrganicCertification = dto.HasOrganicCertification,
                OrganicCertifier = dto.OrganicCertifier,
                OffersPrivateLabel = dto.OffersPrivateLabel,
                OffersCustomPackaging = dto.OffersCustomPackaging,
                OffersProductDevelopment = dto.OffersProductDevelopment,
                PaymentTerms = dto.PaymentTerms,
                PricingCurrency = dto.PricingCurrency,
                SampleCost = dto.SampleCost,
                SamplePolicy = dto.SamplePolicy,
                FactoryEmployeeCount = dto.FactoryEmployeeCount,
                AnnualProductionValue = dto.AnnualProductionValue,
                MainMarkets = dto.MainMarkets,
                CompanyProfile = dto.CompanyProfile,
                Notes = dto.Notes
            };

            // Handle JSON fields
            if (dto.ProductCategories?.Any() == true)
                supplier.ProductCategories = JsonSerializer.Serialize(dto.ProductCategories);
            
            if (dto.ProductionFacilities?.Any() == true)
                supplier.ProductionFacilities = JsonSerializer.Serialize(dto.ProductionFacilities);
            
            if (dto.ExportCountries?.Any() == true)
                supplier.ExportCountries = JsonSerializer.Serialize(dto.ExportCountries);
            
            if (dto.QualityCertifications?.Any() == true)
                supplier.QualityCertifications = JsonSerializer.Serialize(dto.QualityCertifications);

            _context.Suppliers.Add(supplier);
            
            // Update company type if needed
            if (company.Type != CompanyType.Supplier && company.Type != CompanyType.Mixed)
            {
                company.Type = CompanyType.Mixed;
            }
            
            await _context.SaveChangesAsync();

            return CreatedAtAction(nameof(GetSupplier), new { id = supplier.Id }, MapToDto(supplier));
        }

        // PUT: api/suppliers/5
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateSupplier(int id, [FromBody] UpdateSupplierDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            var supplier = await _context.Suppliers
                .Include(s => s.Company)
                .FirstOrDefaultAsync(s => s.Id == id);
                
            if (supplier == null)
            {
                return NotFound();
            }

            // Update fields
            supplier.BrandNames = dto.BrandNames ?? supplier.BrandNames;
            supplier.ProductCatalogUrl = dto.ProductCatalogUrl ?? supplier.ProductCatalogUrl;
            supplier.ManufacturingCapacity = dto.ManufacturingCapacity ?? supplier.ManufacturingCapacity;
            supplier.MinOrderUnit = dto.MinOrderUnit ?? supplier.MinOrderUnit;
            supplier.LeadTime = dto.LeadTime ?? supplier.LeadTime;
            supplier.Incoterms = dto.Incoterms ?? supplier.Incoterms;
            supplier.PortOfLoading = dto.PortOfLoading ?? supplier.PortOfLoading;
            supplier.KosherCertifier = dto.KosherCertifier ?? supplier.KosherCertifier;
            supplier.HalalCertifier = dto.HalalCertifier ?? supplier.HalalCertifier;
            supplier.OrganicCertifier = dto.OrganicCertifier ?? supplier.OrganicCertifier;
            supplier.PaymentTerms = dto.PaymentTerms ?? supplier.PaymentTerms;
            supplier.PricingCurrency = dto.PricingCurrency ?? supplier.PricingCurrency;
            supplier.SamplePolicy = dto.SamplePolicy ?? supplier.SamplePolicy;
            supplier.MainMarkets = dto.MainMarkets ?? supplier.MainMarkets;
            supplier.CompanyProfile = dto.CompanyProfile ?? supplier.CompanyProfile;
            supplier.Notes = dto.Notes ?? supplier.Notes;

            if (dto.MinOrderQuantity.HasValue)
                supplier.MinOrderQuantity = dto.MinOrderQuantity.Value;
            if (dto.CanShipDirect.HasValue)
                supplier.CanShipDirect = dto.CanShipDirect.Value;
            if (dto.HasKosherCertification.HasValue)
                supplier.HasKosherCertification = dto.HasKosherCertification.Value;
            if (dto.HasHalalCertification.HasValue)
                supplier.HasHalalCertification = dto.HasHalalCertification.Value;
            if (dto.HasOrganicCertification.HasValue)
                supplier.HasOrganicCertification = dto.HasOrganicCertification.Value;
            if (dto.OffersPrivateLabel.HasValue)
                supplier.OffersPrivateLabel = dto.OffersPrivateLabel.Value;
            if (dto.OffersCustomPackaging.HasValue)
                supplier.OffersCustomPackaging = dto.OffersCustomPackaging.Value;
            if (dto.OffersProductDevelopment.HasValue)
                supplier.OffersProductDevelopment = dto.OffersProductDevelopment.Value;
            if (dto.SampleCost.HasValue)
                supplier.SampleCost = dto.SampleCost.Value;
            if (dto.FactoryEmployeeCount.HasValue)
                supplier.FactoryEmployeeCount = dto.FactoryEmployeeCount.Value;
            if (dto.AnnualProductionValue.HasValue)
                supplier.AnnualProductionValue = dto.AnnualProductionValue.Value;

            // Update JSON fields
            if (dto.ProductCategories != null)
                supplier.ProductCategories = dto.ProductCategories.Any() ? JsonSerializer.Serialize(dto.ProductCategories) : null;
            
            if (dto.ProductionFacilities != null)
                supplier.ProductionFacilities = dto.ProductionFacilities.Any() ? JsonSerializer.Serialize(dto.ProductionFacilities) : null;
            
            if (dto.ExportCountries != null)
                supplier.ExportCountries = dto.ExportCountries.Any() ? JsonSerializer.Serialize(dto.ExportCountries) : null;
            
            if (dto.QualityCertifications != null)
                supplier.QualityCertifications = dto.QualityCertifications.Any() ? JsonSerializer.Serialize(dto.QualityCertifications) : null;

            supplier.Company.UpdatedAt = DateTime.Now;
            
            await _context.SaveChangesAsync();

            return Ok(new { message = "Supplier updated successfully", supplier = MapToDto(supplier) });
        }

        // DELETE: api/suppliers/5
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteSupplier(int id)
        {
            var supplier = await _context.Suppliers
                .Include(s => s.Company)
                .FirstOrDefaultAsync(s => s.Id == id);
                
            if (supplier == null)
            {
                return NotFound();
            }

            _context.Suppliers.Remove(supplier);
            
            // Update company type if it was specifically a supplier
            if (supplier.Company.Type == CompanyType.Supplier)
            {
                supplier.Company.Type = CompanyType.Mixed;
            }
            
            await _context.SaveChangesAsync();

            return Ok(new { message = "Supplier profile deleted successfully" });
        }

        // GET: api/suppliers/certifications-summary
        [HttpGet("certifications-summary")]
        public async Task<ActionResult> GetCertificationsSummary()
        {
            var suppliers = await _context.Suppliers
                .Include(s => s.Company)
                .Where(s => s.Company.IsActive)
                .ToListAsync();

            var summary = new
            {
                totalSuppliers = suppliers.Count,
                hasKosher = suppliers.Count(s => s.HasKosherCertification),
                hasHalal = suppliers.Count(s => s.HasHalalCertification),
                hasOrganic = suppliers.Count(s => s.HasOrganicCertification),
                offersPrivateLabel = suppliers.Count(s => s.OffersPrivateLabel),
                offersCustomPackaging = suppliers.Count(s => s.OffersCustomPackaging),
                offersProductDevelopment = suppliers.Count(s => s.OffersProductDevelopment),
                canShipDirect = suppliers.Count(s => s.CanShipDirect),
                byCountry = suppliers.GroupBy(s => s.Company.Country)
                    .Select(g => new { country = g.Key, count = g.Count() })
                    .OrderByDescending(x => x.count)
                    .Take(10),
                byIncoterms = suppliers.Where(s => !string.IsNullOrEmpty(s.Incoterms))
                    .GroupBy(s => s.Incoterms)
                    .Select(g => new { incoterms = g.Key, count = g.Count() })
                    .OrderByDescending(x => x.count)
            };

            return Ok(summary);
        }

        // Helper methods
        private SupplierDto MapToDto(Supplier supplier)
        {
            return new SupplierDto
            {
                Id = supplier.Id,
                CompanyId = supplier.CompanyId,
                CompanyName = supplier.Company?.CompanyName ?? "",
                Country = supplier.Company?.Country ?? "",
                BrandNames = supplier.BrandNames,
                HasKosherCertification = supplier.HasKosherCertification,
                HasHalalCertification = supplier.HasHalalCertification,
                HasOrganicCertification = supplier.HasOrganicCertification,
                OffersPrivateLabel = supplier.OffersPrivateLabel,
                OffersCustomPackaging = supplier.OffersCustomPackaging,
                CanShipDirect = supplier.CanShipDirect,
                Incoterms = supplier.Incoterms,
                PaymentTerms = supplier.PaymentTerms,
                IsActive = supplier.Company?.IsActive ?? false,
                IsVerified = supplier.Company?.IsVerified ?? false
            };
        }

        private SupplierDetailDto MapToDetailDto(Supplier supplier)
        {
            var dto = new SupplierDetailDto
            {
                Id = supplier.Id,
                CompanyId = supplier.CompanyId,
                CompanyName = supplier.Company?.CompanyName ?? "",
                Country = supplier.Company?.Country ?? "",
                CompanyEmail = supplier.Company?.Email,
                CompanyPhone = supplier.Company?.PhoneNumber,
                CompanyWebsite = supplier.Company?.Website,
                BrandNames = supplier.BrandNames,
                ProductCatalogUrl = supplier.ProductCatalogUrl,
                ManufacturingCapacity = supplier.ManufacturingCapacity,
                MinOrderQuantity = supplier.MinOrderQuantity,
                MinOrderUnit = supplier.MinOrderUnit,
                LeadTime = supplier.LeadTime,
                Incoterms = supplier.Incoterms,
                CanShipDirect = supplier.CanShipDirect,
                PortOfLoading = supplier.PortOfLoading,
                HasKosherCertification = supplier.HasKosherCertification,
                KosherCertifier = supplier.KosherCertifier,
                HasHalalCertification = supplier.HasHalalCertification,
                HalalCertifier = supplier.HalalCertifier,
                HasOrganicCertification = supplier.HasOrganicCertification,
                OrganicCertifier = supplier.OrganicCertifier,
                OffersPrivateLabel = supplier.OffersPrivateLabel,
                OffersCustomPackaging = supplier.OffersCustomPackaging,
                OffersProductDevelopment = supplier.OffersProductDevelopment,
                PaymentTerms = supplier.PaymentTerms,
                PricingCurrency = supplier.PricingCurrency,
                SampleCost = supplier.SampleCost,
                SamplePolicy = supplier.SamplePolicy,
                FactoryEmployeeCount = supplier.FactoryEmployeeCount,
                AnnualProductionValue = supplier.AnnualProductionValue,
                MainMarkets = supplier.MainMarkets,
                CompanyProfile = supplier.CompanyProfile,
                Notes = supplier.Notes
            };

            // Deserialize JSON fields
            try
            {
                if (!string.IsNullOrEmpty(supplier.ProductCategories))
                    dto.ProductCategories = JsonSerializer.Deserialize<List<string>>(supplier.ProductCategories);
                
                if (!string.IsNullOrEmpty(supplier.ProductionFacilities))
                    dto.ProductionFacilities = JsonSerializer.Deserialize<List<string>>(supplier.ProductionFacilities);
                
                if (!string.IsNullOrEmpty(supplier.ExportCountries))
                    dto.ExportCountries = JsonSerializer.Deserialize<List<string>>(supplier.ExportCountries);
                
                if (!string.IsNullOrEmpty(supplier.QualityCertifications))
                    dto.QualityCertifications = JsonSerializer.Deserialize<List<string>>(supplier.QualityCertifications);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Error deserializing JSON fields for supplier {Id}", supplier.Id);
            }

            // Add contact persons
            if (supplier.Company?.UserRoles != null)
            {
                dto.Contacts = supplier.Company.UserRoles
                    .Where(ur => ur.IsActive)
                    .Select(ur => new SupplierContactDto
                    {
                        UserId = ur.UserId,
                        Name = ur.User?.Username ?? "",
                        Email = ur.User?.Email ?? "",
                        Role = ur.Role,
                        JobTitle = ur.JobTitle,
                        CanSignContracts = ur.CanSignContracts
                    }).ToList();
            }

            return dto;
        }
    }

    // DTOs
    public class SupplierDto
    {
        public int Id { get; set; }
        public int CompanyId { get; set; }
        public string CompanyName { get; set; } = "";
        public string Country { get; set; } = "";
        public string? BrandNames { get; set; }
        public bool HasKosherCertification { get; set; }
        public bool HasHalalCertification { get; set; }
        public bool HasOrganicCertification { get; set; }
        public bool OffersPrivateLabel { get; set; }
        public bool OffersCustomPackaging { get; set; }
        public bool CanShipDirect { get; set; }
        public string? Incoterms { get; set; }
        public string? PaymentTerms { get; set; }
        public bool IsActive { get; set; }
        public bool IsVerified { get; set; }
    }

    public class SupplierDetailDto : SupplierDto
    {
        public string? CompanyEmail { get; set; }
        public string? CompanyPhone { get; set; }
        public string? CompanyWebsite { get; set; }
        public string? ProductCatalogUrl { get; set; }
        public string? ManufacturingCapacity { get; set; }
        public decimal? MinOrderQuantity { get; set; }
        public string? MinOrderUnit { get; set; }
        public string? LeadTime { get; set; }
        public string? PortOfLoading { get; set; }
        public string? KosherCertifier { get; set; }
        public string? HalalCertifier { get; set; }
        public string? OrganicCertifier { get; set; }
        public bool OffersProductDevelopment { get; set; }
        public string? PricingCurrency { get; set; }
        public decimal? SampleCost { get; set; }
        public string? SamplePolicy { get; set; }
        public int? FactoryEmployeeCount { get; set; }
        public decimal? AnnualProductionValue { get; set; }
        public string? MainMarkets { get; set; }
        public string? CompanyProfile { get; set; }
        public string? Notes { get; set; }
        public List<string>? ProductCategories { get; set; }
        public List<string>? ProductionFacilities { get; set; }
        public List<string>? ExportCountries { get; set; }
        public List<string>? QualityCertifications { get; set; }
        public List<SupplierContactDto> Contacts { get; set; } = new();
    }

    public class SupplierContactDto
    {
        public int UserId { get; set; }
        public string Name { get; set; } = "";
        public string Email { get; set; } = "";
        public string? Role { get; set; }
        public string? JobTitle { get; set; }
        public bool CanSignContracts { get; set; }
    }

    public class CreateSupplierDto
    {
        public int CompanyId { get; set; }
        public string? BrandNames { get; set; }
        public string? ProductCatalogUrl { get; set; }
        public string? ManufacturingCapacity { get; set; }
        public decimal? MinOrderQuantity { get; set; }
        public string? MinOrderUnit { get; set; }
        public string? LeadTime { get; set; }
        public string? Incoterms { get; set; }
        public bool CanShipDirect { get; set; }
        public string? PortOfLoading { get; set; }
        public bool HasKosherCertification { get; set; }
        public string? KosherCertifier { get; set; }
        public bool HasHalalCertification { get; set; }
        public string? HalalCertifier { get; set; }
        public bool HasOrganicCertification { get; set; }
        public string? OrganicCertifier { get; set; }
        public bool OffersPrivateLabel { get; set; }
        public bool OffersCustomPackaging { get; set; }
        public bool OffersProductDevelopment { get; set; }
        public string? PaymentTerms { get; set; }
        public string? PricingCurrency { get; set; }
        public decimal? SampleCost { get; set; }
        public string? SamplePolicy { get; set; }
        public int? FactoryEmployeeCount { get; set; }
        public decimal? AnnualProductionValue { get; set; }
        public string? MainMarkets { get; set; }
        public string? CompanyProfile { get; set; }
        public string? Notes { get; set; }
        public List<string>? ProductCategories { get; set; }
        public List<string>? ProductionFacilities { get; set; }
        public List<string>? ExportCountries { get; set; }
        public List<string>? QualityCertifications { get; set; }
    }

    public class UpdateSupplierDto
    {
        public string? BrandNames { get; set; }
        public string? ProductCatalogUrl { get; set; }
        public string? ManufacturingCapacity { get; set; }
        public decimal? MinOrderQuantity { get; set; }
        public string? MinOrderUnit { get; set; }
        public string? LeadTime { get; set; }
        public string? Incoterms { get; set; }
        public bool? CanShipDirect { get; set; }
        public string? PortOfLoading { get; set; }
        public bool? HasKosherCertification { get; set; }
        public string? KosherCertifier { get; set; }
        public bool? HasHalalCertification { get; set; }
        public string? HalalCertifier { get; set; }
        public bool? HasOrganicCertification { get; set; }
        public string? OrganicCertifier { get; set; }
        public bool? OffersPrivateLabel { get; set; }
        public bool? OffersCustomPackaging { get; set; }
        public bool? OffersProductDevelopment { get; set; }
        public string? PaymentTerms { get; set; }
        public string? PricingCurrency { get; set; }
        public decimal? SampleCost { get; set; }
        public string? SamplePolicy { get; set; }
        public int? FactoryEmployeeCount { get; set; }
        public decimal? AnnualProductionValue { get; set; }
        public string? MainMarkets { get; set; }
        public string? CompanyProfile { get; set; }
        public string? Notes { get; set; }
        public List<string>? ProductCategories { get; set; }
        public List<string>? ProductionFacilities { get; set; }
        public List<string>? ExportCountries { get; set; }
        public List<string>? QualityCertifications { get; set; }
    }
}