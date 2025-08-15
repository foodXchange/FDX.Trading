using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("CommissionAccruals", Schema = "fdx")]
public class CommissionAccrual
{
    [Key]
    public Guid AccrualId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid OrderId { get; set; }
    
    [Required]
    public Guid ShipmentId { get; set; }
    
    public Guid? OrderLineId { get; set; }
    
    [Required]
    public Guid RateId { get; set; }
    
    [Required]
    [MaxLength(20)]
    public string Basis { get; set; } = string.Empty;
    
    [Required]
    [Column(TypeName = "decimal(19,4)")]
    public decimal BaseAmount { get; set; }
    
    [Required]
    [MaxLength(3)]
    public string Currency { get; set; } = "USD";
    
    [Required]
    [Column(TypeName = "decimal(19,4)")]
    public decimal CalculatedAmount { get; set; }
    
    [Required]
    [MaxLength(20)]
    public string Status { get; set; } = "accrued"; // accrued/invoiced/cancelled
    
    public DateTimeOffset AccruedAt { get; set; } = DateTimeOffset.UtcNow;
    
    public Guid? InvoiceId { get; set; }
    
    // Navigation properties
    [ForeignKey("OrderId")]
    public virtual Order Order { get; set; } = null!;
    
    [ForeignKey("ShipmentId")]
    public virtual Shipment Shipment { get; set; } = null!;
    
    [ForeignKey("OrderLineId")]
    public virtual OrderLine? OrderLine { get; set; }
    
    [ForeignKey("RateId")]
    public virtual CommissionRate Rate { get; set; } = null!;
    
    [ForeignKey("InvoiceId")]
    public virtual Invoice? Invoice { get; set; }
}