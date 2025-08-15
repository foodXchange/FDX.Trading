-- =====================================================
-- FoodXchange Compliance Module Schema
-- Gates progression to Ordering until 100% complete
-- =====================================================

USE fdxdb;
GO

-- Create fdx schema if not exists
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'fdx')
BEGIN
    EXEC('CREATE SCHEMA fdx');
END
GO

-- =====================================================
-- B1. Workflow containers & templates
-- =====================================================

-- 1) Compliance process instance (per contract)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ComplianceProcesses' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ComplianceProcesses (
        ComplianceId         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ContractId           UNIQUEIDENTIFIER NOT NULL,
        ProjectId            UNIQUEIDENTIFIER NOT NULL,
        Status               NVARCHAR(20) NOT NULL DEFAULT 'in-progress', -- in-progress/approved/rejected/blocked
        StartedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        ApprovedAt           DATETIMEOFFSET NULL,
        ApprovedBy           UNIQUEIDENTIFIER NULL,
        OpenComments         NVARCHAR(MAX) NULL,
        CreatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ComplianceProcesses_Contract ON fdx.ComplianceProcesses(ContractId);
    CREATE INDEX IX_ComplianceProcesses_Status ON fdx.ComplianceProcesses(Status);
END
GO

-- 2) Stage template library (admin-maintained)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ComplianceStageTemplates' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ComplianceStageTemplates (
        StageTemplateId      UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Code                 NVARCHAR(40) NOT NULL UNIQUE,  -- 'KOSHER' | 'QA' | 'LABEL'
        Name                 NVARCHAR(100) NOT NULL,
        DisplayOrder         INT NOT NULL DEFAULT 0,
        IsActive             BIT NOT NULL DEFAULT 1,
        CreatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO

-- 3) Step template library
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ComplianceStepTemplates' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ComplianceStepTemplates (
        StepTemplateId       UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        StageTemplateId      UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceStageTemplates(StageTemplateId),
        StepCode             NVARCHAR(60) NOT NULL,    -- e.g., 'KOSHER_CERT_UPLOAD'
        Title                NVARCHAR(200) NOT NULL,
        Description          NVARCHAR(1000) NULL,
        Required             BIT NOT NULL DEFAULT 1,
        Scope                NVARCHAR(20) NOT NULL DEFAULT 'line', -- 'contract'|'line'
        EvidenceType         NVARCHAR(30) NULL,        -- 'file'|'form'|'checklist'
        DisplayOrder         INT NOT NULL DEFAULT 0,
        CreatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ComplianceStepTemplates_Stage ON fdx.ComplianceStepTemplates(StageTemplateId);
END
GO

-- 4) Process stages (instantiated from templates)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ComplianceStages' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ComplianceStages (
        StageId              UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ComplianceId         UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceProcesses(ComplianceId),
        StageTemplateId      UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceStageTemplates(StageTemplateId),
        Code                 NVARCHAR(40) NOT NULL,    -- cached from template, e.g., KOSHER
        Status               NVARCHAR(20) NOT NULL DEFAULT 'in-progress', -- in-progress/approved/rejected/blocked
        StartedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        ApprovedAt           DATETIMEOFFSET NULL,
        ApprovedBy           UNIQUEIDENTIFIER NULL,
        SLA_Due              DATETIMEOFFSET NULL,
        Progress             INT NOT NULL DEFAULT 0,    -- percentage complete
        CreatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ComplianceStages_Compliance ON fdx.ComplianceStages(ComplianceId);
    CREATE INDEX IX_ComplianceStages_Code_Status ON fdx.ComplianceStages(Code, Status);
END
GO

-- 5) Stage steps (instantiated from templates)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ComplianceSteps' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ComplianceSteps (
        StepId               UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        StageId              UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceStages(StageId),
        StepTemplateId       UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceStepTemplates(StepTemplateId),
        Title                NVARCHAR(200) NOT NULL,
        Required             BIT NOT NULL,
        Scope                NVARCHAR(20) NOT NULL,        -- 'contract'|'line'
        ContractLineId       UNIQUEIDENTIFIER NULL,
        Status               NVARCHAR(20) NOT NULL DEFAULT 'open',  -- open/in-review/approved/rejected
        AssignedToUserId     UNIQUEIDENTIFIER NULL,         -- internal
        AssignedToExternalId UNIQUEIDENTIFIER NULL,         -- external expert/agency
        DueDate              DATE NULL,
        Notes                NVARCHAR(MAX) NULL,
        CreatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ComplianceSteps_Stage ON fdx.ComplianceSteps(StageId, Status);
    CREATE INDEX IX_ComplianceSteps_ContractLine ON fdx.ComplianceSteps(ContractLineId);
END
GO

-- 6) Evidence files (blob URIs)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ComplianceEvidence' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ComplianceEvidence (
        EvidenceId           UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        StepId               UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceSteps(StepId),
        BlobUri              NVARCHAR(800) NOT NULL,
        FileName             NVARCHAR(300) NOT NULL,
        ContentType          NVARCHAR(100) NULL,
        FileSize             BIGINT NULL,
        UploadedBy           UNIQUEIDENTIFIER NULL,
        UploadedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        VerifiedAt           DATETIMEOFFSET NULL,
        VerifiedBy           UNIQUEIDENTIFIER NULL
    );
    CREATE INDEX IX_ComplianceEvidence_Step ON fdx.ComplianceEvidence(StepId);
END
GO

-- 7) Approvals (explicit sign-offs per step)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ComplianceApprovals' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ComplianceApprovals (
        ApprovalId           UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        StepId               UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceSteps(StepId),
        Decision             NVARCHAR(20) NOT NULL, -- approved/rejected
        DecidedBy            UNIQUEIDENTIFIER NULL,
        DecidedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        Comment              NVARCHAR(800) NULL
    );
    CREATE INDEX IX_ComplianceApprovals_Step ON fdx.ComplianceApprovals(StepId);
END
GO

-- =====================================================
-- B2. Participants (internal & external) and assignments
-- =====================================================

-- External partner organizations (rabbinate, QA labs, graphic agencies)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ExternalOrgs' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ExternalOrgs (
        ExternalOrgId        UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        Name                 NVARCHAR(300) NOT NULL,
        Type                 NVARCHAR(40) NOT NULL,   -- 'RABBINATE'|'QA_LAB'|'AGENCY'|...
        CountryCode          CHAR(2) NULL,
        Website              NVARCHAR(500) NULL,
        ContactEmail         NVARCHAR(300) NULL,
        ContactPhone         NVARCHAR(50) NULL,
        Active               BIT NOT NULL DEFAULT 1,
        CreatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ExternalOrgs_Type ON fdx.ExternalOrgs(Type);
END
GO

-- External users from partner organizations
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ExternalUsers' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ExternalUsers (
        ExternalUserId       UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ExternalOrgId        UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ExternalOrgs(ExternalOrgId),
        FullName             NVARCHAR(200) NOT NULL,
        Email                NVARCHAR(300) NULL,
        Phone                NVARCHAR(50) NULL,
        Title                NVARCHAR(100) NULL,
        Active               BIT NOT NULL DEFAULT 1,
        CreatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_ExternalUsers_Org ON fdx.ExternalUsers(ExternalOrgId);
END
GO

-- Who's on this contract's compliance team
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ComplianceParticipants' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.ComplianceParticipants (
        ParticipantId        UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ComplianceId         UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceProcesses(ComplianceId),
        Role                 NVARCHAR(40) NOT NULL,  -- 'buyer_qa_manager','buyer_kosher_mgr','supplier_qc','rabbi','qa_advisor','agency_pm'
        UserId               UNIQUEIDENTIFIER NULL,  -- internal user
        ExternalUserId       UNIQUEIDENTIFIER NULL REFERENCES fdx.ExternalUsers(ExternalUserId),
        JoinedAt             DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT CK_ComplianceParticipants_User CHECK (
            (UserId IS NOT NULL AND ExternalUserId IS NULL) OR 
            (UserId IS NULL AND ExternalUserId IS NOT NULL)
        )
    );
    CREATE INDEX IX_ComplianceParticipants_Compliance ON fdx.ComplianceParticipants(ComplianceId);
END
GO

-- =====================================================
-- B3. Domain specifics: Kosher, QA, Labeling
-- =====================================================

-- Kosher certification record (supplier-site or product-specific)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'KosherCertifications' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.KosherCertifications (
        KosherCertId         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        SupplierId           UNIQUEIDENTIFIER NOT NULL,
        ProductId            UNIQUEIDENTIFIER NULL,
        Authority            NVARCHAR(120) NOT NULL,     -- OU, Badatz, OK, Triangle-K, etc.
        CertificateNumber    NVARCHAR(120) NULL,
        SupervisionType      NVARCHAR(40) NULL,          -- Pareve/Dairy/Meat
        HalavYisrael         BIT NULL,
        PassoverStatus       NVARCHAR(40) NULL,          -- 'Kosher for Passover'|'Kitniyot'|'Not for Passover'
        ValidFrom            DATE NULL,
        ValidTo              DATE NULL,
        Remarks              NVARCHAR(800) NULL,
        CreatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_KosherCertifications_Supplier_Product ON fdx.KosherCertifications(SupplierId, ProductId);
END
GO

-- Kosher certificate files
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'KosherCertFiles' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.KosherCertFiles (
        KosherCertFileId     UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        KosherCertId         UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.KosherCertifications(KosherCertId),
        BlobUri              NVARCHAR(800) NOT NULL,
        FileName             NVARCHAR(300) NOT NULL,
        UploadedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_KosherCertFiles_Cert ON fdx.KosherCertFiles(KosherCertId);
END
GO

-- QA test plan & results (per contract line or product)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'QATestPlans' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.QATestPlans (
        QATestPlanId         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ContractLineId       UNIQUEIDENTIFIER NULL,
        ProductId            UNIQUEIDENTIFIER NULL,
        Title                NVARCHAR(200) NOT NULL,
        LabExternalOrgId     UNIQUEIDENTIFIER NULL REFERENCES fdx.ExternalOrgs(ExternalOrgId),
        Status               NVARCHAR(20) NOT NULL DEFAULT 'planned', -- planned/in-progress/completed
        CreatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_QATestPlans_ContractLine ON fdx.QATestPlans(ContractLineId);
END
GO

-- Individual QA tests
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'QATests' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.QATests (
        QATestId             UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        QATestPlanId         UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.QATestPlans(QATestPlanId),
        TestCode             NVARCHAR(80) NOT NULL,     -- e.g., "MICRO_TOTAL_PLATE"
        Parameter            NVARCHAR(200) NOT NULL,    -- e.g., "TPC (CFU/g)"
        SpecMin              DECIMAL(18,6) NULL,
        SpecMax              DECIMAL(18,6) NULL,
        Result               DECIMAL(18,6) NULL,
        Unit                 NVARCHAR(40) NULL,
        ResultDate           DATE NULL,
        Status               NVARCHAR(20) NOT NULL DEFAULT 'pending', -- pending/pass/fail
        CreatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_QATests_Plan_Status ON fdx.QATests(QATestPlanId, Status);
END
GO

-- Labeling/Graphics project (per contract)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'LabelProjects' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.LabelProjects (
        LabelProjectId       UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        ComplianceId         UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.ComplianceProcesses(ComplianceId),
        Region               NVARCHAR(40) NOT NULL,     -- 'EU','IL','US',...
        Status               NVARCHAR(20) NOT NULL DEFAULT 'in-progress',
        CreatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
        UpdatedAt            DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_LabelProjects_Compliance ON fdx.LabelProjects(ComplianceId);
END
GO

-- Label artifacts (artwork, proofs, etc.)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'LabelArtifacts' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.LabelArtifacts (
        LabelArtifactId      UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        LabelProjectId       UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.LabelProjects(LabelProjectId),
        ArtifactType         NVARCHAR(40) NOT NULL,     -- 'layout','ingredient_list','allergen_panel','nutrition_table','barcode','claims'
        BlobUri              NVARCHAR(800) NOT NULL,
        FileName             NVARCHAR(300) NOT NULL,
        Version              INT NOT NULL DEFAULT 1,
        UploadedBy           UNIQUEIDENTIFIER NULL,
        UploadedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_LabelArtifacts_Project ON fdx.LabelArtifacts(LabelProjectId);
END
GO

-- Label approvals
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'LabelApprovals' AND schema_id = SCHEMA_ID('fdx'))
BEGIN
    CREATE TABLE fdx.LabelApprovals (
        LabelApprovalId      UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        LabelProjectId       UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.LabelProjects(LabelProjectId),
        ApprovedBy           UNIQUEIDENTIFIER NULL,
        ApprovedAt           DATETIMEOFFSET NULL,
        Decision             NVARCHAR(20) NOT NULL DEFAULT 'pending', -- pending/approved/rejected
        Comment              NVARCHAR(800) NULL
    );
    CREATE INDEX IX_LabelApprovals_Project ON fdx.LabelApprovals(LabelProjectId);
END
GO

-- =====================================================
-- Seed initial templates
-- =====================================================

-- Insert stage templates
IF NOT EXISTS (SELECT 1 FROM fdx.ComplianceStageTemplates WHERE Code = 'KOSHER')
BEGIN
    INSERT INTO fdx.ComplianceStageTemplates (Code, Name, DisplayOrder) VALUES
    ('KOSHER', 'Kosher Certification', 1),
    ('QA', 'Quality Assurance', 2),
    ('LABEL', 'Labeling & Graphics', 3);
END
GO

-- Insert Kosher step templates
DECLARE @kosherId UNIQUEIDENTIFIER = (SELECT StageTemplateId FROM fdx.ComplianceStageTemplates WHERE Code = 'KOSHER');
IF @kosherId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM fdx.ComplianceStepTemplates WHERE StageTemplateId = @kosherId)
BEGIN
    INSERT INTO fdx.ComplianceStepTemplates (StageTemplateId, StepCode, Title, Description, Required, Scope, EvidenceType, DisplayOrder) VALUES
    (@kosherId, 'KOSHER_CERT_UPLOAD', 'Upload valid kosher certificate', 'Upload the current kosher certificate from approved authority', 1, 'contract', 'file', 1),
    (@kosherId, 'KOSHER_FORM', 'Fill kosher details', 'Enter authority, supervision type, and validity dates', 1, 'contract', 'form', 2),
    (@kosherId, 'KOSHER_LABEL_MARKING', 'Confirm label kosher marking', 'Verify kosher symbols match certificate', 1, 'line', 'checklist', 3),
    (@kosherId, 'KOSHER_INGREDIENTS', 'Verify ingredient kosher status', 'Confirm all ingredients are kosher certified', 1, 'line', 'checklist', 4),
    (@kosherId, 'RABBI_APPROVAL', 'Rabbi final approval', 'Obtain rabbi sign-off on kosher compliance', 1, 'contract', 'form', 5);
END
GO

-- Insert QA step templates
DECLARE @qaId UNIQUEIDENTIFIER = (SELECT StageTemplateId FROM fdx.ComplianceStageTemplates WHERE Code = 'QA');
IF @qaId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM fdx.ComplianceStepTemplates WHERE StageTemplateId = @qaId)
BEGIN
    INSERT INTO fdx.ComplianceStepTemplates (StageTemplateId, StepCode, Title, Description, Required, Scope, EvidenceType, DisplayOrder) VALUES
    (@qaId, 'QA_PLAN', 'Create QA test plan', 'Define required tests and parameters', 1, 'line', 'form', 1),
    (@qaId, 'QA_SPECS', 'Upload product specifications', 'Technical specifications and COA', 1, 'line', 'file', 2),
    (@qaId, 'QA_MICRO', 'Microbiological test results', 'TPC, Salmonella, E.coli, etc.', 1, 'line', 'form', 3),
    (@qaId, 'QA_CHEMICAL', 'Chemical test results', 'Heavy metals, pesticides, aflatoxins', 1, 'line', 'form', 4),
    (@qaId, 'QA_ALLERGEN', 'Allergen test results', 'Confirm allergen declaration accuracy', 1, 'line', 'form', 5),
    (@qaId, 'QA_SHELF_LIFE', 'Shelf life validation', 'Stability and shelf life testing', 1, 'line', 'file', 6);
END
GO

-- Insert Label step templates
DECLARE @labelId UNIQUEIDENTIFIER = (SELECT StageTemplateId FROM fdx.ComplianceStageTemplates WHERE Code = 'LABEL');
IF @labelId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM fdx.ComplianceStepTemplates WHERE StageTemplateId = @labelId)
BEGIN
    INSERT INTO fdx.ComplianceStepTemplates (StageTemplateId, StepCode, Title, Description, Required, Scope, EvidenceType, DisplayOrder) VALUES
    (@labelId, 'LBL_ARTWORK_UPLOAD', 'Upload artwork/proofs', 'Final packaging artwork and label proofs', 1, 'contract', 'file', 1),
    (@labelId, 'LBL_INGREDIENTS', 'Verify ingredient list', 'Ensure accuracy and regulatory compliance', 1, 'line', 'checklist', 2),
    (@labelId, 'LBL_ALLERGENS', 'Confirm allergen panel', 'Verify allergen declarations are complete', 1, 'line', 'checklist', 3),
    (@labelId, 'LBL_NUTRITION', 'Validate nutrition table', 'Check nutrition facts accuracy', 1, 'line', 'checklist', 4),
    (@labelId, 'LBL_CLAIMS', 'Claims & regulatory check', 'Verify all claims are substantiated', 1, 'line', 'checklist', 5),
    (@labelId, 'LBL_BARCODE', 'Barcode verification', 'Confirm barcode accuracy and readability', 1, 'line', 'checklist', 6),
    (@labelId, 'LBL_FINAL_APPROVAL', 'Final buyer approval', 'Buyer signs off on labeling', 1, 'contract', 'form', 7);
END
GO

PRINT 'Compliance module schema created successfully!';
GO