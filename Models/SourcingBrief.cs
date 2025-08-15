using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

// ============================================
// SOURCING BRIEF - INTEGRATED WITH CONSOLE
// ============================================

public class SourcingBrief
{
    public int Id { get; set; }
    
    [Required]
    [MaxLength(50)]
    public string BriefCode { get; set; } = ""; // Format: SB-2025-0001
    
    [Required]
    [MaxLength(500)]
    public string Title { get; set; } = "";
    
    public string? ExecutiveSummary { get; set; }
    
    // Link to Console System (Primary Integration)
    public int ConsoleId { get; set; }
    public virtual ProjectConsole Console { get; set; } = null!;
    
    // Ownership & Status (Synced with Console)
    public int CreatedByUserId { get; set; }
    public int? AssignedToUserId { get; set; }
    public SourcingBriefStatus Status { get; set; } = SourcingBriefStatus.Draft;
    
    // Timing
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime? PublishedAt { get; set; }
    public DateTime? ResponseDeadline { get; set; }
    public DateTime? RequiredDeliveryDate { get; set; }
    
    // Commercial Terms
    [MaxLength(50)]
    public string? PreferredIncoterms { get; set; }
    [MaxLength(100)]
    public string? PreferredPaymentTerms { get; set; }
    [MaxLength(10)]
    public string Currency { get; set; } = "USD";
    
    // Quality & Optimization
    public decimal QualityScore { get; set; } = 0;
    public decimal ResponseRate { get; set; } = 0;
    public decimal SuccessRate { get; set; } = 0;
    
    // Navigation Properties
    public virtual User CreatedBy { get; set; } = null!;
    public virtual User? AssignedTo { get; set; }
    public virtual ICollection<BriefRequest> LinkedRequests { get; set; } = new List<BriefRequest>();
    public virtual ICollection<BriefProduct> Products { get; set; } = new List<BriefProduct>();
    public virtual ICollection<BriefSupplier> TargetSuppliers { get; set; } = new List<BriefSupplier>();
    public virtual ICollection<BriefResponse> Responses { get; set; } = new List<BriefResponse>();
    public virtual ICollection<BriefDocument> Documents { get; set; } = new List<BriefDocument>();
    public virtual ICollection<BriefActivity> Activities { get; set; } = new List<BriefActivity>();
    public virtual ICollection<BriefAnalytics> Analytics { get; set; } = new List<BriefAnalytics>();
}

// Link to original buyer requests
public class BriefRequest
{
    public int Id { get; set; }
    public int SourcingBriefId { get; set; }
    public int RequestId { get; set; }
    public bool IsPrimary { get; set; } = false;
    
    public virtual SourcingBrief SourcingBrief { get; set; } = null!;
    public virtual Request Request { get; set; } = null!;
}

// Aggregated products in the brief
public class BriefProduct
{
    public int Id { get; set; }
    public int SourcingBriefId { get; set; }
    
    [Required]
    [MaxLength(500)]
    public string ProductName { get; set; } = "";
    
    [MaxLength(200)]
    public string? ProductCode { get; set; }
    
    [MaxLength(200)]
    public string? Category { get; set; }
    
    // Aggregated Requirements
    public decimal TotalQuantity { get; set; }
    [MaxLength(20)]
    public string Unit { get; set; } = "";
    public int BuyerCount { get; set; } = 1;
    
    // Specifications
    public string? Specifications { get; set; } // JSON
    public string? QualityRequirements { get; set; }
    public string? PackagingRequirements { get; set; }
    
    // Pricing
    public decimal? TargetPrice { get; set; }
    public decimal? MaxPrice { get; set; }
    public decimal? HistoricalPrice { get; set; }
    
    // References
    [MaxLength(200)]
    public string? BenchmarkBrand { get; set; }
    public string? AlternativeBrands { get; set; } // JSON array
    
    // Optimization
    public bool IsConsolidated { get; set; } = false;
    public string? ConsolidationNotes { get; set; }
    
    public virtual SourcingBrief SourcingBrief { get; set; } = null!;
    public virtual ICollection<BriefProductImage> Images { get; set; } = new List<BriefProductImage>();
}

// Images for brief products
public class BriefProductImage
{
    public int Id { get; set; }
    public int BriefProductId { get; set; }
    
    [MaxLength(255)]
    public string FileName { get; set; } = "";
    
    [MaxLength(500)]
    public string FilePath { get; set; } = "";
    
    public bool IsPrimary { get; set; } = false;
    
    public virtual BriefProduct BriefProduct { get; set; } = null!;
}

// Suppliers targeted for this brief
public class BriefSupplier
{
    public int Id { get; set; }
    public int SourcingBriefId { get; set; }
    public int SupplierId { get; set; }
    
    public SupplierSelectionReason SelectionReason { get; set; }
    public decimal MatchScore { get; set; } = 0;
    public BriefSupplierStatus Status { get; set; } = BriefSupplierStatus.Pending;
    
    public DateTime? InvitedAt { get; set; }
    public DateTime? ViewedAt { get; set; }
    public DateTime? RespondedAt { get; set; }
    
    public virtual SourcingBrief SourcingBrief { get; set; } = null!;
    public virtual User Supplier { get; set; } = null!;
}

// ============================================
// SUPPLIER RESPONSE SYSTEM
// ============================================

public class BriefResponse
{
    public int Id { get; set; }
    public int SourcingBriefId { get; set; }
    public int SupplierId { get; set; }
    
    [MaxLength(50)]
    public string ResponseCode { get; set; } = ""; // BR-2025-0001
    
    public BriefResponseStatus Status { get; set; } = BriefResponseStatus.Draft;
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime? SubmittedAt { get; set; }
    
    // Commercial Terms
    public string? ProposedTerms { get; set; }
    public DateTime? ValidUntil { get; set; }
    
    // Evaluation
    public decimal? TechnicalScore { get; set; }
    public decimal? CommercialScore { get; set; }
    public decimal? OverallScore { get; set; }
    public int? Ranking { get; set; }
    
    public virtual SourcingBrief SourcingBrief { get; set; } = null!;
    public virtual User Supplier { get; set; } = null!;
    public virtual ICollection<BriefResponseItem> Items { get; set; } = new List<BriefResponseItem>();
    public virtual ICollection<BriefResponseDocument> Documents { get; set; } = new List<BriefResponseDocument>();
}

public class BriefResponseItem
{
    public int Id { get; set; }
    public int BriefResponseId { get; set; }
    public int BriefProductId { get; set; }
    
    // Pricing
    public decimal UnitPrice { get; set; }
    public decimal? VolumeDiscount { get; set; }
    public string? PricingNotes { get; set; }
    
    // Availability
    public decimal AvailableQuantity { get; set; }
    public int LeadTimeDays { get; set; }
    
    // Compliance
    public bool MeetsSpecifications { get; set; } = true;
    public string? DeviationNotes { get; set; }
    public string? AlternativeProposal { get; set; }
    
    public virtual BriefResponse BriefResponse { get; set; } = null!;
    public virtual BriefProduct BriefProduct { get; set; } = null!;
}

// ============================================
// ANALYTICS & TRACKING
// ============================================

public class BriefActivity
{
    public int Id { get; set; }
    public int SourcingBriefId { get; set; }
    public int UserId { get; set; }
    
    public BriefActivityType ActivityType { get; set; }
    public string Description { get; set; } = "";
    public string? AdditionalData { get; set; } // JSON
    public DateTime Timestamp { get; set; } = DateTime.Now;
    
    public virtual SourcingBrief SourcingBrief { get; set; } = null!;
    public virtual User User { get; set; } = null!;
}

public class BriefAnalytics
{
    public int Id { get; set; }
    public int SourcingBriefId { get; set; }
    
    public DateTime AnalysisDate { get; set; } = DateTime.Now;
    
    // Performance Metrics
    public int TotalViews { get; set; }
    public int UniqueSupplierViews { get; set; }
    public int ResponseCount { get; set; }
    public decimal AverageResponseTime { get; set; } // Hours
    
    // Quality Metrics
    public decimal SpecificationCompleteness { get; set; } // 0-100
    public decimal RequirementClarity { get; set; } // 0-100
    public decimal VolumeAttractiveness { get; set; } // 0-100
    
    // Outcome Metrics
    public decimal? AchievedPriceReduction { get; set; } // Percentage
    public decimal? SupplierSatisfactionScore { get; set; } // 1-5
    public bool ResultedInContract { get; set; } = false;
    
    public virtual SourcingBrief SourcingBrief { get; set; } = null!;
}

// ============================================
// DOCUMENTS & ATTACHMENTS
// ============================================

public class BriefDocument
{
    public int Id { get; set; }
    public int SourcingBriefId { get; set; }
    
    [MaxLength(255)]
    public string FileName { get; set; } = "";
    
    [MaxLength(500)]
    public string FilePath { get; set; } = "";
    
    public BriefDocumentType DocumentType { get; set; }
    public DateTime UploadedAt { get; set; } = DateTime.Now;
    public int UploadedByUserId { get; set; }
    
    public virtual SourcingBrief SourcingBrief { get; set; } = null!;
    public virtual User UploadedBy { get; set; } = null!;
}

public class BriefResponseDocument
{
    public int Id { get; set; }
    public int BriefResponseId { get; set; }
    
    [MaxLength(255)]
    public string FileName { get; set; } = "";
    
    [MaxLength(500)]
    public string FilePath { get; set; } = "";
    
    public ResponseDocumentType DocumentType { get; set; }
    public DateTime UploadedAt { get; set; } = DateTime.Now;
    
    public virtual BriefResponse BriefResponse { get; set; } = null!;
}

// ============================================
// ENUMS
// ============================================

public enum SourcingBriefStatus
{
    Draft = 0,
    UnderReview = 1,
    Published = 2,
    ResponsesReceived = 3,
    UnderEvaluation = 4,
    Negotiation = 5,
    Awarded = 6,
    Cancelled = 7,
    Completed = 8
}

public enum BriefPriority
{
    Low = 0,
    Medium = 1,
    High = 2,
    Urgent = 3,
    Critical = 4
}

public enum SupplierSelectionReason
{
    CategoryMatch = 0,
    HistoricalPerformance = 1,
    GeographicMatch = 2,
    CertificationMatch = 3,
    PriceCompetitiveness = 4,
    QualityRating = 5,
    Manual = 6
}

public enum BriefSupplierStatus
{
    Pending = 0,
    Invited = 1,
    Viewed = 2,
    Responded = 3,
    Declined = 4,
    Disqualified = 5
}

public enum BriefResponseStatus
{
    Draft = 0,
    Submitted = 1,
    UnderReview = 2,
    Clarification = 3,
    Shortlisted = 4,
    Rejected = 5,
    Awarded = 6
}

public enum BriefActivityType
{
    Created = 0,
    Modified = 1,
    Published = 2,
    SupplierInvited = 3,
    SupplierViewed = 4,
    ResponseReceived = 5,
    ResponseEvaluated = 6,
    Negotiated = 7,
    Awarded = 8,
    Completed = 9,
    Cancelled = 10
}

public enum BriefDocumentType
{
    Specification = 0,
    Drawing = 1,
    Certificate = 2,
    Terms = 3,
    Other = 4
}

public enum ResponseDocumentType
{
    Quote = 0,
    ProductSheet = 1,
    Certificate = 2,
    Sample = 3,
    Terms = 4,
    Other = 5
}

// ============================================
// DTOs FOR API
// ============================================

public class SourcingBriefDto
{
    public int Id { get; set; }
    public string BriefCode { get; set; } = "";
    public string Title { get; set; } = "";
    public string? ExecutiveSummary { get; set; }
    public string Status { get; set; } = "";
    public string Priority { get; set; } = "";
    public DateTime CreatedAt { get; set; }
    public DateTime? ResponseDeadline { get; set; }
    
    // Aggregated Data
    public int LinkedRequestCount { get; set; }
    public int ProductCount { get; set; }
    public decimal TotalVolume { get; set; }
    public int TargetSupplierCount { get; set; }
    public int ResponseCount { get; set; }
    
    // Quality Metrics
    public decimal QualityScore { get; set; }
    public decimal ResponseRate { get; set; }
    
    public List<BriefProductDto> Products { get; set; } = new();
    public List<LinkedRequestDto>? LinkedRequests { get; set; }
}

public class LinkedRequestDto
{
    public int RequestId { get; set; }
    public string? RequestNumber { get; set; }
    public string? RequestTitle { get; set; }
    public bool IsPrimary { get; set; }
}

public class BriefProductDto
{
    public int Id { get; set; }
    public string ProductName { get; set; } = "";
    public string? Category { get; set; }
    public decimal TotalQuantity { get; set; }
    public string Unit { get; set; } = "";
    public int BuyerCount { get; set; }
    public decimal? TargetPrice { get; set; }
    public string? BenchmarkBrand { get; set; }
    public int ImageCount { get; set; }
    public List<BriefProductImageDto>? Images { get; set; }
}

public class BriefProductImageDto
{
    public int Id { get; set; }
    public string FileName { get; set; } = "";
    public string FilePath { get; set; } = "";
    public bool IsPrimary { get; set; }
}

public class CreateSourcingBriefDto
{
    public string Title { get; set; } = "";
    public string? ExecutiveSummary { get; set; }
    public List<int> RequestIds { get; set; } = new();
    public DateTime? ResponseDeadline { get; set; }
    public DateTime? RequiredDeliveryDate { get; set; }
    public string? PreferredIncoterms { get; set; }
    public string? PreferredPaymentTerms { get; set; }
    public BriefPriority Priority { get; set; } = BriefPriority.Medium;
}