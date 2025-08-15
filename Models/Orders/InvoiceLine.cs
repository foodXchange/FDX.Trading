using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("InvoiceLines", Schema = "fdx")]
public class InvoiceLine
{
    [Key]
    public Guid InvoiceLineId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid InvoiceId { get; set; }
    
    [Required]
    [MaxLength(20)]
    public string Kind { get; set; } = string.Empty;
    // commission/product/freight/customs/service/insurance
    
    [Required]
    [MaxLength(300)]
    public string Description { get; set; } = string.Empty;
    
    [Required]
    [Column(TypeName = "decimal(18,3)")]
    public decimal Quantity { get; set; } = 1;
    
    [Required]
    [Column(TypeName = "decimal(19,4)")]
    public decimal UnitPrice { get; set; }
    
    [DatabaseGenerated(DatabaseGeneratedOption.Computed)]
    [Column(TypeName = "decimal(19,4)")]
    public decimal Amount { get; set; }
    
    [Column(TypeName = "decimal(7,4)")]
    public decimal? TaxPct { get; set; }
    
    public Guid? ProductCategoryId { get; set; }
    
    public Guid? OrderLineId { get; set; }
    
    public Guid? ShipmentId { get; set; }
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("InvoiceId")]
    public virtual Invoice Invoice { get; set; } = null!;
    
    [ForeignKey("OrderLineId")]
    public virtual OrderLine? OrderLine { get; set; }
    
    [ForeignKey("ShipmentId")]
    public virtual Shipment? Shipment { get; set; }
}