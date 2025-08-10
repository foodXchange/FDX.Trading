using System;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class CompanyContact
{
    public int Id { get; set; }
    
    [Required]
    [MaxLength(200)]
    public string CompanyName { get; set; } = "";
    
    [Required]
    [MaxLength(200)]
    public string ContactName { get; set; } = "";
    
    [MaxLength(100)]
    public string? ContactEmail { get; set; }
    
    [MaxLength(50)]
    public string? ContactPhone { get; set; }
    
    [MaxLength(100)]
    public string? ContactRole { get; set; }
    
    public bool IsActive { get; set; } = true;
    
    // Admin and permission fields
    public bool IsOrganizationAdmin { get; set; } = false;
    public bool CanManageContacts { get; set; } = false;
    
    // Link to user account if exists
    public int? UserId { get; set; }
    public User? User { get; set; }
    
    // Audit fields
    public int? CreatedByUserId { get; set; }
    public int? UpdatedByUserId { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    
    public DateTime UpdatedAt { get; set; } = DateTime.Now;
}

// DTOs for API
public class CompanyContactDto
{
    public int Id { get; set; }
    public string CompanyName { get; set; } = "";
    public string ContactName { get; set; } = "";
    public string? ContactEmail { get; set; }
    public string? ContactPhone { get; set; }
    public string? ContactRole { get; set; }
    public bool IsActive { get; set; }
    public bool IsOrganizationAdmin { get; set; }
    public bool CanManageContacts { get; set; }
    public int? UserId { get; set; }
    public DateTime CreatedAt { get; set; }
}

public class CreateCompanyContactDto
{
    [Required]
    public string CompanyName { get; set; } = "";
    
    [Required]
    public string ContactName { get; set; } = "";
    
    public string? ContactEmail { get; set; }
    public string? ContactPhone { get; set; }
    public string? ContactRole { get; set; }
}

public class UpdatePermissionsDto
{
    public bool IsOrganizationAdmin { get; set; }
    public bool CanManageContacts { get; set; }
}

public class UpdateContactFullDto
{
    [Required]
    public string ContactName { get; set; } = "";
    public string? ContactRole { get; set; }
    public string? ContactEmail { get; set; }
    public string? ContactPhone { get; set; }
    public bool IsActive { get; set; }
    public bool IsOrganizationAdmin { get; set; }
    public bool CanManageContacts { get; set; }
}