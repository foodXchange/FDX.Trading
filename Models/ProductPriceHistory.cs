using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class ProductPriceHistory
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public int ProductId { get; set; }
    
    [ForeignKey("ProductId")]
    public virtual Product Product { get; set; } = null!;
    
    public int? SupplierId { get; set; }
    
    [ForeignKey("SupplierId")]
    public virtual User? Supplier { get; set; }
    
    // Price fields
    [Column(TypeName = "decimal(18,2)")]
    public decimal? UnitPrice { get; set; }
    
    [MaxLength(3)]
    public string Currency { get; set; } = "USD";
    
    // When and Why
    [Required]
    [Column(TypeName = "date")]
    public DateTime EffectiveDate { get; set; }
    
    [MaxLength(100)]
    public string? CreatedBy { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    
    [MaxLength(500)]
    public string? ChangeReason { get; set; }
    
    // Is this the current price?
    public bool IsActive { get; set; } = true;
}