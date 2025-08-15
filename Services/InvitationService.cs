using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using FDX.Trading.Data;
using FDX.Trading.Models;

namespace FDX.Trading.Services
{
    public interface IInvitationService
    {
        Task<Invitation> CreateInvitationAsync(string email, string name, string role, string invitedByUserId, string invitedByName);
        Task<Invitation> GetInvitationByTokenAsync(string token);
        Task<bool> AcceptInvitationAsync(string token, string userId);
        Task<bool> ResendInvitationAsync(Guid invitationId);
        Task<bool> CancelInvitationAsync(Guid invitationId);
        Task<List<Invitation>> GetPendingInvitationsAsync();
        Task<List<Invitation>> GetAllInvitationsAsync(int? limit = null);
        Task CleanupExpiredInvitationsAsync();
    }

    public class InvitationService : IInvitationService
    {
        private readonly FdxTradingContext _context;
        private readonly IEmailService _emailService;
        private readonly ILogger<InvitationService> _logger;

        public InvitationService(FdxTradingContext context, IEmailService emailService, ILogger<InvitationService> logger)
        {
            _context = context;
            _emailService = emailService;
            _logger = logger;
        }

        public async Task<Invitation> CreateInvitationAsync(string email, string name, string role, string invitedByUserId, string invitedByName)
        {
            // Check if invitation already exists for this email
            var existingInvitation = await _context.Invitations
                .FirstOrDefaultAsync(i => i.Email == email && i.Status == "pending");

            if (existingInvitation != null)
            {
                throw new InvalidOperationException($"An invitation for {email} is already pending.");
            }

            // Check if user already exists
            var existingUser = await _context.Users
                .FirstOrDefaultAsync(u => u.Email == email);

            if (existingUser != null)
            {
                throw new InvalidOperationException($"A user with email {email} already exists.");
            }

            // Create invitation
            var invitation = new Invitation
            {
                InvitationId = Guid.NewGuid(),
                Email = email,
                Name = name,
                Role = role,
                Token = GenerateSecureToken(),
                Status = "pending",
                InvitedByUserId = Guid.Parse(invitedByUserId),
                InvitedByName = invitedByName,
                CreatedAt = DateTimeOffset.UtcNow,
                ExpiresAt = DateTimeOffset.UtcNow.AddDays(7)
            };

            _context.Invitations.Add(invitation);
            await _context.SaveChangesAsync();

            // Send invitation email
            var invitationLink = $"https://fdx.trading/invitation/accept?token={invitation.Token}";
            await _emailService.SendInvitationEmailAsync(email, name, role, invitedByName, invitationLink);

            _logger.LogInformation("Invitation created for {Email} with role {Role}", email, role);
            return invitation;
        }

        public async Task<Invitation> GetInvitationByTokenAsync(string token)
        {
            return await _context.Invitations
                .FirstOrDefaultAsync(i => i.Token == token && i.Status == "pending");
        }

        public async Task<bool> AcceptInvitationAsync(string token, string userId)
        {
            var invitation = await GetInvitationByTokenAsync(token);
            
            if (invitation == null)
            {
                _logger.LogWarning("Invalid or expired invitation token: {Token}", token);
                return false;
            }

            if (invitation.ExpiresAt < DateTimeOffset.UtcNow)
            {
                invitation.Status = "expired";
                await _context.SaveChangesAsync();
                _logger.LogWarning("Invitation token expired: {Token}", token);
                return false;
            }

            // Update invitation status
            invitation.Status = "accepted";
            invitation.AcceptedAt = DateTimeOffset.UtcNow;
            invitation.AcceptedByUserId = Guid.Parse(userId);

            // Create or update user
            var user = await _context.Users.FirstOrDefaultAsync(u => u.Email == invitation.Email);
            if (user == null)
            {
                user = new User
                {
                    UserId = Guid.Parse(userId),
                    Email = invitation.Email,
                    Name = invitation.Name,
                    Role = invitation.Role,
                    IsActive = true,
                    CreatedAt = DateTimeOffset.UtcNow
                };
                _context.Users.Add(user);
            }
            else
            {
                user.Role = invitation.Role;
                user.IsActive = true;
            }

            await _context.SaveChangesAsync();

            // Send welcome email
            await _emailService.SendWelcomeEmailAsync(invitation.Email, invitation.Name);

            _logger.LogInformation("Invitation accepted for {Email}", invitation.Email);
            return true;
        }

        public async Task<bool> ResendInvitationAsync(Guid invitationId)
        {
            var invitation = await _context.Invitations.FindAsync(invitationId);
            
            if (invitation == null || invitation.Status != "pending")
            {
                return false;
            }

            // Extend expiration
            invitation.ExpiresAt = DateTimeOffset.UtcNow.AddDays(7);
            invitation.ResendCount = (invitation.ResendCount ?? 0) + 1;
            invitation.LastResentAt = DateTimeOffset.UtcNow;

            await _context.SaveChangesAsync();

            // Resend email
            var invitationLink = $"https://fdx.trading/invitation/accept?token={invitation.Token}";
            await _emailService.SendInvitationEmailAsync(
                invitation.Email, 
                invitation.Name, 
                invitation.Role, 
                invitation.InvitedByName, 
                invitationLink
            );

            _logger.LogInformation("Invitation resent to {Email}", invitation.Email);
            return true;
        }

        public async Task<bool> CancelInvitationAsync(Guid invitationId)
        {
            var invitation = await _context.Invitations.FindAsync(invitationId);
            
            if (invitation == null || invitation.Status != "pending")
            {
                return false;
            }

            invitation.Status = "cancelled";
            invitation.CancelledAt = DateTimeOffset.UtcNow;

            await _context.SaveChangesAsync();

            _logger.LogInformation("Invitation cancelled for {Email}", invitation.Email);
            return true;
        }

        public async Task<List<Invitation>> GetPendingInvitationsAsync()
        {
            return await _context.Invitations
                .Where(i => i.Status == "pending" && i.ExpiresAt > DateTimeOffset.UtcNow)
                .OrderByDescending(i => i.CreatedAt)
                .ToListAsync();
        }

        public async Task<List<Invitation>> GetAllInvitationsAsync(int? limit = null)
        {
            var query = _context.Invitations
                .OrderByDescending(i => i.CreatedAt);

            if (limit.HasValue)
            {
                return await query.Take(limit.Value).ToListAsync();
            }

            return await query.ToListAsync();
        }

        public async Task CleanupExpiredInvitationsAsync()
        {
            var expiredInvitations = await _context.Invitations
                .Where(i => i.Status == "pending" && i.ExpiresAt < DateTimeOffset.UtcNow)
                .ToListAsync();

            foreach (var invitation in expiredInvitations)
            {
                invitation.Status = "expired";
            }

            if (expiredInvitations.Any())
            {
                await _context.SaveChangesAsync();
                _logger.LogInformation("Cleaned up {Count} expired invitations", expiredInvitations.Count);
            }
        }

        private string GenerateSecureToken()
        {
            var bytes = new byte[32];
            using (var rng = System.Security.Cryptography.RandomNumberGenerator.Create())
            {
                rng.GetBytes(bytes);
            }
            return Convert.ToBase64String(bytes)
                .Replace("+", "-")
                .Replace("/", "_")
                .Replace("=", "");
        }
    }
}