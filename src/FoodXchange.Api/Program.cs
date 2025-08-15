using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.AI;
using FoodXchange.Infrastructure.Data;
using FoodXchange.Domain.Abstractions;
using OpenAI;
using System.ClientModel;
using System.Data;
using System.Diagnostics;
using Microsoft.Data.SqlClient;
using Azure.Identity;

var builder = WebApplication.CreateBuilder(args);

// Add Azure Key Vault configuration (if deployed to Azure)
if (!builder.Environment.IsDevelopment())
{
    var keyVaultName = builder.Configuration["KeyVaultName"];
    if (!string.IsNullOrEmpty(keyVaultName))
    {
        var keyVaultUri = new Uri($"https://{keyVaultName}.vault.azure.net/");
        builder.Configuration.AddAzureKeyVault(keyVaultUri, new DefaultAzureCredential());
    }
}

// Add services
builder.Services.AddOpenApi();
builder.Services.AddEndpointsApiExplorer();

// Data
var connectionString = builder.Configuration.GetConnectionString("Sql") 
    ?? "Server=(localdb)\\mssqllocaldb;Database=FoodXchange;Trusted_Connection=true;MultipleActiveResultSets=true";

// Observability
builder.Services.AddApplicationInsightsTelemetry();
builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>("database")
    .AddSqlServer(
        connectionString: connectionString,
        name: "AzureSQL",
        timeout: TimeSpan.FromSeconds(5));

// CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowBlazorApp", policy =>
    {
        policy.WithOrigins("https://localhost:5001", "http://localhost:5000")
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(connectionString, sql => sql.EnableRetryOnFailure()));

// Repositories & Unit of Work
builder.Services.AddScoped(typeof(IRepository<>), typeof(Repository<>));
builder.Services.AddScoped<IUnitOfWork, UnitOfWork>();

// Azure OpenAI (optional)
var openAiEndpoint = builder.Configuration["AZURE_OPENAI_ENDPOINT"];
var openAiKey = builder.Configuration["AZURE_OPENAI_KEY"];
var openAiDeployment = builder.Configuration["AZURE_OPENAI_DEPLOYMENT"];

if (!string.IsNullOrEmpty(openAiEndpoint) && !string.IsNullOrEmpty(openAiKey))
{
    // Create OpenAI client for Azure
    var credential = new ApiKeyCredential(openAiKey);
    var options = new OpenAIClientOptions
    {
        Endpoint = new Uri(openAiEndpoint)
    };
    var openAiClient = new OpenAIClient(credential, options);
    
    // Register as IChatClient using Microsoft.Extensions.AI
    builder.Services.AddSingleton(openAiClient);
    builder.Services.AddChatClient(services => 
        services.GetRequiredService<OpenAIClient>()
            .AsChatClient(openAiDeployment ?? "gpt-4o-mini"));
}

var app = builder.Build();

// Configure pipeline
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();
app.UseCors("AllowBlazorApp");

// Health checks
app.MapHealthChecks("/health");

// Example endpoint
app.MapGet("/ping", () => Results.Ok(new { ok = true, at = DateTimeOffset.UtcNow }))
   .WithName("Ping");

// DB Verification endpoint (admin-only in production)
app.MapGet("/db/verify", async (IConfiguration cfg) =>
{
    var cs = cfg.GetConnectionString("Sql");
    var sw = Stopwatch.StartNew();
    
    try
    {
        await using var conn = new SqlConnection(cs);
        await conn.OpenAsync();
        
        await using var cmd = conn.CreateCommand();
        cmd.CommandText = @"
            SELECT 
                @@VERSION AS ServerVersion, 
                DB_NAME() AS DatabaseName, 
                SUSER_SNAME() AS AuthenticatedAs";
        
        await using var reader = await cmd.ExecuteReaderAsync(CommandBehavior.SingleRow);
        await reader.ReadAsync();
        
        sw.Stop();
        return Results.Ok(new
        {
            ok = true,
            latencyMs = sw.ElapsedMilliseconds,
            serverVersion = reader["ServerVersion"]?.ToString() ?? "unknown",
            database = reader["DatabaseName"]?.ToString() ?? "unknown",
            authenticatedAs = reader["AuthenticatedAs"]?.ToString(),
            utc = DateTimeOffset.UtcNow
        });
    }
    catch (Exception ex)
    {
        sw.Stop();
        return Results.Ok(new
        {
            ok = false,
            latencyMs = sw.ElapsedMilliseconds,
            error = ex.Message,
            utc = DateTimeOffset.UtcNow
        });
    }
})
.WithName("DbVerify")
.WithMetadata(new EndpointNameMetadata("DbVerify"));

// AI endpoints (if configured)
if (!string.IsNullOrEmpty(openAiEndpoint))
{
    app.MapPost("/ai/complete", async (IChatClient chat, string prompt, CancellationToken ct) =>
    {
        var messages = new List<ChatMessage> { new ChatMessage(ChatRole.User, prompt) };
        var response = await chat.GetResponseAsync(messages, null, ct);
        return Results.Ok(new { reply = response.Text });
    })
    .WithName("AIComplete");
    
    app.MapGet("/ai/status", async (IChatClient chat, CancellationToken ct) =>
    {
        var sw = Stopwatch.StartNew();
        try
        {
            var messages = new List<ChatMessage> { new ChatMessage(ChatRole.User, "ping") };
            var response = await chat.GetResponseAsync(messages, null, ct);
            sw.Stop();
            
            return Results.Ok(new
            {
                ok = response != null,
                latencyMs = sw.ElapsedMilliseconds,
                model = response?.ModelId ?? "unknown",
                utc = DateTimeOffset.UtcNow
            });
        }
        catch (Exception ex)
        {
            sw.Stop();
            return Results.Ok(new
            {
                ok = false,
                latencyMs = sw.ElapsedMilliseconds,
                error = ex.Message,
                utc = DateTimeOffset.UtcNow
            });
        }
    })
    .WithName("AIStatus");
}

app.Run();
