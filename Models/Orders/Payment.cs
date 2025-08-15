using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("Payments", Schema = "fdx")]
public class Payment
{
    [Key]
    public Guid PaymentId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid InvoiceId { get; set; }
    
    [Required]
    public DateTimeOffset PaidAt { get; set; } = DateTimeOffset.UtcNow;
    
    [Required]
    [MaxLength(3)]
    public string Currency { get; set; } = "USD";
    
    [Required]
    [Column(TypeName = "decimal(19,4)")]
    public decimal Amount { get; set; }
    
    [MaxLength(30)]
    public string? Method { get; set; } // wire/creditnote/etc.
    
    [MaxLength(120)]
    public string? Reference { get; set; }
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("InvoiceId")]
    public virtual Invoice Invoice { get; set; } = null!;
}