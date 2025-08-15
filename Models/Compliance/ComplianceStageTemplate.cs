using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("ComplianceStageTemplates", Schema = "fdx")]
public class ComplianceStageTemplate
{
    [Key]
    public Guid StageTemplateId { get; set; }
    
    [Required]
    [MaxLength(40)]
    public string Code { get; set; } = string.Empty; // KOSHER, QA, LABEL
    
    [Required]
    [MaxLength(100)]
    public string Name { get; set; } = string.Empty;
    
    public int DisplayOrder { get; set; } = 0;
    public bool IsActive { get; set; } = true;
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    public virtual ICollection<ComplianceStepTemplate> StepTemplates { get; set; } = new List<ComplianceStepTemplate>();
    public virtual ICollection<ComplianceStage> Stages { get; set; } = new List<ComplianceStage>();
}