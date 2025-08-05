# 🛡️ FoodXchange Safety Guidelines

## **Critical Safety Measures**

### **1. Git Repository Safety**
- ✅ **Always commit before major changes**
- ✅ **Use descriptive commit messages**
- ✅ **Never use `git rm -rf .` without backup**
- ✅ **Keep remote repository synced**

### **2. Database Safety**
- ✅ **Never delete production data without backup**
- ✅ **Test database changes in development first**
- ✅ **Use transactions for critical operations**
- ✅ **Keep database credentials secure**

### **3. Server Safety**
- ✅ **Use localhost (127.0.0.1) for development**
- ✅ **Avoid port 9000 (use 8000 instead)**
- ✅ **Keep server logs for debugging**
- ✅ **Monitor server performance**

### **4. File Management Safety**
- ✅ **Backup important files before deletion**
- ✅ **Use version control for all code changes**
- ✅ **Keep documentation updated**
- ✅ **Test changes before deployment**

## **Daily Safety Checklist**

### **Before Making Changes:**
1. ✅ Check Git status
2. ✅ Commit current changes
3. ✅ Backup critical files
4. ✅ Test in development environment

### **After Making Changes:**
1. ✅ Test functionality
2. ✅ Commit changes with clear messages
3. ✅ Update documentation if needed
4. ✅ Verify server is running correctly

## **Emergency Recovery Procedures**

### **If Files Are Accidentally Deleted:**
1. ✅ Check Git history: `git log --oneline`
2. ✅ Restore from last commit: `git checkout HEAD~1 -- filename`
3. ✅ Use Git stash if available: `git stash pop`
4. ✅ Check for backup files

### **If Server Won't Start:**
1. ✅ Check port availability
2. ✅ Use different port (8000 instead of 9000)
3. ✅ Check for syntax errors
4. ✅ Verify dependencies are installed

### **If Database Connection Fails:**
1. ✅ Check DATABASE_URL in .env
2. ✅ Verify network connectivity
3. ✅ Check Azure PostgreSQL status
4. ✅ Test connection manually

## **Security Best Practices**

### **Environment Variables:**
- ✅ Never commit .env files
- ✅ Use strong passwords
- ✅ Rotate credentials regularly
- ✅ Use environment-specific configs

### **Authentication:**
- ✅ Use secure login credentials
- ✅ Implement proper session management
- ✅ Add rate limiting for login attempts
- ✅ Log authentication events

### **Data Protection:**
- ✅ Encrypt sensitive data
- ✅ Use HTTPS in production
- ✅ Implement proper access controls
- ✅ Regular security audits

## **Backup Strategy**

### **Code Backup:**
- ✅ Git repository (primary)
- ✅ Local backup folder
- ✅ Cloud storage (GitHub/GitLab)
- ✅ Regular commits

### **Database Backup:**
- ✅ Azure PostgreSQL automated backups
- ✅ Manual export before major changes
- ✅ Test restore procedures
- ✅ Keep backup logs

### **Configuration Backup:**
- ✅ Environment files
- ✅ Server configurations
- ✅ Documentation
- ✅ Deployment scripts

## **Monitoring & Alerts**

### **Server Monitoring:**
- ✅ Check server logs regularly
- ✅ Monitor performance metrics
- ✅ Set up error alerts
- ✅ Track user activity

### **Database Monitoring:**
- ✅ Query performance
- ✅ Connection pool status
- ✅ Storage usage
- ✅ Error logs

## **Development Workflow Safety**

### **Feature Development:**
1. ✅ Create feature branch
2. ✅ Develop and test locally
3. ✅ Commit frequently
4. ✅ Merge to main after testing

### **Testing:**
1. ✅ Unit tests for critical functions
2. ✅ Integration tests for API endpoints
3. ✅ Manual testing for UI changes
4. ✅ Performance testing

### **Deployment:**
1. ✅ Test in staging environment
2. ✅ Backup production data
3. ✅ Deploy during low-traffic hours
4. ✅ Monitor after deployment

## **Contact Information**

### **Emergency Contacts:**
- **Azure Support:** For database issues
- **GitHub Support:** For repository issues
- **Local Backup:** Check local backup folder
- **Documentation:** FOODXCHANGE_DOCUMENTATION.md

## **Quick Commands Reference**

### **Git Safety Commands:**
```bash
# Check status
git status

# Safe commit
git add .
git commit -m "Descriptive message"

# Check history
git log --oneline

# Restore file
git checkout HEAD~1 -- filename

# Create backup branch
git checkout -b backup-branch
```

### **Server Safety Commands:**
```bash
# Start server safely
python -c "import uvicorn; uvicorn.run('app:app', host='127.0.0.1', port=8000, reload=True)"

# Check if port is in use
netstat -an | findstr :8000

# Kill process on port
taskkill /F /PID <process_id>
```

### **Database Safety Commands:**
```bash
# Test connection
python -c "from database import get_db_connection; print(get_db_connection())"

# Backup database
pg_dump <connection_string> > backup.sql

# Restore database
psql <connection_string> < backup.sql
```

---

**Remember: Safety first, always! 🛡️** 