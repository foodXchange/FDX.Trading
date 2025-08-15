-- =====================================================
-- Marketing and Public Site Tables
-- =====================================================

USE fdxdb;
GO

-- Marketing Leads table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'MarketingLeads' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.MarketingLeads (
        MarketingLeadId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Name NVARCHAR(200) NULL,
        Email NVARCHAR(200) NULL,
        Company NVARCHAR(200) NULL,
        Phone NVARCHAR(50) NULL,
        Message NVARCHAR(MAX) NULL,
        Source NVARCHAR(60) NULL,
        IpAddress NVARCHAR(100) NULL,
        UserAgent NVARCHAR(500) NULL,
        IsQualified BIT NOT NULL DEFAULT 0,
        IsContacted BIT NOT NULL DEFAULT 0,
        Notes NVARCHAR(500) NULL,
        CreatedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        ContactedAt DATETIMEOFFSET NULL,
        ContactedBy UNIQUEIDENTIFIER NULL
    );
    
    CREATE INDEX IX_MarketingLeads_Email ON fdx.MarketingLeads(Email);
    CREATE INDEX IX_MarketingLeads_Company ON fdx.MarketingLeads(Company);
    CREATE INDEX IX_MarketingLeads_CreatedAt ON fdx.MarketingLeads(CreatedAt DESC);
    CREATE INDEX IX_MarketingLeads_IsQualified ON fdx.MarketingLeads(IsQualified) WHERE IsQualified = 1;
END
GO

-- Newsletter Subscribers (optional)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'NewsletterSubscribers' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.NewsletterSubscribers (
        SubscriberId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Email NVARCHAR(200) NOT NULL,
        Name NVARCHAR(200) NULL,
        Company NVARCHAR(200) NULL,
        Topics NVARCHAR(500) NULL, -- JSON array of interests
        IsActive BIT NOT NULL DEFAULT 1,
        SubscribedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UnsubscribedAt DATETIMEOFFSET NULL,
        Source NVARCHAR(60) NULL,
        ConfirmationToken NVARCHAR(100) NULL,
        IsConfirmed BIT NOT NULL DEFAULT 0
    );
    
    CREATE UNIQUE INDEX UX_NewsletterSubscribers_Email ON fdx.NewsletterSubscribers(Email);
END
GO

-- Marketing Campaigns (for tracking)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'MarketingCampaigns' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.MarketingCampaigns (
        CampaignId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Name NVARCHAR(200) NOT NULL,
        Type NVARCHAR(50) NOT NULL, -- email/social/ppc/content
        Status NVARCHAR(20) NOT NULL DEFAULT 'draft', -- draft/active/paused/completed
        StartDate DATE NULL,
        EndDate DATE NULL,
        Budget DECIMAL(19,4) NULL,
        Spend DECIMAL(19,4) NULL,
        TargetLeads INT NULL,
        ActualLeads INT NULL,
        ConversionRate DECIMAL(5,2) NULL,
        CreatedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        CreatedBy UNIQUEIDENTIFIER NULL
    );
END
GO

-- Page Views / Analytics (simple tracking)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PageViews' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.PageViews (
        ViewId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        SessionId NVARCHAR(100) NOT NULL,
        PageUrl NVARCHAR(500) NOT NULL,
        Referrer NVARCHAR(500) NULL,
        UserAgent NVARCHAR(500) NULL,
        IpAddress NVARCHAR(100) NULL,
        Country NVARCHAR(2) NULL,
        ViewedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        TimeOnPage INT NULL, -- seconds
        UserId UNIQUEIDENTIFIER NULL -- if logged in
    );
    
    CREATE INDEX IX_PageViews_SessionId ON fdx.PageViews(SessionId);
    CREATE INDEX IX_PageViews_ViewedAt ON fdx.PageViews(ViewedAt DESC);
    CREATE INDEX IX_PageViews_PageUrl ON fdx.PageViews(PageUrl);
    
    -- Partition by month for performance (optional)
END
GO

-- Lead Scoring Rules
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'LeadScoringRules' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.LeadScoringRules (
        RuleId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Name NVARCHAR(200) NOT NULL,
        Condition NVARCHAR(500) NOT NULL, -- JSON or SQL expression
        Points INT NOT NULL,
        IsActive BIT NOT NULL DEFAULT 1,
        CreatedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    
    -- Sample scoring rules
    INSERT INTO fdx.LeadScoringRules (Name, Condition, Points) VALUES
    ('Enterprise Company', 'Company size > 100', 20),
    ('Food Industry', 'Industry = Food/Beverage', 15),
    ('Requested Demo', 'Action = demo_request', 25),
    ('Downloaded Whitepaper', 'Action = download', 10),
    ('Multiple Page Views', 'PageViews > 5', 5);
END
GO

-- View for Lead Analytics
CREATE OR ALTER VIEW fdx.vw_LeadAnalytics AS
SELECT 
    CONVERT(date, CreatedAt) AS Date,
    Source,
    COUNT(*) AS TotalLeads,
    SUM(CASE WHEN IsQualified = 1 THEN 1 ELSE 0 END) AS QualifiedLeads,
    SUM(CASE WHEN IsContacted = 1 THEN 1 ELSE 0 END) AS ContactedLeads,
    CAST(SUM(CASE WHEN IsQualified = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
        NULLIF(COUNT(*), 0) * 100 AS QualificationRate
FROM fdx.MarketingLeads
GROUP BY CONVERT(date, CreatedAt), Source;
GO

PRINT 'Marketing tables created successfully!';
GO