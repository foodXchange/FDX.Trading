using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("ShipmentMilestones", Schema = "fdx")]
public class ShipmentMilestone
{
    [Key]
    public Guid MilestoneId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid ShipmentId { get; set; }
    
    [Required]
    [MaxLength(40)]
    public string Code { get; set; } = string.Empty;
    // BOOKED/ETD_CONFIRMED/DEPARTED/IN_TRANSIT/ARRIVED/CUSTOMS_CLEARED/DELIVERED
    
    [Required]
    public DateTimeOffset OccurredAt { get; set; }
    
    [MaxLength(120)]
    public string? Location { get; set; }
    
    [MaxLength(400)]
    public string? Notes { get; set; }
    
    public Guid? CreatedBy { get; set; }
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("ShipmentId")]
    public virtual Shipment Shipment { get; set; } = null!;
}