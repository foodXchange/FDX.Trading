using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("OrderLines", Schema = "fdx")]
public class OrderLine
{
    [Key]
    public Guid OrderLineId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid OrderId { get; set; }
    
    public Guid? ContractLineId { get; set; }
    
    public Guid? ProductId { get; set; }
    
    [Required]
    [MaxLength(300)]
    public string ProductName { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(20)]
    public string Unit { get; set; } = string.Empty;
    
    [Required]
    [Column(TypeName = "decimal(18,3)")]
    public decimal Quantity { get; set; }
    
    [Required]
    [Column(TypeName = "decimal(19,4)")]
    public decimal UnitPrice { get; set; }
    
    [Required]
    [MaxLength(3)]
    public string Currency { get; set; } = "USD";
    
    [Required]
    [MaxLength(10)]
    public string Incoterms { get; set; } = "FOB";
    
    public DateTime? RequestedDelivery { get; set; }
    
    [MaxLength(800)]
    public string? Notes { get; set; }
    
    [DatabaseGenerated(DatabaseGeneratedOption.Computed)]
    [Column(TypeName = "decimal(19,4)")]
    public decimal LineTotal { get; set; }
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("OrderId")]
    public virtual Order Order { get; set; } = null!;
    
    public virtual ICollection<ShipmentLineAllocation> ShipmentAllocations { get; set; } = new List<ShipmentLineAllocation>();
}