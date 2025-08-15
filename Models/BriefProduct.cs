using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class BriefProduct
{
    [Key]
    public int Id { get; set; }
    
    public int SourcingBriefId { get; set; }
    
    [Required]
    [StringLength(500)]
    public string ProductName { get; set; } = string.Empty;
    
    [Column(TypeName = "decimal(18,3)")]
    public decimal? TotalQuantity { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? TargetPrice { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? MaxPrice { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? HistoricalPrice { get; set; }
    
    public string? Category { get; set; }
    public string? Unit { get; set; }
    
    // Navigation properties
    public virtual SourcingBrief SourcingBrief { get; set; } = null!;
}