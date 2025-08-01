# FoodXchange Support System

A comprehensive support system for the FoodXchange platform that provides automated error handling, ticket management, and user support capabilities.

## 🚀 Features

### **1. Automated Error Handling**
- **Intelligent Error Capture**: Automatically logs errors with context and categorization
- **Error Classification**: Categorizes errors by type (authentication, RFQ processing, system errors, etc.)
- **Severity Assessment**: Automatically determines error severity (critical, high, medium, low)
- **Support Ticket Creation**: Automatically creates support tickets for critical and high-severity errors
- **User-Friendly Error Pages**: Replaces generic error messages with contextual, helpful information

### **2. Support Ticket Management**
- **Ticket Creation**: Users can create support tickets with detailed information
- **Status Tracking**: Full workflow from new → acknowledged → investigating → in progress → testing → resolved → closed
- **Priority Management**: Support for low, medium, high, and critical priorities
- **Category Classification**: Organized by authentication, RFQ processing, supplier management, etc.
- **Assignment System**: Tickets can be assigned to specific team members
- **Response System**: Support for internal notes and user-visible responses

### **3. User Support Interface**
- **Support Center**: User-friendly interface for creating tickets and reporting issues
- **Bug Reporting**: Dedicated forms for bug reports with detailed information capture
- **Feature Requests**: Streamlined process for submitting feature requests
- **Self-Service**: Help articles and troubleshooting guides
- **Ticket Tracking**: Users can view their ticket history and status

### **4. Admin Dashboard**
- **Analytics Dashboard**: Real-time statistics and metrics
- **Ticket Management**: Comprehensive interface for managing all support tickets
- **Error Logs**: Detailed view of all system errors with filtering and search
- **Performance Monitoring**: Track resolution times and support team performance
- **Export Capabilities**: Export data for analysis and reporting

### **5. Integration Features**
- **Existing System Integration**: Seamlessly integrates with current error handling
- **Notification System**: Integrates with existing notification infrastructure
- **Help System Integration**: Connects with existing help and documentation system
- **Database Integration**: Uses existing database infrastructure with new support tables

## 📁 File Structure

```
foodxchange/
├── models/
│   └── support.py                    # Support system database models
├── services/
│   ├── support_service.py            # Main support service
│   └── enhanced_error_handler.py     # Enhanced error handling
├── routes/
│   └── support_routes.py             # Support system API routes
├── templates/
│   └── pages/
│       ├── error_page.html           # Enhanced error page template
│       └── support_admin.html        # Admin dashboard template
└── create_support_tables.py          # Database migration script
```

## 🗄️ Database Schema

### **SupportTicket**
- `id`: Primary key
- `ticket_id`: Unique ticket identifier (e.g., TKT-20250101-ABC12345)
- `user_id`: User who created the ticket
- `title`: Ticket title
- `description`: Detailed description
- `category`: Error category (authentication, RFQ processing, etc.)
- `priority`: Priority level (low, medium, high, critical)
- `status`: Current status in workflow
- `assigned_to`: Team member assigned to ticket
- `error_id`: Link to error log (if applicable)
- `browser_info`: Browser and device information
- `created_at`, `updated_at`, `resolved_at`, `closed_at`: Timestamps

### **TicketStatusHistory**
- Tracks all status changes with timestamps and notes
- Links to user who made the change

### **TicketResponse**
- Support responses and internal notes
- Distinguishes between user-visible and internal responses

### **ErrorLog**
- Enhanced error logging with support integration
- Includes severity, category, browser info, and request context
- Links to support tickets when created

### **SupportAnalytics**
- Daily analytics snapshots
- Performance metrics and trends

### **UserFeedback**
- Bug reports and feature requests
- Separate from support tickets for different workflows

## 🚀 Quick Start

### **1. Database Setup**
```bash
cd foodxchange
python create_support_tables.py
```

### **2. Start the Application**
```bash
python main.py
```

### **3. Access Support System**
- **Admin Dashboard**: Visit `/support`
- **User Support Center**: Visit `/api/support/center`
- **API Documentation**: Visit `/docs` for full API documentation

## 📊 API Endpoints

### **Public Support Endpoints**
- `POST /api/support/tickets` - Create support ticket
- `GET /api/support/tickets` - Get user's tickets
- `GET /api/support/tickets/{ticket_id}` - Get ticket details
- `POST /api/support/tickets/{ticket_id}/responses` - Add response to ticket
- `POST /api/support/feedback` - Submit user feedback
- `GET /api/support/categories` - Get available categories
- `GET /api/support/priorities` - Get available priorities
- `GET /api/support/statuses` - Get available statuses

### **Admin Support Endpoints**
- `GET /api/support/admin/tickets` - Get all tickets (admin only)
- `PUT /api/support/admin/tickets/{ticket_id}/status` - Update ticket status
- `PUT /api/support/admin/tickets/{ticket_id}/assign` - Assign ticket
- `GET /api/support/admin/analytics` - Get support analytics
- `GET /api/support/admin/errors` - Get error logs
- `PUT /api/support/admin/errors/{error_id}/resolve` - Mark error as resolved

## 🎯 Usage Examples

### **Creating a Support Ticket**
```javascript
const ticketData = {
    title: "Login Issue",
    description: "Unable to log in with correct credentials",
    category: "authentication",
    priority: "high",
    steps_to_reproduce: "1. Go to login page\n2. Enter credentials\n3. Click login",
    expected_behavior: "Should log in successfully",
    actual_behavior: "Shows 'Invalid credentials' error"
};

fetch('/api/support/tickets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(ticketData)
});
```

### **Reporting a Bug**
```javascript
const bugReport = {
    feedback_type: "bug_report",
    title: "Button not working",
    description: "Submit button on form doesn't respond",
    category: "ui_ux_issue",
    priority: "medium",
    browser_info: {
        user_agent: navigator.userAgent,
        url: window.location.href
    }
};

fetch('/api/support/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bugReport)
});
```

## 🔧 Configuration

### **Error Handling Configuration**
The enhanced error handler automatically:
- Categorizes errors based on error type and message
- Determines severity based on keywords and context
- Creates support tickets for critical and high-severity errors
- Provides user-friendly error messages

### **Support Categories**
- `authentication` - Login, password, session issues
- `rfq_processing` - Request for quote processing issues
- `supplier_management` - Supplier-related issues
- `email_intelligence` - Email analysis and processing
- `payment_transaction` - Payment and billing issues
- `ui_ux_issue` - Interface and user experience issues
- `system_error` - General system errors
- `feature_request` - New feature requests
- `general_inquiry` - General questions and support

### **Priority Levels**
- `low` - Minor issues, cosmetic problems
- `medium` - Feature degradation, workaround available
- `high` - Feature broken, user blocked
- `critical` - System down, data loss

## 📈 Analytics and Reporting

The support system provides comprehensive analytics:
- **Ticket Volume**: Daily/weekly ticket counts
- **Resolution Times**: Average time to resolve tickets
- **Category Distribution**: Breakdown by issue type
- **Priority Distribution**: Breakdown by priority level
- **Error Trends**: System error patterns and frequency
- **User Satisfaction**: Feedback and resolution rates

## 🔒 Security and Access Control

- **User Authentication**: All endpoints require user authentication
- **Admin Access**: Admin-only endpoints for sensitive operations
- **Data Privacy**: Sensitive information is properly handled
- **Audit Trail**: All actions are logged with timestamps

## 🛠️ Customization

### **Adding New Categories**
1. Update `TicketCategory` enum in `models/support.py`
2. Add category patterns in `enhanced_error_handler.py`
3. Update frontend category lists

### **Custom Error Handling**
1. Extend `EnhancedErrorHandler` class
2. Add custom error patterns and categorization
3. Implement custom recovery suggestions

### **Custom Workflows**
1. Modify `TicketStatus` enum for custom statuses
2. Update status transition logic in `support_service.py`
3. Customize admin dashboard for new workflows

## 🐛 Troubleshooting

### **Common Issues**

**Database Connection Errors**
- Ensure database is running and accessible
- Check `DATABASE_URL` configuration
- Run migration script to create tables

**Missing Tables**
- Run `python create_support_tables.py`
- Check database permissions
- Verify SQLAlchemy configuration

**API Endpoint Errors**
- Check FastAPI application is running
- Verify route registration in `main.py`
- Check authentication and permissions

### **Debug Mode**
Enable debug mode for detailed error information:
```python
# In config.py or environment variables
DEBUG_MODE = True
```

## 📞 Support

For issues with the support system itself:
1. Check the logs in `logs/` directory
2. Review error messages in the admin dashboard
3. Check database connectivity and table structure
4. Verify all dependencies are installed

## 🔄 Updates and Maintenance

### **Regular Maintenance Tasks**
- Monitor error logs for patterns
- Review and resolve old tickets
- Update help articles and documentation
- Analyze support analytics for improvements
- Clean up old error logs and resolved tickets

### **Performance Optimization**
- Index frequently queried database columns
- Implement caching for analytics data
- Optimize database queries for large datasets
- Monitor API response times

## 📝 License

This support system is part of the FoodXchange platform and follows the same licensing terms.

---

**🎉 The FoodXchange Support System is now ready to provide comprehensive support for your platform!** 