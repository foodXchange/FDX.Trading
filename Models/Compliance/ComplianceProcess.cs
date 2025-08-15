using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("ComplianceProcesses", Schema = "fdx")]
public class ComplianceProcess
{
    [Key]
    public Guid ComplianceId { get; set; }
    
    [Required]
    public Guid ContractId { get; set; }
    
    [Required]
    public Guid ProjectId { get; set; }
    
    [Required]
    [MaxLength(20)]
    public string Status { get; set; } = "in-progress"; // in-progress/approved/rejected/blocked
    
    public DateTimeOffset StartedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? ApprovedAt { get; set; }
    public Guid? ApprovedBy { get; set; }
    public string? OpenComments { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    public virtual ICollection<ComplianceStage> Stages { get; set; } = new List<ComplianceStage>();
    public virtual ICollection<ComplianceParticipant> Participants { get; set; } = new List<ComplianceParticipant>();
    public virtual ICollection<LabelProject> LabelProjects { get; set; } = new List<LabelProject>();
    
    // Computed properties
    [NotMapped]
    public int OverallProgress => Stages?.Count > 0 
        ? (int)(Stages.Average(s => s.Progress)) 
        : 0;
    
    [NotMapped]
    public bool IsComplete => Status == "approved";
    
    [NotMapped]
    public bool CanProceedToOrdering => IsComplete;
}