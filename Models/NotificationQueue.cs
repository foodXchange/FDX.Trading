using System;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models
{
    public enum NotificationChannel
    {
        InApp,          // Show in application
        Email,          // Send email
        SMS,            // Send SMS (future)
        Push,           // Push notification (future)
        Webhook         // External webhook (future)
    }

    public enum NotificationCategory
    {
        StageUpdate,
        MessageReceived,
        ActionRequired,
        QuoteReceived,
        ApprovalNeeded,
        SystemAlert,
        Reminder,
        DeadlineApproaching,
        StatusChange,
        DocumentShared
    }

    /// <summary>
    /// Queue for async notification processing
    /// Decouples notification sending from business logic
    /// </summary>
    public class NotificationQueue
    {
        public int Id { get; set; }
        
        // Who gets notified
        public int RecipientUserId { get; set; }
        public virtual User RecipientUser { get; set; } = null!;
        
        // What triggered this
        public int? ConsoleId { get; set; }
        public virtual ProjectConsole? Console { get; set; }
        
        public int? MessageId { get; set; }
        public virtual ConsoleMessage? Message { get; set; }
        
        public NotificationChannel Channel { get; set; }
        public NotificationCategory Category { get; set; }
        
        [Required]
        [MaxLength(200)]
        public string Title { get; set; } = string.Empty;
        
        [Required]
        [MaxLength(1000)]
        public string Body { get; set; } = string.Empty;
        
        // For rich notifications (JSON)
        public string? Data { get; set; }
        
        // Processing status
        public bool IsProcessed { get; set; }
        public int RetryCount { get; set; }
        public DateTime? ProcessedAt { get; set; }
        public string? ErrorMessage { get; set; }
        
        // Scheduling
        public DateTime CreatedAt { get; set; }
        public DateTime ScheduledFor { get; set; } // Can be immediate or future
        public DateTime? ExpiresAt { get; set; } // Don't send after this time
        
        // Email specific (for when we add email)
        public string? EmailTo { get; set; }
        public string? EmailCc { get; set; }
        public string? EmailTemplate { get; set; }
        
        // Priority for processing order
        public int Priority { get; set; } // 0 = highest priority
    }
}