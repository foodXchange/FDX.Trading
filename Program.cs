using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Services;

var builder = WebApplication.CreateBuilder(args);

// Add user secrets in development
if (builder.Environment.IsDevelopment() || builder.Environment.IsProduction())
{
    builder.Configuration.AddUserSecrets<Program>();
}

// Get connection string
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
if (string.IsNullOrEmpty(connectionString) || connectionString == "MOVED_TO_USER_SECRETS")
{
    // Fallback to direct connection string if user secrets not loaded
    connectionString = "Server=fdx-sql-prod.database.windows.net;Database=fdxdb;User Id=fdxadmin;Password=FDX2030!;TrustServerCertificate=True;";
}

// Add services
builder.Services.AddDbContext<FdxTradingContext>(options =>
    options.UseSqlServer(connectionString));

builder.Services.AddControllers();
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader());
});

// Add services
builder.Services.AddScoped<CsvProductImportService>();
builder.Services.AddScoped<SupplierProductImportService>();
builder.Services.AddScoped<PriceBookImportService>();
builder.Services.AddHttpClient<AzureAIService>();
builder.Services.AddScoped<ConsoleService>();
builder.Services.AddScoped<DataMigrationService>();
builder.Services.AddScoped<ProductAggregationService>();
builder.Services.AddScoped<SupplierScoringService>();
builder.Services.AddScoped<ImprovedSupplierMatchingService>(); // New improved matching service
builder.Services.AddScoped<ComprehensiveDataImportService>();
builder.Services.AddScoped<PriceBookService>();
builder.Services.AddScoped<ProductCategoryImportService>();
builder.Services.AddScoped<ContractImportService>();

var app = builder.Build();

// Configure pipeline
app.UseCors("AllowAll");
app.UseDefaultFiles();

// Configure static files with proper content types
var provider = new Microsoft.AspNetCore.StaticFiles.FileExtensionContentTypeProvider();
provider.Mappings[".js"] = "text/javascript; charset=utf-8";
provider.Mappings[".css"] = "text/css; charset=utf-8";
provider.Mappings[".json"] = "application/json; charset=utf-8";
provider.Mappings[".html"] = "text/html; charset=utf-8";

app.UseStaticFiles(new StaticFileOptions
{
    ContentTypeProvider = provider,
    OnPrepareResponse = ctx =>
    {
        // Add security headers
        ctx.Context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
        
        // Add cache headers for better performance
        const int durationInSeconds = 60 * 60 * 24 * 7; // 7 days
        ctx.Context.Response.Headers.Add("Cache-Control", $"public, max-age={durationInSeconds}");
    }
});

app.MapControllers();

app.Run();