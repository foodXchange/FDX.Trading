# Email Configuration Guide for FoodXchange

This guide explains how to set up email notifications for your FoodXchange application.

## Email Service Options

### Option 1: Gmail (Recommended for Development)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and generate a password
   - Copy the generated password

3. **Update .env file**:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
```

### Option 2: Microsoft 365 / Outlook

1. **Update .env file**:
```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yourdomain.com
SMTP_PASSWORD=your-password
```

### Option 3: SendGrid (Recommended for Production)

1. **Create a SendGrid account**: https://sendgrid.com/
2. **Generate an API Key**
3. **Update .env file**:
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

### Option 4: Azure Communication Services

1. **Create Azure Communication Service**:
```bash
az communication create --name foodxchange-comm --resource-group foodxchange-rg --data-location "United States"
```

2. **Get connection string**:
```bash
az communication list-key --name foodxchange-comm --resource-group foodxchange-rg
```

3. **Update .env file**:
```env
AZURE_EMAIL_CONNECTION_STRING=your-connection-string
```

## Testing Email Configuration

### 1. Check Email Status

```bash
curl -X GET http://localhost:8000/api/email-test/status
```

### 2. Send Test Emails

**Welcome Email:**
```bash
curl -X POST http://localhost:8000/api/email-test/send-test \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "email_type": "welcome"
  }'
```

**Order Confirmation:**
```bash
curl -X POST http://localhost:8000/api/email-test/send-test \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "email_type": "order"
  }'
```

**RFQ Notification:**
```bash
curl -X POST http://localhost:8000/api/email-test/send-test \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "email_type": "rfq"
  }'
```

**Quote Received:**
```bash
curl -X POST http://localhost:8000/api/email-test/send-test \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "email_type": "quote"
  }'
```

## Email Templates

The system includes pre-built HTML email templates for:

1. **Welcome Emails** - Sent when new users register
2. **Order Confirmations** - Sent when orders are placed
3. **RFQ Notifications** - Sent to suppliers when new RFQs are created
4. **Quote Notifications** - Sent to buyers when quotes are received
5. **Password Reset** - Sent when users request password reset
6. **Generic Notifications** - For system alerts and updates

## Notification Channels

When creating notifications, you can specify multiple channels:

```python
await notification_service.create_notification(
    user_id=user.id,
    notification_type=NotificationType.ORDER_PLACED,
    title="New Order",
    message="You have a new order",
    channels=["in_app", "email", "sms", "push"],
    db=db
)
```

Current supported channels:
- ✅ `in_app` - In-application notifications
- ✅ `email` - Email notifications
- 🚧 `sms` - SMS notifications (coming soon)
- 🚧 `push` - Push notifications (coming soon)

## Production Considerations

### 1. Email Limits
- Gmail: 500 emails/day
- SendGrid Free: 100 emails/day
- Azure Communication Services: Pay-per-use

### 2. Best Practices
- Use email queuing for bulk sends
- Implement retry logic for failed sends
- Monitor email bounce rates
- Use dedicated transactional email service
- Implement unsubscribe functionality

### 3. Security
- Never commit SMTP credentials to git
- Use environment variables for all credentials
- Rotate passwords regularly
- Use OAuth2 when available

### 4. Monitoring
- Track email delivery rates
- Monitor for spam complaints
- Set up alerts for failed sends
- Log all email activities

## Troubleshooting

### Email not sending?

1. Check configuration:
```bash
curl http://localhost:8000/api/email-test/status
```

2. Verify SMTP settings in .env file

3. Check application logs for errors

4. Common issues:
   - Wrong SMTP port (587 for TLS, 465 for SSL)
   - Firewall blocking SMTP ports
   - Invalid credentials
   - 2FA not configured for Gmail

### Gmail specific issues:

- Enable "Less secure app access" (not recommended)
- Use App Passwords instead (recommended)
- Check if account has 2FA enabled

### Production deployment:

Ensure these environment variables are set in Azure App Service:
```bash
az webapp config appsettings set --name foodxchange-app --resource-group foodxchange-rg \
  --settings SMTP_HOST="smtp.sendgrid.net" \
  SMTP_PORT="587" \
  SMTP_USERNAME="apikey" \
  SMTP_PASSWORD="your-api-key"
```