using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class Request
{
    public int Id { get; set; }
    
    [Required]
    [MaxLength(50)]
    public string RequestNumber { get; set; } = "";
    
    [Required]
    [MaxLength(500)]
    public string Title { get; set; } = "";
    
    public string? Description { get; set; }
    
    [Required]
    public int BuyerId { get; set; }
    
    // Buyer Information
    [MaxLength(200)]
    public string? BuyerName { get; set; }
    
    [MaxLength(200)]
    public string? BuyerCompany { get; set; }
    
    public ProcurementRequestStatus Status { get; set; } = ProcurementRequestStatus.Draft;
    
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    
    public DateTime UpdatedAt { get; set; } = DateTime.Now;
    
    // Navigation properties
    public virtual User Buyer { get; set; } = null!;
    public virtual ICollection<RequestItem> RequestItems { get; set; } = new List<RequestItem>();
}

public class RequestItem
{
    public int Id { get; set; }
    
    [Required]
    public int RequestId { get; set; }
    
    [Required]
    [MaxLength(500)]
    public string ProductName { get; set; } = "";
    
    [Required]
    public decimal Quantity { get; set; }
    
    [Required]
    [MaxLength(20)]
    public string Unit { get; set; } = "pcs";
    
    public string? Description { get; set; }
    
    public decimal? TargetPrice { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.Now;
    
    // Navigation property
    public virtual Request Request { get; set; } = null!;
}

public enum ProcurementRequestStatus
{
    Draft = 0,
    Active = 1,
    Closed = 2
}

// DTOs for API
public class RequestDto
{
    public int Id { get; set; }
    public string RequestNumber { get; set; } = "";
    public string Title { get; set; } = "";
    public string? Description { get; set; }
    public int BuyerId { get; set; }
    public string BuyerName { get; set; } = "";
    public string? BuyerCompany { get; set; }
    public ProcurementRequestStatus Status { get; set; }
    public int ItemCount { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public List<RequestItemDto> Items { get; set; } = new();
}

public class RequestItemDto
{
    public int Id { get; set; }
    public int RequestId { get; set; }
    public string ProductName { get; set; } = "";
    public decimal Quantity { get; set; }
    public string Unit { get; set; } = "";
    public string? Description { get; set; }
    public decimal? TargetPrice { get; set; }
    public DateTime CreatedAt { get; set; }
}

public class CreateRequestDto
{
    [Required]
    public string Title { get; set; } = "";
    public string? BuyerName { get; set; }
    public string? BuyerCompany { get; set; }
    public string? Description { get; set; }
    public List<CreateRequestItemDto> Items { get; set; } = new();
}

public class CreateRequestItemDto
{
    [Required]
    public string ProductName { get; set; } = "";
    [Required]
    public decimal Quantity { get; set; }
    [Required]
    public string Unit { get; set; } = "";
    public string? Description { get; set; }
    public decimal? TargetPrice { get; set; }
}

public class UpdateRequestStatusDto
{
    [Required]
    public ProcurementRequestStatus Status { get; set; }
}