using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("KosherCertifications", Schema = "fdx")]
public class KosherCertification
{
    [Key]
    public Guid KosherCertId { get; set; }
    
    [Required]
    public Guid SupplierId { get; set; }
    
    public Guid? ProductId { get; set; }
    
    [Required]
    [MaxLength(120)]
    public string Authority { get; set; } = string.Empty; // OU, Badatz, OK, Triangle-K, etc.
    
    [MaxLength(120)]
    public string? CertificateNumber { get; set; }
    
    [MaxLength(40)]
    public string? SupervisionType { get; set; } // Pareve/Dairy/Meat
    
    public bool? HalavYisrael { get; set; }
    
    [MaxLength(40)]
    public string? PassoverStatus { get; set; } // Kosher for Passover/Kitniyot/Not for Passover
    
    public DateTime? ValidFrom { get; set; }
    public DateTime? ValidTo { get; set; }
    
    [MaxLength(800)]
    public string? Remarks { get; set; }
    
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    public virtual ICollection<KosherCertFile> Files { get; set; } = new List<KosherCertFile>();
}