using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class ProjectConsole
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [StringLength(50)]
    public string ConsoleCode { get; set; } = string.Empty;
    
    [Required]
    [StringLength(500)]
    public string Title { get; set; } = string.Empty;
    
    public int OwnerId { get; set; }
    public int? SourceId { get; set; }
    public string? Status { get; set; }
    public string? Type { get; set; }
    public string? Priority { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    // Navigation properties
    public virtual User Owner { get; set; } = null!;
    public virtual Request? SourceRequest { get; set; }
    public virtual ICollection<WorkflowStage> WorkflowStages { get; set; } = new List<WorkflowStage>();
    public virtual ICollection<ConsoleParticipant> ConsoleParticipants { get; set; } = new List<ConsoleParticipant>();
    public virtual ICollection<ConsoleAction> ConsoleActions { get; set; } = new List<ConsoleAction>();
    public virtual ICollection<ConsoleDocument> ConsoleDocuments { get; set; } = new List<ConsoleDocument>();
}