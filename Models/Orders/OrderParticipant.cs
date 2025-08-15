using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("OrderParticipants", Schema = "fdx")]
public class OrderParticipant
{
    [Key]
    public Guid OrderParticipantId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid OrderId { get; set; }
    
    [Required]
    [MaxLength(40)]
    public string Role { get; set; } = string.Empty;
    // import_manager/forwarder/customs_agent/insurer/warehouse
    
    public Guid? UserId { get; set; } // Internal employee
    
    public Guid? ExternalUserId { get; set; } // External user
    
    public DateTimeOffset AssignedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("OrderId")]
    public virtual Order Order { get; set; } = null!;
    
    [ForeignKey("UserId")]
    public virtual User? User { get; set; }
}