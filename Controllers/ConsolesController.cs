using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Models;
using FDX.Trading.Data;
using System.Text.Json;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ConsolesController : ControllerBase
{
    private readonly FdxTradingContext _context;
    
    public ConsolesController(FdxTradingContext context)
    {
        _context = context;
    }

    // GET: api/consoles
    [HttpGet]
    public async Task<IActionResult> GetConsoles()
    {
        var consoles = await _context.Consoles
            .Include(c => c.Owner)
            .Include(c => c.WorkflowStages)
            .OrderByDescending(c => c.CreatedAt)
            .Select(c => new ConsoleListDto
            {
                Id = c.Id,
                ConsoleCode = c.ConsoleCode,
                Title = c.Title,
                Type = c.Type,
                Priority = c.Priority,
                Status = c.Status,
                OwnerName = c.Owner.DisplayName ?? c.Owner.Username,
                CurrentStageNumber = c.CurrentStageNumber,
                TotalStages = c.WorkflowStages.Count,
                CompletedStages = c.WorkflowStages.Count(s => s.Status == StageStatus.Completed),
                CreatedAt = c.CreatedAt,
                UpdatedAt = c.UpdatedAt
            })
            .ToListAsync();

        return Ok(consoles);
    }

    // GET: api/consoles/{id}
    [HttpGet("{id}")]
    public async Task<IActionResult> GetConsole(int id)
    {
        var console = await _context.Consoles
            .Include(c => c.Owner)
            .Include(c => c.WorkflowStages)
                .ThenInclude(s => s.AssignedUser)
            .Include(c => c.ConsoleParticipants)
                .ThenInclude(p => p.User)
            .FirstOrDefaultAsync(c => c.Id == id);

        if (console == null)
            return NotFound(new { message = "Console not found" });

        var dto = new ConsoleDetailDto
        {
            Id = console.Id,
            ConsoleCode = console.ConsoleCode,
            Title = console.Title,
            Type = console.Type,
            Priority = console.Priority,
            Status = console.Status,
            SourceType = console.SourceType,
            SourceId = console.SourceId,
            OwnerId = console.OwnerId,
            OwnerName = console.Owner.DisplayName ?? console.Owner.Username,
            CurrentStageNumber = console.CurrentStageNumber,
            Metadata = console.Metadata,
            CreatedAt = console.CreatedAt,
            UpdatedAt = console.UpdatedAt,
            CompletedAt = console.CompletedAt,
            Stages = console.WorkflowStages.OrderBy(s => s.StageNumber).Select(s => new StageDto
            {
                Id = s.Id,
                StageNumber = s.StageNumber,
                StageName = s.StageName,
                StageType = s.StageType,
                Status = s.Status,
                RequiredRole = s.RequiredRole,
                AssignedUserId = s.AssignedUserId,
                AssignedUserName = s.AssignedUser != null ? (s.AssignedUser.DisplayName ?? s.AssignedUser.Username) : null,
                DueDate = s.DueDate,
                StartedAt = s.StartedAt,
                CompletedAt = s.CompletedAt,
                IsParallel = s.IsParallel,
                IsCritical = s.IsCritical,
                IsOptional = s.IsOptional,
                Description = s.Description,
                Instructions = s.Instructions,
                EstimatedMinutes = s.EstimatedMinutes,
                ActualMinutes = s.ActualMinutes
            }).ToList(),
            Participants = console.ConsoleParticipants.Select(p => new ParticipantDto
            {
                Id = p.Id,
                UserId = p.UserId,
                UserName = p.User.DisplayName ?? p.User.Username,
                CompanyName = p.User.CompanyName,
                Role = p.Role,
                IsActive = p.IsActive,
                JoinedAt = p.JoinedAt
            }).ToList()
        };

        return Ok(dto);
    }

    // PUT: api/consoles/{consoleId}/stages/{stageId}/complete
    [HttpPut("{consoleId}/stages/{stageId}/complete")]
    public async Task<IActionResult> CompleteStage(int consoleId, int stageId)
    {
        var stage = await _context.WorkflowStages
            .Include(s => s.Console)
            .FirstOrDefaultAsync(s => s.Id == stageId && s.ConsoleId == consoleId);

        if (stage == null)
            return NotFound(new { message = "Stage not found" });

        if (stage.Status == StageStatus.Completed)
            return BadRequest(new { message = "Stage already completed" });

        // Complete the stage
        stage.Status = StageStatus.Completed;
        stage.CompletedAt = DateTime.Now;
        stage.ActualMinutes = stage.StartedAt.HasValue 
            ? (int)(DateTime.Now - stage.StartedAt.Value).TotalMinutes 
            : stage.EstimatedMinutes;

        // Update console
        stage.Console.UpdatedAt = DateTime.Now;

        // Move to next stage
        var nextStage = await _context.WorkflowStages
            .Where(s => s.ConsoleId == consoleId && s.StageNumber == stage.StageNumber + 1)
            .FirstOrDefaultAsync();

        if (nextStage != null)
        {
            nextStage.Status = StageStatus.Active;
            nextStage.StartedAt = DateTime.Now;
            stage.Console.CurrentStageNumber = nextStage.StageNumber;
        }
        else
        {
            // All stages completed
            stage.Console.Status = ConsoleStatus.Completed;
            stage.Console.CompletedAt = DateTime.Now;
        }

        // Log action
        _context.ConsoleActions.Add(new ConsoleAction
        {
            ConsoleId = consoleId,
            StageId = stageId,
            UserId = 1, // TODO: Get from auth
            ActionType = ActionType.StageCompleted,
            Description = $"Completed stage: {stage.StageName}",
            Timestamp = DateTime.Now,
            IsSystemAction = false
        });

        await _context.SaveChangesAsync();

        return Ok(new { 
            success = true, 
            message = "Stage completed successfully",
            nextStageNumber = nextStage?.StageNumber
        });
    }

    // PUT: api/consoles/{consoleId}/stages/{stageId}/start
    [HttpPut("{consoleId}/stages/{stageId}/start")]
    public async Task<IActionResult> StartStage(int consoleId, int stageId)
    {
        var stage = await _context.WorkflowStages
            .FirstOrDefaultAsync(s => s.Id == stageId && s.ConsoleId == consoleId);

        if (stage == null)
            return NotFound(new { message = "Stage not found" });

        if (stage.Status != StageStatus.Pending && stage.Status != StageStatus.Active)
            return BadRequest(new { message = "Stage cannot be started" });

        stage.Status = StageStatus.InProgress;
        stage.StartedAt = DateTime.Now;

        // Log action
        _context.ConsoleActions.Add(new ConsoleAction
        {
            ConsoleId = consoleId,
            StageId = stageId,
            UserId = 1, // TODO: Get from auth
            ActionType = ActionType.StageStarted,
            Description = $"Started stage: {stage.StageName}",
            Timestamp = DateTime.Now,
            IsSystemAction = false
        });

        await _context.SaveChangesAsync();

        return Ok(new { 
            success = true, 
            message = "Stage started successfully" 
        });
    }

    // GET: api/consoles/{consoleId}/messages
    [HttpGet("{consoleId}/messages")]
    public async Task<IActionResult> GetMessages(int consoleId, [FromQuery] int? stageId = null)
    {
        var query = _context.ConsoleMessages
            .Include(m => m.Sender)
            .Include(m => m.Recipient)
            .Where(m => m.ConsoleId == consoleId);

        if (stageId.HasValue)
            query = query.Where(m => m.StageId == stageId);

        var messages = await query
            .OrderBy(m => m.CreatedAt)
            .Select(m => new MessageDto
            {
                Id = m.Id,
                ConsoleId = m.ConsoleId,
                StageId = m.StageId,
                SenderId = m.SenderId,
                SenderName = m.Sender.DisplayName ?? m.Sender.Username,
                RecipientId = m.RecipientId,
                RecipientName = m.Recipient != null ? (m.Recipient.DisplayName ?? m.Recipient.Username) : "All",
                MessageType = m.MessageType,
                Priority = m.Priority,
                Status = m.Status,
                Subject = m.Subject,
                Content = m.Content,
                CreatedAt = m.CreatedAt,
                ReadAt = m.ReadAt
            })
            .ToListAsync();

        return Ok(messages);
    }

    // POST: api/consoles/{consoleId}/messages
    [HttpPost("{consoleId}/messages")]
    public async Task<IActionResult> PostMessage(int consoleId, [FromBody] CreateMessageDto dto)
    {
        var console = await _context.Consoles.FindAsync(consoleId);
        if (console == null)
            return NotFound(new { message = "Console not found" });

        var message = new ConsoleMessage
        {
            ConsoleId = consoleId,
            StageId = dto.StageId,
            SenderId = dto.SenderId ?? 1, // TODO: Get from auth
            RecipientId = dto.RecipientId,
            MessageType = dto.MessageType ?? MessageType.Comment,
            Priority = dto.Priority ?? MessagePriority.Normal,
            Status = MessageStatus.Unread,
            Subject = dto.Subject ?? "Message",
            Content = dto.Content,
            CreatedAt = DateTime.Now,
            RequiresEmail = dto.RequiresEmail
        };

        _context.ConsoleMessages.Add(message);

        // Create notification for recipient
        if (dto.RecipientId.HasValue || dto.NotifyAll)
        {
            var participants = await _context.ConsoleParticipants
                .Where(p => p.ConsoleId == consoleId && p.IsActive)
                .ToListAsync();

            foreach (var participant in participants)
            {
                // Skip sender
                if (participant.UserId == message.SenderId)
                    continue;

                // Skip if specific recipient and not matched
                if (dto.RecipientId.HasValue && participant.UserId != dto.RecipientId)
                    continue;

                var notification = new NotificationQueue
                {
                    RecipientUserId = participant.UserId,
                    ConsoleId = consoleId,
                    MessageId = message.Id,
                    Channel = NotificationChannel.InApp,
                    Category = NotificationCategory.MessageReceived,
                    Title = $"New message in {console.ConsoleCode}",
                    Body = $"{dto.Subject}: {dto.Content.Substring(0, Math.Min(100, dto.Content.Length))}...",
                    CreatedAt = DateTime.Now,
                    ScheduledFor = DateTime.Now,
                    Priority = dto.Priority == MessagePriority.Urgent ? 0 : 1
                };

                _context.NotificationQueues.Add(notification);
            }
        }

        // Log action
        _context.ConsoleActions.Add(new ConsoleAction
        {
            ConsoleId = consoleId,
            StageId = dto.StageId,
            UserId = message.SenderId,
            ActionType = ActionType.Message,
            Description = $"Posted message: {dto.Subject}",
            Timestamp = DateTime.Now,
            IsSystemAction = false
        });

        await _context.SaveChangesAsync();

        return Ok(new
        {
            success = true,
            message = "Message posted successfully",
            messageId = message.Id
        });
    }

    // POST: api/consoles/create-from-request
    [HttpPost("create-from-request")]
    public async Task<IActionResult> CreateFromRequest([FromBody] CreateConsoleFromRequestDto dto)
    {
        // Get the request
        var request = await _context.Requests
            .Include(r => r.Buyer)
            .Include(r => r.RequestItems)
            .FirstOrDefaultAsync(r => r.Id == dto.RequestId);

        if (request == null)
            return NotFound(new { message = "Request not found" });

        // Generate console code
        var year = DateTime.Now.Year;
        var lastConsole = await _context.Consoles
            .Where(c => c.ConsoleCode.StartsWith($"CON-{year}-"))
            .OrderByDescending(c => c.ConsoleCode)
            .FirstOrDefaultAsync();

        int nextNumber = 1;
        if (lastConsole != null)
        {
            var lastNumberStr = lastConsole.ConsoleCode.Split('-').Last();
            if (int.TryParse(lastNumberStr, out int lastNumber))
                nextNumber = lastNumber + 1;
        }

        var consoleCode = $"CON-{year}-{nextNumber:D4}";

        // Create the console
        var console = new ProjectConsole
        {
            ConsoleCode = consoleCode,
            Title = $"Sourcing: {request.Title}",
            Type = ConsoleType.Procurement,
            Priority = dto.Priority ?? ConsolePriority.Medium,
            Status = ConsoleStatus.Active,
            SourceType = "Request",
            SourceId = request.Id,
            OwnerId = dto.OwnerId ?? request.BuyerId,
            CurrentStageNumber = 1,
            CreatedAt = DateTime.Now,
            UpdatedAt = DateTime.Now
        };

        // Add default workflow stages
        console.WorkflowStages.Add(new WorkflowStage
        {
            StageNumber = 1,
            StageName = "Request Analysis",
            StageType = StageType.Review,
            Status = StageStatus.Active,
            Description = "Review and understand the procurement request",
            Instructions = "Analyze the request details, items, and requirements",
            EstimatedMinutes = 30,
            IsParallel = false,
            IsCritical = true,
            IsOptional = false
        });

        console.WorkflowStages.Add(new WorkflowStage
        {
            StageNumber = 2,
            StageName = "Supplier Sourcing",
            StageType = StageType.Action,
            Status = StageStatus.Pending,
            Description = "Identify and contact potential suppliers",
            Instructions = "Search for suppliers that can fulfill the request",
            EstimatedMinutes = 120,
            IsParallel = false,
            IsCritical = true,
            IsOptional = false
        });

        console.WorkflowStages.Add(new WorkflowStage
        {
            StageNumber = 3,
            StageName = "Quote Collection",
            StageType = StageType.Action,
            Status = StageStatus.Pending,
            Description = "Collect quotes from suppliers",
            Instructions = "Send RFQs and collect price quotes",
            EstimatedMinutes = 240,
            IsParallel = true,
            IsCritical = true,
            IsOptional = false
        });

        console.WorkflowStages.Add(new WorkflowStage
        {
            StageNumber = 4,
            StageName = "Price Comparison",
            StageType = StageType.Review,
            Status = StageStatus.Pending,
            Description = "Compare and analyze quotes",
            Instructions = "Create comparison matrix and evaluate offers",
            EstimatedMinutes = 60,
            IsParallel = false,
            IsCritical = true,
            IsOptional = false
        });

        console.WorkflowStages.Add(new WorkflowStage
        {
            StageNumber = 5,
            StageName = "Supplier Selection",
            StageType = StageType.Approval,
            Status = StageStatus.Pending,
            Description = "Select winning supplier(s)",
            Instructions = "Choose the best offer and approve supplier",
            EstimatedMinutes = 30,
            IsParallel = false,
            IsCritical = true,
            IsOptional = false
        });

        console.WorkflowStages.Add(new WorkflowStage
        {
            StageNumber = 6,
            StageName = "Order Placement",
            StageType = StageType.Action,
            Status = StageStatus.Pending,
            Description = "Place order with selected supplier",
            Instructions = "Create and send purchase order",
            EstimatedMinutes = 45,
            IsParallel = false,
            IsCritical = true,
            IsOptional = false
        });

        // Add owner as participant
        console.ConsoleParticipants.Add(new ConsoleParticipant
        {
            UserId = console.OwnerId,
            Role = ConsoleRole.Owner,
            JoinedAt = DateTime.Now,
            IsActive = true,
            CanEdit = true,
            CanApprove = true,
            CanReassign = true
        });

        // Add buyer as participant if different from owner
        if (request.BuyerId != console.OwnerId)
        {
            console.ConsoleParticipants.Add(new ConsoleParticipant
            {
                UserId = request.BuyerId,
                Role = ConsoleRole.Buyer,
                JoinedAt = DateTime.Now,
                IsActive = true,
                CanEdit = false,
                CanApprove = false,
                CanReassign = false
            });
        }

        // Log the creation action
        console.ConsoleActions.Add(new ConsoleAction
        {
            UserId = console.OwnerId,
            ActionType = ActionType.StageStarted,
            Description = $"Console created from Request #{request.RequestNumber}",
            Timestamp = DateTime.Now,
            IsSystemAction = false
        });

        _context.Consoles.Add(console);
        await _context.SaveChangesAsync();

        return Ok(new
        {
            success = true,
            message = "Console created successfully",
            consoleId = console.Id,
            consoleCode = console.ConsoleCode
        });
    }
}

// DTOs
public class ConsoleListDto
{
    public int Id { get; set; }
    public string ConsoleCode { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public ConsoleType Type { get; set; }
    public ConsolePriority Priority { get; set; }
    public ConsoleStatus Status { get; set; }
    public string OwnerName { get; set; } = string.Empty;
    public int CurrentStageNumber { get; set; }
    public int TotalStages { get; set; }
    public int CompletedStages { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}

public class ConsoleDetailDto
{
    public int Id { get; set; }
    public string ConsoleCode { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public ConsoleType Type { get; set; }
    public ConsolePriority Priority { get; set; }
    public ConsoleStatus Status { get; set; }
    public string? SourceType { get; set; }
    public int? SourceId { get; set; }
    public int OwnerId { get; set; }
    public string OwnerName { get; set; } = string.Empty;
    public int CurrentStageNumber { get; set; }
    public string? Metadata { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public List<StageDto> Stages { get; set; } = new();
    public List<ParticipantDto> Participants { get; set; } = new();
}

public class StageDto
{
    public int Id { get; set; }
    public int StageNumber { get; set; }
    public string StageName { get; set; } = string.Empty;
    public StageType StageType { get; set; }
    public StageStatus Status { get; set; }
    public string? RequiredRole { get; set; }
    public int? AssignedUserId { get; set; }
    public string? AssignedUserName { get; set; }
    public DateTime? DueDate { get; set; }
    public DateTime? StartedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public bool IsParallel { get; set; }
    public bool IsCritical { get; set; }
    public bool IsOptional { get; set; }
    public string? Description { get; set; }
    public string? Instructions { get; set; }
    public int EstimatedMinutes { get; set; }
    public int? ActualMinutes { get; set; }
}

public class ParticipantDto
{
    public int Id { get; set; }
    public int UserId { get; set; }
    public string UserName { get; set; } = string.Empty;
    public string? CompanyName { get; set; }
    public ConsoleRole Role { get; set; }
    public bool IsActive { get; set; }
    public DateTime JoinedAt { get; set; }
}

public class CreateConsoleFromRequestDto
{
    public int RequestId { get; set; }
    public int? OwnerId { get; set; }
    public ConsolePriority? Priority { get; set; }
}

public class MessageDto
{
    public int Id { get; set; }
    public int ConsoleId { get; set; }
    public int? StageId { get; set; }
    public int SenderId { get; set; }
    public string SenderName { get; set; } = string.Empty;
    public int? RecipientId { get; set; }
    public string RecipientName { get; set; } = string.Empty;
    public MessageType MessageType { get; set; }
    public MessagePriority Priority { get; set; }
    public MessageStatus Status { get; set; }
    public string Subject { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime? ReadAt { get; set; }
}

public class CreateMessageDto
{
    public int? StageId { get; set; }
    public int? SenderId { get; set; }
    public int? RecipientId { get; set; }
    public bool NotifyAll { get; set; }
    public MessageType? MessageType { get; set; }
    public MessagePriority? Priority { get; set; }
    public string Subject { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public bool RequiresEmail { get; set; }
}