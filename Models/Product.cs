using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class Product
{
    [Key]
    public int Id { get; set; }
    
    // Product Identification
    [Required]
    [MaxLength(50)]
    public string ProductCode { get; set; } = "";  // Unique product code
    
    [Required]
    [MaxLength(500)]
    public string ProductName { get; set; } = "";
    
    // Categorization
    [MaxLength(200)]
    public string? Category { get; set; }  // Main category
    
    [MaxLength(200)]
    public string? SubCategory { get; set; }  // Sub-category or family
    
    [MaxLength(200)]
    public string? ProductFamily { get; set; }  // Product family/type
    
    // Product Details
    public string? Description { get; set; }  // Detailed product description
    
    [MaxLength(50)]
    public string? HSCode { get; set; }  // HS/Tariff code for customs
    
    [MaxLength(50)]
    public string? Barcode { get; set; }  // EAN/UPC barcode
    
    // Measurements and Packaging
    [MaxLength(20)]
    public string? UnitOfMeasure { get; set; }  // gr, kg, liter, etc.
    
    public decimal? NetWeight { get; set; }  // Net weight per unit
    public decimal? GrossWeight { get; set; }  // Gross weight per unit
    public int? UnitsPerCarton { get; set; }
    public int? CartonsPerPallet { get; set; }
    
    // Storage Requirements
    public decimal? MinTemperature { get; set; }  // Minimum storage temperature
    public decimal? MaxTemperature { get; set; }  // Maximum storage temperature
    public int? ShelfLifeDays { get; set; }  // Shelf life in days
    public string? StorageConditions { get; set; }  // Special storage requirements
    
    // Certifications
    public bool IsKosher { get; set; } = false;
    public string? KosherCertificate { get; set; }  // Certificate details
    public bool IsOrganic { get; set; } = false;
    public string? OrganicCertificate { get; set; }
    public bool IsVegan { get; set; } = false;
    public bool IsGlutenFree { get; set; } = false;
    public string? OtherCertifications { get; set; }  // Additional certifications
    
    // Images and Media
    [MaxLength(500)]
    public string? ProductImage { get; set; }  // Main product image URL
    
    [MaxLength(500)]
    public string? LabelImage { get; set; }  // Private label image URL
    
    public string? AdditionalImages { get; set; }  // JSON array of additional image URLs
    
    // Origin and Manufacturing
    [MaxLength(100)]
    public string? CountryOfOrigin { get; set; }
    
    [MaxLength(200)]
    public string? Manufacturer { get; set; }
    
    [MaxLength(200)]
    public string? Brand { get; set; }
    
    // Status and Metadata
    public ProductStatus Status { get; set; } = ProductStatus.Active;
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime? UpdatedAt { get; set; }
    public string? CreatedBy { get; set; }
    public string? UpdatedBy { get; set; }
    
    // Import tracking
    public string? OriginalProductId { get; set; }  // Original ID from CSV
    public DateTime? ImportedAt { get; set; }
    public string? ImportNotes { get; set; }
    
    // Supplier relationship (one supplier per product)
    public int? SupplierId { get; set; }
    
    [ForeignKey("SupplierId")]
    public virtual User? Supplier { get; set; }
    
    // Supplier-specific pricing and terms
    [Column(TypeName = "decimal(18,2)")]
    public decimal? UnitWholesalePrice { get; set; }  // Price per unit
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? CartonWholesalePrice { get; set; }  // Price per carton
    
    [MaxLength(10)]
    public string? Currency { get; set; } = "USD";  // Currency for prices
    
    [MaxLength(50)]
    public string? Incoterms { get; set; }  // FOB, CIF, DDP, etc.
    
    [MaxLength(100)]
    public string? PaymentTerms { get; set; }  // Net 30, Net 60, etc.
    
    public int? MOQ { get; set; }  // Minimum Order Quantity in units
    public int? MOQCartons { get; set; }  // MOQ in cartons
    
    // Container and logistics info
    public int? CartonsPerContainer20ft { get; set; }
    public int? CartonsPerContainer40ft { get; set; }
    public int? PalletsPerContainer20ft { get; set; }
    public int? PalletsPerContainer40ft { get; set; }
    
    [MaxLength(200)]
    public string? PreferredPort { get; set; }  // Preferred shipping port
    
    public int? LeadTimeDays { get; set; }  // Lead time for delivery
    
    // Supplier's product code
    [MaxLength(100)]
    public string? SupplierProductCode { get; set; }
    
    // Buyer reference (who initially requested this product)
    public int? InitialBuyerId { get; set; }
    
    [ForeignKey("InitialBuyerId")]
    public virtual User? InitialBuyer { get; set; }
    
    [MaxLength(100)]
    public string? BuyerCompany { get; set; }
    
    [MaxLength(50)]
    public string? BuyerProductCode { get; set; }
    
    // Additional fields from CSV
    [MaxLength(500)]
    public string? ProductImages { get; set; }
    
    [MaxLength(500)]
    public string? OpenComments { get; set; }
    
    // Navigation Properties
    public virtual ICollection<ProductRequestItem> RequestItems { get; set; } = new List<ProductRequestItem>();
    public virtual ICollection<PriceProposal> PriceProposals { get; set; } = new List<PriceProposal>();
}

public enum ProductStatus
{
    Active,
    Inactive,
    Discontinued,
    OutOfStock,
    Pending
}