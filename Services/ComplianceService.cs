using FDX.Trading.Data;
using FDX.Trading.Models.Compliance;
using Microsoft.EntityFrameworkCore;
using Microsoft.Data.SqlClient;

namespace FDX.Trading.Services;

public interface IComplianceService
{
    Task<ComplianceProcess> CreateComplianceProcessAsync(Guid contractId, Guid projectId);
    Task<ComplianceProcess?> GetComplianceProcessAsync(Guid complianceId);
    Task<List<ComplianceProcess>> GetComplianceProcessesByProjectAsync(Guid projectId);
    Task<bool> UpdateStepStatusAsync(Guid stepId, string status, string? notes = null);
    Task<ComplianceEvidence> AddEvidenceAsync(Guid stepId, string fileName, string blobUri, string? contentType = null, long? fileSize = null);
    Task<ComplianceApproval> ApproveStepAsync(Guid stepId, Guid userId, string decision, string? comment = null);
    Task<bool> UpdateStageProgressAsync(Guid stageId);
    Task<bool> CheckComplianceCompletionAsync(Guid complianceId);
    Task<KosherCertification> AddKosherCertificationAsync(KosherCertification certification);
    Task<List<ComplianceStageTemplate>> GetStageTemplatesAsync();
    Task<List<ComplianceStepTemplate>> GetStepTemplatesByStageAsync(Guid stageTemplateId);
    
    // Checklist methods
    Task<ComplianceChecklist?> GetOrCreateChecklistAsync(Guid stepId);
    Task<ComplianceChecklist?> GetChecklistWithItemsAsync(Guid stepId);
    Task<ChecklistProgressResult> SetChecklistItemStatusAsync(Guid itemId, string status, Guid? userId = null);
    Task<ComplianceEvidence> AddChecklistItemEvidenceAsync(Guid itemId, string fileName, string blobUri, string? contentType = null, long? fileSize = null);
    Task<bool> AssignChecklistItemAsync(Guid itemId, Guid? userId, Guid? externalUserId = null);
    Task<bool> SetChecklistItemDueDateAsync(Guid itemId, DateTime? dueDate);
}

public class ChecklistProgressResult
{
    public Guid ChecklistId { get; set; }
    public Guid StepId { get; set; }
    public int RequiredCount { get; set; }
    public int DoneCount { get; set; }
    public int ProgressPercent { get; set; }
}

public class ComplianceService : IComplianceService
{
    private readonly FdxTradingContext _context;
    private readonly ILogger<ComplianceService> _logger;

    public ComplianceService(FdxTradingContext context, ILogger<ComplianceService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<ComplianceProcess> CreateComplianceProcessAsync(Guid contractId, Guid projectId)
    {
        try
        {
            // Create the compliance process
            var complianceProcess = new ComplianceProcess
            {
                ComplianceId = Guid.NewGuid(),
                ContractId = contractId,
                ProjectId = projectId,
                Status = "in-progress",
                StartedAt = DateTimeOffset.UtcNow,
                CreatedAt = DateTimeOffset.UtcNow,
                UpdatedAt = DateTimeOffset.UtcNow,
                Stages = new List<ComplianceStage>()
            };

            // Get all active stage templates
            var stageTemplates = await _context.ComplianceStageTemplates
                .Include(st => st.StepTemplates)
                .Where(st => st.IsActive)
                .OrderBy(st => st.DisplayOrder)
                .ToListAsync();

            // Create stages from templates
            foreach (var stageTemplate in stageTemplates)
            {
                var stage = new ComplianceStage
                {
                    StageId = Guid.NewGuid(),
                    ComplianceId = complianceProcess.ComplianceId,
                    StageTemplateId = stageTemplate.StageTemplateId,
                    Code = stageTemplate.Code,
                    Status = "in-progress",
                    StartedAt = DateTimeOffset.UtcNow,
                    Progress = 0,
                    CreatedAt = DateTimeOffset.UtcNow,
                    UpdatedAt = DateTimeOffset.UtcNow,
                    Steps = new List<ComplianceStep>()
                };

                // Create steps from templates
                foreach (var stepTemplate in stageTemplate.StepTemplates.OrderBy(st => st.DisplayOrder))
                {
                    var step = new ComplianceStep
                    {
                        StepId = Guid.NewGuid(),
                        StageId = stage.StageId,
                        StepTemplateId = stepTemplate.StepTemplateId,
                        Title = stepTemplate.Title,
                        Required = stepTemplate.Required,
                        Scope = stepTemplate.Scope,
                        Status = "open",
                        CreatedAt = DateTimeOffset.UtcNow,
                        UpdatedAt = DateTimeOffset.UtcNow,
                        Evidence = new List<ComplianceEvidence>(),
                        Approvals = new List<ComplianceApproval>()
                    };

                    stage.Steps.Add(step);
                }

                complianceProcess.Stages.Add(stage);
            }

            _context.ComplianceProcesses.Add(complianceProcess);
            await _context.SaveChangesAsync();

            _logger.LogInformation("Created compliance process {ComplianceId} for contract {ContractId}", 
                complianceProcess.ComplianceId, contractId);

            return complianceProcess;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating compliance process for contract {ContractId}", contractId);
            throw;
        }
    }

    public async Task<ComplianceProcess?> GetComplianceProcessAsync(Guid complianceId)
    {
        return await _context.ComplianceProcesses
            .Include(cp => cp.Stages)
                .ThenInclude(s => s.Steps)
                    .ThenInclude(st => st.Evidence)
            .Include(cp => cp.Stages)
                .ThenInclude(s => s.Steps)
                    .ThenInclude(st => st.Approvals)
            .FirstOrDefaultAsync(cp => cp.ComplianceId == complianceId);
    }

    public async Task<List<ComplianceProcess>> GetComplianceProcessesByProjectAsync(Guid projectId)
    {
        return await _context.ComplianceProcesses
            .Include(cp => cp.Stages)
                .ThenInclude(s => s.Steps)
            .Where(cp => cp.ProjectId == projectId)
            .OrderByDescending(cp => cp.CreatedAt)
            .ToListAsync();
    }

    public async Task<bool> UpdateStepStatusAsync(Guid stepId, string status, string? notes = null)
    {
        try
        {
            var step = await _context.ComplianceSteps
                .Include(s => s.Stage)
                .FirstOrDefaultAsync(s => s.StepId == stepId);

            if (step == null)
                return false;

            step.Status = status;
            if (!string.IsNullOrEmpty(notes))
                step.Notes = notes;
            step.UpdatedAt = DateTimeOffset.UtcNow;

            await _context.SaveChangesAsync();

            // Update stage progress
            await UpdateStageProgressAsync(step.StageId);

            _logger.LogInformation("Updated step {StepId} status to {Status}", stepId, status);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating step {StepId} status", stepId);
            throw;
        }
    }

    public async Task<ComplianceEvidence> AddEvidenceAsync(Guid stepId, string fileName, string blobUri, 
        string? contentType = null, long? fileSize = null)
    {
        try
        {
            var evidence = new ComplianceEvidence
            {
                EvidenceId = Guid.NewGuid(),
                StepId = stepId,
                FileName = fileName,
                BlobUri = blobUri,
                ContentType = contentType,
                FileSize = fileSize,
                UploadedAt = DateTimeOffset.UtcNow
            };

            _context.ComplianceEvidence.Add(evidence);
            await _context.SaveChangesAsync();

            // Update step status to in-review
            await UpdateStepStatusAsync(stepId, "in-review");

            _logger.LogInformation("Added evidence {EvidenceId} to step {StepId}", evidence.EvidenceId, stepId);
            return evidence;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding evidence to step {StepId}", stepId);
            throw;
        }
    }

    public async Task<ComplianceApproval> ApproveStepAsync(Guid stepId, Guid userId, string decision, string? comment = null)
    {
        try
        {
            var approval = new ComplianceApproval
            {
                ApprovalId = Guid.NewGuid(),
                StepId = stepId,
                Decision = decision,
                DecidedBy = userId,
                DecidedAt = DateTimeOffset.UtcNow,
                Comment = comment
            };

            _context.ComplianceApprovals.Add(approval);

            // Update step status based on decision
            var stepStatus = decision == "approved" ? "approved" : "rejected";
            await UpdateStepStatusAsync(stepId, stepStatus);

            await _context.SaveChangesAsync();

            _logger.LogInformation("Created approval {ApprovalId} for step {StepId} with decision {Decision}", 
                approval.ApprovalId, stepId, decision);
            return approval;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating approval for step {StepId}", stepId);
            throw;
        }
    }

    public async Task<bool> UpdateStageProgressAsync(Guid stageId)
    {
        try
        {
            var stage = await _context.ComplianceStages
                .Include(s => s.Steps)
                .FirstOrDefaultAsync(s => s.StageId == stageId);

            if (stage == null)
                return false;

            var totalSteps = stage.Steps.Count;
            var completedSteps = stage.Steps.Count(s => s.Status == "approved");
            
            stage.Progress = totalSteps > 0 ? (completedSteps * 100) / totalSteps : 0;
            stage.UpdatedAt = DateTimeOffset.UtcNow;

            // Check if stage is complete
            if (stage.Progress == 100)
            {
                stage.Status = "approved";
                stage.ApprovedAt = DateTimeOffset.UtcNow;
            }

            await _context.SaveChangesAsync();

            // Check if entire compliance process is complete
            await CheckComplianceCompletionAsync(stage.ComplianceId);

            _logger.LogInformation("Updated stage {StageId} progress to {Progress}%", stageId, stage.Progress);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating stage {StageId} progress", stageId);
            throw;
        }
    }

    public async Task<bool> CheckComplianceCompletionAsync(Guid complianceId)
    {
        try
        {
            var process = await _context.ComplianceProcesses
                .Include(cp => cp.Stages)
                .FirstOrDefaultAsync(cp => cp.ComplianceId == complianceId);

            if (process == null)
                return false;

            var allStagesApproved = process.Stages.All(s => s.Status == "approved");

            if (allStagesApproved && process.Status != "approved")
            {
                process.Status = "approved";
                process.ApprovedAt = DateTimeOffset.UtcNow;
                process.UpdatedAt = DateTimeOffset.UtcNow;
                await _context.SaveChangesAsync();

                _logger.LogInformation("Compliance process {ComplianceId} completed and approved", complianceId);
                return true;
            }

            return false;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking compliance completion for {ComplianceId}", complianceId);
            throw;
        }
    }

    public async Task<KosherCertification> AddKosherCertificationAsync(KosherCertification certification)
    {
        try
        {
            certification.KosherCertId = Guid.NewGuid();
            certification.CreatedAt = DateTimeOffset.UtcNow;
            certification.UpdatedAt = DateTimeOffset.UtcNow;

            _context.KosherCertifications.Add(certification);
            await _context.SaveChangesAsync();

            _logger.LogInformation("Added kosher certification {KosherCertId} for supplier {SupplierId}", 
                certification.KosherCertId, certification.SupplierId);
            return certification;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding kosher certification");
            throw;
        }
    }

    public async Task<List<ComplianceStageTemplate>> GetStageTemplatesAsync()
    {
        return await _context.ComplianceStageTemplates
            .Where(st => st.IsActive)
            .OrderBy(st => st.DisplayOrder)
            .ToListAsync();
    }

    public async Task<List<ComplianceStepTemplate>> GetStepTemplatesByStageAsync(Guid stageTemplateId)
    {
        return await _context.ComplianceStepTemplates
            .Where(st => st.StageTemplateId == stageTemplateId)
            .OrderBy(st => st.DisplayOrder)
            .ToListAsync();
    }
    
    // Checklist Methods Implementation
    
    public async Task<ComplianceChecklist?> GetOrCreateChecklistAsync(Guid stepId)
    {
        try
        {
            // Check if checklist already exists
            var existingChecklist = await _context.ComplianceChecklists
                .Include(c => c.Items)
                .FirstOrDefaultAsync(c => c.StepId == stepId);
            
            if (existingChecklist != null)
                return existingChecklist;
            
            // Execute stored procedure to create checklist
            var checklistIdParam = new SqlParameter
            {
                ParameterName = "@ChecklistId",
                SqlDbType = System.Data.SqlDbType.UniqueIdentifier,
                Direction = System.Data.ParameterDirection.Output
            };
            
            await _context.Database.ExecuteSqlRawAsync(
                "EXEC fdx.usp_Compliance_EnsureChecklistForStep @StepId",
                new SqlParameter("@StepId", stepId));
            
            // Fetch the newly created checklist
            return await _context.ComplianceChecklists
                .Include(c => c.Items)
                .FirstOrDefaultAsync(c => c.StepId == stepId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating checklist for step {StepId}", stepId);
            throw;
        }
    }
    
    public async Task<ComplianceChecklist?> GetChecklistWithItemsAsync(Guid stepId)
    {
        return await _context.ComplianceChecklists
            .Include(c => c.Items.OrderBy(i => i.SortOrder))
            .ThenInclude(i => i.Evidence)
            .FirstOrDefaultAsync(c => c.StepId == stepId);
    }
    
    public async Task<ChecklistProgressResult> SetChecklistItemStatusAsync(Guid itemId, string status, Guid? userId = null)
    {
        try
        {
            // Execute stored procedure
            var result = new ChecklistProgressResult();
            
            using var command = _context.Database.GetDbConnection().CreateCommand();
            command.CommandText = "fdx.usp_Compliance_ChecklistItemSet";
            command.CommandType = System.Data.CommandType.StoredProcedure;
            
            command.Parameters.Add(new SqlParameter("@ItemId", itemId));
            command.Parameters.Add(new SqlParameter("@Status", status));
            command.Parameters.Add(new SqlParameter("@UserId", userId ?? (object)DBNull.Value));
            
            await _context.Database.OpenConnectionAsync();
            
            using var reader = await command.ExecuteReaderAsync();
            if (await reader.ReadAsync())
            {
                result.ChecklistId = reader.GetGuid(0);
                result.StepId = reader.GetGuid(1);
                result.RequiredCount = reader.GetInt32(2);
                result.DoneCount = reader.GetInt32(3);
                result.ProgressPercent = reader.GetInt32(4);
            }
            
            _logger.LogInformation("Set checklist item {ItemId} status to {Status}", itemId, status);
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error setting checklist item {ItemId} status", itemId);
            throw;
        }
    }
    
    public async Task<ComplianceEvidence> AddChecklistItemEvidenceAsync(Guid itemId, string fileName, string blobUri, 
        string? contentType = null, long? fileSize = null)
    {
        try
        {
            // Get the step ID through the checklist
            var stepId = await _context.ComplianceChecklistItems
                .Where(i => i.ItemId == itemId)
                .Join(_context.ComplianceChecklists,
                    i => i.ChecklistId,
                    c => c.ChecklistId,
                    (i, c) => c.StepId)
                .FirstOrDefaultAsync();
            
            if (stepId == Guid.Empty)
                throw new InvalidOperationException($"Checklist item {itemId} not found");
            
            var evidence = new ComplianceEvidence
            {
                EvidenceId = Guid.NewGuid(),
                StepId = stepId,
                ChecklistItemId = itemId,
                FileName = fileName,
                BlobUri = blobUri,
                ContentType = contentType,
                FileSize = fileSize,
                UploadedAt = DateTimeOffset.UtcNow
            };
            
            _context.ComplianceEvidence.Add(evidence);
            await _context.SaveChangesAsync();
            
            // Update item status to indicate evidence uploaded
            var item = await _context.ComplianceChecklistItems.FindAsync(itemId);
            if (item != null && item.Status == "open")
            {
                item.Status = "done";
                item.UpdatedAt = DateTimeOffset.UtcNow;
                await _context.SaveChangesAsync();
            }
            
            _logger.LogInformation("Added evidence {EvidenceId} to checklist item {ItemId}", 
                evidence.EvidenceId, itemId);
            return evidence;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding evidence to checklist item {ItemId}", itemId);
            throw;
        }
    }
    
    public async Task<bool> AssignChecklistItemAsync(Guid itemId, Guid? userId, Guid? externalUserId = null)
    {
        try
        {
            var item = await _context.ComplianceChecklistItems.FindAsync(itemId);
            if (item == null)
                return false;
            
            item.AssignedToUserId = userId;
            item.AssignedToExternalId = externalUserId;
            item.UpdatedAt = DateTimeOffset.UtcNow;
            
            await _context.SaveChangesAsync();
            
            _logger.LogInformation("Assigned checklist item {ItemId} to user {UserId}/{ExternalUserId}", 
                itemId, userId, externalUserId);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error assigning checklist item {ItemId}", itemId);
            throw;
        }
    }
    
    public async Task<bool> SetChecklistItemDueDateAsync(Guid itemId, DateTime? dueDate)
    {
        try
        {
            var item = await _context.ComplianceChecklistItems.FindAsync(itemId);
            if (item == null)
                return false;
            
            item.DueDate = dueDate;
            item.UpdatedAt = DateTimeOffset.UtcNow;
            
            await _context.SaveChangesAsync();
            
            _logger.LogInformation("Set checklist item {ItemId} due date to {DueDate}", itemId, dueDate);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error setting due date for checklist item {ItemId}", itemId);
            throw;
        }
    }
}