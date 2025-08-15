using System;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models
{
    public class Invitation
    {
        [Key]
        public Guid InvitationId { get; set; }

        [Required]
        [EmailAddress]
        [MaxLength(200)]
        public string Email { get; set; }

        [Required]
        [MaxLength(200)]
        public string Name { get; set; }

        [Required]
        [MaxLength(50)]
        public string Role { get; set; } // Admin, Buyer, Supplier, Expert

        [Required]
        [MaxLength(100)]
        public string Token { get; set; }

        [Required]
        [MaxLength(20)]
        public string Status { get; set; } // pending, accepted, expired, cancelled

        public Guid InvitedByUserId { get; set; }

        [MaxLength(200)]
        public string InvitedByName { get; set; }

        public DateTimeOffset CreatedAt { get; set; }

        public DateTimeOffset ExpiresAt { get; set; }

        public DateTimeOffset? AcceptedAt { get; set; }

        public Guid? AcceptedByUserId { get; set; }

        public DateTimeOffset? CancelledAt { get; set; }

        public int? ResendCount { get; set; }

        public DateTimeOffset? LastResentAt { get; set; }

        [MaxLength(500)]
        public string Notes { get; set; }

        // Navigation properties
        public virtual User InvitedByUser { get; set; }
        public virtual User AcceptedByUser { get; set; }
    }
}