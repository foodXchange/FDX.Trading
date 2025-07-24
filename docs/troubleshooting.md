# Troubleshooting Guide

## Common Issues

### Cannot Connect to Azure OpenAI
**Symptoms**: AI features not working
**Solutions**:
1. Check API key in .env
2. Verify endpoint URL
3. Ensure deployment name matches
4. Check Azure subscription status

### Email Not Sending
**Symptoms**: Emails stuck in queue
**Solutions**:
1. Verify SMTP credentials
2. Check Gmail app password
3. Test with simple email first
4. Check spam folder

### Slow Performance
**Symptoms**: Dashboard loading slowly
**Solutions**:
1. Check Cosmos DB RU usage
2. Optimize database queries
3. Enable caching
4. Reduce supplier list pagination

### Import Failures
**Symptoms**: CSV import errors
**Solutions**:
1. Check column names match
2. Verify UTF-8 encoding
3. Remove special characters
4. Split large files

## Error Messages

### "Token Expired"
- User needs to login again
- Check token expiration settings

### "Rate Limit Exceeded"
- Too many AI requests
- Implement request queuing

### "Database Connection Failed"
- Check Cosmos DB firewall
- Verify connection string
- Check network connectivity

## Getting Help
1. Check error logs: `logs/error.log`
2. Enable debug mode: `DEBUG=true`
3. Contact support with error details 