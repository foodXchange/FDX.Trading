using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class ProductRequest
{
    [Key]
    public int Id { get; set; }
    
    public int BuyerId { get; set; }
    
    [Required]
    [StringLength(200)]
    public string Title { get; set; } = string.Empty;
    
    [StringLength(1000)]
    public string? Description { get; set; }
    
    public string? Status { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation properties
    public virtual User Buyer { get; set; } = null!;
    public virtual ICollection<ProductRequestItem> RequestItems { get; set; } = new List<ProductRequestItem>();
    public virtual ICollection<PriceProposal> Proposals { get; set; } = new List<PriceProposal>();
}