using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;

namespace FDX.Trading.Models.Compliance;

[Table("ComplianceChecklists", Schema = "fdx")]
public class ComplianceChecklist
{
    [Key]
    public Guid ChecklistId { get; set; }
    
    [Required]
    public Guid StepId { get; set; }
    
    [Required]
    [MaxLength(200)]
    public string Title { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(20)]
    public string Status { get; set; } = "open"; // open/in-review/done/blocked
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("StepId")]
    public virtual ComplianceStep? Step { get; set; }
    
    public virtual ICollection<ComplianceChecklistItem> Items { get; set; } = new List<ComplianceChecklistItem>();
    
    // Computed properties
    [NotMapped]
    public int RequiredItemsCount => Items?.Count(i => i.Required) ?? 0;
    
    [NotMapped]
    public int CompletedItemsCount => Items?.Count(i => i.Required && (i.Status == "done" || i.Status == "na")) ?? 0;
    
    [NotMapped]
    public int ProgressPercent => RequiredItemsCount > 0 
        ? (int)Math.Round((double)CompletedItemsCount / RequiredItemsCount * 100) 
        : 0;
    
    [NotMapped]
    public bool IsBlocked => Items?.Any(i => i.Status == "blocked") ?? false;
    
    [NotMapped]
    public bool IsComplete => RequiredItemsCount > 0 && CompletedItemsCount == RequiredItemsCount;
}