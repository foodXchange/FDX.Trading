using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Compliance;

[Table("ComplianceParticipants", Schema = "fdx")]
public class ComplianceParticipant
{
    [Key]
    public Guid ParticipantId { get; set; }
    
    [Required]
    public Guid ComplianceId { get; set; }
    
    [Required]
    [MaxLength(40)]
    public string Role { get; set; } = string.Empty; // buyer_qa_manager/buyer_kosher_mgr/supplier_qc/rabbi/qa_advisor/agency_pm
    
    public Guid? UserId { get; set; } // internal user
    public Guid? ExternalUserId { get; set; } // external user
    
    public DateTimeOffset JoinedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("ComplianceId")]
    public virtual ComplianceProcess? ComplianceProcess { get; set; }
}