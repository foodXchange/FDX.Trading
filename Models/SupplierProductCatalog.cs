using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

// Represents products that suppliers can provide in their catalog
public class SupplierProductCatalog
{
    public int Id { get; set; }
    
    [Required]
    public int SupplierId { get; set; }
    
    [Required]
    [MaxLength(500)]
    public string ProductName { get; set; } = "";
    
    [MaxLength(200)]
    public string? ProductCode { get; set; }
    
    [MaxLength(200)]
    public string? Category { get; set; }
    
    [MaxLength(200)]
    public string? SubCategory { get; set; }
    
    [MaxLength(500)]
    public string? Brand { get; set; }
    
    // Product specifications
    public string? Description { get; set; }
    public string? Specifications { get; set; } // JSON with detailed specs
    
    // Pricing information
    public decimal? MinOrderQuantity { get; set; }
    [MaxLength(20)]
    public string? Unit { get; set; }
    public decimal? PricePerUnit { get; set; }
    [MaxLength(10)]
    public string? Currency { get; set; } = "USD";
    
    // Availability
    public bool IsAvailable { get; set; } = true;
    public int? LeadTimeDays { get; set; }
    public decimal? StockQuantity { get; set; }
    
    // Certifications
    public bool IsKosher { get; set; }
    public bool IsHalal { get; set; }
    public bool IsOrganic { get; set; }
    public bool IsGlutenFree { get; set; }
    public bool IsVegan { get; set; }
    public string? Certifications { get; set; } // JSON array of certifications
    
    // Origin and logistics
    [MaxLength(100)]
    public string? CountryOfOrigin { get; set; }
    [MaxLength(50)]
    public string? Incoterms { get; set; }
    
    // Quality metrics
    public decimal? QualityScore { get; set; } // 0-100
    public int? CustomerRating { get; set; } // 1-5 stars
    
    // Search optimization
    public string? SearchTags { get; set; } // Comma-separated tags for better matching
    
    // Image
    [MaxLength(500)]
    public string? ImageUrl { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime UpdatedAt { get; set; } = DateTime.Now;
    
    // Navigation properties
    public virtual User Supplier { get; set; } = null!;
    public virtual ICollection<SupplierProductCatalogMatch> ProductMatches { get; set; } = new List<SupplierProductCatalogMatch>();
}

// Tracks matches between supplier catalog products and brief products
public class SupplierProductCatalogMatch
{
    public int Id { get; set; }
    
    public int SupplierProductCatalogId { get; set; }
    public int BriefProductId { get; set; }
    
    public decimal MatchScore { get; set; } // 0-100
    public string? MatchReason { get; set; } // JSON with match details
    
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    
    public virtual SupplierProductCatalog SupplierProductCatalog { get; set; } = null!;
    public virtual BriefProduct BriefProduct { get; set; } = null!;
}

// DTO for supplier product catalog
public class SupplierProductDto
{
    public int Id { get; set; }
    public int SupplierId { get; set; }
    public string SupplierName { get; set; } = "";
    public string ProductName { get; set; } = "";
    public string? ProductCode { get; set; }
    public string? Category { get; set; }
    public string? SubCategory { get; set; }
    public string? Brand { get; set; }
    public string? Description { get; set; }
    public decimal? MinOrderQuantity { get; set; }
    public string? Unit { get; set; }
    public decimal? PricePerUnit { get; set; }
    public string? Currency { get; set; }
    public bool IsAvailable { get; set; }
    public int? LeadTimeDays { get; set; }
    public string? CountryOfOrigin { get; set; }
    public List<string> Certifications { get; set; } = new();
    public decimal? QualityScore { get; set; }
}