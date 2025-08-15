using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;

namespace FDX.Trading.Models.Compliance;

[Table("ComplianceStages", Schema = "fdx")]
public class ComplianceStage
{
    [Key]
    public Guid StageId { get; set; }
    
    [Required]
    public Guid ComplianceId { get; set; }
    
    [Required]
    public Guid StageTemplateId { get; set; }
    
    [Required]
    [MaxLength(40)]
    public string Code { get; set; } = string.Empty; // KOSHER, QA, LABEL
    
    [Required]
    [MaxLength(20)]
    public string Status { get; set; } = "in-progress";
    
    public DateTimeOffset StartedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? ApprovedAt { get; set; }
    public Guid? ApprovedBy { get; set; }
    public DateTimeOffset? SLA_Due { get; set; }
    public int Progress { get; set; } = 0;
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    public virtual ComplianceProcess ComplianceProcess { get; set; } = null!;
    public virtual ComplianceStageTemplate Template { get; set; } = null!;
    public virtual ICollection<ComplianceStep> Steps { get; set; } = new List<ComplianceStep>();
    
    // Computed properties
    [NotMapped]
    public string Name => Template?.Name ?? Code;
    
    [NotMapped]
    public int RequiredStepsCount => Steps?.Count(s => s.Required) ?? 0;
    
    [NotMapped]
    public int ApprovedStepsCount => Steps?.Count(s => s.Required && s.Status == "approved") ?? 0;
    
    [NotMapped]
    public bool IsComplete => RequiredStepsCount > 0 && ApprovedStepsCount == RequiredStepsCount;
    
    [NotMapped]
    public string SLAStatus
    {
        get
        {
            if (SLA_Due == null) return "normal";
            var daysUntilDue = (SLA_Due.Value - DateTimeOffset.UtcNow).TotalDays;
            if (daysUntilDue < 0) return "overdue";
            if (daysUntilDue < 3) return "at-risk";
            return "on-track";
        }
    }
    
    public void UpdateProgress()
    {
        if (RequiredStepsCount > 0)
        {
            Progress = (int)((double)ApprovedStepsCount / RequiredStepsCount * 100);
        }
        UpdatedAt = DateTimeOffset.UtcNow;
    }
}