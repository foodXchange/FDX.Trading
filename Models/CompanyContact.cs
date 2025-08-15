using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class CompanyContact
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [StringLength(200)]
    public string CompanyName { get; set; } = string.Empty;
    
    [Required]
    [StringLength(200)]
    public string ContactName { get; set; } = string.Empty;
    
    [StringLength(100)]
    public string? ContactEmail { get; set; }
    
    [StringLength(50)]
    public string? ContactPhone { get; set; }
    
    [StringLength(100)]
    public string? ContactRole { get; set; }
    
    public int? UserId { get; set; }
    public bool IsActive { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation properties
    public virtual User? User { get; set; }
}