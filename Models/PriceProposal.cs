using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class PriceProposal
{
    [Key]
    public int Id { get; set; }
    
    public int ProductRequestId { get; set; }
    public int SupplierId { get; set; }
    public int ProductId { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal InitialPrice { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal CurrentPrice { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? PricePerCarton { get; set; }
    
    [Required]
    [StringLength(3)]
    public string Currency { get; set; } = string.Empty;
    
    [StringLength(50)]
    public string? Unit { get; set; }
    
    [StringLength(50)]
    public string? Incoterms { get; set; }
    
    [StringLength(100)]
    public string? PaymentTerms { get; set; }
    
    [StringLength(100)]
    public string? PreferredPort { get; set; }
    
    [StringLength(1000)]
    public string? Notes { get; set; }
    
    public string? Status { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation properties
    public virtual ProductRequest ProductRequest { get; set; } = null!;
    public virtual User Supplier { get; set; } = null!;
    public virtual Product Product { get; set; } = null!;
    public virtual ICollection<PriceHistory> PriceHistories { get; set; } = new List<PriceHistory>();
}