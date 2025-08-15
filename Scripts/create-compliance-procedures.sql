-- =====================================================
-- FoodXchange Compliance Module Stored Procedures
-- Automates status roll-ups and workflow
-- =====================================================

USE fdxdb;
GO

-- =====================================================
-- 1. Instantiate a compliance process for a contract
-- =====================================================
CREATE OR ALTER PROCEDURE fdx.usp_Compliance_InstantiateForContract
  @ContractId UNIQUEIDENTIFIER,
  @Region NVARCHAR(40) = N'IL',
  @StartedBy UNIQUEIDENTIFIER = NULL
AS
BEGIN
  SET NOCOUNT ON;
  
  -- Check if compliance already exists
  IF EXISTS (SELECT 1 FROM fdx.ComplianceProcesses WHERE ContractId = @ContractId) 
  BEGIN
    SELECT ComplianceId FROM fdx.ComplianceProcesses WHERE ContractId = @ContractId;
    RETURN;
  END

  -- Get ProjectId from Contract (assuming fdx.Contracts exists)
  DECLARE @ProjectId UNIQUEIDENTIFIER;
  -- For now, using a placeholder since Contracts table might not exist yet
  SET @ProjectId = NEWID(); -- Replace with: SELECT ProjectId FROM fdx.Contracts WHERE ContractId = @ContractId
  
  -- Create compliance process
  DECLARE @Compliance TABLE (Id UNIQUEIDENTIFIER);
  INSERT INTO fdx.ComplianceProcesses (ContractId, ProjectId, OpenComments)
  OUTPUT inserted.ComplianceId INTO @Compliance(Id)
  VALUES (@ContractId, @ProjectId, N'Auto-created from contract');
  
  DECLARE @ComplianceId UNIQUEIDENTIFIER = (SELECT Id FROM @Compliance);
  
  -- Create stages from templates
  INSERT INTO fdx.ComplianceStages (ComplianceId, StageTemplateId, Code, SLA_Due)
  SELECT 
    @ComplianceId, 
    st.StageTemplateId, 
    st.Code,
    DATEADD(day, 
      CASE st.Code 
        WHEN 'KOSHER' THEN 7
        WHEN 'QA' THEN 14
        WHEN 'LABEL' THEN 10
        ELSE 7
      END, 
      SYSUTCDATETIME())
  FROM fdx.ComplianceStageTemplates st
  WHERE st.IsActive = 1 AND st.Code IN ('KOSHER','QA','LABEL')
  ORDER BY st.DisplayOrder;
  
  -- Create steps from templates
  -- Contract-scoped steps
  INSERT INTO fdx.ComplianceSteps (StageId, StepTemplateId, Title, Required, Scope, ContractLineId, DueDate)
  SELECT 
    s.StageId, 
    t.StepTemplateId, 
    t.Title, 
    t.Required, 
    t.Scope, 
    NULL,
    DATEADD(day, 5, GETDATE())
  FROM fdx.ComplianceStages s
  INNER JOIN fdx.ComplianceStageTemplates st ON st.StageTemplateId = s.StageTemplateId
  INNER JOIN fdx.ComplianceStepTemplates t ON t.StageTemplateId = st.StageTemplateId
  WHERE s.ComplianceId = @ComplianceId
    AND t.Scope = 'contract';
  
  -- Line-scoped steps (would need ContractLines table)
  -- Placeholder for line-scoped steps - uncomment when ContractLines exists
  /*
  INSERT INTO fdx.ComplianceSteps (StageId, StepTemplateId, Title, Required, Scope, ContractLineId, DueDate)
  SELECT 
    s.StageId, 
    t.StepTemplateId, 
    CONCAT(t.Title, ' - ', LEFT(cl.ProductName, 100)),
    t.Required, 
    t.Scope, 
    cl.ContractLineId,
    DATEADD(day, 5, GETDATE())
  FROM fdx.ComplianceStages s
  INNER JOIN fdx.ComplianceStageTemplates st ON st.StageTemplateId = s.StageTemplateId
  INNER JOIN fdx.ComplianceStepTemplates t ON t.StageTemplateId = st.StageTemplateId
  CROSS JOIN fdx.ContractLines cl
  WHERE s.ComplianceId = @ComplianceId
    AND t.Scope = 'line'
    AND cl.ContractId = @ContractId;
  */
  
  -- Create label project for the region
  INSERT INTO fdx.LabelProjects (ComplianceId, Region)
  VALUES (@ComplianceId, @Region);
  
  -- Return the new ComplianceId
  SELECT @ComplianceId AS ComplianceId;
END
GO

-- =====================================================
-- 2. Approve/Reject a step and roll up status
-- =====================================================
CREATE OR ALTER PROCEDURE fdx.usp_Compliance_ApproveStep
  @StepId UNIQUEIDENTIFIER,
  @Decision NVARCHAR(20),  -- 'approved' or 'rejected'
  @UserId UNIQUEIDENTIFIER = NULL,
  @Comment NVARCHAR(800) = NULL
AS
BEGIN
  SET NOCOUNT ON;
  
  -- Validate decision
  IF @Decision NOT IN ('approved', 'rejected')
  BEGIN
    THROW 50002, 'Invalid decision. Must be approved or rejected', 1;
  END
  
  -- Insert approval record
  INSERT INTO fdx.ComplianceApprovals (StepId, Decision, DecidedBy, Comment)
  VALUES (@StepId, @Decision, @UserId, @Comment);
  
  -- Update step status
  UPDATE fdx.ComplianceSteps
  SET 
    Status = @Decision,
    UpdatedAt = SYSUTCDATETIME()
  WHERE StepId = @StepId;
  
  -- Get stage info
  DECLARE @StageId UNIQUEIDENTIFIER;
  SELECT @StageId = StageId FROM fdx.ComplianceSteps WHERE StepId = @StepId;
  
  -- Recalculate stage status
  DECLARE @RequiredSteps INT, @ApprovedSteps INT, @RejectedSteps INT;
  
  SELECT 
    @RequiredSteps = COUNT(CASE WHEN Required = 1 THEN 1 END),
    @ApprovedSteps = COUNT(CASE WHEN Required = 1 AND Status = 'approved' THEN 1 END),
    @RejectedSteps = COUNT(CASE WHEN Status = 'rejected' THEN 1 END)
  FROM fdx.ComplianceSteps
  WHERE StageId = @StageId;
  
  -- Update stage status and progress
  UPDATE fdx.ComplianceStages
  SET 
    Status = CASE 
      WHEN @RejectedSteps > 0 THEN 'blocked'
      WHEN @RequiredSteps > 0 AND @ApprovedSteps = @RequiredSteps THEN 'approved'
      ELSE 'in-progress'
    END,
    Progress = CASE 
      WHEN @RequiredSteps > 0 THEN (@ApprovedSteps * 100) / @RequiredSteps
      ELSE 0
    END,
    ApprovedAt = CASE 
      WHEN @RequiredSteps > 0 AND @ApprovedSteps = @RequiredSteps THEN SYSUTCDATETIME()
      ELSE ApprovedAt
    END,
    ApprovedBy = CASE 
      WHEN @RequiredSteps > 0 AND @ApprovedSteps = @RequiredSteps THEN @UserId
      ELSE ApprovedBy
    END,
    UpdatedAt = SYSUTCDATETIME()
  WHERE StageId = @StageId;
  
  -- Get compliance info
  DECLARE @ComplianceId UNIQUEIDENTIFIER;
  SELECT @ComplianceId = ComplianceId FROM fdx.ComplianceStages WHERE StageId = @StageId;
  
  -- Recalculate overall compliance status
  DECLARE @TotalStages INT, @ApprovedStages INT, @BlockedStages INT;
  
  SELECT 
    @TotalStages = COUNT(*),
    @ApprovedStages = COUNT(CASE WHEN Status = 'approved' THEN 1 END),
    @BlockedStages = COUNT(CASE WHEN Status = 'blocked' THEN 1 END)
  FROM fdx.ComplianceStages
  WHERE ComplianceId = @ComplianceId;
  
  -- Update compliance process status
  UPDATE fdx.ComplianceProcesses
  SET 
    Status = CASE 
      WHEN @BlockedStages > 0 THEN 'blocked'
      WHEN @TotalStages > 0 AND @ApprovedStages = @TotalStages THEN 'approved'
      ELSE 'in-progress'
    END,
    ApprovedAt = CASE 
      WHEN @TotalStages > 0 AND @ApprovedStages = @TotalStages THEN SYSUTCDATETIME()
      ELSE ApprovedAt
    END,
    ApprovedBy = CASE 
      WHEN @TotalStages > 0 AND @ApprovedStages = @TotalStages THEN @UserId
      ELSE ApprovedBy
    END,
    UpdatedAt = SYSUTCDATETIME()
  WHERE ComplianceId = @ComplianceId;
  
  -- Return updated status
  SELECT 
    cp.ComplianceId,
    cp.Status AS ProcessStatus,
    cs.StageId,
    cs.Status AS StageStatus,
    cs.Progress AS StageProgress
  FROM fdx.ComplianceProcesses cp
  INNER JOIN fdx.ComplianceStages cs ON cs.StageId = @StageId
  WHERE cp.ComplianceId = @ComplianceId;
END
GO

-- =====================================================
-- 3. Get compliance summary for a contract
-- =====================================================
CREATE OR ALTER PROCEDURE fdx.usp_Compliance_GetSummary
  @ContractId UNIQUEIDENTIFIER
AS
BEGIN
  SET NOCOUNT ON;
  
  SELECT 
    cp.ComplianceId,
    cp.ContractId,
    cp.ProjectId,
    cp.Status,
    cp.StartedAt,
    cp.ApprovedAt,
    cp.OpenComments,
    -- Stage counts
    (SELECT COUNT(*) FROM fdx.ComplianceStages WHERE ComplianceId = cp.ComplianceId) AS TotalStages,
    (SELECT COUNT(*) FROM fdx.ComplianceStages WHERE ComplianceId = cp.ComplianceId AND Status = 'approved') AS ApprovedStages,
    -- Overall progress
    (SELECT AVG(Progress) FROM fdx.ComplianceStages WHERE ComplianceId = cp.ComplianceId) AS OverallProgress
  FROM fdx.ComplianceProcesses cp
  WHERE cp.ContractId = @ContractId;
  
  -- Return stages
  SELECT 
    cs.StageId,
    cs.Code,
    cs.Status,
    cs.Progress,
    cs.SLA_Due,
    cs.ApprovedAt,
    -- Step counts
    (SELECT COUNT(*) FROM fdx.ComplianceSteps WHERE StageId = cs.StageId AND Required = 1) AS RequiredSteps,
    (SELECT COUNT(*) FROM fdx.ComplianceSteps WHERE StageId = cs.StageId AND Required = 1 AND Status = 'approved') AS ApprovedSteps
  FROM fdx.ComplianceStages cs
  INNER JOIN fdx.ComplianceProcesses cp ON cp.ComplianceId = cs.ComplianceId
  WHERE cp.ContractId = @ContractId
  ORDER BY cs.CreatedAt;
END
GO

-- =====================================================
-- 4. Assign step to user
-- =====================================================
CREATE OR ALTER PROCEDURE fdx.usp_Compliance_AssignStep
  @StepId UNIQUEIDENTIFIER,
  @AssignedToUserId UNIQUEIDENTIFIER = NULL,
  @AssignedToExternalId UNIQUEIDENTIFIER = NULL
AS
BEGIN
  SET NOCOUNT ON;
  
  UPDATE fdx.ComplianceSteps
  SET 
    AssignedToUserId = @AssignedToUserId,
    AssignedToExternalId = @AssignedToExternalId,
    Status = CASE WHEN Status = 'open' THEN 'in-review' ELSE Status END,
    UpdatedAt = SYSUTCDATETIME()
  WHERE StepId = @StepId;
  
  SELECT StepId, Status, AssignedToUserId, AssignedToExternalId
  FROM fdx.ComplianceSteps
  WHERE StepId = @StepId;
END
GO

PRINT 'Compliance stored procedures created successfully!';
GO