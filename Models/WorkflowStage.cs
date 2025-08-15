using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class WorkflowStage
{
    [Key]
    public int Id { get; set; }
    
    public int ConsoleId { get; set; }
    
    [Required]
    [StringLength(200)]
    public string StageName { get; set; } = string.Empty;
    
    public int StageNumber { get; set; }
    public string? Status { get; set; }
    public string? StageType { get; set; }
    public int? AssignedUserId { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    
    // Navigation properties
    public virtual ProjectConsole Console { get; set; } = null!;
    public virtual User? AssignedUser { get; set; }
}