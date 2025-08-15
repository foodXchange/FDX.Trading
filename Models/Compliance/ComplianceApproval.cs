using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("ComplianceApprovals", Schema = "fdx")]
public class ComplianceApproval
{
    [Key]
    public Guid ApprovalId { get; set; }
    
    [Required]
    public Guid StepId { get; set; }
    
    [Required]
    [MaxLength(20)]
    public string Decision { get; set; } = string.Empty; // approved or rejected
    
    public Guid? DecidedBy { get; set; }
    public DateTimeOffset DecidedAt { get; set; } = DateTimeOffset.UtcNow;
    
    [MaxLength(800)]
    public string? Comment { get; set; }
    
    // Navigation properties
    public virtual ComplianceStep Step { get; set; } = null!;
}