-- =========================
-- CONTRACT MANAGEMENT SCHEMA
-- Extends existing FoodXchange platform with contract workflow
-- =========================

-- CONTRACT header table
CREATE TABLE fdx.Contracts (
    ContractId           UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ProjectId            UNIQUEIDENTIFIER NOT NULL, -- References dbo.Projects(ProjectId)
    RequestId            INT NULL REFERENCES dbo.Requests(Id),
    ProposalId           UNIQUEIDENTIFIER NULL, -- References fdx.Proposals(ProposalId) when implemented

    BuyerId              INT NULL, -- Legacy buyer id (INT)
    BuyerUserId          UNIQUEIDENTIFIER NULL, -- Platform user (future)
    SupplierId           INT NOT NULL REFERENCES dbo.Users(Id), -- Using existing Users table

    Title                NVARCHAR(300) NOT NULL,
    Description          NVARCHAR(MAX) NULL,
    AutoNumber           NVARCHAR(50) NULL,
    Currency             CHAR(3) NOT NULL DEFAULT 'USD',

    Status               NVARCHAR(30) NOT NULL DEFAULT 'draft',
    EffectiveFrom        DATE NULL,
    EffectiveTo          DATE NULL,

    SubtotalAmount       DECIMAL(19,4) NULL,
    DiscountAmount       DECIMAL(19,4) NULL,
    FreightAmount        DECIMAL(19,4) NULL,
    TaxAmount            DECIMAL(19,4) NULL,
    TotalAmount          DECIMAL(19,4) NULL,

    FirstCreated         DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
    LastUpdated          DATETIMEOFFSET NULL,
    OpenComments         NVARCHAR(MAX) NULL,

    CreatedBy            INT NULL REFERENCES dbo.Users(Id),
    FilesNote            NVARCHAR(MAX) NULL
);

-- CONTRACT lines (derived from accepted proposal lines)
CREATE TABLE fdx.ContractLines (
    ContractLineId       UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ContractId           UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Contracts(ContractId),

    ProposalLineId       UNIQUEIDENTIFIER NULL, -- References fdx.ProposalLines when implemented
    RequestItemId        INT NULL REFERENCES dbo.RequestItems(Id),
    ProductId            INT NULL REFERENCES dbo.Products(Id),

    ProductName          NVARCHAR(300) NOT NULL,
    Unit                 NVARCHAR(20) NOT NULL,
    Quantity             DECIMAL(18,3) NOT NULL,
    Currency             CHAR(3) NOT NULL,
    Incoterms            NVARCHAR(10) NOT NULL,
    UnitPrice            DECIMAL(19,4) NOT NULL,
    LineTotal            AS (ROUND(ISNULL(Quantity,0) * ISNULL(UnitPrice,0), 4)) PERSISTED
);

-- Contract file attachments
CREATE TABLE fdx.ContractFiles (
    ContractFileId       UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ContractId           UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Contracts(ContractId),
    BlobUri              NVARCHAR(800) NOT NULL,
    FileName             NVARCHAR(300) NOT NULL,
    ContentType          NVARCHAR(100) NULL,
    UploadedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
    UploadedBy           INT NULL REFERENCES dbo.Users(Id)
);

-- Buyer acceptance of proposal lines (price agreement checkpoint)
CREATE TABLE fdx.ProposalLineAcceptances (
    AcceptanceId         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ProposalLineId       UNIQUEIDENTIFIER NOT NULL, -- References fdx.ProposalLines
    RequestItemId        INT NULL REFERENCES dbo.RequestItems(Id), -- Fallback to existing data
    BuyerUserId          INT NULL REFERENCES dbo.Users(Id),
    AcceptedAt           DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
    Notes                NVARCHAR(400) NULL
);

-- Sample evaluation results (quality gate before contract)
CREATE TABLE fdx.SampleEvaluations (
    EvaluationId         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    SampleRequestId      UNIQUEIDENTIFIER NOT NULL, -- References fdx.SampleRequests
    SampleRequestLineId  UNIQUEIDENTIFIER NULL, -- References fdx.SampleRequestLines
    RequestItemId        INT NULL REFERENCES dbo.RequestItems(Id), -- Fallback
    EvaluatedBy          INT NULL REFERENCES dbo.Users(Id),
    EvaluatedAt          DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
    Result               NVARCHAR(20) NOT NULL, -- pass/fail/conditional
    Score                DECIMAL(5,2) NULL,
    Comments             NVARCHAR(1000) NULL
);

-- Adaptation workflows (post-contract tasks)
CREATE TABLE fdx.AdaptationWorkflows (
    AdaptationId         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ContractId           UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.Contracts(ContractId),
    Status               NVARCHAR(20) NOT NULL DEFAULT 'pending',
    StartedAt            DATETIMEOFFSET NULL,
    CompletedAt          DATETIMEOFFSET NULL
);

-- Adaptation task list
CREATE TABLE fdx.AdaptationTasks (
    TaskId               UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    AdaptationId         UNIQUEIDENTIFIER NOT NULL REFERENCES fdx.AdaptationWorkflows(AdaptationId),
    Title                NVARCHAR(200) NOT NULL,
    AssigneeRole         NVARCHAR(40) NULL, -- buyer/supplier/expert
    AssigneeUserId       INT NULL REFERENCES dbo.Users(Id),
    Status               NVARCHAR(20) NOT NULL DEFAULT 'open',
    DueDate              DATE NULL,
    CompletedAt          DATETIMEOFFSET NULL,
    Notes                NVARCHAR(MAX) NULL
);

-- INDEXES for performance
CREATE INDEX IX_Contracts_Project ON fdx.Contracts(ProjectId, Status);
CREATE INDEX IX_Contracts_Supplier ON fdx.Contracts(SupplierId, Status);
CREATE INDEX IX_Contracts_Request ON fdx.Contracts(RequestId);
CREATE INDEX IX_ContractLines_Contract ON fdx.ContractLines(ContractId);
CREATE INDEX IX_ContractFiles_Contract ON fdx.ContractFiles(ContractId);
CREATE INDEX IX_Acceptances_ProposalLine ON fdx.ProposalLineAcceptances(ProposalLineId);
CREATE INDEX IX_Acceptances_RequestItem ON fdx.ProposalLineAcceptances(RequestItemId);
CREATE INDEX IX_SampleEvaluations_Request ON fdx.SampleEvaluations(SampleRequestId);
CREATE INDEX IX_SampleEvaluations_RequestItem ON fdx.SampleEvaluations(RequestItemId);
CREATE INDEX IX_AdaptationWorkflows_Contract ON fdx.AdaptationWorkflows(ContractId);
CREATE INDEX IX_AdaptationTasks_Adaptation ON fdx.AdaptationTasks(AdaptationId);
CREATE INDEX IX_AdaptationTasks_Assignee ON fdx.AdaptationTasks(AssigneeUserId, Status);

-- Contract status check constraint
ALTER TABLE fdx.Contracts 
ADD CONSTRAINT CHK_Contract_Status 
CHECK (Status IN ('draft', 'negotiating', 'ready', 'signing', 'active', 'closed', 'cancelled'));

-- Sample evaluation result constraint
ALTER TABLE fdx.SampleEvaluations
ADD CONSTRAINT CHK_SampleEvaluation_Result
CHECK (Result IN ('pass', 'fail', 'conditional'));

-- Adaptation workflow status constraint
ALTER TABLE fdx.AdaptationWorkflows
ADD CONSTRAINT CHK_AdaptationWorkflow_Status
CHECK (Status IN ('pending', 'in-progress', 'approved', 'rejected'));

-- Adaptation task status constraint
ALTER TABLE fdx.AdaptationTasks
ADD CONSTRAINT CHK_AdaptationTask_Status
CHECK (Status IN ('open', 'in-progress', 'done', 'blocked'));

-- Trigger to update LastUpdated timestamp
CREATE TRIGGER TR_Contracts_UpdateTimestamp
ON fdx.Contracts
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE fdx.Contracts
    SET LastUpdated = SYSUTCDATETIME()
    WHERE ContractId IN (SELECT ContractId FROM inserted);
END;

-- Sample data for testing (optional)
-- INSERT INTO fdx.Contracts (ProjectId, RequestId, SupplierId, Title, Currency, Status, CreatedBy)
-- VALUES (NEWID(), 1, 1, 'Sample Contract - Organic Tomatoes', 'USD', 'draft', 1);