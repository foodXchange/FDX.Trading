using System;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models
{
    public enum MessageType
    {
        Comment,        // Simple comment/note
        Question,       // Needs response
        Answer,         // Response to question
        Notification,   // System notification
        Request,        // Action request
        Approval,       // Approval message
        Rejection,      // Rejection message
        Update,         // Status update
        Document,       // Document shared
        Quotation,      // Price quote
        Negotiation,    // Negotiation message
        System          // System automated message
    }

    public enum MessagePriority
    {
        Low,
        Normal,
        High,
        Urgent
    }

    public enum MessageStatus
    {
        Unread,
        Read,
        Replied,
        Archived
    }

    /// <summary>
    /// Flexible message model for console communications
    /// Can be used for chat, notifications, and collaboration
    /// </summary>
    public class ConsoleMessage
    {
        public int Id { get; set; }
        
        public int ConsoleId { get; set; }
        public virtual ProjectConsole Console { get; set; } = null!;
        
        public int? StageId { get; set; }
        public virtual WorkflowStage? Stage { get; set; }
        
        // Sender information
        public int SenderId { get; set; }
        public virtual User Sender { get; set; } = null!;
        
        // Recipient information (null = broadcast to all participants)
        public int? RecipientId { get; set; }
        public virtual User? Recipient { get; set; }
        
        // Parent message for threading/replies
        public int? ParentMessageId { get; set; }
        public virtual ConsoleMessage? ParentMessage { get; set; }
        
        public MessageType MessageType { get; set; }
        public MessagePriority Priority { get; set; }
        public MessageStatus Status { get; set; }
        
        [Required]
        [MaxLength(500)]
        public string Subject { get; set; } = string.Empty;
        
        [Required]
        public string Content { get; set; } = string.Empty;
        
        // For structured data (JSON)
        public string? Metadata { get; set; }
        
        // For attachments/documents
        public string? AttachmentPath { get; set; }
        public string? AttachmentName { get; set; }
        
        // Tracking
        public DateTime CreatedAt { get; set; }
        public DateTime? ReadAt { get; set; }
        public DateTime? RepliedAt { get; set; }
        
        // For future email integration
        public bool RequiresEmail { get; set; }
        public bool EmailSent { get; set; }
        public DateTime? EmailSentAt { get; set; }
        
        // For mentions/tags (JSON array of user IDs)
        public string? MentionedUsers { get; set; }
        
        // Navigation for replies
        public virtual ICollection<ConsoleMessage> Replies { get; set; } = new List<ConsoleMessage>();
    }
}