using System.Collections.Generic;

namespace FDX.Trading.Models;

public enum VerificationStatus
{
    Unverified,
    Pending,
    Verified,
    Rejected
}

public class User
{
    public int Id { get; set; }
    public string Username { get; set; } = "";
    public string Password { get; set; } = "";
    public string Email { get; set; } = "";
    public string? Title { get; set; }
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string CompanyName { get; set; } = "";
    public UserType Type { get; set; }
    public string Country { get; set; } = "";
    public string PhoneNumber { get; set; } = "";
    public string? PhoneType { get; set; }
    public string? PhoneUsage { get; set; }
    public string? PhoneCategory { get; set; }
    public string? MainPhone { get; set; }
    public string? Extension { get; set; }
    public string Website { get; set; } = "";
    public string Address { get; set; } = "";
    public string Category { get; set; } = "";  // Keep for backward compatibility
    
    // New category fields
    public CategoryType? CategoryId { get; set; }
    public string BusinessType { get; set; } = "";  // Short business description
    public string FullDescription { get; set; } = "";  // Long description from CSV
    public string SubCategories { get; set; } = "";  // Additional categories
    
    // Profile fields
    public string? Bio { get; set; }
    public string? Department { get; set; }
    public string? Role { get; set; }
    public string? AvatarType { get; set; }
    public string? AvatarValue { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime? LastLogin { get; set; }
    public bool IsActive { get; set; } = true;
    
    // New fields for better data management
    public bool RequiresPasswordChange { get; set; } = false;
    public bool DataComplete { get; set; } = true;
    public VerificationStatus Verification { get; set; } = VerificationStatus.Pending;
    public string? AlternateEmails { get; set; }
    public string? DisplayName { get; set; }  // For Hebrew or alternative names
    public string? ProfileImage { get; set; }  // Company logo/profile image (URL or base64)
    public string? ImportNotes { get; set; }  // Track import issues
    public DateTime? ImportedAt { get; set; }
    public string? OriginalId { get; set; }  // Store original CSV ID
    
    // Link to company contact if this user is associated with a contact
    public int? ContactId { get; set; }
    
    // Navigation Properties
    public virtual ICollection<Product> Products { get; set; } = new List<Product>();  // For suppliers (Type=3)
    
    // Temporary property for import process
    [System.ComponentModel.DataAnnotations.Schema.NotMapped]
    public List<SupplierProductCatalog>? ExtractedProducts { get; set; }
    
    // Navigation property for supplier details
    public virtual SupplierDetails? SupplierDetails { get; set; }
}

public enum UserType
{
    Admin = 0,
    Expert = 1,     // Contractors/Experts - subcontractors for projects
    Buyer = 2,      // Buyers
    Supplier = 3    // Suppliers - companies that provide products
}

public class LoginRequest
{
    public string Username { get; set; } = "";
    public string Password { get; set; } = "";
}

public class UserDto
{
    public int Id { get; set; }
    public string Username { get; set; } = "";
    public string Email { get; set; } = "";
    public string? Title { get; set; }
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string CompanyName { get; set; } = "";
    public string TypeName { get; set; } = "";
    public UserType Type { get; set; }
    public string Country { get; set; } = "";
    public string PhoneNumber { get; set; } = "";
    public string? PhoneType { get; set; }
    public string? PhoneUsage { get; set; }
    public string? PhoneCategory { get; set; }
    public string? MainPhone { get; set; }
    public string? Extension { get; set; }
    public string Website { get; set; } = "";
    public string Address { get; set; } = "";
    public string Category { get; set; } = "";
    public CategoryType? CategoryId { get; set; }
    public string BusinessType { get; set; } = "";
    public string CategoryDisplayName { get; set; } = "";
    public string CategoryColor { get; set; } = "";
    public string? Bio { get; set; }
    public string? Department { get; set; }
    public string? Role { get; set; }
    public string? AvatarType { get; set; }
    public string? AvatarValue { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? LastLogin { get; set; }
    public bool IsActive { get; set; }
    public bool RequiresPasswordChange { get; set; }
    public bool DataComplete { get; set; }
    public VerificationStatus Verification { get; set; }
    public string? AlternateEmails { get; set; }
    public string? DisplayName { get; set; }
    public DateTime? ImportedAt { get; set; }
    public string? ProfileImage { get; set; }
}