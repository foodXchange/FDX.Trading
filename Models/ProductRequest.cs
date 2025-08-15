using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models;

public enum RequestStatus
{
    Draft = 0,
    Active = 1,
    Closed = 2,
    Cancelled = 3
}

public class ProductRequest
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public int BuyerId { get; set; }
    
    [ForeignKey("BuyerId")]
    public virtual User Buyer { get; set; } = null!;
    
    [Required]
    [MaxLength(200)]
    public string Title { get; set; } = "";
    
    [MaxLength(1000)]
    public string Description { get; set; } = "";
    
    [Required]
    public RequestStatus Status { get; set; } = RequestStatus.Draft;
    
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    
    public DateTime? ClosedAt { get; set; }
    
    public DateTime? Deadline { get; set; }
    
    // Navigation properties
    public virtual ICollection<ProductRequestItem> RequestItems { get; set; } = new List<ProductRequestItem>();
    public virtual ICollection<PriceProposal> Proposals { get; set; } = new List<PriceProposal>();
}

public class ProductRequestItem
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public int ProductRequestId { get; set; }
    
    [ForeignKey("ProductRequestId")]
    public virtual ProductRequest ProductRequest { get; set; } = null!;
    
    [Required]
    public int ProductId { get; set; }
    
    [ForeignKey("ProductId")]
    public virtual Product Product { get; set; } = null!;
    
    public int RequestedQuantity { get; set; }
    
    [MaxLength(50)]
    public string Unit { get; set; } = "units";
    
    [MaxLength(500)]
    public string SpecialRequirements { get; set; } = "";
}