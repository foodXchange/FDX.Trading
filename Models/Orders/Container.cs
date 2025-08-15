using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("Containers", Schema = "fdx")]
public class Container
{
    [Key]
    public Guid ContainerId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid ShipmentId { get; set; }
    
    [Required]
    [MaxLength(50)]
    public string ContainerType { get; set; } = string.Empty; // 20GP/40HC/LCL/Pallet
    
    [MaxLength(20)]
    public string? ContainerNumber { get; set; }
    
    [MaxLength(30)]
    public string? SealNumber { get; set; }
    
    [Column(TypeName = "decimal(18,3)")]
    public decimal? GrossWeightKg { get; set; }
    
    [Column(TypeName = "decimal(18,3)")]
    public decimal? NetWeightKg { get; set; }
    
    [Column(TypeName = "decimal(18,3)")]
    public decimal? VolumeM3 { get; set; }
    
    public int? Pallets { get; set; }
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("ShipmentId")]
    public virtual Shipment Shipment { get; set; } = null!;
    
    public virtual ICollection<ShipmentLineAllocation> LineAllocations { get; set; } = new List<ShipmentLineAllocation>();
}