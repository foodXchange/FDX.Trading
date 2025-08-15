using FDX.Trading.Models.Compliance;
using FDX.Trading.Services;
using Microsoft.AspNetCore.Mvc;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ComplianceController : ControllerBase
{
    private readonly IComplianceService _complianceService;
    private readonly ILogger<ComplianceController> _logger;

    public ComplianceController(IComplianceService complianceService, ILogger<ComplianceController> logger)
    {
        _complianceService = complianceService;
        _logger = logger;
    }

    [HttpPost("process")]
    public async Task<IActionResult> CreateComplianceProcess([FromBody] CreateComplianceProcessRequest request)
    {
        try
        {
            if (request.ContractId == Guid.Empty || request.ProjectId == Guid.Empty)
            {
                return BadRequest("ContractId and ProjectId are required");
            }

            var process = await _complianceService.CreateComplianceProcessAsync(request.ContractId, request.ProjectId);
            return Ok(new { success = true, complianceId = process.ComplianceId });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating compliance process");
            return StatusCode(500, new { success = false, message = "Error creating compliance process" });
        }
    }

    [HttpGet("process/{complianceId}")]
    public async Task<IActionResult> GetComplianceProcess(Guid complianceId)
    {
        try
        {
            var process = await _complianceService.GetComplianceProcessAsync(complianceId);
            if (process == null)
            {
                return NotFound(new { success = false, message = "Compliance process not found" });
            }

            return Ok(new { success = true, data = process });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting compliance process {ComplianceId}", complianceId);
            return StatusCode(500, new { success = false, message = "Error retrieving compliance process" });
        }
    }

    [HttpGet("project/{projectId}")]
    public async Task<IActionResult> GetComplianceProcessesByProject(Guid projectId)
    {
        try
        {
            var processes = await _complianceService.GetComplianceProcessesByProjectAsync(projectId);
            return Ok(new { success = true, data = processes });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting compliance processes for project {ProjectId}", projectId);
            return StatusCode(500, new { success = false, message = "Error retrieving compliance processes" });
        }
    }

    [HttpPut("step/{stepId}/status")]
    public async Task<IActionResult> UpdateStepStatus(Guid stepId, [FromBody] UpdateStepStatusRequest request)
    {
        try
        {
            if (string.IsNullOrEmpty(request.Status))
            {
                return BadRequest("Status is required");
            }

            var success = await _complianceService.UpdateStepStatusAsync(stepId, request.Status, request.Notes);
            
            if (!success)
            {
                return NotFound(new { success = false, message = "Step not found" });
            }

            return Ok(new { success = true, message = "Step status updated successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating step {StepId} status", stepId);
            return StatusCode(500, new { success = false, message = "Error updating step status" });
        }
    }

    [HttpPost("step/{stepId}/evidence")]
    public async Task<IActionResult> AddEvidence(Guid stepId, [FromBody] AddEvidenceRequest request)
    {
        try
        {
            if (string.IsNullOrEmpty(request.FileName) || string.IsNullOrEmpty(request.BlobUri))
            {
                return BadRequest("FileName and BlobUri are required");
            }

            var evidence = await _complianceService.AddEvidenceAsync(
                stepId, 
                request.FileName, 
                request.BlobUri, 
                request.ContentType, 
                request.FileSize
            );

            return Ok(new { success = true, evidenceId = evidence.EvidenceId });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding evidence to step {StepId}", stepId);
            return StatusCode(500, new { success = false, message = "Error adding evidence" });
        }
    }

    [HttpPost("step/{stepId}/approve")]
    public async Task<IActionResult> ApproveStep(Guid stepId, [FromBody] ApproveStepRequest request)
    {
        try
        {
            if (request.UserId == Guid.Empty || string.IsNullOrEmpty(request.Decision))
            {
                return BadRequest("UserId and Decision are required");
            }

            var approval = await _complianceService.ApproveStepAsync(
                stepId, 
                request.UserId, 
                request.Decision, 
                request.Comment
            );

            return Ok(new { success = true, approvalId = approval.ApprovalId });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error approving step {StepId}", stepId);
            return StatusCode(500, new { success = false, message = "Error approving step" });
        }
    }

    [HttpPost("kosher")]
    public async Task<IActionResult> AddKosherCertification([FromBody] KosherCertification certification)
    {
        try
        {
            if (certification.SupplierId == Guid.Empty || string.IsNullOrEmpty(certification.Authority))
            {
                return BadRequest("SupplierId and Authority are required");
            }

            var result = await _complianceService.AddKosherCertificationAsync(certification);
            return Ok(new { success = true, kosherCertId = result.KosherCertId });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding kosher certification");
            return StatusCode(500, new { success = false, message = "Error adding kosher certification" });
        }
    }

    [HttpGet("templates/stages")]
    public async Task<IActionResult> GetStageTemplates()
    {
        try
        {
            var templates = await _complianceService.GetStageTemplatesAsync();
            return Ok(new { success = true, data = templates });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting stage templates");
            return StatusCode(500, new { success = false, message = "Error retrieving stage templates" });
        }
    }

    [HttpGet("templates/steps/{stageTemplateId}")]
    public async Task<IActionResult> GetStepTemplates(Guid stageTemplateId)
    {
        try
        {
            var templates = await _complianceService.GetStepTemplatesByStageAsync(stageTemplateId);
            return Ok(new { success = true, data = templates });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting step templates for stage {StageTemplateId}", stageTemplateId);
            return StatusCode(500, new { success = false, message = "Error retrieving step templates" });
        }
    }

    // ===== CHECKLIST ENDPOINTS =====

    [HttpGet("steps/{stepId}/checklist")]
    public async Task<IActionResult> GetStepChecklist(Guid stepId)
    {
        try
        {
            // Ensure checklist exists (create from template if needed)
            var checklist = await _complianceService.GetOrCreateChecklistAsync(stepId);
            
            if (checklist == null)
            {
                return Ok(new { checklist = (object?)null });
            }

            // Get full checklist with items
            var fullChecklist = await _complianceService.GetChecklistWithItemsAsync(stepId);
            
            if (fullChecklist == null)
            {
                return Ok(new { checklist = (object?)null });
            }

            var items = fullChecklist.Items
                .OrderBy(i => i.SortOrder)
                .ThenBy(i => i.Title)
                .Select(i => new
                {
                    i.ItemId,
                    i.ItemCode,
                    i.Title,
                    i.Required,
                    i.Status,
                    i.AssignedToUserId,
                    i.AssignedToExternalId,
                    i.DueDate,
                    i.Notes,
                    EvidenceCount = i.Evidence.Count
                }).ToList();

            var requiredCount = items.Count(x => x.Required);
            var doneCount = items.Count(x => x.Required && (x.Status == "done" || x.Status == "na"));

            return Ok(new
            {
                fullChecklist.ChecklistId,
                fullChecklist.Title,
                fullChecklist.Status,
                Progress = new
                {
                    Required = requiredCount,
                    Done = doneCount,
                    Percent = requiredCount > 0 ? (doneCount * 100) / requiredCount : 0
                },
                Items = items
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting checklist for step {StepId}", stepId);
            return StatusCode(500, new { success = false, message = "Error retrieving checklist" });
        }
    }

    [HttpPost("checklist/items/{itemId}/set")]
    public async Task<IActionResult> SetChecklistItemStatus(Guid itemId, [FromBody] SetItemStatusRequest request)
    {
        try
        {
            if (string.IsNullOrEmpty(request.Status))
            {
                return BadRequest("Status is required");
            }

            var progress = await _complianceService.SetChecklistItemStatusAsync(
                itemId, 
                request.Status, 
                request.UserId
            );

            return Ok(new
            {
                success = true,
                progress = new
                {
                    progress.ChecklistId,
                    progress.StepId,
                    progress.RequiredCount,
                    progress.DoneCount,
                    progress.ProgressPercent
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error setting checklist item {ItemId} status", itemId);
            return StatusCode(500, new { success = false, message = "Error updating item status" });
        }
    }

    [HttpPost("checklist/items/{itemId}/evidence")]
    public async Task<IActionResult> AddChecklistItemEvidence(Guid itemId, [FromBody] AddEvidenceRequest request)
    {
        try
        {
            if (string.IsNullOrEmpty(request.FileName) || string.IsNullOrEmpty(request.BlobUri))
            {
                return BadRequest("FileName and BlobUri are required");
            }

            var evidence = await _complianceService.AddChecklistItemEvidenceAsync(
                itemId,
                request.FileName,
                request.BlobUri,
                request.ContentType,
                request.FileSize
            );

            return Ok(new
            {
                success = true,
                evidenceId = evidence.EvidenceId,
                uri = evidence.BlobUri
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding evidence to checklist item {ItemId}", itemId);
            return StatusCode(500, new { success = false, message = "Error adding evidence" });
        }
    }

    [HttpPut("checklist/items/{itemId}/assign")]
    public async Task<IActionResult> AssignChecklistItem(Guid itemId, [FromBody] AssignItemRequest request)
    {
        try
        {
            var success = await _complianceService.AssignChecklistItemAsync(
                itemId,
                request.UserId,
                request.ExternalUserId
            );

            if (!success)
            {
                return NotFound(new { success = false, message = "Checklist item not found" });
            }

            return Ok(new { success = true, message = "Item assigned successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error assigning checklist item {ItemId}", itemId);
            return StatusCode(500, new { success = false, message = "Error assigning item" });
        }
    }

    [HttpPut("checklist/items/{itemId}/due-date")]
    public async Task<IActionResult> SetChecklistItemDueDate(Guid itemId, [FromBody] SetDueDateRequest request)
    {
        try
        {
            var success = await _complianceService.SetChecklistItemDueDateAsync(itemId, request.DueDate);

            if (!success)
            {
                return NotFound(new { success = false, message = "Checklist item not found" });
            }

            return Ok(new { success = true, message = "Due date updated successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error setting due date for checklist item {ItemId}", itemId);
            return StatusCode(500, new { success = false, message = "Error setting due date" });
        }
    }
}

// Request DTOs
public class CreateComplianceProcessRequest
{
    public Guid ContractId { get; set; }
    public Guid ProjectId { get; set; }
}

public class UpdateStepStatusRequest
{
    public string Status { get; set; } = string.Empty;
    public string? Notes { get; set; }
}

public class AddEvidenceRequest
{
    public string FileName { get; set; } = string.Empty;
    public string BlobUri { get; set; } = string.Empty;
    public string? ContentType { get; set; }
    public long? FileSize { get; set; }
}

public class ApproveStepRequest
{
    public Guid UserId { get; set; }
    public string Decision { get; set; } = string.Empty;
    public string? Comment { get; set; }
}

public class SetItemStatusRequest
{
    public string Status { get; set; } = string.Empty;
    public Guid? UserId { get; set; }
}

public class AssignItemRequest
{
    public Guid? UserId { get; set; }
    public Guid? ExternalUserId { get; set; }
}

public class SetDueDateRequest
{
    public DateTime? DueDate { get; set; }
}