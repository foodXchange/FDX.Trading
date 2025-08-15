-- =====================================================
-- Invitation System Tables
-- =====================================================

USE fdxdb;
GO

-- Invitations table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Invitations' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.Invitations (
        InvitationId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Email NVARCHAR(200) NOT NULL,
        Name NVARCHAR(200) NOT NULL,
        Role NVARCHAR(50) NOT NULL, -- Admin, Buyer, Supplier, Expert
        Token NVARCHAR(100) NOT NULL,
        Status NVARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, accepted, expired, cancelled
        InvitedByUserId UNIQUEIDENTIFIER NOT NULL,
        InvitedByName NVARCHAR(200) NULL,
        CreatedAt DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        ExpiresAt DATETIMEOFFSET NOT NULL,
        AcceptedAt DATETIMEOFFSET NULL,
        AcceptedByUserId UNIQUEIDENTIFIER NULL,
        CancelledAt DATETIMEOFFSET NULL,
        ResendCount INT NULL DEFAULT 0,
        LastResentAt DATETIMEOFFSET NULL,
        Notes NVARCHAR(500) NULL
    );
    
    CREATE UNIQUE INDEX UX_Invitations_Token ON fdx.Invitations(Token);
    CREATE INDEX IX_Invitations_Email ON fdx.Invitations(Email);
    CREATE INDEX IX_Invitations_Status ON fdx.Invitations(Status);
    CREATE INDEX IX_Invitations_ExpiresAt ON fdx.Invitations(ExpiresAt);
    CREATE INDEX IX_Invitations_InvitedByUserId ON fdx.Invitations(InvitedByUserId);
END
GO

-- View for invitation analytics
CREATE OR ALTER VIEW fdx.vw_InvitationAnalytics AS
SELECT 
    Role,
    Status,
    COUNT(*) AS InvitationCount,
    SUM(CASE WHEN Status = 'accepted' THEN 1 ELSE 0 END) AS AcceptedCount,
    SUM(CASE WHEN Status = 'pending' THEN 1 ELSE 0 END) AS PendingCount,
    SUM(CASE WHEN Status = 'expired' THEN 1 ELSE 0 END) AS ExpiredCount,
    SUM(CASE WHEN Status = 'cancelled' THEN 1 ELSE 0 END) AS CancelledCount,
    CAST(SUM(CASE WHEN Status = 'accepted' THEN 1 ELSE 0 END) AS FLOAT) / 
        NULLIF(COUNT(*), 0) * 100 AS AcceptanceRate,
    AVG(DATEDIFF(HOUR, CreatedAt, AcceptedAt)) AS AvgHoursToAccept
FROM fdx.Invitations
GROUP BY Role, Status;
GO

-- Stored procedure to create invitation
CREATE OR ALTER PROCEDURE fdx.sp_CreateInvitation
    @Email NVARCHAR(200),
    @Name NVARCHAR(200),
    @Role NVARCHAR(50),
    @InvitedByUserId UNIQUEIDENTIFIER,
    @InvitedByName NVARCHAR(200) = NULL,
    @Notes NVARCHAR(500) = NULL,
    @InvitationId UNIQUEIDENTIFIER OUTPUT,
    @Token NVARCHAR(100) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if user already exists
    IF EXISTS (SELECT 1 FROM fdx.FdxUsers WHERE Email = @Email)
    BEGIN
        THROW 50001, 'User with this email already exists', 1;
    END
    
    -- Check if pending invitation exists
    IF EXISTS (SELECT 1 FROM fdx.Invitations WHERE Email = @Email AND Status = 'pending')
    BEGIN
        THROW 50002, 'Pending invitation already exists for this email', 1;
    END
    
    -- Generate token
    SET @Token = REPLACE(NEWID(), '-', '') + REPLACE(NEWID(), '-', '');
    SET @InvitationId = NEWID();
    
    -- Create invitation
    INSERT INTO fdx.Invitations (
        InvitationId, Email, Name, Role, Token, Status,
        InvitedByUserId, InvitedByName, CreatedAt, ExpiresAt, Notes
    )
    VALUES (
        @InvitationId, @Email, @Name, @Role, @Token, 'pending',
        @InvitedByUserId, @InvitedByName, SYSUTCDATETIME(), 
        DATEADD(DAY, 7, SYSUTCDATETIME()), @Notes
    );
    
    RETURN 0;
END
GO

-- Stored procedure to accept invitation
CREATE OR ALTER PROCEDURE fdx.sp_AcceptInvitation
    @Token NVARCHAR(100),
    @UserId UNIQUEIDENTIFIER,
    @Success BIT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @InvitationId UNIQUEIDENTIFIER;
    DECLARE @Email NVARCHAR(200);
    DECLARE @Name NVARCHAR(200);
    DECLARE @Role NVARCHAR(50);
    
    -- Find invitation
    SELECT @InvitationId = InvitationId, @Email = Email, @Name = Name, @Role = Role
    FROM fdx.Invitations
    WHERE Token = @Token AND Status = 'pending';
    
    IF @InvitationId IS NULL
    BEGIN
        SET @Success = 0;
        RETURN;
    END
    
    -- Check if expired
    IF EXISTS (SELECT 1 FROM fdx.Invitations WHERE InvitationId = @InvitationId AND ExpiresAt < SYSUTCDATETIME())
    BEGIN
        UPDATE fdx.Invitations 
        SET Status = 'expired' 
        WHERE InvitationId = @InvitationId;
        
        SET @Success = 0;
        RETURN;
    END
    
    BEGIN TRANSACTION;
    
    -- Update invitation
    UPDATE fdx.Invitations
    SET Status = 'accepted',
        AcceptedAt = SYSUTCDATETIME(),
        AcceptedByUserId = @UserId
    WHERE InvitationId = @InvitationId;
    
    -- Create or update user
    IF NOT EXISTS (SELECT 1 FROM fdx.FdxUsers WHERE Email = @Email)
    BEGIN
        INSERT INTO fdx.FdxUsers (UserId, Email, Name, Role, IsActive, CreatedAt)
        VALUES (@UserId, @Email, @Name, @Role, 1, SYSUTCDATETIME());
    END
    ELSE
    BEGIN
        UPDATE fdx.FdxUsers
        SET Role = @Role, IsActive = 1
        WHERE Email = @Email;
    END
    
    COMMIT TRANSACTION;
    
    SET @Success = 1;
    RETURN;
END
GO

-- Stored procedure to cleanup expired invitations
CREATE OR ALTER PROCEDURE fdx.sp_CleanupExpiredInvitations
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE fdx.Invitations
    SET Status = 'expired'
    WHERE Status = 'pending' 
        AND ExpiresAt < SYSUTCDATETIME();
    
    RETURN @@ROWCOUNT;
END
GO

PRINT 'Invitation tables created successfully!';
GO