using System;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models
{
    public enum StageType
    {
        Approval,
        Review,
        Action,
        Notification,
        Validation,
        QualityCheck,
        Compliance
    }

    public enum StageStatus
    {
        Pending,
        Active,
        InProgress,
        Completed,
        Failed,
        Skipped,
        OnHold
    }

    public class WorkflowStage
    {
        public int Id { get; set; }
        
        public int ConsoleId { get; set; }
        public virtual ProjectConsole Console { get; set; } = null!;
        
        public int StageNumber { get; set; }
        
        [Required]
        [MaxLength(200)]
        public string StageName { get; set; } = string.Empty;
        
        public StageType StageType { get; set; }
        
        public StageStatus Status { get; set; }
        
        [MaxLength(100)]
        public string? RequiredRole { get; set; } // "KosherExpert", "GraphicsExpert", etc.
        
        public int? AssignedUserId { get; set; }
        public virtual User? AssignedUser { get; set; }
        
        public DateTime? DueDate { get; set; }
        public DateTime? StartedAt { get; set; }
        public DateTime? CompletedAt { get; set; }
        
        public string? ValidationRules { get; set; } // JSON for flexible validation criteria
        public string? OutputData { get; set; } // JSON for stage results/decisions
        public string? Dependencies { get; set; } // JSON array of stage IDs
        
        public bool IsParallel { get; set; } // Can run alongside other stages
        public bool IsCritical { get; set; } // Blocks progress if failed
        public bool IsOptional { get; set; } // Can be skipped
        
        [MaxLength(2000)]
        public string? Description { get; set; }
        
        [MaxLength(2000)]
        public string? Instructions { get; set; } // Instructions for the assigned user
        
        public int EstimatedMinutes { get; set; } // Estimated time to complete
        public int? ActualMinutes { get; set; } // Actual time taken
    }
}