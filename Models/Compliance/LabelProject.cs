using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("LabelProjects", Schema = "fdx")]
public class LabelProject
{
    [Key]
    public Guid LabelProjectId { get; set; }
    
    [Required]
    public Guid ComplianceId { get; set; }
    
    [Required]
    [MaxLength(40)]
    public string Region { get; set; } = "IL"; // EU, IL, US, etc.
    
    [Required]
    [MaxLength(20)]
    public string Status { get; set; } = "in-progress";
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    public virtual ComplianceProcess ComplianceProcess { get; set; } = null!;
    public virtual ICollection<LabelArtifact> Artifacts { get; set; } = new List<LabelArtifact>();
    public virtual ICollection<LabelApproval> Approvals { get; set; } = new List<LabelApproval>();
}