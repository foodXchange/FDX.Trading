using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class Request
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [StringLength(50)]
    public string RequestNumber { get; set; } = string.Empty;
    
    [Required]
    [StringLength(200)]
    public string Title { get; set; } = string.Empty;
    
    [StringLength(2000)]
    public string? Description { get; set; }
    
    public int BuyerId { get; set; }
    public string? Status { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    public string? BuyerName { get; set; }
    public string? BuyerCompany { get; set; }
    public DateTime? CompletedAt { get; set; }
    public int? CompletedByUserId { get; set; }
    public string? CompletionNotes { get; set; }
    
    // Navigation properties
    public virtual User Buyer { get; set; } = null!;
    public virtual ICollection<RequestItem> RequestItems { get; set; } = new List<RequestItem>();
}