-- FDX Project/Console Schema with Request Integration
-- Run this on Azure SQL Database: fdxdb

-- 1. Add ProjectId to Requests if missing
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Name = 'ProjectId' AND Object_ID = Object_ID('dbo.Requests'))
BEGIN
    ALTER TABLE dbo.Requests
    ADD ProjectId UNIQUEIDENTIFIER NULL;
END
GO

-- 2. Create Projects table if not exists
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Projects')
BEGIN
    CREATE TABLE dbo.Projects (
        ProjectId UNIQUEIDENTIFIER NOT NULL PRIMARY KEY DEFAULT NEWID(),
        ProjectCode NVARCHAR(50) NOT NULL,
        Name NVARCHAR(300) NOT NULL,
        CreatedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        CreatedBy NVARCHAR(100) NULL,
        ModifiedAt DATETIMEOFFSET NULL,
        ModifiedBy NVARCHAR(100) NULL,
        IsDeleted BIT NOT NULL DEFAULT 0
    );
    
    CREATE UNIQUE INDEX UX_Projects_ProjectCode ON dbo.Projects(ProjectCode);
    CREATE INDEX IX_Projects_CreatedAt ON dbo.Projects(CreatedAt DESC);
END
GO

-- 3. Create sequence for ProjectCode generation
IF NOT EXISTS (SELECT * FROM sys.sequences WHERE name = 'seq_ProjectNumber')
BEGIN
    CREATE SEQUENCE dbo.seq_ProjectNumber 
    START WITH 100001 
    INCREMENT BY 1
    MINVALUE 100001
    MAXVALUE 999999
    CYCLE;
END
GO

-- 4. Create ProjectMembers table for role-based access
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'ProjectMembers')
BEGIN
    CREATE TABLE dbo.ProjectMembers (
        ProjectMemberId INT IDENTITY(1,1) PRIMARY KEY,
        ProjectId UNIQUEIDENTIFIER NOT NULL,
        
        -- Support both legacy BuyerId (INT) and new UserId (GUID)
        UserId UNIQUEIDENTIFIER NULL,
        BuyerId INT NULL,
        
        RoleInProject NVARCHAR(40) NOT NULL, -- buyer/supplier/agent/admin
        JoinedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        IsActive BIT NOT NULL DEFAULT 1,
        
        CONSTRAINT FK_ProjectMembers_Projects 
            FOREIGN KEY (ProjectId) REFERENCES dbo.Projects(ProjectId),
        
        -- Ensure exactly one identity column is set
        CONSTRAINT CK_ProjectMembers_OneIdentity CHECK (
            (UserId IS NOT NULL AND BuyerId IS NULL) OR
            (UserId IS NULL AND BuyerId IS NOT NULL)
        )
    );
    
    CREATE INDEX IX_ProjectMembers_ProjectId ON dbo.ProjectMembers(ProjectId);
    CREATE INDEX IX_ProjectMembers_UserId ON dbo.ProjectMembers(UserId) WHERE UserId IS NOT NULL;
    CREATE INDEX IX_ProjectMembers_BuyerId ON dbo.ProjectMembers(BuyerId) WHERE BuyerId IS NOT NULL;
    CREATE INDEX IX_ProjectMembers_Role ON dbo.ProjectMembers(RoleInProject);
    
    -- Unique constraint to prevent duplicate memberships
    CREATE UNIQUE INDEX UX_ProjectMembers_Unique 
        ON dbo.ProjectMembers(ProjectId, ISNULL(CAST(UserId AS NVARCHAR(36)), ''), ISNULL(CAST(BuyerId AS NVARCHAR(10)), ''));
END
GO

-- 5. Backfill: Create Projects for existing Requests without ProjectId
INSERT INTO dbo.Projects (ProjectId, ProjectCode, Name, CreatedAt)
SELECT 
    NEWID(),
    CONCAT('FDX-', YEAR(GETUTCDATE()), '-', FORMAT(NEXT VALUE FOR dbo.seq_ProjectNumber, '000000')),
    r.Title,
    r.CreatedAt
FROM dbo.Requests r
WHERE r.ProjectId IS NULL;
GO

-- 6. Link existing Requests to their new Projects
UPDATE r
SET r.ProjectId = p.ProjectId
FROM dbo.Requests r
INNER JOIN (
    SELECT 
        r2.Id,
        p2.ProjectId,
        ROW_NUMBER() OVER (PARTITION BY r2.Id ORDER BY p2.CreatedAt DESC) as rn
    FROM dbo.Requests r2
    INNER JOIN dbo.Projects p2 ON p2.Name = r2.Title
    WHERE r2.ProjectId IS NULL
) p ON r.Id = p.Id AND p.rn = 1;
GO

-- 7. Add ProjectMembers for existing Request buyers
INSERT INTO dbo.ProjectMembers (ProjectId, BuyerId, RoleInProject, JoinedAt)
SELECT DISTINCT
    r.ProjectId,
    r.BuyerId,
    'buyer',
    r.CreatedAt
FROM dbo.Requests r
WHERE r.ProjectId IS NOT NULL
    AND r.BuyerId IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM dbo.ProjectMembers pm 
        WHERE pm.ProjectId = r.ProjectId 
            AND pm.BuyerId = r.BuyerId
    );
GO

-- 8. Add foreign key constraint (after backfill)
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Requests_Projects')
BEGIN
    ALTER TABLE dbo.Requests
    ADD CONSTRAINT FK_Requests_Projects 
        FOREIGN KEY (ProjectId) REFERENCES dbo.Projects(ProjectId);
END
GO

-- 9. Verification queries
PRINT 'Projects created: ' + CAST((SELECT COUNT(*) FROM dbo.Projects) AS NVARCHAR(10));
PRINT 'Requests linked: ' + CAST((SELECT COUNT(*) FROM dbo.Requests WHERE ProjectId IS NOT NULL) AS NVARCHAR(10));
PRINT 'Project members: ' + CAST((SELECT COUNT(*) FROM dbo.ProjectMembers) AS NVARCHAR(10));

-- Sample data check
SELECT TOP 5
    p.ProjectCode,
    p.Name,
    r.RequestNumber,
    r.Title,
    pm.RoleInProject,
    pm.BuyerId
FROM dbo.Projects p
INNER JOIN dbo.Requests r ON r.ProjectId = p.ProjectId
LEFT JOIN dbo.ProjectMembers pm ON pm.ProjectId = p.ProjectId
ORDER BY p.CreatedAt DESC;