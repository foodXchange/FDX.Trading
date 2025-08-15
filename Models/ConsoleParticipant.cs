using System.ComponentModel.DataAnnotations;

namespace FDX.Trading.Models;

public class ConsoleParticipant
{
    [Key]
    public int Id { get; set; }
    
    public int ConsoleId { get; set; }
    public int UserId { get; set; }
    public string? Role { get; set; }
    public bool IsActive { get; set; }
    public DateTime JoinedAt { get; set; }
    
    // Navigation properties
    public virtual ProjectConsole Console { get; set; } = null!;
    public virtual User User { get; set; } = null!;
}