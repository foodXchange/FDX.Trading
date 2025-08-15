using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class User
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string Username { get; set; } = string.Empty;
    
    [Required]
    [StringLength(200)]
    public string Password { get; set; } = string.Empty;
    
    [Required]
    [StringLength(200)]
    public string Email { get; set; } = string.Empty;
    
    [StringLength(200)]
    public string? CompanyName { get; set; }
    
    [StringLength(100)]
    public string? Country { get; set; }
    
    [StringLength(50)]
    public string? PhoneNumber { get; set; }
    
    [StringLength(500)]
    public string? Website { get; set; }
    
    [StringLength(500)]
    public string? Address { get; set; }
    
    [StringLength(200)]
    public string? Category { get; set; }
    
    [StringLength(500)]
    public string? BusinessType { get; set; }
    
    [StringLength(2000)]
    public string? FullDescription { get; set; }
    
    [StringLength(500)]
    public string? SubCategories { get; set; }
    
    [StringLength(500)]
    public string? AlternateEmails { get; set; }
    
    [StringLength(200)]
    public string? DisplayName { get; set; }
    
    public UserType Type { get; set; }
    public bool IsActive { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? LastLogin { get; set; }
    public bool DataComplete { get; set; }
    public bool RequiresPasswordChange { get; set; }
    public VerificationStatus Verification { get; set; }
    
    // Profile fields
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string? ProfileImagePath { get; set; }
    
    // Navigation properties
    public virtual ICollection<Product> Products { get; set; } = new List<Product>();
}

public enum UserType
{
    Admin,
    Buyer,
    Supplier,
    Expert,
    Agent
}

public enum VerificationStatus
{
    Pending,
    Verified,
    Rejected
}