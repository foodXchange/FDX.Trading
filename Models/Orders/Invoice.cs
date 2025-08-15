using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("Invoices", Schema = "fdx")]
public class Invoice
{
    [Key]
    public Guid InvoiceId { get; set; } = Guid.NewGuid();
    
    [Required]
    [MaxLength(2)]
    public string Type { get; set; } = "AR"; // AR/AP
    
    public Guid? OrderId { get; set; }
    
    public Guid? ShipmentId { get; set; }
    
    [Required]
    [MaxLength(20)]
    public string CounterpartyType { get; set; } = string.Empty; // buyer/supplier/external_org
    
    [Required]
    public Guid CounterpartyId { get; set; }
    
    [Required]
    [MaxLength(60)]
    public string InvoiceCode { get; set; } = string.Empty;
    
    [Required]
    public DateTime IssueDate { get; set; } = DateTime.UtcNow;
    
    public DateTime? DueDate { get; set; }
    
    [Required]
    [MaxLength(3)]
    public string Currency { get; set; } = "USD";
    
    [Required]
    [Column(TypeName = "decimal(19,4)")]
    public decimal Subtotal { get; set; } = 0;
    
    [Required]
    [Column(TypeName = "decimal(19,4)")]
    public decimal TaxAmount { get; set; } = 0;
    
    [DatabaseGenerated(DatabaseGeneratedOption.Computed)]
    [Column(TypeName = "decimal(19,4)")]
    public decimal Total { get; set; }
    
    [Required]
    [MaxLength(20)]
    public string Status { get; set; } = "draft"; // draft/issued/paid/cancelled
    
    [MaxLength(120)]
    public string? ExternalRef { get; set; }
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("OrderId")]
    public virtual Order? Order { get; set; }
    
    [ForeignKey("ShipmentId")]
    public virtual Shipment? Shipment { get; set; }
    
    public virtual ICollection<InvoiceLine> InvoiceLines { get; set; } = new List<InvoiceLine>();
    public virtual ICollection<Payment> Payments { get; set; } = new List<Payment>();
    public virtual ICollection<CommissionAccrual> CommissionAccruals { get; set; } = new List<CommissionAccrual>();
}