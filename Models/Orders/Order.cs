using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("Orders", Schema = "fdx")]
public class Order
{
    [Key]
    public Guid OrderId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid ProjectId { get; set; }
    
    [Required]
    public Guid ContractId { get; set; }
    
    public Guid? BuyerUserId { get; set; }
    
    [Required]
    public Guid SupplierId { get; set; }
    
    [Required]
    [MaxLength(60)]
    public string OrderCode { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(30)]
    public string Status { get; set; } = "draft";
    // draft/placed/confirmed/ready_to_ship/shipped/in_transit/arrived/customs_cleared/delivered/closed/cancelled
    
    [Required]
    [MaxLength(3)]
    public string Currency { get; set; } = "USD";
    
    [Required]
    [MaxLength(10)]
    public string Incoterms { get; set; } = "FOB";
    
    [MaxLength(2)]
    public string? DestinationCountry { get; set; }
    
    public DateTime? RequestedDelivery { get; set; }
    
    [Column(TypeName = "decimal(19,4)")]
    public decimal? SubtotalAmount { get; set; }
    
    [Column(TypeName = "decimal(19,4)")]
    public decimal? FreightAmount { get; set; }
    
    [Column(TypeName = "decimal(19,4)")]
    public decimal? InsuranceAmount { get; set; }
    
    [Column(TypeName = "decimal(19,4)")]
    public decimal? TaxAmount { get; set; }
    
    [Column(TypeName = "decimal(19,4)")]
    public decimal? TotalAmount { get; set; }
    
    public string? OpenComments { get; set; }
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    public virtual ICollection<OrderLine> OrderLines { get; set; } = new List<OrderLine>();
    public virtual ICollection<OrderParticipant> OrderParticipants { get; set; } = new List<OrderParticipant>();
    public virtual ICollection<Shipment> Shipments { get; set; } = new List<Shipment>();
    public virtual ICollection<OrderPaymentTerm> PaymentTerms { get; set; } = new List<OrderPaymentTerm>();
    public virtual ICollection<CommissionAccrual> CommissionAccruals { get; set; } = new List<CommissionAccrual>();
    public virtual ICollection<Invoice> Invoices { get; set; } = new List<Invoice>();
}