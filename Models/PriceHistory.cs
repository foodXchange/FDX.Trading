using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public class PriceHistory
{
    [Key]
    public int Id { get; set; }
    
    public int PriceProposalId { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal OldPrice { get; set; }
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal NewPrice { get; set; }
    
    [StringLength(500)]
    public string? ChangeReason { get; set; }
    
    [StringLength(100)]
    public string? ChangedBy { get; set; }
    
    public DateTime ChangedAt { get; set; }
    
    // Navigation properties
    public virtual PriceProposal PriceProposal { get; set; } = null!;
}