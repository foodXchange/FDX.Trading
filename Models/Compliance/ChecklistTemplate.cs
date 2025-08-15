using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("ChecklistTemplates", Schema = "fdx")]
public class ChecklistTemplate
{
    [Key]
    public Guid ChecklistTemplateId { get; set; }
    
    [Required]
    public Guid StepTemplateId { get; set; }
    
    [Required]
    [MaxLength(200)]
    public string Title { get; set; } = string.Empty;
    
    public bool IsActive { get; set; } = true;
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("StepTemplateId")]
    public virtual ComplianceStepTemplate? StepTemplate { get; set; }
    
    public virtual ICollection<ChecklistTemplateItem> TemplateItems { get; set; } = new List<ChecklistTemplateItem>();
}