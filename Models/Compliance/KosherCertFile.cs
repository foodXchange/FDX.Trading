using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("KosherCertFiles", Schema = "fdx")]
public class KosherCertFile
{
    [Key]
    public Guid KosherCertFileId { get; set; }
    
    [Required]
    public Guid KosherCertId { get; set; }
    
    [Required]
    [MaxLength(800)]
    public string BlobUri { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(300)]
    public string FileName { get; set; } = string.Empty;
    
    public DateTimeOffset UploadedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    public virtual KosherCertification KosherCertification { get; set; } = null!;
}