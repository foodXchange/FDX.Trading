using System;
using System.Collections.Generic;

namespace FDX.Trading.Models
{
    public enum MatchLevel
    {
        ExactProduct = 100,      // Has exact product in catalog
        CategoryMatch = 80,       // Supplier categories match
        BusinessType = 60,        // Business type indicates capability
        ProductFamily = 40,       // Has related products
        KeywordMatch = 20         // Keywords in name/description
    }

    public class SupplierMatch
    {
        public int SupplierId { get; set; }
        public string CompanyName { get; set; } = "";
        public string? Country { get; set; }
        public string? ContactEmail { get; set; }
        public string? ContactPhone { get; set; }
        public decimal MatchScore { get; set; }
        public decimal NormalizedScore { get; set; } // 0-100 scale
        public List<MatchReason> MatchReasons { get; set; } = new List<MatchReason>();
        public List<string> AvailableProducts { get; set; } = new List<string>();
        public string? ProductCategories { get; set; }
        public string? BusinessType { get; set; }
        public bool IsVerified { get; set; }
        public int? TotalOrders { get; set; }
        public decimal? Rating { get; set; }
        
        // Capabilities
        public bool CanManufacture { get; set; }
        public bool CanTrade { get; set; }
        public bool CanExport { get; set; }
        public string? Certifications { get; set; }
        public string? PaymentTerms { get; set; }
        public string? Incoterms { get; set; }
    }

    public class MatchReason
    {
        public MatchLevel Level { get; set; }
        public string Type { get; set; } = "";
        public string Detail { get; set; } = "";
        public decimal Score { get; set; }
        public decimal Weight { get; set; } = 1.0m;
    }

    public class ProductRequirement
    {
        public string ProductName { get; set; } = "";
        public string? Category { get; set; }
        public List<string> Keywords { get; set; } = new List<string>();
        public string? Specifications { get; set; }
        public decimal? TargetQuantity { get; set; }
        public string? Unit { get; set; }
        
        public static ProductRequirement FromBriefProduct(BriefProduct product)
        {
            var requirement = new ProductRequirement
            {
                ProductName = product.ProductName ?? "",
                Category = product.Category,
                Specifications = product.Specifications,
                TargetQuantity = product.TotalQuantity,
                Unit = product.Unit
            };
            
            // Extract keywords from product name
            requirement.ExtractKeywords();
            
            return requirement;
        }
        
        private void ExtractKeywords()
        {
            if (string.IsNullOrWhiteSpace(ProductName))
                return;
                
            var words = ProductName.ToLower()
                .Split(new[] { ' ', '-', ',', '/', '\\' }, StringSplitOptions.RemoveEmptyEntries)
                .Where(w => w.Length > 2 && !IsCommonWord(w))
                .ToList();
                
            Keywords = words;
            
            // Add category-specific keywords
            if (ProductName.ToLower().Contains("oil"))
            {
                Keywords.Add("oils");
                Keywords.Add("edible");
                
                if (ProductName.ToLower().Contains("sunflower"))
                {
                    Keywords.Add("sunflower");
                    Keywords.Add("vegetable");
                    Keywords.Add("cooking");
                }
            }
        }
        
        private bool IsCommonWord(string word)
        {
            var commonWords = new[] { "the", "and", "for", "with", "from", "this", "that" };
            return commonWords.Contains(word);
        }
    }
    
    public class SupplierMatchingOptions
    {
        public decimal MinimumScore { get; set; } = 70m; // Minimum 70% match - high confidence
        public int MaxResults { get; set; } = 50;
        public bool IncludeUnverified { get; set; } = true; // Include all suppliers initially
        public bool RequireExactMatch { get; set; } = false; // Allow category matches too
        public List<string>? PreferredCountries { get; set; }
        public List<string>? RequiredCertifications { get; set; }
    }
}