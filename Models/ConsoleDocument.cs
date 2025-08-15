using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class ConsoleDocument
{
    [Key]
    public int Id { get; set; }
    
    public int ConsoleId { get; set; }
    public int? StageId { get; set; }
    
    [Required]
    [StringLength(500)]
    public string FileName { get; set; } = string.Empty;
    
    public string? DocumentType { get; set; }
    public string? FilePath { get; set; }
    public long FileSize { get; set; }
    public int UploadedByUserId { get; set; }
    public DateTime UploadedAt { get; set; }
    
    // Navigation properties
    public virtual ProjectConsole Console { get; set; } = null!;
    public virtual WorkflowStage? Stage { get; set; }
    public virtual User UploadedBy { get; set; } = null!;
}