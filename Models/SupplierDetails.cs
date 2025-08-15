using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class SupplierDetails
{
    [Key]
    public int Id { get; set; }
    
    public int UserId { get; set; }
    
    [StringLength(100)]
    public string? CompanyRegistrationNumber { get; set; }
    
    [StringLength(100)]
    public string? TaxId { get; set; }
    
    [StringLength(500)]
    public string? ProductCategories { get; set; }
    
    [StringLength(500)]
    public string? Certifications { get; set; }
    
    [StringLength(200)]
    public string? PreferredSeaPort { get; set; }
    
    [StringLength(200)]
    public string? PaymentTerms { get; set; }
    
    [StringLength(100)]
    public string? Incoterms { get; set; }
    
    [StringLength(10)]
    public string? Currency { get; set; }
    
    [StringLength(500)]
    public string? WarehouseLocations { get; set; }
    
    [StringLength(200)]
    public string? SalesContactName { get; set; }
    
    [StringLength(200)]
    public string? SalesContactEmail { get; set; }
    
    [StringLength(50)]
    public string? SalesContactPhone { get; set; }
    
    [StringLength(200)]
    public string? VerifiedBy { get; set; }
    
    [Column(TypeName = "decimal(3,2)")]
    public decimal Rating { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal MinimumOrderValue { get; set; }
    
    public bool IsVerified { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    public string? LogoPath { get; set; }
    
    // Navigation properties
    public virtual User User { get; set; } = null!;
    public virtual ICollection<SupplierProduct> SupplierProducts { get; set; } = new List<SupplierProduct>();
}