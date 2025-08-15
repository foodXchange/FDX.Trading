using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.Extensions.Logging;
using FDX.Trading.Services;

namespace FDX.Trading.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class InvitationsController : ControllerBase
    {
        private readonly IInvitationService _invitationService;
        private readonly ILogger<InvitationsController> _logger;

        public InvitationsController(IInvitationService invitationService, ILogger<InvitationsController> logger)
        {
            _invitationService = invitationService;
            _logger = logger;
        }

        [HttpPost("create")]
        [Authorize(Policy = "AdminOnly")]
        public async Task<IActionResult> CreateInvitation([FromBody] CreateInvitationRequest request)
        {
            try
            {
                var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? Guid.NewGuid().ToString();
                var userName = User.FindFirst(ClaimTypes.Name)?.Value ?? "System Admin";

                var invitation = await _invitationService.CreateInvitationAsync(
                    request.Email,
                    request.Name,
                    request.Role,
                    userId,
                    userName
                );

                return Ok(new
                {
                    success = true,
                    invitationId = invitation.InvitationId,
                    message = $"Invitation sent to {request.Email}"
                });
            }
            catch (InvalidOperationException ex)
            {
                return BadRequest(new { success = false, message = ex.Message });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create invitation");
                return StatusCode(500, new { success = false, message = "Failed to create invitation" });
            }
        }

        [HttpPost("accept")]
        [AllowAnonymous]
        [EnableRateLimiting("public-form")]
        public async Task<IActionResult> AcceptInvitation([FromBody] AcceptInvitationRequest request)
        {
            try
            {
                // Get user ID from authenticated user or generate new one
                var userId = User.Identity?.IsAuthenticated == true 
                    ? User.FindFirst(ClaimTypes.NameIdentifier)?.Value 
                    : Guid.NewGuid().ToString();

                var success = await _invitationService.AcceptInvitationAsync(request.Token, userId ?? Guid.NewGuid().ToString());

                if (success)
                {
                    return Ok(new { success = true, message = "Invitation accepted successfully", redirectUrl = "/dashboard" });
                }
                else
                {
                    return BadRequest(new { success = false, message = "Invalid or expired invitation" });
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to accept invitation");
                return StatusCode(500, new { success = false, message = "Failed to accept invitation" });
            }
        }

        [HttpPost("{invitationId}/resend")]
        [Authorize(Policy = "AdminOnly")]
        public async Task<IActionResult> ResendInvitation(Guid invitationId)
        {
            try
            {
                var success = await _invitationService.ResendInvitationAsync(invitationId);

                if (success)
                {
                    return Ok(new { success = true, message = "Invitation resent successfully" });
                }
                else
                {
                    return NotFound(new { success = false, message = "Invitation not found" });
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to resend invitation");
                return StatusCode(500, new { success = false, message = "Failed to resend invitation" });
            }
        }

        [HttpPost("{invitationId}/cancel")]
        [Authorize(Policy = "AdminOnly")]
        public async Task<IActionResult> CancelInvitation(Guid invitationId)
        {
            try
            {
                var success = await _invitationService.CancelInvitationAsync(invitationId);

                if (success)
                {
                    return Ok(new { success = true, message = "Invitation cancelled successfully" });
                }
                else
                {
                    return NotFound(new { success = false, message = "Invitation not found" });
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to cancel invitation");
                return StatusCode(500, new { success = false, message = "Failed to cancel invitation" });
            }
        }

        [HttpGet("pending")]
        [Authorize(Policy = "AdminOnly")]
        public async Task<IActionResult> GetPendingInvitations()
        {
            try
            {
                var invitations = await _invitationService.GetPendingInvitationsAsync();
                return Ok(invitations);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get pending invitations");
                return StatusCode(500, new { message = "Failed to get pending invitations" });
            }
        }

        [HttpGet("all")]
        [Authorize(Policy = "AdminOnly")]
        public async Task<IActionResult> GetAllInvitations([FromQuery] int? limit = null)
        {
            try
            {
                var invitations = await _invitationService.GetAllInvitationsAsync(limit);
                return Ok(invitations);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get invitations");
                return StatusCode(500, new { message = "Failed to get invitations" });
            }
        }

        [HttpPost("cleanup")]
        [Authorize(Policy = "AdminOnly")]
        public async Task<IActionResult> CleanupExpiredInvitations()
        {
            try
            {
                await _invitationService.CleanupExpiredInvitationsAsync();
                return Ok(new { success = true, message = "Expired invitations cleaned up" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to cleanup expired invitations");
                return StatusCode(500, new { success = false, message = "Failed to cleanup expired invitations" });
            }
        }

        [HttpGet("validate/{token}")]
        [AllowAnonymous]
        public async Task<IActionResult> ValidateInvitation(string token)
        {
            try
            {
                var invitation = await _invitationService.GetInvitationByTokenAsync(token);
                
                if (invitation == null)
                {
                    return NotFound(new { valid = false, message = "Invalid invitation token" });
                }

                if (invitation.ExpiresAt < DateTimeOffset.UtcNow)
                {
                    return BadRequest(new { valid = false, message = "Invitation has expired" });
                }

                return Ok(new
                {
                    valid = true,
                    email = invitation.Email,
                    name = invitation.Name,
                    role = invitation.Role,
                    invitedBy = invitation.InvitedByName
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to validate invitation");
                return StatusCode(500, new { valid = false, message = "Failed to validate invitation" });
            }
        }
    }

    public class CreateInvitationRequest
    {
        public string Email { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Role { get; set; } = string.Empty;
        public string? Notes { get; set; }
    }

    public class AcceptInvitationRequest
    {
        public string Token { get; set; } = string.Empty;
    }
}