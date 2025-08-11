using System;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models
{
    public enum DocumentType
    {
        Contract,
        Invoice,
        Certificate,
        KosherCertificate,
        QualityReport,
        ShippingDocument,
        PackagingDesign,
        Specification,
        Correspondence,
        Other
    }

    public class ConsoleDocument
    {
        public int Id { get; set; }
        
        public int ConsoleId { get; set; }
        public virtual ProjectConsole Console { get; set; } = null!;
        
        public int? StageId { get; set; }
        public virtual WorkflowStage? Stage { get; set; }
        
        [Required]
        [MaxLength(500)]
        public string FileName { get; set; } = string.Empty;
        
        [MaxLength(500)]
        public string? FilePath { get; set; }
        
        public DocumentType DocumentType { get; set; }
        
        public long FileSize { get; set; } // in bytes
        
        [MaxLength(100)]
        public string? MimeType { get; set; }
        
        public int UploadedByUserId { get; set; }
        public virtual User UploadedBy { get; set; } = null!;
        
        public DateTime UploadedAt { get; set; }
        
        public bool IsApproved { get; set; }
        public int? ApprovedByUserId { get; set; }
        public DateTime? ApprovedAt { get; set; }
        
        [MaxLength(1000)]
        public string? Description { get; set; }
        
        [MaxLength(500)]
        public string? Tags { get; set; } // Comma-separated tags for searching
    }
}