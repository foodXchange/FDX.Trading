using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using System.Net.Mail;
using System.Text;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class MarketingController : ControllerBase
{
    private readonly FdxTradingContext _context;
    private readonly ILogger<MarketingController> _logger;
    private readonly IConfiguration _configuration;

    public MarketingController(FdxTradingContext context, ILogger<MarketingController> logger, IConfiguration configuration)
    {
        _context = context;
        _logger = logger;
        _configuration = configuration;
    }

    [HttpPost("leads")]
    [AllowAnonymous]
    [EnableRateLimiting("public-form")] // Rate limit to prevent spam
    public async Task<IActionResult> SubmitLead([FromBody] MarketingLeadDto dto)
    {
        try
        {
            // Basic validation
            if (string.IsNullOrWhiteSpace(dto.Email) || string.IsNullOrWhiteSpace(dto.Name))
            {
                return BadRequest(new { error = "Name and email are required" });
            }

            // Bot protection - check honeypot field
            if (!string.IsNullOrEmpty(dto.Website))
            {
                // Log potential bot submission but return success to confuse bots
                _logger.LogWarning("Potential bot submission detected from IP: {IP}", HttpContext.Connection.RemoteIpAddress);
                return Accepted();
            }

            // Create lead record
            var lead = new MarketingLead
            {
                Name = dto.Name?.Trim(),
                Email = dto.Email?.Trim().ToLowerInvariant(),
                Company = dto.Company?.Trim(),
                Phone = dto.Phone?.Trim(),
                Message = dto.Message?.Trim(),
                Source = dto.Source ?? "website",
                IpAddress = HttpContext.Connection.RemoteIpAddress?.ToString(),
                UserAgent = Request.Headers["User-Agent"].ToString(),
                CreatedAt = DateTimeOffset.UtcNow
            };

            _context.MarketingLeads.Add(lead);
            await _context.SaveChangesAsync();

            // Send notification email (async, don't wait)
            _ = Task.Run(async () => await SendLeadNotificationEmail(lead));

            _logger.LogInformation("New marketing lead captured: {Email} from {Company}", lead.Email, lead.Company);

            return Accepted(new { leadId = lead.MarketingLeadId, message = "Thank you for your interest!" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error submitting lead");
            return StatusCode(500, new { error = "An error occurred. Please try again later." });
        }
    }

    [HttpGet("leads")]
    [Authorize(Roles = "Admin,Sales")]
    public async Task<IActionResult> GetLeads(
        [FromQuery] bool? qualified = null,
        [FromQuery] bool? contacted = null,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 50)
    {
        try
        {
            var query = _context.MarketingLeads.AsQueryable();

            if (qualified.HasValue)
                query = query.Where(l => l.IsQualified == qualified.Value);

            if (contacted.HasValue)
                query = query.Where(l => l.IsContacted == contacted.Value);

            var totalCount = await query.CountAsync();

            var leads = await query
                .OrderByDescending(l => l.CreatedAt)
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .Select(l => new
                {
                    l.MarketingLeadId,
                    l.Name,
                    l.Email,
                    l.Company,
                    l.Phone,
                    l.Source,
                    l.IsQualified,
                    l.IsContacted,
                    l.CreatedAt,
                    l.ContactedAt,
                    MessagePreview = l.Message != null ? l.Message.Substring(0, Math.Min(l.Message.Length, 100)) : null
                })
                .ToListAsync();

            return Ok(new
            {
                leads,
                pagination = new
                {
                    totalCount,
                    page,
                    pageSize,
                    totalPages = (int)Math.Ceiling(totalCount / (double)pageSize)
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting leads");
            return StatusCode(500, new { error = "Error retrieving leads" });
        }
    }

    [HttpGet("leads/{leadId}")]
    [Authorize(Roles = "Admin,Sales")]
    public async Task<IActionResult> GetLead(Guid leadId)
    {
        try
        {
            var lead = await _context.MarketingLeads
                .Include(l => l.ContactedByUser)
                .FirstOrDefaultAsync(l => l.MarketingLeadId == leadId);

            if (lead == null)
                return NotFound(new { error = "Lead not found" });

            return Ok(lead);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting lead {LeadId}", leadId);
            return StatusCode(500, new { error = "Error retrieving lead" });
        }
    }

    [HttpPut("leads/{leadId}/qualify")]
    [Authorize(Roles = "Admin,Sales")]
    public async Task<IActionResult> QualifyLead(Guid leadId, [FromBody] QualifyLeadDto dto)
    {
        try
        {
            var lead = await _context.MarketingLeads.FindAsync(leadId);
            if (lead == null)
                return NotFound(new { error = "Lead not found" });

            lead.IsQualified = dto.IsQualified;
            lead.Notes = dto.Notes;

            await _context.SaveChangesAsync();

            return Ok(new { message = "Lead updated successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error qualifying lead {LeadId}", leadId);
            return StatusCode(500, new { error = "Error updating lead" });
        }
    }

    [HttpPut("leads/{leadId}/contacted")]
    [Authorize(Roles = "Admin,Sales")]
    public async Task<IActionResult> MarkContacted(Guid leadId, [FromBody] ContactedDto dto)
    {
        try
        {
            var lead = await _context.MarketingLeads.FindAsync(leadId);
            if (lead == null)
                return NotFound(new { error = "Lead not found" });

            lead.IsContacted = true;
            lead.ContactedAt = DateTimeOffset.UtcNow;
            // In production, get from auth context
            // lead.ContactedBy = User.GetUserId();
            
            if (!string.IsNullOrEmpty(dto.Notes))
            {
                lead.Notes = (lead.Notes ?? "") + $"\n[{DateTimeOffset.UtcNow:yyyy-MM-dd HH:mm}] " + dto.Notes;
            }

            await _context.SaveChangesAsync();

            return Ok(new { message = "Lead marked as contacted" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error marking lead as contacted {LeadId}", leadId);
            return StatusCode(500, new { error = "Error updating lead" });
        }
    }

    [HttpGet("leads/stats")]
    [Authorize(Roles = "Admin,Sales")]
    public async Task<IActionResult> GetLeadStats()
    {
        try
        {
            var thirtyDaysAgo = DateTimeOffset.UtcNow.AddDays(-30);
            
            var stats = new
            {
                Total = await _context.MarketingLeads.CountAsync(),
                ThisMonth = await _context.MarketingLeads.CountAsync(l => l.CreatedAt >= thirtyDaysAgo),
                Qualified = await _context.MarketingLeads.CountAsync(l => l.IsQualified),
                Contacted = await _context.MarketingLeads.CountAsync(l => l.IsContacted),
                ConversionRate = await CalculateConversionRate(),
                TopSources = await _context.MarketingLeads
                    .GroupBy(l => l.Source)
                    .Select(g => new { Source = g.Key, Count = g.Count() })
                    .OrderByDescending(x => x.Count)
                    .Take(5)
                    .ToListAsync(),
                RecentLeads = await _context.MarketingLeads
                    .OrderByDescending(l => l.CreatedAt)
                    .Take(10)
                    .Select(l => new { l.Name, l.Company, l.CreatedAt })
                    .ToListAsync()
            };

            return Ok(stats);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting lead stats");
            return StatusCode(500, new { error = "Error calculating stats" });
        }
    }

    private async Task<double> CalculateConversionRate()
    {
        var total = await _context.MarketingLeads.CountAsync();
        if (total == 0) return 0;

        var qualified = await _context.MarketingLeads.CountAsync(l => l.IsQualified);
        return Math.Round((double)qualified / total * 100, 2);
    }

    private async Task SendLeadNotificationEmail(MarketingLead lead)
    {
        try
        {
            var salesEmail = _configuration["Marketing:SalesEmail"] ?? "sales@fdx.trading";
            var smtpHost = _configuration["Email:SmtpHost"];
            
            if (string.IsNullOrEmpty(smtpHost))
            {
                _logger.LogWarning("SMTP not configured, skipping lead notification email");
                return;
            }

            var subject = $"New Demo Request - {lead.Company ?? "Unknown"}";
            var body = new StringBuilder();
            body.AppendLine($"New demo request received:");
            body.AppendLine($"");
            body.AppendLine($"Name: {lead.Name}");
            body.AppendLine($"Email: {lead.Email}");
            body.AppendLine($"Company: {lead.Company}");
            body.AppendLine($"Phone: {lead.Phone}");
            body.AppendLine($"");
            body.AppendLine($"Message:");
            body.AppendLine(lead.Message ?? "(No message provided)");
            body.AppendLine($"");
            body.AppendLine($"Source: {lead.Source}");
            body.AppendLine($"Submitted: {lead.CreatedAt:yyyy-MM-dd HH:mm:ss} UTC");
            body.AppendLine($"");
            body.AppendLine($"View in CRM: https://fdx.trading/admin/leads/{lead.MarketingLeadId}");

            // In production, use proper email service
            _logger.LogInformation("Lead notification email would be sent to {Email}", salesEmail);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error sending lead notification email");
        }
    }
}

// DTOs
public class MarketingLeadDto
{
    public string? Name { get; set; }
    public string? Email { get; set; }
    public string? Company { get; set; }
    public string? Phone { get; set; }
    public string? Message { get; set; }
    public string? Source { get; set; }
    public string? Website { get; set; } // Honeypot field
}

public class QualifyLeadDto
{
    public bool IsQualified { get; set; }
    public string? Notes { get; set; }
}

public class ContactedDto
{
    public string? Notes { get; set; }
}