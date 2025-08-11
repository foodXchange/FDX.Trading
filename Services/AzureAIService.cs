using System.Text;
using System.Text.Json;
using System.Net.Http;
using Microsoft.Extensions.Configuration;

namespace FDX.Trading.Services
{
    public class AzureAIService
    {
        private readonly HttpClient _httpClient;
        private readonly string _endpoint;
        private readonly string _apiKey;
        private readonly IConfiguration _configuration;

        public AzureAIService(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _configuration = configuration;
            
            // Get Azure OpenAI settings from configuration
            _endpoint = configuration["AzureOpenAI:Endpoint"] ?? "";
            _apiKey = configuration["AzureOpenAI:ApiKey"] ?? "";
            
            // Set up headers
            _httpClient.DefaultRequestHeaders.Add("api-key", _apiKey);
        }

        public async Task<RequestAnalysisResult> AnalyzeRequest(string requestTitle, string requestDescription, List<string> productNames)
        {
            try
            {
                var prompt = BuildAnalysisPrompt(requestTitle, requestDescription, productNames);
                var response = await GetAICompletion(prompt);
                return ParseAnalysisResponse(response);
            }
            catch (Exception ex)
            {
                // Fallback to basic analysis if AI fails
                return GetFallbackAnalysis(requestTitle, requestDescription, productNames);
            }
        }

        private string BuildAnalysisPrompt(string title, string description, List<string> products)
        {
            var productList = string.Join(", ", products);
            
            return $@"
Analyze this procurement request and extract structured information:

Title: {title}
Description: {description}
Products: {productList}

Extract and return in JSON format:
1. category: Main food category (Pasta, Cereals, Dairy, Beverages, Snacks, Frozen, Fresh, Organic, or General)
2. urgency: Priority level (Critical, High, Medium, Low)
3. estimatedValue: Estimated total value in USD
4. isContainerOrder: Is this a container-level order (true/false)
5. containerCount: Number of containers if applicable
6. requiresColdChain: Needs refrigeration (true/false)
7. suggestedSupplierTypes: Array of supplier types to contact
8. keywords: Array of important keywords for matching
9. consoleType: Recommended console type (Food, Standard, Complex)
10. estimatedProcessingDays: Days needed to complete

Example response format:
{{
    ""category"": ""Pasta"",
    ""urgency"": ""High"",
    ""estimatedValue"": 145000,
    ""isContainerOrder"": true,
    ""containerCount"": 40,
    ""requiresColdChain"": false,
    ""suggestedSupplierTypes"": [""Food Distributor"", ""Import Specialist""],
    ""keywords"": [""premium"", ""pasta"", ""containers"", ""italian""],
    ""consoleType"": ""Food"",
    ""estimatedProcessingDays"": 10
}}";
        }

        private async Task<string> GetAICompletion(string prompt)
        {
            // If no API key configured, use fallback
            if (string.IsNullOrEmpty(_apiKey) || string.IsNullOrEmpty(_endpoint))
            {
                return "{}"; // Return empty JSON, will use fallback
            }

            var requestBody = new
            {
                messages = new[]
                {
                    new { role = "system", content = "You are an expert procurement analyst specializing in food products and supply chain optimization." },
                    new { role = "user", content = prompt }
                },
                max_tokens = 500,
                temperature = 0.3,
                response_format = new { type = "json_object" }
            };

            var json = JsonSerializer.Serialize(requestBody);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            // Azure OpenAI endpoint format: https://{resource}.openai.azure.com/openai/deployments/{deployment}/chat/completions?api-version=2024-02-01
            var deploymentName = _configuration["AzureOpenAI:DeploymentName"] ?? "gpt-35-turbo";
            var apiVersion = "2024-02-01";
            var url = $"{_endpoint}/openai/deployments/{deploymentName}/chat/completions?api-version={apiVersion}";

            var response = await _httpClient.PostAsync(url, content);
            
            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                var result = JsonDocument.Parse(responseContent);
                return result.RootElement.GetProperty("choices")[0].GetProperty("message").GetProperty("content").GetString() ?? "{}";
            }

            return "{}";
        }

        private RequestAnalysisResult ParseAnalysisResponse(string jsonResponse)
        {
            try
            {
                if (string.IsNullOrEmpty(jsonResponse) || jsonResponse == "{}")
                {
                    return new RequestAnalysisResult();
                }

                var doc = JsonDocument.Parse(jsonResponse);
                var root = doc.RootElement;

                return new RequestAnalysisResult
                {
                    Category = root.TryGetProperty("category", out var cat) ? cat.GetString() ?? "General" : "General",
                    Urgency = root.TryGetProperty("urgency", out var urg) ? ParseUrgency(urg.GetString()) : RequestUrgency.Medium,
                    EstimatedValue = root.TryGetProperty("estimatedValue", out var val) ? val.GetDecimal() : 0,
                    IsContainerOrder = root.TryGetProperty("isContainerOrder", out var cont) && cont.GetBoolean(),
                    ContainerCount = root.TryGetProperty("containerCount", out var count) ? count.GetInt32() : 0,
                    RequiresColdChain = root.TryGetProperty("requiresColdChain", out var cold) && cold.GetBoolean(),
                    SuggestedSupplierTypes = root.TryGetProperty("suggestedSupplierTypes", out var types) 
                        ? types.EnumerateArray().Select(t => t.GetString() ?? "").ToList() 
                        : new List<string>(),
                    Keywords = root.TryGetProperty("keywords", out var keys) 
                        ? keys.EnumerateArray().Select(k => k.GetString() ?? "").ToList()
                        : new List<string>(),
                    ConsoleType = root.TryGetProperty("consoleType", out var cType) ? cType.GetString() ?? "Standard" : "Standard",
                    EstimatedProcessingDays = root.TryGetProperty("estimatedProcessingDays", out var days) ? days.GetInt32() : 7
                };
            }
            catch
            {
                return new RequestAnalysisResult();
            }
        }

        private RequestAnalysisResult GetFallbackAnalysis(string title, string description, List<string> products)
        {
            var content = $"{title} {description} {string.Join(" ", products)}".ToLower();
            
            // Basic keyword detection
            var foodKeywords = new[] { "pasta", "cereal", "dairy", "beverage", "snack", "frozen", "fresh", "organic", "food", "container" };
            var urgentKeywords = new[] { "urgent", "asap", "immediately", "critical", "rush" };
            
            var isFood = foodKeywords.Any(k => content.Contains(k));
            var isUrgent = urgentKeywords.Any(k => content.Contains(k));
            var isContainer = content.Contains("container");
            
            // Extract numbers for container count
            var numbers = System.Text.RegularExpressions.Regex.Matches(content, @"\d+");
            var containerCount = 0;
            if (isContainer && numbers.Count > 0)
            {
                int.TryParse(numbers[0].Value, out containerCount);
            }

            return new RequestAnalysisResult
            {
                Category = DetectFoodCategory(content),
                Urgency = isUrgent ? RequestUrgency.High : RequestUrgency.Medium,
                EstimatedValue = containerCount * 3500, // Rough estimate
                IsContainerOrder = isContainer,
                ContainerCount = containerCount,
                RequiresColdChain = content.Contains("frozen") || content.Contains("fresh"),
                SuggestedSupplierTypes = isFood ? new List<string> { "Food Distributor", "Wholesale Supplier" } : new List<string> { "General Supplier" },
                Keywords = foodKeywords.Where(k => content.Contains(k)).ToList(),
                ConsoleType = isFood ? "Food" : "Standard",
                EstimatedProcessingDays = isUrgent ? 5 : 10
            };
        }

        private string DetectFoodCategory(string content)
        {
            if (content.Contains("pasta")) return "Pasta";
            if (content.Contains("cereal")) return "Cereals";
            if (content.Contains("dairy") || content.Contains("milk") || content.Contains("cheese")) return "Dairy";
            if (content.Contains("beverage") || content.Contains("drink")) return "Beverages";
            if (content.Contains("snack")) return "Snacks";
            if (content.Contains("frozen")) return "Frozen";
            if (content.Contains("fresh")) return "Fresh";
            if (content.Contains("organic")) return "Organic";
            return "General";
        }

        private RequestUrgency ParseUrgency(string? urgency)
        {
            return urgency?.ToLower() switch
            {
                "critical" => RequestUrgency.Critical,
                "high" => RequestUrgency.High,
                "medium" => RequestUrgency.Medium,
                "low" => RequestUrgency.Low,
                _ => RequestUrgency.Medium
            };
        }

        public async Task<List<int>> FindBestSuppliers(RequestAnalysisResult analysis, int maxResults = 5)
        {
            // This would integrate with your database to find suppliers
            // For now, returning placeholder
            return new List<int> { 1, 2, 3, 4, 5 };
        }
    }

    public class RequestAnalysisResult
    {
        public string Category { get; set; } = "General";
        public RequestUrgency Urgency { get; set; } = RequestUrgency.Medium;
        public decimal EstimatedValue { get; set; }
        public bool IsContainerOrder { get; set; }
        public int ContainerCount { get; set; }
        public bool RequiresColdChain { get; set; }
        public List<string> SuggestedSupplierTypes { get; set; } = new();
        public List<string> Keywords { get; set; } = new();
        public string ConsoleType { get; set; } = "Standard";
        public int EstimatedProcessingDays { get; set; } = 7;
    }

    public enum RequestUrgency
    {
        Critical,
        High,
        Medium,
        Low
    }
}