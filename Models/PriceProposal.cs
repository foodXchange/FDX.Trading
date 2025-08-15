using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public enum ProposalStatus
{
    Draft = 0,
    SourcingStage = 1,
    PriceProposed = 2,
    PriceConfirmed = 3,
    OrderPlaced = 4,
    Rejected = 5
}

public class PriceProposal
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public int ProductRequestId { get; set; }
    
    [ForeignKey("ProductRequestId")]
    public virtual ProductRequest ProductRequest { get; set; } = null!;
    
    [Required]
    public int SupplierId { get; set; }
    
    [ForeignKey("SupplierId")]
    public virtual User Supplier { get; set; } = null!;
    
    [Required]
    public int ProductId { get; set; }
    
    [ForeignKey("ProductId")]
    public virtual Product Product { get; set; } = null!;
    
    [Required]
    [Column(TypeName = "decimal(18,2)")]
    public decimal InitialPrice { get; set; }
    
    [Required]
    [Column(TypeName = "decimal(18,2)")]
    public decimal CurrentPrice { get; set; }
    
    [Required]
    [MaxLength(3)]
    public string Currency { get; set; } = "USD";
    
    [Column(TypeName = "decimal(18,2)")]
    public decimal? PricePerCarton { get; set; }
    
    public int MinimumOrderQuantity { get; set; }
    
    [MaxLength(50)]
    public string Unit { get; set; } = "units";
    
    [Required]
    public ProposalStatus Status { get; set; } = ProposalStatus.Draft;
    
    // Terms and conditions
    [MaxLength(50)]
    public string Incoterms { get; set; } = "FOB";
    
    [MaxLength(100)]
    public string PaymentTerms { get; set; } = "";
    
    [MaxLength(100)]
    public string PreferredPort { get; set; } = "";
    
    public int LeadTimeDays { get; set; }
    
    // Logistics information
    public int? UnitsPerCarton { get; set; }
    public int? CartonsPerContainer20ft { get; set; }
    public int? CartonsPerContainer40ft { get; set; }
    public int? PalletsPerContainer20ft { get; set; }
    public int? PalletsPerContainer40ft { get; set; }
    
    [MaxLength(1000)]
    public string Notes { get; set; } = "";
    
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    public DateTime UpdatedAt { get; set; } = DateTime.Now;
    public DateTime? ConfirmedAt { get; set; }
    
    // Price history tracking
    public virtual ICollection<PriceHistory> PriceHistories { get; set; } = new List<PriceHistory>();
}

public class PriceHistory
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public int PriceProposalId { get; set; }
    
    [ForeignKey("PriceProposalId")]
    public virtual PriceProposal PriceProposal { get; set; } = null!;
    
    [Required]
    [Column(TypeName = "decimal(18,2)")]
    public decimal OldPrice { get; set; }
    
    [Required]
    [Column(TypeName = "decimal(18,2)")]
    public decimal NewPrice { get; set; }
    
    [MaxLength(500)]
    public string ChangeReason { get; set; } = "";
    
    [MaxLength(100)]
    public string ChangedBy { get; set; } = "";
    
    public DateTime ChangedAt { get; set; } = DateTime.Now;
}