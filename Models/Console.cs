using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models
{
    public enum ConsoleType
    {
        Procurement,
        QualityControl,
        Compliance,
        Logistics,
        Custom
    }

    public enum ConsolePriority
    {
        Critical,
        High,
        Medium,
        Low
    }

    public enum ConsoleStatus
    {
        Active,
        Paused,
        Completed,
        Cancelled
    }

    public class ProjectConsole
    {
        public int Id { get; set; }
        
        [Required]
        [MaxLength(50)]
        public string ConsoleCode { get; set; } = string.Empty;
        
        [Required]
        [MaxLength(500)]
        public string Title { get; set; } = string.Empty;
        
        public ConsoleType Type { get; set; }
        
        public ConsolePriority Priority { get; set; }
        
        public ConsoleStatus Status { get; set; }
        
        [MaxLength(50)]
        public string? SourceType { get; set; } // "Request", "Manual", "System"
        
        public int? SourceId { get; set; } // RequestId or other source ID
        
        public int OwnerId { get; set; }
        public virtual User Owner { get; set; } = null!;
        
        public int CurrentStageNumber { get; set; }
        
        public string? Metadata { get; set; } // JSON for flexible data
        
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }
        public DateTime? CompletedAt { get; set; }
        
        // Navigation properties
        public virtual ICollection<WorkflowStage> WorkflowStages { get; set; } = new List<WorkflowStage>();
        public virtual ICollection<ConsoleParticipant> ConsoleParticipants { get; set; } = new List<ConsoleParticipant>();
        public virtual ICollection<ConsoleAction> ConsoleActions { get; set; } = new List<ConsoleAction>();
        public virtual ICollection<ConsoleDocument> ConsoleDocuments { get; set; } = new List<ConsoleDocument>();
        
        // Link to Request if sourced from there
        public virtual Request? SourceRequest { get; set; }
    }
}