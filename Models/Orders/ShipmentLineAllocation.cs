using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("ShipmentLineAllocations", Schema = "fdx")]
public class ShipmentLineAllocation
{
    [Key]
    public Guid AllocationId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid ShipmentId { get; set; }
    
    [Required]
    public Guid OrderLineId { get; set; }
    
    public Guid? ContainerId { get; set; }
    
    [Required]
    [Column(TypeName = "decimal(18,3)")]
    public decimal Quantity { get; set; }
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("ShipmentId")]
    public virtual Shipment Shipment { get; set; } = null!;
    
    [ForeignKey("OrderLineId")]
    public virtual OrderLine OrderLine { get; set; } = null!;
    
    [ForeignKey("ContainerId")]
    public virtual Container? Container { get; set; }
}