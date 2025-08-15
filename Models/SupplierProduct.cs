using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

// Existing SupplierProduct model for legacy compatibility
public class SupplierProduct
{
    [Key]
    public int Id { get; set; }
    
    [ForeignKey("SupplierDetails")]
    public int SupplierDetailsId { get; set; }
    public virtual SupplierDetails SupplierDetails { get; set; } = null!;
    
    [ForeignKey("Product")]
    public int ProductId { get; set; }
    public virtual Product Product { get; set; } = null!;
    
    // Supplier-specific product information
    public string? SupplierProductCode { get; set; }  // Supplier's own product code
    
    // Pricing information
    public decimal? UnitWholesalePrice { get; set; }
    public decimal? CartonWholesalePrice { get; set; }
    public decimal? MinimumOrderQuantity { get; set; }
    public decimal? MinimumOrderValue { get; set; }
    public decimal? DiscountPercentage { get; set; }
    public decimal? PromotionalPrice { get; set; }
    public decimal? LastPurchasePrice { get; set; }
    
    // Container and shipping details
    public int? CartonsPerContainer20ft { get; set; }
    public int? CartonsPerContainer40ft { get; set; }
    public int? PalletsPerContainer20ft { get; set; }
    public int? PalletsPerContainer40ft { get; set; }
    
    // Terms and conditions
    public string? PaymentTerms { get; set; }
    public string? ShippingPort { get; set; }
    public string? Currency { get; set; }
    public string? Incoterms { get; set; }
    
    // Additional fields
    public int? MinimumOrderCartons { get; set; }
    public int? LeadTimeDays { get; set; }
    
    // Status and dates
    public SupplierProductStatus Status { get; set; } = SupplierProductStatus.Active;
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime? UpdatedAt { get; set; }
    public DateTime? ImportedAt { get; set; }
    public string? ImportSource { get; set; }
}

public enum SupplierProductStatus
{
    Available = 0,  // Legacy compatibility
    Active = 1,
    Inactive = 2,
    Discontinued = 3,
    OutOfStock = 4
}