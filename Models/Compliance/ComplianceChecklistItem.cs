using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("ComplianceChecklistItems", Schema = "fdx")]
public class ComplianceChecklistItem
{
    [Key]
    public Guid ItemId { get; set; }
    
    [Required]
    public Guid ChecklistId { get; set; }
    
    [MaxLength(80)]
    public string? ItemCode { get; set; }
    
    [Required]
    [MaxLength(300)]
    public string Title { get; set; } = string.Empty;
    
    public bool Required { get; set; } = true;
    
    [Required]
    [MaxLength(15)]
    public string Status { get; set; } = "open"; // open/done/na/blocked
    
    public Guid? AssignedToUserId { get; set; }
    public Guid? AssignedToExternalId { get; set; }
    
    public DateTime? DueDate { get; set; }
    
    [MaxLength(800)]
    public string? Notes { get; set; }
    
    public int SortOrder { get; set; } = 0;
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("ChecklistId")]
    public virtual ComplianceChecklist? Checklist { get; set; }
    
    public virtual ICollection<ComplianceEvidence> Evidence { get; set; } = new List<ComplianceEvidence>();
    
    // Computed properties
    [NotMapped]
    public bool IsComplete => Status == "done" || Status == "na";
    
    [NotMapped]
    public bool IsOverdue => DueDate.HasValue && DueDate.Value < DateTime.Today && !IsComplete;
    
    [NotMapped]
    public string StatusColor => Status switch
    {
        "done" => "success",
        "na" => "secondary",
        "blocked" => "danger",
        _ => "primary"
    };
}