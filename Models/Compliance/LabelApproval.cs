using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("LabelApprovals", Schema = "fdx")]
public class LabelApproval
{
    [Key]
    public Guid LabelApprovalId { get; set; }
    
    [Required]
    public Guid LabelProjectId { get; set; }
    
    public Guid? ApprovedBy { get; set; }
    public DateTimeOffset? ApprovedAt { get; set; }
    
    [Required]
    [MaxLength(20)]
    public string Decision { get; set; } = "pending"; // pending/approved/rejected
    
    [MaxLength(800)]
    public string? Comment { get; set; }
    
    // Navigation properties
    [ForeignKey("LabelProjectId")]
    public virtual LabelProject? LabelProject { get; set; }
}