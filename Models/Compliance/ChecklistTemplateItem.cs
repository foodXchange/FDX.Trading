using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("ChecklistTemplateItems", Schema = "fdx")]
public class ChecklistTemplateItem
{
    [Key]
    public Guid ChecklistTemplateItemId { get; set; }
    
    [Required]
    public Guid ChecklistTemplateId { get; set; }
    
    [Required]
    [MaxLength(80)]
    public string ItemCode { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(300)]
    public string Title { get; set; } = string.Empty;
    
    public bool Required { get; set; } = true;
    
    [MaxLength(40)]
    public string? DefaultAssigneeRole { get; set; }
    
    public int SortOrder { get; set; } = 0;
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("ChecklistTemplateId")]
    public virtual ChecklistTemplate? ChecklistTemplate { get; set; }
}