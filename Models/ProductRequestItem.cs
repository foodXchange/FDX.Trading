using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class ProductRequestItem
{
    [Key]
    public int Id { get; set; }
    
    public int ProductRequestId { get; set; }
    public int ProductId { get; set; }
    
    [StringLength(50)]
    public string? Unit { get; set; }
    
    [StringLength(500)]
    public string? SpecialRequirements { get; set; }
    
    public int Quantity { get; set; }
    public DateTime CreatedAt { get; set; }
    
    // Navigation properties
    public virtual ProductRequest ProductRequest { get; set; } = null!;
    public virtual Product Product { get; set; } = null!;
}