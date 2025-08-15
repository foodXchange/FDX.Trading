using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("OrderPaymentTerms", Schema = "fdx")]
public class OrderPaymentTerm
{
    [Key]
    public Guid OrderPaymentTermId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid OrderId { get; set; }
    
    [Required]
    [MaxLength(40)]
    public string TermCode { get; set; } = string.Empty; // e.g., '30%_DEPOSIT','70%_BALANCE'
    
    [Required]
    [MaxLength(3)]
    public string Currency { get; set; } = "USD";
    
    [Required]
    [Column(TypeName = "decimal(19,4)")]
    public decimal Amount { get; set; }
    
    public DateTime? DueDate { get; set; }
    
    [Required]
    [MaxLength(20)]
    public string Status { get; set; } = "pending"; // pending/paid/overdue
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("OrderId")]
    public virtual Order Order { get; set; } = null!;
}