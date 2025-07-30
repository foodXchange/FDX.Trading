# Azure Email Service Setup

## Required Environment Variables

To enable email functionality in FoodXchange, you need to configure the following environment variables in your `.env` file:

```bash
# Azure Communication Services Email
AZURE_COMMUNICATION_EMAIL_CONNECTION_STRING=your_connection_string_here
AZURE_EMAIL_SENDER_ADDRESS=DoNotReply@your-verified-domain.com
```

## How to Get These Values

1. **Azure Communication Services Email Connection String**:
   - Go to Azure Portal
   - Navigate to your Communication Services resource
   - Go to Settings > Keys
   - Copy the primary connection string

2. **Email Sender Address**:
   - In your Communication Services resource
   - Go to Email > Domains
   - Add and verify a domain
   - Use an email address from that verified domain

## Features Enabled

With email configuration, you can:
- Send product briefs as email attachments
- Include custom messages in emails
- Send to multiple recipients
- Attach DOCX documents automatically

## Testing Email Service

To test if email is configured correctly:
1. Analyze a product in the Product Analysis page
2. Click "Email Brief" button
3. Enter recipient email and send

## Troubleshooting

If emails are not sending:
1. Check that environment variables are set correctly
2. Verify your domain is approved in Azure
3. Check Azure Communication Services logs
4. Ensure you have sufficient credits/quota

Without email configuration, the application will still work but email features will show an error message.