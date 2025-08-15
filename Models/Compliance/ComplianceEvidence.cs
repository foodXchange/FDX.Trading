using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("ComplianceEvidence", Schema = "fdx")]
public class ComplianceEvidence
{
    [Key]
    public Guid EvidenceId { get; set; }
    
    [Required]
    public Guid StepId { get; set; }
    
    [Required]
    [MaxLength(800)]
    public string BlobUri { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(300)]
    public string FileName { get; set; } = string.Empty;
    
    [MaxLength(100)]
    public string? ContentType { get; set; }
    
    public long? FileSize { get; set; }
    public Guid? UploadedBy { get; set; }
    public DateTimeOffset UploadedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? VerifiedAt { get; set; }
    public Guid? VerifiedBy { get; set; }
    
    // Link to checklist item (optional - for checklist-based evidence)
    public Guid? ChecklistItemId { get; set; }
    
    // Navigation properties
    public virtual ComplianceStep Step { get; set; } = null!;
    
    [ForeignKey("ChecklistItemId")]
    public virtual ComplianceChecklistItem? ChecklistItem { get; set; }
}