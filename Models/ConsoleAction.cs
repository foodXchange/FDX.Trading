using System;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models
{
    public enum ActionType
    {
        // Stage actions
        StageStarted,
        StageCompleted,
        StageFailed,
        StageSkipped,
        StageReassigned,
        
        // Approval actions
        Approved,
        Rejected,
        RequestedChanges,
        ConditionalApproval,
        
        // Communication
        Comment,
        Message,
        Note,
        
        // Document actions
        DocumentUploaded,
        DocumentReviewed,
        DocumentApproved,
        DocumentRejected,
        
        // Status changes
        StatusChanged,
        PriorityChanged,
        DueDateChanged,
        
        // Participant actions
        ParticipantAdded,
        ParticipantRemoved,
        RoleChanged,
        
        // Quality/Compliance
        QualityCheckPassed,
        QualityCheckFailed,
        ComplianceVerified,
        ComplianceIssue,
        
        // System actions
        AutomatedAction,
        SystemNotification,
        ReminderSent
    }

    public class ConsoleAction
    {
        public int Id { get; set; }
        
        public int ConsoleId { get; set; }
        public virtual ProjectConsole Console { get; set; } = null!;
        
        public int? StageId { get; set; }
        public virtual WorkflowStage? Stage { get; set; }
        
        public int UserId { get; set; }
        public virtual User User { get; set; } = null!;
        
        public ActionType ActionType { get; set; }
        
        public string? ActionData { get; set; } // JSON - detailed action data
        
        [MaxLength(2000)]
        public string? Description { get; set; }
        
        public DateTime Timestamp { get; set; }
        
        [MaxLength(50)]
        public string? IPAddress { get; set; }
        
        public bool IsSystemAction { get; set; } // True if automated/system generated
    }
}