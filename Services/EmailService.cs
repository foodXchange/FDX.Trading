using Azure;
using Azure.Communication.Email;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace FDX.Trading.Services
{
    public interface IEmailService
    {
        Task<bool> SendInvitationEmailAsync(string recipientEmail, string recipientName, string role, string inviterName, string invitationLink);
        Task<bool> SendWelcomeEmailAsync(string recipientEmail, string recipientName);
        Task<bool> SendOrderConfirmationAsync(string recipientEmail, string orderNumber, decimal totalAmount);
        Task<bool> SendComplianceApprovedAsync(string recipientEmail, string contractNumber, string supplierName);
        Task<bool> SendCustomEmailAsync(string recipientEmail, string subject, string htmlContent, string plainTextContent = null);
    }

    public class EmailService : IEmailService
    {
        private readonly EmailClient _emailClient;
        private readonly IConfiguration _configuration;
        private readonly ILogger<EmailService> _logger;
        private readonly string _senderAddress;

        public EmailService(EmailClient emailClient, IConfiguration configuration, ILogger<EmailService> logger)
        {
            _emailClient = emailClient;
            _configuration = configuration;
            _logger = logger;
            _senderAddress = configuration["AzureCommunicationServices:SenderAddress"] ?? "DoNotReply@fdx.trading";
        }

        public async Task<bool> SendInvitationEmailAsync(string recipientEmail, string recipientName, string role, string inviterName, string invitationLink)
        {
            var subject = _configuration["EmailTemplates:InvitationSubject"] ?? "You're Invited to Join FDX Trading Platform";
            
            var htmlContent = $@"
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; }}
        .role-badge {{ display: inline-block; padding: 5px 15px; background: #f0f0f0; border-radius: 20px; font-weight: 600; }}
    </style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h1>Welcome to FDX Trading</h1>
        </div>
        <div class='content'>
            <h2>Hello {recipientName},</h2>
            <p>{inviterName} has invited you to join the FDX Trading platform as a <span class='role-badge'>{role}</span>.</p>
            
            <p>FDX Trading is the leading B2B food sourcing platform that connects buyers with verified suppliers worldwide. Join us to:</p>
            <ul>
                <li>Access a global network of pre-qualified food suppliers</li>
                <li>Streamline your sourcing and compliance processes</li>
                <li>Track orders and shipments in real-time</li>
                <li>Manage contracts and financial transactions seamlessly</li>
            </ul>
            
            <p><strong>Your role as {role} includes:</strong></p>
            {GetRoleDescription(role)}
            
            <div style='text-align: center;'>
                <a href='{invitationLink}' class='button'>Accept Invitation</a>
            </div>
            
            <p style='color: #666; font-size: 14px;'>This invitation link will expire in 7 days. If you have any questions, please contact our support team.</p>
        </div>
        <div class='footer'>
            <p>© 2025 FDX Trading. All rights reserved.</p>
            <p>This email was sent to {recipientEmail}</p>
        </div>
    </div>
</body>
</html>";

            var plainTextContent = $@"
Hello {recipientName},

{inviterName} has invited you to join the FDX Trading platform as a {role}.

Accept your invitation here: {invitationLink}

This invitation link will expire in 7 days.

Best regards,
The FDX Trading Team
";

            return await SendCustomEmailAsync(recipientEmail, subject, htmlContent, plainTextContent);
        }

        public async Task<bool> SendWelcomeEmailAsync(string recipientEmail, string recipientName)
        {
            var subject = _configuration["EmailTemplates:WelcomeSubject"] ?? "Welcome to FDX Trading";
            
            var htmlContent = $@"
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; }}
    </style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h1>Welcome to FDX Trading!</h1>
        </div>
        <div class='content'>
            <h2>Hello {recipientName},</h2>
            <p>Your account has been successfully created. You're now part of the FDX Trading community!</p>
            
            <h3>Getting Started:</h3>
            <ol>
                <li><strong>Complete Your Profile:</strong> Add your company information and preferences</li>
                <li><strong>Explore the Platform:</strong> Browse suppliers, products, and opportunities</li>
                <li><strong>Start Trading:</strong> Create your first request or respond to opportunities</li>
            </ol>
            
            <div style='text-align: center;'>
                <a href='https://fdx.trading/dashboard' class='button'>Go to Dashboard</a>
            </div>
            
            <p>Need help? Check out our <a href='https://fdx.trading/help'>Help Center</a> or contact support.</p>
        </div>
        <div class='footer'>
            <p>© 2025 FDX Trading. All rights reserved.</p>
        </div>
    </div>
</body>
</html>";

            var plainTextContent = $@"
Hello {recipientName},

Welcome to FDX Trading! Your account has been successfully created.

Getting Started:
1. Complete Your Profile
2. Explore the Platform
3. Start Trading

Visit your dashboard: https://fdx.trading/dashboard

Best regards,
The FDX Trading Team
";

            return await SendCustomEmailAsync(recipientEmail, subject, htmlContent, plainTextContent);
        }

        public async Task<bool> SendOrderConfirmationAsync(string recipientEmail, string orderNumber, decimal totalAmount)
        {
            var subject = (_configuration["EmailTemplates:OrderConfirmationSubject"] ?? "Order Confirmation - {OrderNumber}")
                .Replace("{OrderNumber}", orderNumber);
            
            var htmlContent = $@"
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #28a745; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px; }}
        .order-box {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .amount {{ font-size: 24px; font-weight: bold; color: #28a745; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; }}
    </style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h1>Order Confirmed!</h1>
        </div>
        <div class='content'>
            <div class='order-box'>
                <p><strong>Order Number:</strong> {orderNumber}</p>
                <p><strong>Total Amount:</strong> <span class='amount'>${totalAmount:N2}</span></p>
                <p><strong>Status:</strong> Confirmed</p>
            </div>
            
            <p>Your order has been confirmed and is being processed. You can track your order status in your dashboard.</p>
            
            <p><strong>Next Steps:</strong></p>
            <ul>
                <li>Your supplier will prepare the shipment</li>
                <li>You'll receive tracking information once shipped</li>
                <li>Track real-time updates in your dashboard</li>
            </ul>
            
            <p style='text-align: center;'>
                <a href='https://fdx.trading/orders/{orderNumber}' style='display: inline-block; padding: 12px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;'>View Order</a>
            </p>
        </div>
        <div class='footer'>
            <p>© 2025 FDX Trading. All rights reserved.</p>
        </div>
    </div>
</body>
</html>";

            var plainTextContent = $@"
Order Confirmed!

Order Number: {orderNumber}
Total Amount: ${totalAmount:N2}

Your order has been confirmed and is being processed.

View your order: https://fdx.trading/orders/{orderNumber}

Best regards,
The FDX Trading Team
";

            return await SendCustomEmailAsync(recipientEmail, subject, htmlContent, plainTextContent);
        }

        public async Task<bool> SendComplianceApprovedAsync(string recipientEmail, string contractNumber, string supplierName)
        {
            var subject = _configuration["EmailTemplates:ComplianceApprovedSubject"] ?? "Compliance Approved - Ready to Order";
            
            var htmlContent = $@"
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #28a745; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px; }}
        .success-badge {{ display: inline-block; padding: 10px 20px; background: #d4edda; color: #155724; border-radius: 5px; font-weight: bold; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; }}
    </style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h1>✓ Compliance Approved</h1>
        </div>
        <div class='content'>
            <p>Great news! The compliance review for your contract with <strong>{supplierName}</strong> has been approved.</p>
            
            <div style='text-align: center; margin: 20px 0;'>
                <span class='success-badge'>Contract #{contractNumber} - Ready for Orders</span>
            </div>
            
            <p><strong>You can now:</strong></p>
            <ul>
                <li>Create purchase orders against this contract</li>
                <li>Schedule shipments with the supplier</li>
                <li>Access all contract terms and pricing</li>
            </ul>
            
            <p style='text-align: center;'>
                <a href='https://fdx.trading/contracts/{contractNumber}' style='display: inline-block; padding: 12px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;'>Create Order</a>
            </p>
        </div>
        <div class='footer'>
            <p>© 2025 FDX Trading. All rights reserved.</p>
        </div>
    </div>
</body>
</html>";

            var plainTextContent = $@"
Compliance Approved!

The compliance review for your contract with {supplierName} has been approved.

Contract #{contractNumber} is now ready for orders.

You can now create purchase orders against this contract.

View contract: https://fdx.trading/contracts/{contractNumber}

Best regards,
The FDX Trading Team
";

            return await SendCustomEmailAsync(recipientEmail, subject, htmlContent, plainTextContent);
        }

        public async Task<bool> SendCustomEmailAsync(string recipientEmail, string subject, string htmlContent, string plainTextContent = null)
        {
            try
            {
                if (_emailClient == null)
                {
                    _logger.LogWarning("Email client not configured. Skipping email to {RecipientEmail}", recipientEmail);
                    return false;
                }

                var emailMessage = new EmailMessage(
                    senderAddress: _senderAddress,
                    recipients: new EmailRecipients(new List<EmailAddress> { new EmailAddress(recipientEmail) }),
                    content: new EmailContent(subject)
                    {
                        Html = htmlContent,
                        PlainText = plainTextContent ?? StripHtml(htmlContent)
                    }
                );

                var emailSendOperation = await _emailClient.SendAsync(WaitUntil.Completed, emailMessage);
                
                _logger.LogInformation("Email sent successfully to {RecipientEmail} with subject: {Subject}", recipientEmail, subject);
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to send email to {RecipientEmail}", recipientEmail);
                return false;
            }
        }

        private string GetRoleDescription(string role)
        {
            return role?.ToLower() switch
            {
                "supplier" => @"<ul>
                    <li>Showcase your products and capabilities</li>
                    <li>Respond to buyer requests and RFQs</li>
                    <li>Manage orders and shipments</li>
                    <li>Build your reputation through successful transactions</li>
                </ul>",
                "expert" => @"<ul>
                    <li>Review and approve compliance documentation</li>
                    <li>Provide expertise on regulatory requirements</li>
                    <li>Support quality assurance processes</li>
                    <li>Help ensure safe and compliant trade</li>
                </ul>",
                "buyer" => @"<ul>
                    <li>Source products from verified suppliers</li>
                    <li>Create and manage RFQs</li>
                    <li>Track orders and shipments</li>
                    <li>Manage compliance and contracts</li>
                </ul>",
                _ => "<ul><li>Access the FDX Trading platform features</li></ul>"
            };
        }

        private string StripHtml(string html)
        {
            if (string.IsNullOrEmpty(html))
                return string.Empty;

            // Simple HTML stripping - in production, use a proper HTML parser
            var result = System.Text.RegularExpressions.Regex.Replace(html, "<.*?>", " ");
            result = System.Text.RegularExpressions.Regex.Replace(result, @"\s+", " ");
            return result.Trim();
        }
    }
}