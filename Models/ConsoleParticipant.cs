using System;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models
{
    public enum ConsoleRole
    {
        Owner,           // Primary responsible person
        Admin,           // Full control
        KosherExpert,    // Kosher compliance validation
        GraphicsExpert,  // Packaging/graphics review
        QualityAgent,    // QA processes
        ComplianceOfficer, // Regulatory compliance
        Supplier,        // External supplier participant
        Buyer,           // Original requestor
        Agent,           // Trade agent/broker
        Observer,        // Read-only access
        Auditor         // Audit and review
    }

    public class ConsoleParticipant
    {
        public int Id { get; set; }
        
        public int ConsoleId { get; set; }
        public virtual ProjectConsole Console { get; set; } = null!;
        
        public int UserId { get; set; }
        public virtual User User { get; set; } = null!;
        
        public ConsoleRole Role { get; set; }
        
        public string? Permissions { get; set; } // JSON - specific permissions
        public string? AssignedStages { get; set; } // JSON - array of stage IDs
        
        public DateTime JoinedAt { get; set; }
        public DateTime? LastActivityAt { get; set; }
        
        public bool IsActive { get; set; }
        public bool CanEdit { get; set; }
        public bool CanApprove { get; set; }
        public bool CanReassign { get; set; }
        
        [MaxLength(500)]
        public string? Notes { get; set; } // Internal notes about this participant
    }
}