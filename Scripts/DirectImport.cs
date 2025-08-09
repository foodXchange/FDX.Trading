using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Services;
using Microsoft.Extensions.DependencyInjection;

// This script directly imports suppliers and products bypassing the API

var connectionString = "Server=fdx-sql-prod.database.windows.net;Database=fdxdb;User Id=fdxadmin;Password=FDX2030!;TrustServerCertificate=True;";

var serviceProvider = new ServiceCollection()
    .AddDbContext<FdxTradingContext>(options =>
        options.UseSqlServer(connectionString))
    .BuildServiceProvider();

using var scope = serviceProvider.CreateScope();
var context = scope.ServiceProvider.GetRequiredService<FdxTradingContext>();

var importService = new SupplierProductImportService(context);
var csvFilePath = @"C:\Users\fdxadmin\Downloads\Products 9_8_2025.csv";

Console.WriteLine("Starting import from: " + csvFilePath);
var result = await importService.ImportFromCsvAsync(csvFilePath);

Console.WriteLine($"Import {(result.Success ? "Successful" : "Failed")}: {result.Message}");
Console.WriteLine($"Suppliers Created: {result.SuppliersCreated}");
Console.WriteLine($"Products Created: {result.ProductsCreated}");
Console.WriteLine($"Associations Created: {result.AssociationsCreated}");

if (result.Errors.Any())
{
    Console.WriteLine("\nErrors:");
    foreach (var error in result.Errors.Take(10))
    {
        Console.WriteLine($"  - {error}");
    }
    if (result.Errors.Count > 10)
    {
        Console.WriteLine($"  ... and {result.Errors.Count - 10} more errors");
    }
}