# Azure Communication Services Email Setup Guide

This guide walks you through setting up Azure Communication Services for email in FoodXchange.

## Prerequisites

- Azure subscription
- Azure CLI installed
- PowerShell (for Windows) or Bash (for Linux/Mac)

## Step 1: Create Azure Communication Service

```powershell
# Create Communication Service
az communication create `
  --name "foodxchange-email" `
  --resource-group "foodxchange-rg" `
  --data-location "United States"
```

## Step 2: Get Connection String

```powershell
# Get connection string
$connectionString = az communication list-key `
  --name "foodxchange-email" `
  --resource-group "foodxchange-rg" `
  --query "primaryConnectionString" `
  --output tsv

Write-Host "Connection String: $connectionString"
```

## Step 3: Create Email Communication Service

```powershell
# Create Email Communication Service
az communication email create `
  --name "foodxchange-email-service" `
  --resource-group "foodxchange-rg" `
  --location "global" `
  --data-location "United States"
```

## Step 4: Create Email Domain

```powershell
# Create a domain (Azure managed domain)
az communication email domain create `
  --name "AzureManagedDomain" `
  --email-service-name "foodxchange-email-service" `
  --resource-group "foodxchange-rg" `
  --domain-management "AzureManaged"
```

## Step 5: Get Sender Address

After creating the domain, you'll get a sender address like:
- `DoNotReply@<random-id>.azurecomm.net`

## Step 6: Update Environment Variables

Add these to your `.env` file:

```env
# Azure Communication Services Email
AZURE_EMAIL_CONNECTION_STRING=endpoint=https://foodxchange-email.communication.azure.com/;accesskey=your-key-here
AZURE_EMAIL_SENDER=DoNotReply@abc123.azurecomm.net
```

## Step 7: Test Email Sending

```bash
# Check email status
curl http://localhost:8000/api/email-test/status

# Send test email
curl -X POST http://localhost:8000/api/email-test/send-test \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "email_type": "welcome"
  }'
```

## Using Custom Domain (Optional)

If you want to use your own domain (e.g., noreply@fdx.trading):

### Step 1: Create Custom Domain

```powershell
# Create custom domain
az communication email domain create `
  --name "fdx.trading" `
  --email-service-name "foodxchange-email-service" `
  --resource-group "foodxchange-rg" `
  --domain-management "CustomerManaged"
```

### Step 2: Configure DNS Records

Add these DNS records to your domain:

1. **SPF Record** (TXT):
   - Name: `@`
   - Value: `v=spf1 include:spf.protection.outlook.com -all`

2. **DKIM Records** (CNAME):
   - Name: `selector1._domainkey`
   - Value: `selector1-fdx-trading._domainkey.azurecomm.net`
   
   - Name: `selector2._domainkey`
   - Value: `selector2-fdx-trading._domainkey.azurecomm.net`

3. **Domain Ownership** (TXT):
   - Name: `@`
   - Value: `azure-communication-verification=<verification-code>`

### Step 3: Verify Domain

```powershell
# Initiate verification
az communication email domain initiate-verification `
  --name "fdx.trading" `
  --email-service-name "foodxchange-email-service" `
  --resource-group "foodxchange-rg" `
  --verification-type "Domain"
```

### Step 4: Update Sender Address

```env
AZURE_EMAIL_SENDER=noreply@fdx.trading
```

## Email Service Features

### Current Implementation

The email service now supports both SMTP and Azure Communication Services:

1. **Automatic Failover**: If Azure is configured, it will be used. Otherwise, falls back to SMTP.
2. **HTML Templates**: All email types support both plain text and HTML versions.
3. **Async Support**: All email sending is asynchronous for better performance.

### Supported Email Types

- Welcome emails
- Order confirmations
- RFQ notifications
- Quote notifications
- Password reset
- Generic notifications

### Benefits of Azure Communication Services

1. **High Deliverability**: Built on Microsoft's infrastructure
2. **No SMTP Limits**: No daily sending limits like Gmail
3. **Better Analytics**: Track delivery, opens, and clicks
4. **Global Scale**: Automatically scales with your needs
5. **Security**: Enterprise-grade security and compliance

## Troubleshooting

### Email Not Sending?

1. Check configuration:
```bash
curl http://localhost:8000/api/email-test/status
```

2. Verify connection string format:
```
endpoint=https://<resource-name>.communication.azure.com/;accesskey=<access-key>
```

3. Check sender address matches your domain configuration

4. View application logs for detailed error messages

### Common Issues

1. **Invalid Sender Address**: Make sure the sender address matches your configured domain
2. **Connection String Format**: Ensure it includes both endpoint and accesskey
3. **Domain Not Verified**: For custom domains, ensure DNS records are properly configured
4. **Rate Limiting**: Azure has rate limits, but they're much higher than SMTP providers

## Production Deployment

Set environment variables in Azure App Service:

```bash
az webapp config appsettings set \
  --name foodxchange-app \
  --resource-group foodxchange-rg \
  --settings \
    AZURE_EMAIL_CONNECTION_STRING="your-connection-string" \
    AZURE_EMAIL_SENDER="DoNotReply@your-domain.azurecomm.net"
```

## Monitoring

View email analytics in Azure Portal:
1. Go to your Communication Service resource
2. Navigate to "Email" > "Analytics"
3. View delivery rates, bounce rates, and more

## Costs

Azure Communication Services Email pricing:
- First 1,000 emails per month: Free
- Additional emails: $0.00025 per email
- No setup or monthly fees
- Pay only for what you use

## Next Steps

1. Set up email analytics tracking
2. Implement email templates for more notification types
3. Add email preference management for users
4. Set up bounce and complaint handling