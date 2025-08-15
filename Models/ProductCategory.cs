using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models
{
    public class ProductCategory
    {
        [Key]
        public int Id { get; set; }
        
        // Level 1 - Main Category
        [Required]
        [MaxLength(100)]
        public string Category { get; set; } = string.Empty;
        
        // Level 2 - SubCategory
        [Required]
        [MaxLength(100)]
        public string SubCategory { get; set; } = string.Empty;
        
        // Level 3 - Product Family
        [Required]
        [MaxLength(100)]
        public string Family { get; set; } = string.Empty;
        
        // Level 4 - Sub-Family (specific product types)
        [MaxLength(200)]
        public string? SubFamily { get; set; }
        
        // Product Family ID from the CSV
        [MaxLength(20)]
        public string? ProductFamilyId { get; set; }
        
        // Full path for easy searching
        [MaxLength(500)]
        public string FullPath { get; set; } = string.Empty;
        
        // Metadata
        public DateTime CreatedAt { get; set; } = DateTime.Now;
        public DateTime UpdatedAt { get; set; } = DateTime.Now;
        public string? CreatedBy { get; set; }
        public string? UpdatedBy { get; set; }
        
        // Navigation properties
        public virtual ICollection<SupplierProductCatalog> Products { get; set; } = new List<SupplierProductCatalog>();
        
        // Helper method to build the full path
        public void BuildFullPath()
        {
            var parts = new List<string> { Category, SubCategory, Family };
            if (!string.IsNullOrWhiteSpace(SubFamily))
                parts.Add(SubFamily);
            FullPath = string.Join(" > ", parts);
        }
    }
    
    // DTO for category hierarchy display
    public class CategoryHierarchyDto
    {
        public string Category { get; set; } = string.Empty;
        public List<SubCategoryDto> SubCategories { get; set; } = new List<SubCategoryDto>();
    }
    
    public class SubCategoryDto
    {
        public string Name { get; set; } = string.Empty;
        public List<FamilyDto> Families { get; set; } = new List<FamilyDto>();
    }
    
    public class FamilyDto
    {
        public string Name { get; set; } = string.Empty;
        public List<string> SubFamilies { get; set; } = new List<string>();
    }
}