using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("CommissionRates", Schema = "fdx")]
public class CommissionRate
{
    [Key]
    public Guid RateId { get; set; } = Guid.NewGuid();
    
    [Required]
    [MaxLength(200)]
    public string Name { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(20)]
    public string Payer { get; set; } = string.Empty; // supplier/buyer
    
    [Required]
    [MaxLength(20)]
    public string Basis { get; set; } = string.Empty; // order_value/line_value/freight_value
    
    [Column(TypeName = "decimal(9,4)")]
    public decimal? RatePct { get; set; }
    
    [Column(TypeName = "decimal(19,4)")]
    public decimal? FlatAmount { get; set; }
    
    [MaxLength(3)]
    public string? Currency { get; set; }
    
    [Column(TypeName = "decimal(19,4)")]
    public decimal? MinFee { get; set; }
    
    [Column(TypeName = "decimal(19,4)")]
    public decimal? MaxFee { get; set; }
    
    // Matching dimensions (nullable = wildcard)
    public Guid? BuyerCompanyId { get; set; }
    
    public Guid? SupplierId { get; set; }
    
    public Guid? ProductCategoryId { get; set; }
    
    [MaxLength(15)]
    public string? Mode { get; set; } // sea/air/road/rail
    
    [MaxLength(2)]
    public string? OriginCountry { get; set; }
    
    [MaxLength(2)]
    public string? DestCountry { get; set; }
    
    [MaxLength(10)]
    public string? Incoterms { get; set; }
    
    [Required]
    public DateTime EffectiveFrom { get; set; } = DateTime.UtcNow;
    
    public DateTime? EffectiveTo { get; set; }
    
    public int Priority { get; set; } = 100;
    
    public bool IsActive { get; set; } = true;
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    public virtual ICollection<CommissionAccrual> Accruals { get; set; } = new List<CommissionAccrual>();
}