using System;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models
{
    public enum TemplateType
    {
        RFQ,                    // Request for Quote
        QuoteResponse,          // Supplier quote
        Introduction,           // First contact with supplier
        FollowUp,              // Follow up message
        Negotiation,           // Price negotiation
        Approval,              // Approval notification
        Rejection,             // Rejection notification
        OrderConfirmation,     // Order placed
        ShippingUpdate,        // Shipping status
        QualityIssue,          // Quality concern
        ComplianceRequest,     // Compliance documentation
        Custom                 // User-defined
    }

    /// <summary>
    /// Reusable message templates for common communications
    /// Supports variables like {SupplierName}, {ProductName}, etc.
    /// </summary>
    public class CommunicationTemplate
    {
        public int Id { get; set; }
        
        [Required]
        [MaxLength(100)]
        public string TemplateName { get; set; } = string.Empty;
        
        public TemplateType Type { get; set; }
        
        [Required]
        [MaxLength(200)]
        public string Subject { get; set; } = string.Empty;
        
        [Required]
        public string Body { get; set; } = string.Empty;
        
        // Variables that can be used in this template (JSON array)
        public string? AvailableVariables { get; set; }
        
        // Default values for variables (JSON object)
        public string? DefaultValues { get; set; }
        
        // Who can use this template
        public string? AllowedRoles { get; set; } // JSON array of roles
        
        // Language for multi-language support
        [MaxLength(10)]
        public string Language { get; set; } = "en";
        
        // Category for organization
        [MaxLength(50)]
        public string? Category { get; set; }
        
        public bool IsActive { get; set; }
        public bool IsSystem { get; set; } // System templates can't be edited
        
        public int? CreatedByUserId { get; set; }
        public virtual User? CreatedBy { get; set; }
        
        public DateTime CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
        
        // Usage tracking
        public int UsageCount { get; set; }
        public DateTime? LastUsedAt { get; set; }
    }
}