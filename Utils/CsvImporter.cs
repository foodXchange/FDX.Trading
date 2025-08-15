using System.Data;
using System.Globalization;
using CsvHelper;
using CsvHelper.Configuration;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace FDX.Trading.Utils;

public interface ICsvImporter
{
    Task<int> ImportCommissionRatesAsync(string csvPath);
    Task<int> ImportInvoicesAsync(string csvPath);
    Task<int> ImportShippingAsync(string csvPath);
    Task NormalizeAllDataAsync();
}

public class CsvImporter : ICsvImporter
{
    private readonly string _connectionString;
    private readonly ILogger<CsvImporter> _logger;
    
    public CsvImporter(IConfiguration configuration, ILogger<CsvImporter> logger)
    {
        _connectionString = configuration.GetConnectionString("DefaultConnection") 
            ?? throw new InvalidOperationException("Connection string not configured");
        _logger = logger;
    }

    public async Task<int> ImportCommissionRatesAsync(string csvPath)
    {
        if (!File.Exists(csvPath))
        {
            _logger.LogWarning("Commission rates CSV not found: {Path}", csvPath);
            return 0;
        }

        try
        {
            // First, clear the staging table
            await using var conn = new SqlConnection(_connectionString);
            await conn.OpenAsync();
            
            await using (var cmd = new SqlCommand("TRUNCATE TABLE stg.CommissionRatesRaw", conn))
            {
                await cmd.ExecuteNonQueryAsync();
            }

            // Import CSV to staging
            var count = await BulkImportToStagingAsync(conn, "stg.CommissionRatesRaw", csvPath);
            
            _logger.LogInformation("Imported {Count} commission rate records", count);
            return count;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error importing commission rates from {Path}", csvPath);
            throw;
        }
    }

    public async Task<int> ImportInvoicesAsync(string csvPath)
    {
        if (!File.Exists(csvPath))
        {
            _logger.LogWarning("Invoices CSV not found: {Path}", csvPath);
            return 0;
        }

        try
        {
            await using var conn = new SqlConnection(_connectionString);
            await conn.OpenAsync();
            
            await using (var cmd = new SqlCommand("TRUNCATE TABLE stg.InvoicesRaw", conn))
            {
                await cmd.ExecuteNonQueryAsync();
            }

            var count = await BulkImportToStagingAsync(conn, "stg.InvoicesRaw", csvPath);
            
            _logger.LogInformation("Imported {Count} invoice records", count);
            return count;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error importing invoices from {Path}", csvPath);
            throw;
        }
    }

    public async Task<int> ImportShippingAsync(string csvPath)
    {
        if (!File.Exists(csvPath))
        {
            _logger.LogWarning("Shipping CSV not found: {Path}", csvPath);
            return 0;
        }

        try
        {
            await using var conn = new SqlConnection(_connectionString);
            await conn.OpenAsync();
            
            await using (var cmd = new SqlCommand("TRUNCATE TABLE stg.ShippingRaw", conn))
            {
                await cmd.ExecuteNonQueryAsync();
            }

            var count = await BulkImportToStagingAsync(conn, "stg.ShippingRaw", csvPath);
            
            _logger.LogInformation("Imported {Count} shipping records", count);
            return count;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error importing shipping from {Path}", csvPath);
            throw;
        }
    }

    public async Task NormalizeAllDataAsync()
    {
        try
        {
            await using var conn = new SqlConnection(_connectionString);
            await conn.OpenAsync();

            // Normalize commission rates
            _logger.LogInformation("Normalizing commission rates...");
            await using (var cmd = new SqlCommand("EXEC stg.usp_NormalizeCommissionRates", conn))
            {
                cmd.CommandTimeout = 300;
                var result = await cmd.ExecuteScalarAsync();
                _logger.LogInformation("Normalized {Count} commission rates", result);
            }

            // Normalize invoices
            _logger.LogInformation("Normalizing invoices...");
            await using (var cmd = new SqlCommand("EXEC stg.usp_NormalizeInvoices", conn))
            {
                cmd.CommandTimeout = 300;
                var result = await cmd.ExecuteScalarAsync();
                _logger.LogInformation("Normalized {Count} invoices", result);
            }

            // Create AP invoices from shipping
            _logger.LogInformation("Creating AP invoices from shipping data...");
            await using (var cmd = new SqlCommand("EXEC stg.usp_CreateAPFromShipping", conn))
            {
                cmd.CommandTimeout = 300;
                var result = await cmd.ExecuteScalarAsync();
                _logger.LogInformation("Created {Count} AP invoices", result);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error normalizing data");
            throw;
        }
    }

    private async Task<int> BulkImportToStagingAsync(SqlConnection conn, string tableName, string csvPath)
    {
        var config = new CsvConfiguration(CultureInfo.InvariantCulture)
        {
            PrepareHeaderForMatch = args => args.Header?.Trim(),
            DetectDelimiter = true,
            BadDataFound = null,
            MissingFieldFound = null,
            HeaderValidated = null,
            TrimOptions = TrimOptions.Trim
        };

        using var reader = new StreamReader(csvPath);
        using var csv = new CsvReader(reader, config);
        
        // Read all records into a DataTable
        var records = csv.GetRecords<dynamic>();
        var dataTable = new DataTable();
        var recordCount = 0;
        
        foreach (var record in records)
        {
            var dict = record as IDictionary<string, object>;
            if (dict == null) continue;
            
            // Create columns on first record
            if (dataTable.Columns.Count == 0)
            {
                foreach (var key in dict.Keys)
                {
                    dataTable.Columns.Add(key, typeof(string));
                }
            }
            
            // Add row
            var row = dataTable.NewRow();
            foreach (var kvp in dict)
            {
                row[kvp.Key] = kvp.Value?.ToString() ?? (object)DBNull.Value;
            }
            dataTable.Rows.Add(row);
            recordCount++;
        }

        if (recordCount == 0)
        {
            _logger.LogWarning("No records found in CSV: {Path}", csvPath);
            return 0;
        }

        // Bulk copy to SQL Server
        using var bulkCopy = new SqlBulkCopy(conn)
        {
            DestinationTableName = tableName,
            BulkCopyTimeout = 0,
            BatchSize = 1000
        };

        // Map columns
        foreach (DataColumn column in dataTable.Columns)
        {
            bulkCopy.ColumnMappings.Add(column.ColumnName, column.ColumnName);
        }

        await bulkCopy.WriteToServerAsync(dataTable);
        
        return recordCount;
    }
}

// Import service for background processing
public class CsvImportService
{
    private readonly ICsvImporter _importer;
    private readonly ILogger<CsvImportService> _logger;
    private readonly IConfiguration _configuration;

    public CsvImportService(ICsvImporter importer, ILogger<CsvImportService> logger, IConfiguration configuration)
    {
        _importer = importer;
        _logger = logger;
        _configuration = configuration;
    }

    public async Task ImportAllAsync(string? basePath = null)
    {
        try
        {
            basePath ??= _configuration["CsvImport:BasePath"] ?? @"C:\FDX.Trading\Data\Import";
            
            _logger.LogInformation("Starting CSV import from {BasePath}", basePath);

            // Import commission rates
            var commissionPath = Path.Combine(basePath, "Commission Rates 15_8_2025.csv");
            if (!File.Exists(commissionPath))
                commissionPath = Path.Combine(basePath, "CommissionRates.csv");
            await _importer.ImportCommissionRatesAsync(commissionPath);

            // Import invoices
            var invoicesPath = Path.Combine(basePath, "Invoices 15_8_2025.csv");
            if (!File.Exists(invoicesPath))
                invoicesPath = Path.Combine(basePath, "Invoices.csv");
            await _importer.ImportInvoicesAsync(invoicesPath);

            // Import shipping
            var shippingPath = Path.Combine(basePath, "Shipping 15_8_2025.csv");
            if (!File.Exists(shippingPath))
                shippingPath = Path.Combine(basePath, "Shipping.csv");
            await _importer.ImportShippingAsync(shippingPath);

            // Normalize all data
            _logger.LogInformation("Normalizing imported data...");
            await _importer.NormalizeAllDataAsync();

            _logger.LogInformation("CSV import completed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "CSV import failed");
            throw;
        }
    }
}