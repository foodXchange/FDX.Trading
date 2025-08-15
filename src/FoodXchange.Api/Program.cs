using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.AI;
using FoodXchange.Infrastructure.Data;
using FoodXchange.Domain.Abstractions;
using OpenAI;
using System.ClientModel;

var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddOpenApi();
builder.Services.AddEndpointsApiExplorer();

// Observability
builder.Services.AddApplicationInsightsTelemetry();
builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>("database");

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

// Data
var connectionString = builder.Configuration.GetConnectionString("Sql") 
    ?? "Server=(localdb)\\mssqllocaldb;Database=FoodXchange;Trusted_Connection=true;MultipleActiveResultSets=true";

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(connectionString));

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

// AI endpoint (if configured)
if (!string.IsNullOrEmpty(openAiEndpoint))
{
    app.MapPost("/ai/complete", async (IChatClient chat, string prompt, CancellationToken ct) =>
    {
        var messages = new List<ChatMessage> { new ChatMessage(ChatRole.User, prompt) };
        var response = await chat.GetResponseAsync(messages, null, ct);
        return Results.Ok(new { reply = response.Text });
    })
    .WithName("AIComplete");
}

app.Run();
