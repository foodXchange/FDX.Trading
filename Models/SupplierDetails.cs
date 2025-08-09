using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class SupplierDetails
{
    [Key]
    public int Id { get; set; }
    
    [ForeignKey("User")]
    public int UserId { get; set; }
    public virtual User User { get; set; } = null!;
    
    // Company Information
    public string? CompanyRegistrationNumber { get; set; }
    public string? TaxId { get; set; }
    public string? Description { get; set; }  // Detailed company description
    
    // Business Details
    public string? ProductCategories { get; set; }  // Comma-separated list of categories they supply
    public string? Certifications { get; set; }  // Kosher, Organic, ISO, etc.
    
    // Logistics Information
    public string? PreferredSeaPort { get; set; }
    public string? PaymentTerms { get; set; }  // Net 30, Net 60, etc.
    public string? Incoterms { get; set; }  // FOB, CIF, DDP, etc.
    public string? Currency { get; set; }  // Primary currency for transactions
    
    // Supply Capabilities
    public decimal? MinimumOrderValue { get; set; }
    public int? LeadTimeDays { get; set; }  // Average lead time in days
    public string? WarehouseLocations { get; set; }
    
    // Ratings and Performance
    public decimal? Rating { get; set; }  // Average rating from buyers
    public int? TotalOrders { get; set; }
    public int? CompletedOrders { get; set; }
    public DateTime? LastOrderDate { get; set; }
    
    // Contact Information (additional to User)
    public string? SalesContactName { get; set; }
    public string? SalesContactEmail { get; set; }
    public string? SalesContactPhone { get; set; }
    
    // Status and Dates
    public bool IsVerified { get; set; } = false;
    public DateTime? VerifiedAt { get; set; }
    public string? VerifiedBy { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime? UpdatedAt { get; set; }
    
    // Navigation Properties
    public virtual ICollection<SupplierProduct> SupplierProducts { get; set; } = new List<SupplierProduct>();
}