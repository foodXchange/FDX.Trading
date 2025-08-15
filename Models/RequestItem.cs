using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class RequestItem
{
    [Key]
    public int Id { get; set; }
    
    public int RequestId { get; set; }
    
    [Required]
    [StringLength(200)]
    public string ProductName { get; set; } = string.Empty;
    
    [Column(TypeName = "decimal(18,3)")]
    public decimal Quantity { get; set; }
    
    [Required]
    [StringLength(20)]
    public string Unit { get; set; } = string.Empty;
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? TargetPrice { get; set; }
    
    public string? ImagePath { get; set; }
    public DateTime CreatedAt { get; set; }
    
    // Navigation properties
    public virtual Request Request { get; set; } = null!;
}