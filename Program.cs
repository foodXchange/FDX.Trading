using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;

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

var app = builder.Build();

// Configure pipeline
app.UseCors("AllowAll");
app.UseDefaultFiles();
app.UseStaticFiles();
app.MapControllers();

app.Run();