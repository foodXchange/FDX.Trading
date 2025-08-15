using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("ComplianceSteps", Schema = "fdx")]
public class ComplianceStep
{
    [Key]
    public Guid StepId { get; set; }
    
    [Required]
    public Guid StageId { get; set; }
    
    [Required]
    public Guid StepTemplateId { get; set; }
    
    [Required]
    [MaxLength(200)]
    public string Title { get; set; } = string.Empty;
    
    public bool Required { get; set; } = true;
    
    [Required]
    [MaxLength(20)]
    public string Scope { get; set; } = "line"; // contract or line
    
    public Guid? ContractLineId { get; set; }
    
    [Required]
    [MaxLength(20)]
    public string Status { get; set; } = "open"; // open/in-review/approved/rejected
    
    public Guid? AssignedToUserId { get; set; }
    public Guid? AssignedToExternalId { get; set; }
    public DateTime? DueDate { get; set; }
    public string? Notes { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    public virtual ComplianceStage Stage { get; set; } = null!;
    public virtual ComplianceStepTemplate Template { get; set; } = null!;
    public virtual ICollection<ComplianceEvidence> Evidence { get; set; } = new List<ComplianceEvidence>();
    public virtual ICollection<ComplianceApproval> Approvals { get; set; } = new List<ComplianceApproval>();
    
    // Computed properties
    [NotMapped]
    public string AssigneeName { get; set; } = "Unassigned";
    
    [NotMapped]
    public int EvidenceCount => Evidence?.Count ?? 0;
    
    [NotMapped]
    public bool CanApprove => Status == "in-review" && EvidenceCount > 0;
    
    [NotMapped]
    public string StatusColor => Status switch
    {
        "approved" => "success",
        "rejected" => "danger",
        "in-review" => "warning",
        _ => "secondary"
    };
}