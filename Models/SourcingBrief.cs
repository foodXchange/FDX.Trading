using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class SourcingBrief
{
    [Key]
    public int Id { get; set; }
    
    public int ConsoleId { get; set; }
    public int CreatedByUserId { get; set; }
    
    [Required]
    [StringLength(50)]
    public string BriefCode { get; set; } = string.Empty;
    
    public string? Status { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    [Column(TypeName = "decimal(5,2)")]
    public decimal? QualityScore { get; set; }
    
    [Column(TypeName = "decimal(5,2)")]
    public decimal? ResponseRate { get; set; }
    
    [Column(TypeName = "decimal(5,2)")]
    public decimal? SuccessRate { get; set; }
    
    // Navigation properties
    public virtual ProjectConsole Console { get; set; } = null!;
    public virtual User CreatedBy { get; set; } = null!;
    public virtual ICollection<BriefProduct> Products { get; set; } = new List<BriefProduct>();
    //public virtual ICollection<BriefSupplier> TargetSuppliers { get; set; } = new List<BriefSupplier>();
    //public virtual ICollection<BriefResponse> Responses { get; set; } = new List<BriefResponse>();
}