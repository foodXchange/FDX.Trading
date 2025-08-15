using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("Shipments", Schema = "fdx")]
public class Shipment
{
    [Key]
    public Guid ShipmentId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid OrderId { get; set; }
    
    [Required]
    [MaxLength(60)]
    public string ShipmentCode { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(15)]
    public string Mode { get; set; } = "sea"; // sea/air/road/rail
    
    [MaxLength(120)]
    public string? TermsLocation { get; set; }
    
    [MaxLength(200)]
    public string? Carrier { get; set; }
    
    [MaxLength(200)]
    public string? VesselVoyage { get; set; }
    
    [MaxLength(60)]
    public string? AWB { get; set; } // Air Waybill
    
    [MaxLength(60)]
    public string? BL { get; set; } // Bill of Lading
    
    public DateTimeOffset? ETD { get; set; } // Estimated Time of Departure
    
    public DateTimeOffset? ETA { get; set; } // Estimated Time of Arrival
    
    public DateTimeOffset? ATD { get; set; } // Actual Time of Departure
    
    public DateTimeOffset? ATA { get; set; } // Actual Time of Arrival
    
    [Required]
    [MaxLength(30)]
    public string Status { get; set; } = "planning";
    // planning/booked/departed/in_transit/arrived/customs_cleared/delivered
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("OrderId")]
    public virtual Order Order { get; set; } = null!;
    
    public virtual ICollection<Container> Containers { get; set; } = new List<Container>();
    public virtual ICollection<ShipmentLineAllocation> LineAllocations { get; set; } = new List<ShipmentLineAllocation>();
    public virtual ICollection<ShipmentDocument> Documents { get; set; } = new List<ShipmentDocument>();
    public virtual ICollection<ShipmentMilestone> Milestones { get; set; } = new List<ShipmentMilestone>();
    public virtual ICollection<CommissionAccrual> CommissionAccruals { get; set; } = new List<CommissionAccrual>();
}