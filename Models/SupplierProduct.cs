using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class SupplierProduct
{
    [Key]
    public int Id { get; set; }
    
    // Foreign Keys
    [ForeignKey("SupplierDetails")]
    public int SupplierDetailsId { get; set; }
    public virtual SupplierDetails SupplierDetails { get; set; } = null!;
    
    [ForeignKey("Product")]
    public int ProductId { get; set; }
    public virtual Product Product { get; set; } = null!;
    
    // Supplier-specific Product Information
    [MaxLength(100)]
    public string? SupplierProductCode { get; set; }  // Supplier's own product code
    
    [MaxLength(500)]
    public string? SupplierProductName { get; set; }  // Supplier's product name (if different)
    
    // Pricing Information
    [Column(TypeName = "decimal(18,2)")]
    public decimal? UnitWholesalePrice { get; set; }  // Price per unit
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? CartonWholesalePrice { get; set; }  // Price per carton
    
    [MaxLength(10)]
    public string Currency { get; set; } = "USD";  // Currency for prices
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? DiscountPercentage { get; set; }  // Volume discount percentage
    
    // Minimum Order Requirements
    public int? MinimumOrderQuantity { get; set; }  // MOQ in units
    public int? MinimumOrderCartons { get; set; }  // MOQ in cartons
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? MinimumOrderValue { get; set; }  // MOQ in currency value
    
    // Container and Logistics Information
    public int? UnitsPerContainer20ft { get; set; }
    public int? UnitsPerContainer40ft { get; set; }
    public int? CartonsPerContainer20ft { get; set; }
    public int? CartonsPerContainer40ft { get; set; }
    public int? PalletsPerContainer20ft { get; set; }
    public int? PalletsPerContainer40ft { get; set; }
    
    // Supply Information
    public int? LeadTimeDays { get; set; }  // Lead time for this specific product
    public int? StockQuantity { get; set; }  // Current stock available
    public DateTime? StockLastUpdated { get; set; }
    
    // Terms and Conditions
    [MaxLength(50)]
    public string? Incoterms { get; set; }  // FOB, CIF, DDP, etc.
    
    [MaxLength(100)]
    public string? PaymentTerms { get; set; }  // Net 30, Net 60, etc.
    
    [MaxLength(200)]
    public string? ShippingPort { get; set; }  // Preferred shipping port
    
    // Status and Availability
    public SupplierProductStatus Status { get; set; } = SupplierProductStatus.Available;
    public DateTime? AvailableFrom { get; set; }
    public DateTime? AvailableUntil { get; set; }
    public bool IsPromotional { get; set; } = false;
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? PromotionalPrice { get; set; }
    public DateTime? PromotionalPriceEndDate { get; set; }
    
    // Quality and Compliance
    public string? QualityGrade { get; set; }  // A, B, C grade
    public string? ComplianceNotes { get; set; }  // Any compliance or regulatory notes
    public DateTime? CertificationExpiryDate { get; set; }
    
    // Historical Data
    [Column(TypeName = "decimal(18,2)")]
    public decimal? LastPurchasePrice { get; set; }
    public DateTime? LastPurchaseDate { get; set; }
    public int? TotalUnitsSold { get; set; }
    
    // Metadata
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime? UpdatedAt { get; set; }
    public string? CreatedBy { get; set; }
    public string? UpdatedBy { get; set; }
    public string? Notes { get; set; }  // Any additional notes
    
    // Import tracking
    public DateTime? ImportedAt { get; set; }
    public string? ImportSource { get; set; }  // CSV file name or API source
}

public enum SupplierProductStatus
{
    Available,
    OutOfStock,
    Discontinued,
    Seasonal,
    PreOrder,
    Limited,
    OnHold
}