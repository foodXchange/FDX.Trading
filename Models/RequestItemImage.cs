using System;
using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class RequestItemImage
{
    public int Id { get; set; }
    
    [Required]
    public int RequestItemId { get; set; }
    
    [Required]
    [MaxLength(255)]
    public string FileName { get; set; } = "";
    
    [Required]
    [MaxLength(500)]
    public string FilePath { get; set; } = "";
    
    [MaxLength(100)]
    public string ContentType { get; set; } = "image/jpeg";
    
    public long FileSize { get; set; }
    
    [MaxLength(500)]
    public string? Description { get; set; }
    
    public bool IsPrimary { get; set; }
    
    public DateTime UploadedAt { get; set; } = DateTime.Now;
    
    // Navigation property
    public virtual RequestItem RequestItem { get; set; } = null!;
}