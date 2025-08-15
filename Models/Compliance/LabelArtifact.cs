using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("LabelArtifacts", Schema = "fdx")]
public class LabelArtifact
{
    [Key]
    public Guid LabelArtifactId { get; set; }
    
    [Required]
    public Guid LabelProjectId { get; set; }
    
    [Required]
    [MaxLength(40)]
    public string ArtifactType { get; set; } = string.Empty; // layout/ingredient_list/allergen_panel/nutrition_table/barcode/claims
    
    [Required]
    [MaxLength(800)]
    public string BlobUri { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(300)]
    public string FileName { get; set; } = string.Empty;
    
    public int Version { get; set; } = 1;
    public Guid? UploadedBy { get; set; }
    public DateTimeOffset UploadedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("LabelProjectId")]
    public virtual LabelProject? LabelProject { get; set; }
}