using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using FDX.Trading.Services;
using Microsoft.Extensions.Logging;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class SourcingBriefController : ControllerBase
{
    private readonly FdxTradingContext _context;
    //private readonly ProductAggregationService _aggregationService;
    //private readonly SupplierScoringService _scoringService;
    private readonly ImprovedSupplierMatchingService _matchingService;
    private readonly ILogger<SourcingBriefController> _logger;

    public SourcingBriefController(
        FdxTradingContext context,
        //ProductAggregationService aggregationService,
        //SupplierScoringService scoringService,
        ImprovedSupplierMatchingService matchingService,
        ILogger<SourcingBriefController> logger)
    {
        _context = context;
        //_aggregationService = aggregationService;
        //_scoringService = scoringService;
        _matchingService = matchingService;
        _logger = logger;
    }

    // GET: api/SourcingBrief
    [HttpGet]
    public async Task<ActionResult<IEnumerable<SourcingBriefDto>>> GetSourcingBriefs()
    {
        var briefs = await _context.SourcingBriefs
            .Include(sb => sb.Console)
            .Include(sb => sb.CreatedBy)
            .Include(sb => sb.Products)
            .Include(sb => sb.TargetSuppliers)
            .Include(sb => sb.Responses)
            .OrderByDescending(sb => sb.CreatedAt)
            .ToListAsync();

        var dtos = briefs.Select(b => MapToDto(b)).ToList();
        return Ok(dtos);
    }
    
    // GET: api/SourcingBrief/ByRequest/{requestId}
    [HttpGet("ByRequest/{requestId}")]
    public async Task<ActionResult<SourcingBriefDto>> GetSourcingBriefByRequest(int requestId)
    {
        var brief = await _context.SourcingBriefs
            .Include(sb => sb.Console)
            .Include(sb => sb.CreatedBy)
            .Include(sb => sb.LinkedRequests)
            .Where(sb => sb.LinkedRequests.Any(br => br.RequestId == requestId))
            .OrderByDescending(sb => sb.CreatedAt)
            .FirstOrDefaultAsync();

        if (brief == null)
        {
            return NotFound();
        }

        return Ok(MapToDto(brief));
    }

    // GET: api/SourcingBrief/5
    [HttpGet("{id}")]
    public async Task<ActionResult<SourcingBriefDto>> GetSourcingBrief(int id)
    {
        var brief = await _context.SourcingBriefs
            .Include(sb => sb.Console)
                .ThenInclude(c => c.WorkflowStages)
            .Include(sb => sb.CreatedBy)
            .Include(sb => sb.Products)
                .ThenInclude(p => p.Images)
            .Include(sb => sb.TargetSuppliers)
                .ThenInclude(ts => ts.Supplier)
            .Include(sb => sb.Responses)
            .Include(sb => sb.Documents)
            .Include(sb => sb.LinkedRequests)
                .ThenInclude(lr => lr.Request)
            .FirstOrDefaultAsync(sb => sb.Id == id);

        if (brief == null)
        {
            return NotFound();
        }

        var dto = MapToDto(brief);
        dto.Products = brief.Products.Select(p => new BriefProductDto
        {
            Id = p.Id,
            ProductName = p.ProductName,
            Category = p.Category,
            TotalQuantity = p.TotalQuantity,
            Unit = p.Unit,
            BuyerCount = p.BuyerCount,
            TargetPrice = p.TargetPrice,
            BenchmarkBrand = p.BenchmarkBrand,
            ImageCount = p.Images.Count,
            Images = p.Images.Select(img => new BriefProductImageDto
            {
                Id = img.Id,
                FileName = img.FileName,
                FilePath = img.FilePath,
                IsPrimary = img.IsPrimary
            }).ToList()
        }).ToList();

        return Ok(dto);
    }

    // POST: api/SourcingBrief
    [HttpPost]
    public async Task<ActionResult<SourcingBriefDto>> CreateSourcingBrief(CreateSourcingBriefDto dto)
    {
        using var transaction = await _context.Database.BeginTransactionAsync();

        try
        {
            // Validate that all requests are complete and published
            var requests = await _context.Requests
                .Where(r => dto.RequestIds.Contains(r.Id))
                .ToListAsync();

            if (requests.Count != dto.RequestIds.Count)
            {
                return BadRequest("One or more requested IDs were not found");
            }

            // Check if all requests are complete and published (Active status)
            var incompleteRequests = requests.Where(r => 
                r.CompletionPercentage < 100 || 
                !r.IsComplete || 
                r.Status != ProcurementRequestStatus.Active
            ).ToList();

            if (incompleteRequests.Any())
            {
                var errorDetails = incompleteRequests.Select(r => new 
                {
                    r.RequestNumber,
                    r.Title,
                    r.CompletionPercentage,
                    r.IsComplete,
                    Status = r.Status.ToString(),
                    Issues = new List<string>
                    {
                        r.CompletionPercentage < 100 ? $"Completion is only {r.CompletionPercentage}%" : null,
                        !r.IsComplete ? "Request is not marked as complete" : null,
                        r.Status != ProcurementRequestStatus.Active ? $"Request status is {r.Status}, must be Active/Published" : null
                    }.Where(i => i != null)
                });

                return BadRequest(new 
                {
                    error = "Cannot create sourcing brief from incomplete or unpublished requests",
                    details = errorDetails
                });
            }

            // Create Console for the sourcing brief
            var console = new ProjectConsole
            {
                ConsoleCode = GenerateConsoleCode(),
                Title = dto.Title,
                Type = ConsoleType.Procurement,
                Priority = ConsolePriority.Medium,
                Status = ConsoleStatus.Active,
                SourceType = "SourcingBrief",
                OwnerId = 1, // TODO: Get from authenticated user
                CurrentStageNumber = 1,
                CreatedAt = DateTime.Now,
                UpdatedAt = DateTime.Now
            };

            // Create workflow stages
            console.WorkflowStages = new List<WorkflowStage>
            {
                new() { StageNumber = 1, StageName = "Request Aggregation", StageType = StageType.Action, Status = StageStatus.InProgress },
                new() { StageNumber = 2, StageName = "Brief Creation", StageType = StageType.Action, Status = StageStatus.Pending },
                new() { StageNumber = 3, StageName = "Supplier Selection", StageType = StageType.Action, Status = StageStatus.Pending },
                new() { StageNumber = 4, StageName = "Publishing", StageType = StageType.Notification, Status = StageStatus.Pending },
                new() { StageNumber = 5, StageName = "Response Collection", StageType = StageType.Action, Status = StageStatus.Pending },
                new() { StageNumber = 6, StageName = "Evaluation", StageType = StageType.Review, Status = StageStatus.Pending },
                new() { StageNumber = 7, StageName = "Negotiation", StageType = StageType.Action, Status = StageStatus.Pending },
                new() { StageNumber = 8, StageName = "Award", StageType = StageType.Approval, Status = StageStatus.Pending }
            };

            _context.Consoles.Add(console);
            await _context.SaveChangesAsync();

            // Create sourcing brief
            var brief = new SourcingBrief
            {
                BriefCode = GenerateBriefCode(),
                Title = dto.Title,
                ExecutiveSummary = dto.ExecutiveSummary,
                ConsoleId = console.Id,
                CreatedByUserId = 1, // TODO: Get from authenticated user
                Status = SourcingBriefStatus.Draft,
                CreatedAt = DateTime.Now,
                ResponseDeadline = dto.ResponseDeadline,
                RequiredDeliveryDate = dto.RequiredDeliveryDate,
                PreferredIncoterms = dto.PreferredIncoterms,
                PreferredPaymentTerms = dto.PreferredPaymentTerms,
                Currency = "USD"
            };

            _context.SourcingBriefs.Add(brief);
            await _context.SaveChangesAsync();

            // Link to requests
            foreach (var requestId in dto.RequestIds)
            {
                var briefRequest = new BriefRequest
                {
                    SourcingBriefId = brief.Id,
                    RequestId = requestId,
                    IsPrimary = dto.RequestIds.IndexOf(requestId) == 0
                };
                _context.BriefRequests.Add(briefRequest);
            }

            // Aggregate products from requests
            // TODO: Uncomment when aggregation service is available
            // var aggregatedProducts = await _aggregationService.AggregateProductsFromRequestsAsync(dto.RequestIds);
            // foreach (var product in aggregatedProducts)
            // {
            //     product.SourcingBriefId = brief.Id;
            //     _context.BriefProducts.Add(product);
            // }

            await _context.SaveChangesAsync();

            // Score and select suppliers
            // TODO: Uncomment when scoring service is available
            // var selectedSuppliers = await _scoringService.SelectOptimalSuppliersAsync(aggregatedProducts);
            // foreach (var supplier in selectedSuppliers)
            // {
            //     supplier.SourcingBriefId = brief.Id;
            //     _context.BriefSuppliers.Add(supplier);
            // }

            // Log activity
            var activity = new BriefActivity
            {
                SourcingBriefId = brief.Id,
                UserId = 1, // TODO: Get from authenticated user
                ActivityType = BriefActivityType.Created,
                Description = $"Sourcing brief created from {dto.RequestIds.Count} requests",
                Timestamp = DateTime.Now
            };
            _context.BriefActivities.Add(activity);

            // Calculate initial quality score
            // brief.QualityScore = CalculateBriefQualityScore(brief, aggregatedProducts);

            await _context.SaveChangesAsync();
            await transaction.CommitAsync();

            // Reload with includes for response
            brief = await _context.SourcingBriefs
                .Include(sb => sb.Console)
                .Include(sb => sb.Products)
                .Include(sb => sb.TargetSuppliers)
                .FirstAsync(sb => sb.Id == brief.Id);

            return CreatedAtAction(nameof(GetSourcingBrief), new { id = brief.Id }, MapToDto(brief));
        }
        catch (Exception ex)
        {
            await transaction.RollbackAsync();
            _logger.LogError(ex, "Error creating sourcing brief");
            return StatusCode(500, "An error occurred while creating the sourcing brief");
        }
    }

    // PUT: api/SourcingBrief/5
    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateSourcingBrief(int id, SourcingBriefDto dto)
    {
        if (id != dto.Id)
        {
            return BadRequest();
        }

        var brief = await _context.SourcingBriefs.FindAsync(id);
        if (brief == null)
        {
            return NotFound();
        }

        brief.Title = dto.Title;
        brief.ExecutiveSummary = dto.ExecutiveSummary;
        brief.ResponseDeadline = dto.ResponseDeadline;
        // UpdatedAt field doesn't exist, update Console instead
        brief.Console.UpdatedAt = DateTime.Now;

        try
        {
            await _context.SaveChangesAsync();
        }
        catch (DbUpdateConcurrencyException)
        {
            if (!SourcingBriefExists(id))
            {
                return NotFound();
            }
            throw;
        }

        return NoContent();
    }

    // POST: api/SourcingBrief/5/publish
    [HttpPost("{id}/publish")]
    public async Task<IActionResult> PublishSourcingBrief(int id)
    {
        var brief = await _context.SourcingBriefs
            .Include(sb => sb.Console)
                .ThenInclude(c => c.WorkflowStages)
            .Include(sb => sb.TargetSuppliers)
            .FirstOrDefaultAsync(sb => sb.Id == id);

        if (brief == null)
        {
            return NotFound();
        }

        if (brief.Status != SourcingBriefStatus.Draft && brief.Status != SourcingBriefStatus.UnderReview)
        {
            return BadRequest("Brief must be in Draft or Under Review status to publish");
        }

        // Update brief status
        brief.Status = SourcingBriefStatus.Published;
        brief.PublishedAt = DateTime.Now;

        // Update console stage
        brief.Console.CurrentStageNumber = 4;
        var publishStage = brief.Console.WorkflowStages.First(ws => ws.StageNumber == 4);
        publishStage.Status = StageStatus.InProgress;
        publishStage.StartedAt = DateTime.Now;

        // Mark suppliers as invited
        foreach (var supplier in brief.TargetSuppliers)
        {
            supplier.Status = BriefSupplierStatus.Invited;
            supplier.InvitedAt = DateTime.Now;
        }

        // Log activity
        var activity = new BriefActivity
        {
            SourcingBriefId = brief.Id,
            UserId = 1, // TODO: Get from authenticated user
            ActivityType = BriefActivityType.Published,
            Description = $"Brief published to {brief.TargetSuppliers.Count} suppliers",
            Timestamp = DateTime.Now
        };
        _context.BriefActivities.Add(activity);

        await _context.SaveChangesAsync();

        return Ok(new { message = "Sourcing brief published successfully" });
    }

    // GET: api/SourcingBrief/5/responses
    [HttpGet("{id}/responses")]
    public async Task<ActionResult<IEnumerable<BriefResponse>>> GetBriefResponses(int id)
    {
        var responses = await _context.BriefResponses
            .Include(br => br.Supplier)
            .Include(br => br.Items)
                .ThenInclude(i => i.BriefProduct)
            .Where(br => br.SourcingBriefId == id)
            .OrderByDescending(br => br.OverallScore)
            .ToListAsync();

        return Ok(responses);
    }

    // POST: api/SourcingBrief/5/analyze
    [HttpPost("{id}/analyze")]
    public async Task<ActionResult<BriefAnalytics>> AnalyzeSourcingBrief(int id)
    {
        var brief = await _context.SourcingBriefs
            .Include(sb => sb.Products)
            .Include(sb => sb.TargetSuppliers)
            .Include(sb => sb.Responses)
            .FirstOrDefaultAsync(sb => sb.Id == id);

        if (brief == null)
        {
            return NotFound();
        }

        var analytics = new BriefAnalytics
        {
            SourcingBriefId = id,
            AnalysisDate = DateTime.Now,
            TotalViews = brief.TargetSuppliers.Count(ts => ts.ViewedAt.HasValue),
            UniqueSupplierViews = brief.TargetSuppliers.Count(ts => ts.Status >= BriefSupplierStatus.Viewed),
            ResponseCount = brief.Responses.Count(r => r.Status == BriefResponseStatus.Submitted),
            SpecificationCompleteness = CalculateSpecificationCompleteness(brief),
            RequirementClarity = CalculateRequirementClarity(brief),
            VolumeAttractiveness = CalculateVolumeAttractiveness(brief)
        };

        // Calculate average response time
        var responseTimes = brief.Responses
            .Where(r => r.SubmittedAt.HasValue && brief.PublishedAt.HasValue)
            .Select(r => (r.SubmittedAt!.Value - brief.PublishedAt!.Value).TotalHours)
            .ToList();

        if (responseTimes.Any())
        {
            analytics.AverageResponseTime = (decimal)responseTimes.Average();
        }

        // Calculate response rate
        if (brief.TargetSuppliers.Any())
        {
            brief.ResponseRate = (decimal)analytics.ResponseCount / brief.TargetSuppliers.Count * 100;
        }

        _context.BriefAnalytics.Add(analytics);
        await _context.SaveChangesAsync();

        return Ok(analytics);
    }

    // POST: api/SourcingBrief/5/evaluate
    [HttpPost("{id}/evaluate")]
    public async Task<ActionResult<IEnumerable<BriefResponse>>> EvaluateResponses(int id)
    {
        // TODO: Uncomment when scoring service is available
        // var responses = await _scoringService.EvaluateResponsesAsync(id);
        var responses = new List<object>();
        return Ok(responses);
    }

    // GET: api/SourcingBrief/available-requests
    [HttpGet("available-requests")]
    public async Task<ActionResult<IEnumerable<Request>>> GetAvailableRequests()
    {
        // Get requests that are not yet linked to a sourcing brief
        var linkedRequestIds = await _context.BriefRequests
            .Select(br => br.RequestId)
            .ToListAsync();

        // Only return requests that are 100% complete and published (Active status)
        var availableRequests = await _context.Requests
            .Include(r => r.RequestItems)
            .Include(r => r.Buyer)
            .Where(r => !linkedRequestIds.Contains(r.Id) && 
                       r.CompletionPercentage == 100 &&
                       r.IsComplete == true &&
                       r.Status == ProcurementRequestStatus.Active)
            .OrderByDescending(r => r.CreatedAt)
            .ToListAsync();

        return Ok(availableRequests);
    }

    // GET: api/SourcingBrief/check-request-eligibility/{requestId}
    [HttpGet("check-request-eligibility/{requestId}")]
    public async Task<ActionResult> CheckRequestEligibility(int requestId)
    {
        var request = await _context.Requests
            .Include(r => r.RequestItems)
            .FirstOrDefaultAsync(r => r.Id == requestId);

        if (request == null)
        {
            return NotFound($"Request with ID {requestId} not found");
        }

        // Check if already linked to a sourcing brief
        var isLinked = await _context.BriefRequests
            .AnyAsync(br => br.RequestId == requestId);

        if (isLinked)
        {
            var linkedBrief = await _context.BriefRequests
                .Include(br => br.SourcingBrief)
                .Where(br => br.RequestId == requestId)
                .Select(br => new { br.SourcingBrief.BriefCode, br.SourcingBrief.Title })
                .FirstOrDefaultAsync();

            return Ok(new 
            {
                eligible = false,
                reason = "Already linked to sourcing brief",
                linkedBrief
            });
        }

        var issues = new List<string>();
        
        if (request.CompletionPercentage < 100)
            issues.Add($"Request is only {request.CompletionPercentage}% complete (must be 100%)");
        
        if (!request.IsComplete)
            issues.Add("Request is not marked as complete");
        
        if (request.Status != ProcurementRequestStatus.Active)
            issues.Add($"Request status is '{request.Status}' (must be 'Active/Published')");

        if (issues.Any())
        {
            return Ok(new 
            {
                eligible = false,
                request = new 
                {
                    request.RequestNumber,
                    request.Title,
                    request.CompletionPercentage,
                    request.IsComplete,
                    Status = request.Status.ToString()
                },
                issues
            });
        }

        return Ok(new 
        {
            eligible = true,
            message = "Request is eligible for sourcing brief creation",
            request = new 
            {
                request.RequestNumber,
                request.Title,
                request.CompletionPercentage,
                request.IsComplete,
                Status = request.Status.ToString(),
                ItemCount = request.RequestItems.Count
            }
        });
    }

    private SourcingBriefDto MapToDto(SourcingBrief brief)
    {
        return new SourcingBriefDto
        {
            Id = brief.Id,
            BriefCode = brief.BriefCode,
            Title = brief.Title,
            ExecutiveSummary = brief.ExecutiveSummary,
            Status = brief.Status.ToString(),
            Priority = "Medium", // TODO: Add priority to model
            CreatedAt = brief.CreatedAt,
            ResponseDeadline = brief.ResponseDeadline,
            LinkedRequestCount = brief.LinkedRequests?.Count ?? 0,
            ProductCount = brief.Products?.Count ?? 0,
            TotalVolume = brief.Products?.Sum(p => p.TotalQuantity) ?? 0,
            TargetSupplierCount = brief.TargetSuppliers?.Count ?? 0,
            ResponseCount = brief.Responses?.Count(r => r.Status == BriefResponseStatus.Submitted) ?? 0,
            QualityScore = brief.QualityScore,
            ResponseRate = brief.ResponseRate,
            LinkedRequests = brief.LinkedRequests?.Select(lr => new LinkedRequestDto
            {
                RequestId = lr.RequestId,
                RequestNumber = lr.Request?.RequestNumber,
                RequestTitle = lr.Request?.Title,
                IsPrimary = lr.IsPrimary
            }).ToList()
        };
    }

    private string GenerateConsoleCode()
    {
        var year = DateTime.Now.Year;
        var lastConsole = _context.Consoles
            .Where(c => c.ConsoleCode.StartsWith($"CON-{year}-"))
            .OrderByDescending(c => c.ConsoleCode)
            .FirstOrDefault();

        int nextNumber = 1;
        if (lastConsole != null)
        {
            var parts = lastConsole.ConsoleCode.Split('-');
            if (parts.Length == 3 && int.TryParse(parts[2], out int lastNumber))
            {
                nextNumber = lastNumber + 1;
            }
        }

        return $"CON-{year}-{nextNumber:D4}";
    }

    private string GenerateBriefCode()
    {
        var year = DateTime.Now.Year;
        var lastBrief = _context.SourcingBriefs
            .Where(sb => sb.BriefCode.StartsWith($"SB-{year}-"))
            .OrderByDescending(sb => sb.BriefCode)
            .FirstOrDefault();

        int nextNumber = 1;
        if (lastBrief != null)
        {
            var parts = lastBrief.BriefCode.Split('-');
            if (parts.Length == 3 && int.TryParse(parts[2], out int lastNumber))
            {
                nextNumber = lastNumber + 1;
            }
        }

        return $"SB-{year}-{nextNumber:D4}";
    }

    private decimal CalculateBriefQualityScore(SourcingBrief brief, List<BriefProduct> products)
    {
        decimal score = 0;
        int factors = 0;

        // Factor 1: Completeness of information
        if (!string.IsNullOrWhiteSpace(brief.ExecutiveSummary))
        {
            score += 20;
            factors++;
        }

        // Factor 2: Product specifications
        var productsWithSpecs = products.Count(p => !string.IsNullOrWhiteSpace(p.Specifications));
        if (products.Any())
        {
            score += (decimal)productsWithSpecs / products.Count * 25;
            factors++;
        }

        // Factor 3: Target prices provided
        var productsWithPrices = products.Count(p => p.TargetPrice.HasValue);
        if (products.Any())
        {
            score += (decimal)productsWithPrices / products.Count * 25;
            factors++;
        }

        // Factor 4: Timeline clarity
        if (brief.ResponseDeadline.HasValue && brief.RequiredDeliveryDate.HasValue)
        {
            score += 15;
            factors++;
        }

        // Factor 5: Commercial terms
        if (!string.IsNullOrWhiteSpace(brief.PreferredIncoterms) && !string.IsNullOrWhiteSpace(brief.PreferredPaymentTerms))
        {
            score += 15;
            factors++;
        }

        return factors > 0 ? score : 0;
    }

    private decimal CalculateSpecificationCompleteness(SourcingBrief brief)
    {
        if (!brief.Products.Any())
            return 0;

        var completenessScores = brief.Products.Select(p =>
        {
            decimal productScore = 0;
            if (!string.IsNullOrWhiteSpace(p.ProductName)) productScore += 20;
            if (!string.IsNullOrWhiteSpace(p.Specifications)) productScore += 30;
            if (!string.IsNullOrWhiteSpace(p.QualityRequirements)) productScore += 20;
            if (p.TargetPrice.HasValue) productScore += 15;
            if (!string.IsNullOrWhiteSpace(p.BenchmarkBrand)) productScore += 15;
            return productScore;
        });

        return completenessScores.Average();
    }

    private decimal CalculateRequirementClarity(SourcingBrief brief)
    {
        decimal score = 0;
        
        if (!string.IsNullOrWhiteSpace(brief.ExecutiveSummary))
            score += 25;
        
        if (brief.ResponseDeadline.HasValue)
            score += 25;
        
        if (brief.RequiredDeliveryDate.HasValue)
            score += 25;
        
        if (!string.IsNullOrWhiteSpace(brief.PreferredIncoterms))
            score += 12.5m;
        
        if (!string.IsNullOrWhiteSpace(brief.PreferredPaymentTerms))
            score += 12.5m;

        return score;
    }

    private decimal CalculateVolumeAttractiveness(SourcingBrief brief)
    {
        if (!brief.Products.Any())
            return 0;

        var totalValue = brief.Products
            .Where(p => p.TargetPrice.HasValue)
            .Sum(p => p.TotalQuantity * p.TargetPrice!.Value);

        // Score based on total value tiers
        if (totalValue >= 1000000) return 100;
        if (totalValue >= 500000) return 85;
        if (totalValue >= 100000) return 70;
        if (totalValue >= 50000) return 55;
        if (totalValue >= 10000) return 40;
        return 25;
    }

    private bool SourcingBriefExists(int id)
    {
        return _context.SourcingBriefs.Any(e => e.Id == id);
    }
    
    // POST: api/SourcingBrief/{id}/match-suppliers
    [HttpPost("{id}/match-suppliers")]
    public async Task<ActionResult<IEnumerable<SupplierMatchDto>>> MatchSuppliers(int id)
    {
        try
        {
            _logger.LogInformation($"Starting supplier matching for brief {id}");
            
            // Use reasonable matching - show suppliers with actual sunflower oil products
            var options = new SupplierMatchingOptions
            {
                MinimumScore = 70m, // Show 70%+ matches (still high confidence for actual products)
                MaxResults = 30,
                IncludeUnverified = true, // Include all suppliers for now
                RequireExactMatch = false // Allow both exact and category matches
            };
            
            var matches = await _matchingService.MatchSuppliersForBrief(id, options);
            
            if (!matches.Any())
            {
                _logger.LogWarning($"No supplier matches found for brief {id}");
                return Ok(new List<SupplierMatchDto>());
            }
            
            _logger.LogInformation($"Found {matches.Count} supplier matches for brief {id}");
            
            // Log match details for debugging
            foreach (var match in matches.Take(5))
            {
                _logger.LogInformation($"Supplier: {match.CompanyName}, Score: {match.NormalizedScore:F1}%, Products: {match.AvailableProducts?.Count ?? 0}");
                if (match.AvailableProducts?.Any() == true)
                {
                    _logger.LogInformation($"  Products: {string.Join(", ", match.AvailableProducts.Take(3))}");
                }
            }
            
            // Map to DTOs that match frontend expectations
            var dtos = matches.Select(m => new SupplierMatchDto
            {
                SupplierId = m.SupplierId,
                SupplierName = m.CompanyName, // Frontend expects 'supplierName'
                MatchScore = (double)(m.NormalizedScore / 100m), // Convert to 0-1 range for frontend
                MatchedProductCount = m.AvailableProducts?.Count ?? 0, // Frontend expects 'matchedProductCount'
                TotalBriefProducts = 0, // Will be set if needed
                MatchedProducts = m.AvailableProducts.Take(5).Select((p, idx) => new MatchedProductDto
                {
                    ProductId = idx + 1,
                    ProductName = p ?? "",
                    UnitPrice = null,
                    Currency = "USD",
                    MOQ = 0
                }).ToList()
            }).ToList();
            
            return Ok(dtos);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error matching suppliers for brief {BriefId}", id);
            return StatusCode(500, "Error matching suppliers");
        }
    }
    
    private double CalculateSimilarity(string s1, string s2)
    {
        if (string.IsNullOrEmpty(s1) || string.IsNullOrEmpty(s2))
            return 0;
            
        // Simple word-based similarity
        var words1 = s1.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        var words2 = s2.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        
        var commonWords = words1.Intersect(words2).Count();
        var totalWords = Math.Max(words1.Length, words2.Length);
        
        return totalWords > 0 ? (double)commonWords / totalWords : 0;
    }
}

// DTOs for supplier matching
public class SupplierMatchDto
{
    public int SupplierId { get; set; }
    public string SupplierName { get; set; } = string.Empty;
    public double MatchScore { get; set; }
    public int MatchedProductCount { get; set; }
    public int TotalBriefProducts { get; set; }
    public List<MatchedProductDto> MatchedProducts { get; set; } = new();
}

public class MatchedProductDto  
{
    public int ProductId { get; set; }
    public string ProductName { get; set; } = string.Empty;
    public decimal? UnitPrice { get; set; }
    public string? Currency { get; set; }
    public int MOQ { get; set; }
}