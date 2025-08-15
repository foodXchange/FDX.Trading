using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class Product
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [StringLength(50)]
    public string ProductCode { get; set; } = string.Empty;
    
    [Required]
    [StringLength(500)]
    public string ProductName { get; set; } = string.Empty;
    
    public string? Description { get; set; }
    public string? Category { get; set; }
    public string? Brand { get; set; }
    public string? PackagingType { get; set; }
    public string? Unit { get; set; }
    public int? UnitsPerCarton { get; set; }
    
    [Column(TypeName = "decimal(18,3)")]
    public decimal? NetWeight { get; set; }
    
    [Column(TypeName = "decimal(18,3)")]
    public decimal? GrossWeight { get; set; }
    
    [Column(TypeName = "decimal(5,2)")]
    public decimal? MinTemperature { get; set; }
    
    [Column(TypeName = "decimal(5,2)")]
    public decimal? MaxTemperature { get; set; }
    
    public string? Status { get; set; }
    public bool IsKosher { get; set; }
    public bool IsOrganic { get; set; }
    public bool IsHalal { get; set; }
    public bool IsGlutenFree { get; set; }
    public bool IsVegan { get; set; }
    public bool IsPrivateLabel { get; set; }
    
    public string? ImagePath { get; set; }
    public int? SupplierId { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? UnitWholesalePrice { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? CartonWholesalePrice { get; set; }
    
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation properties
    public virtual User? Supplier { get; set; }
    public virtual ICollection<ProductRequestItem> RequestItems { get; set; } = new List<ProductRequestItem>();
    public virtual ICollection<PriceProposal> PriceProposals { get; set; } = new List<PriceProposal>();
}