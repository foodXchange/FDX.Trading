using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Services;
using FDX.Trading.Utils;
using Microsoft.Identity.Web;
using Microsoft.Identity.Web.UI;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.AspNetCore.Authorization;
using Microsoft.ApplicationInsights.AspNetCore.Extensions;
using Microsoft.AspNetCore.RateLimiting;
using System.Threading.RateLimiting;
using Azure.Communication.Email;
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;

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

// Add Azure AD authentication
builder.Services.AddAuthentication(OpenIdConnectDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(builder.Configuration.GetSection("AzureAd"));

builder.Services.AddControllersWithViews()
    .AddMicrosoftIdentityUI();

builder.Services.AddAuthorization(options =>
{
    // Define role-based policies
    options.AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"));
    options.AddPolicy("BuyerOnly", policy => policy.RequireRole("Buyer", "Admin"));
    options.AddPolicy("SupplierOnly", policy => policy.RequireRole("Supplier", "Admin"));
    options.AddPolicy("ExpertOnly", policy => policy.RequireRole("Expert", "Admin"));
    options.AddPolicy("AuthenticatedUser", policy => policy.RequireAuthenticatedUser());
    
    // Composite policies
    options.AddPolicy("BuyerOrSupplier", policy => 
        policy.RequireRole("Buyer", "Supplier", "Admin"));
    options.AddPolicy("ComplianceAccess", policy => 
        policy.RequireRole("Buyer", "Expert", "Admin"));
    options.AddPolicy("OrderAccess", policy => 
        policy.RequireRole("Buyer", "Supplier", "Admin"));
    options.AddPolicy("FinanceAccess", policy => 
        policy.RequireRole("Buyer", "Admin"));
});

// Add services
builder.Services.AddDbContext<FdxTradingContext>(options =>
    options.UseSqlServer(connectionString));

// Add basic web services
builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor()
    .AddMicrosoftIdentityConsentHandler();

builder.Services.AddControllers();
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader());
});

// Add services
builder.Services.AddScoped<IComplianceService, ComplianceService>();
builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddScoped<ICsvImporter, CsvImporter>();
builder.Services.AddScoped<IEmailService, EmailService>();
builder.Services.AddScoped<IInvitationService, InvitationService>();
builder.Services.AddHttpClient();

// Add Azure Communication Services for email
var acsConnectionString = builder.Configuration["AzureCommunicationServices:ConnectionString"];
if (!string.IsNullOrEmpty(acsConnectionString) && acsConnectionString != "MOVED_TO_USER_SECRETS")
{
    builder.Services.AddSingleton(new EmailClient(acsConnectionString));
}
else
{
    // Add a null email client for development without Azure Communication Services
    builder.Services.AddSingleton<EmailClient>(provider => null);
}

// Add Application Insights
builder.Services.AddApplicationInsightsTelemetry(new ApplicationInsightsServiceOptions
{
    ConnectionString = builder.Configuration["ApplicationInsights:ConnectionString"],
    EnableAdaptiveSampling = true,
    EnableQuickPulseMetricStream = true
});

// Add localization support
builder.Services.AddLocalization(options => options.ResourcesPath = "Resources");
builder.Services.Configure<RequestLocalizationOptions>(options =>
{
    var supportedCultures = new[] { "en-US", "he-IL" };
    options.SetDefaultCulture("en-US")
        .AddSupportedCultures(supportedCultures)
        .AddSupportedUICultures(supportedCultures);
});

// Add rate limiting for public forms
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("public-form", limiterOptions =>
    {
        limiterOptions.PermitLimit = 5;
        limiterOptions.Window = TimeSpan.FromMinutes(15);
        limiterOptions.QueueProcessingOrder = System.Threading.RateLimiting.QueueProcessingOrder.OldestFirst;
        limiterOptions.QueueLimit = 2;
    });
});

var app = builder.Build();

// Configure pipeline
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseCors("AllowAll");
app.UseRateLimiter();
app.UseRequestLocalization();

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
        ctx.Context.Response.Headers.Append("X-Content-Type-Options", "nosniff");
        
        // Add cache headers for better performance
        const int durationInSeconds = 60 * 60 * 24 * 7; // 7 days
        ctx.Context.Response.Headers.Append("Cache-Control", $"public, max-age={durationInSeconds}");
    }
});

app.UseRouting();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.MapRazorPages();
app.MapBlazorHub();
app.MapFallbackToPage("/_Host");

app.Run();