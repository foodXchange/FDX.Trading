using Microsoft.EntityFrameworkCore;
using FDX.Trading.Models;
using FDX.Trading.Data;
using System.Text.Json;

namespace FDX.Trading.Services
{
    public class ConsoleService
    {
        private readonly FdxTradingContext _context;
        private readonly AzureAIService _aiService;

        public ConsoleService(FdxTradingContext context, AzureAIService aiService)
        {
            _context = context;
            _aiService = aiService;
        }

        public async Task<ProjectConsole> CreateConsoleFromRequest(Request request)
        {
            // Use AI to analyze the request
            var productNames = request.RequestItems?.Select(i => i.ProductName ?? "").ToList() ?? new List<string>();
            var analysis = await _aiService.AnalyzeRequest(
                request.Title ?? "", 
                request.Description ?? "", 
                productNames
            );

            // Use AI analysis or fallback to basic detection
            var consoleType = analysis.ConsoleType == "Food" ? ConsoleType.Procurement : ConsoleType.Procurement;
            var priority = ConvertUrgencyToPriority(analysis.Urgency);
            var owner = await SelectBestOwner(consoleType);

            // Generate console code
            var year = DateTime.Now.Year;
            var consoleCode = await GenerateConsoleCode(year);

            // Create console
            var console = new ProjectConsole
            {
                ConsoleCode = consoleCode,
                Title = $"Procurement Console: {request.Title}",
                Type = consoleType,
                Priority = priority,
                Status = ConsoleStatus.Active,
                SourceType = "Request",
                SourceId = request.Id,
                OwnerId = owner.Id,
                CurrentStageNumber = 1,
                Metadata = CreateConsoleMetadata(request, analysis),
                CreatedAt = DateTime.Now,
                UpdatedAt = DateTime.Now
            };

            _context.Consoles.Add(console);
            await _context.SaveChangesAsync();

            // Create workflow stages
            await CreateWorkflowStages(console, consoleType);

            return console;
        }

        private ConsolePriority ConvertUrgencyToPriority(RequestUrgency urgency)
        {
            return urgency switch
            {
                RequestUrgency.Critical => ConsolePriority.Critical,
                RequestUrgency.High => ConsolePriority.High,
                RequestUrgency.Medium => ConsolePriority.Medium,
                RequestUrgency.Low => ConsolePriority.Low,
                _ => ConsolePriority.Medium
            };
        }

        private ConsolePriority DeterminePriority(Request request)
        {
            // Determine priority based on request items and total value
            var totalItems = request.RequestItems?.Count ?? 0;
            var hasHighValueItems = request.RequestItems?.Any(i => i.TargetPrice > 1000) ?? false;

            if (totalItems > 5 || hasHighValueItems)
                return ConsolePriority.High;
            
            if (totalItems > 2)
                return ConsolePriority.Medium;
            
            return ConsolePriority.Low;
        }

        private async Task<User> SelectBestOwner(ConsoleType consoleType)
        {
            // Find the best expert for this console type
            // For now, find an expert or admin user
            var expert = await _context.FdxUsers
                .Where(u => u.Type == UserType.Expert && u.IsActive == true)
                .FirstOrDefaultAsync();

            if (expert != null)
                return expert;

            // Fallback to admin
            var admin = await _context.FdxUsers
                .Where(u => u.Type == UserType.Admin)
                .FirstOrDefaultAsync();

            return admin ?? throw new InvalidOperationException("No suitable console owner found");
        }

        private async Task<string> GenerateConsoleCode(int year)
        {
            var lastConsole = await _context.Consoles
                .Where(c => c.ConsoleCode.StartsWith($"CON-{year}-"))
                .OrderByDescending(c => c.ConsoleCode)
                .FirstOrDefaultAsync();

            int nextNumber = 1;
            if (lastConsole != null)
            {
                var lastNumberStr = lastConsole.ConsoleCode.Split('-').Last();
                if (int.TryParse(lastNumberStr, out int lastNumber))
                    nextNumber = lastNumber + 1;
            }

            return $"CON-{year}-{nextNumber:D4}";
        }

        private string CreateConsoleMetadata(Request request, RequestAnalysisResult analysis)
        {
            var metadata = new
            {
                SourceRequest = new
                {
                    Id = request.Id,
                    RequestNumber = request.RequestNumber,
                    BuyerCompany = request.BuyerCompany,
                    ItemCount = request.RequestItems?.Count ?? 0,
                    Categories = ExtractCategories(request),
                    EstimatedValue = analysis.EstimatedValue > 0 ? analysis.EstimatedValue : EstimateValue(request)
                },
                AIAnalysis = new
                {
                    Category = analysis.Category,
                    Urgency = analysis.Urgency.ToString(),
                    IsContainerOrder = analysis.IsContainerOrder,
                    ContainerCount = analysis.ContainerCount,
                    RequiresColdChain = analysis.RequiresColdChain,
                    Keywords = analysis.Keywords,
                    EstimatedProcessingDays = analysis.EstimatedProcessingDays,
                    SuggestedSupplierTypes = analysis.SuggestedSupplierTypes
                },
                AutoCreated = true,
                CreationReason = "AI-powered automatic console creation from request submission"
            };

            return JsonSerializer.Serialize(metadata);
        }

        private string[] ExtractCategories(Request request)
        {
            var categories = new List<string>();
            
            // Extract categories from product names
            foreach (var item in request.RequestItems ?? new List<RequestItem>())
            {
                var productName = item.ProductName?.ToLower() ?? "";
                
                if (productName.Contains("pasta")) categories.Add("Pasta");
                if (productName.Contains("cereal")) categories.Add("Cereals");
                if (productName.Contains("dairy")) categories.Add("Dairy");
                if (productName.Contains("organic")) categories.Add("Organic");
                if (productName.Contains("frozen")) categories.Add("Frozen");
                if (productName.Contains("fresh")) categories.Add("Fresh");
            }

            return categories.Distinct().ToArray();
        }

        private decimal EstimateValue(Request request)
        {
            return request.RequestItems?.Sum(i => i.TargetPrice ?? 0) ?? 0;
        }

        private async Task CreateWorkflowStages(ProjectConsole console, ConsoleType consoleType)
        {
            var stages = GetDefaultWorkflowStages(consoleType);
            
            for (int i = 0; i < stages.Length; i++)
            {
                var stage = new WorkflowStage
                {
                    ConsoleId = console.Id,
                    StageNumber = i + 1,
                    StageName = stages[i].Name,
                    Description = stages[i].Description,
                    Status = i == 0 ? StageStatus.Active : StageStatus.Pending,
                    StageType = StageType.Action
                };

                _context.WorkflowStages.Add(stage);
            }

            await _context.SaveChangesAsync();
        }

        private (string Name, string Description)[] GetDefaultWorkflowStages(ConsoleType consoleType)
        {
            return consoleType switch
            {
                ConsoleType.Procurement => new[]
                {
                    ("Supplier Discovery", "Identify and contact relevant suppliers"),
                    ("Quote Collection", "Gather quotes and proposals from suppliers"),
                    ("Evaluation", "Compare quotes and assess supplier capabilities"),
                    ("Negotiation", "Negotiate terms and pricing"),
                    ("Approval", "Get final approval for selected supplier"),
                    ("Purchase Order", "Generate and send purchase order"),
                    ("Delivery Tracking", "Monitor delivery and quality confirmation")
                },
                _ => new[]
                {
                    ("Planning", "Define requirements and scope"),
                    ("Execution", "Execute the planned activities"),
                    ("Review", "Review results and close console")
                }
            };
        }
    }
}