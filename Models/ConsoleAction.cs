using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class ConsoleAction
{
    [Key]
    public int Id { get; set; }
    
    public int ConsoleId { get; set; }
    public int? StageId { get; set; }
    public int UserId { get; set; }
    public string? ActionType { get; set; }
    public string? ActionData { get; set; }
    public DateTime Timestamp { get; set; }
    
    // Navigation properties
    public virtual ProjectConsole Console { get; set; } = null!;
    public virtual WorkflowStage? Stage { get; set; }
    public virtual User User { get; set; } = null!;
}