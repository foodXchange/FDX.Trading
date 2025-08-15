using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

[Table("MarketingLeads", Schema = "fdx")]
public class MarketingLead
{
    [Key]
    public Guid MarketingLeadId { get; set; } = Guid.NewGuid();
    
    [MaxLength(200)]
    public string? Name { get; set; }
    
    [MaxLength(200)]
    public string? Email { get; set; }
    
    [MaxLength(200)]
    public string? Company { get; set; }
    
    [MaxLength(50)]
    public string? Phone { get; set; }
    
    public string? Message { get; set; }
    
    [MaxLength(60)]
    public string? Source { get; set; }
    
    [MaxLength(100)]
    public string? IpAddress { get; set; }
    
    [MaxLength(500)]
    public string? UserAgent { get; set; }
    
    public bool IsQualified { get; set; } = false;
    
    public bool IsContacted { get; set; } = false;
    
    [MaxLength(500)]
    public string? Notes { get; set; }
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    public DateTimeOffset? ContactedAt { get; set; }
    
    public Guid? ContactedBy { get; set; }
    
    // Navigation
    [ForeignKey("ContactedBy")]
    public virtual User? ContactedByUser { get; set; }
}