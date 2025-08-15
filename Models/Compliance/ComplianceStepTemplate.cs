using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("ComplianceStepTemplates", Schema = "fdx")]
public class ComplianceStepTemplate
{
    [Key]
    public Guid StepTemplateId { get; set; }
    
    [Required]
    public Guid StageTemplateId { get; set; }
    
    [Required]
    [MaxLength(60)]
    public string StepCode { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(200)]
    public string Title { get; set; } = string.Empty;
    
    [MaxLength(1000)]
    public string? Description { get; set; }
    
    public bool Required { get; set; } = true;
    
    [Required]
    [MaxLength(20)]
    public string Scope { get; set; } = "line"; // contract or line
    
    [MaxLength(30)]
    public string? EvidenceType { get; set; } // file, form, checklist
    
    public int DisplayOrder { get; set; } = 0;
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    public virtual ComplianceStageTemplate StageTemplate { get; set; } = null!;
    public virtual ICollection<ComplianceStep> Steps { get; set; } = new List<ComplianceStep>();
}