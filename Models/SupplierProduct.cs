using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class SupplierProduct
{
    [Key]
    public int Id { get; set; }
    
    public int SupplierDetailsId { get; set; }
    public int ProductId { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? UnitWholesalePrice { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? CartonWholesalePrice { get; set; }
    
    [Column(TypeName = "decimal(5,2)")]
    public decimal? DiscountPercentage { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? MinimumOrderValue { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? PromotionalPrice { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? LastPurchasePrice { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? MinimumOrderQuantity { get; set; }
    
    public string? Status { get; set; }
    public string? Currency { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation properties
    public virtual SupplierDetails SupplierDetails { get; set; } = null!;
    public virtual Product Product { get; set; } = null!;
}