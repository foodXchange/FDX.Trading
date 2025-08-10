using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using CsvHelper;
using CsvHelper.Configuration;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;

namespace FDX.Trading.Services;

public class PriceBookImportService
{
    private readonly FdxTradingContext _context;
    
    public PriceBookImportService(FdxTradingContext context)
    {
        _context = context;
    }
    
    public async Task<PriceBookImportResult> ImportPriceBookAsync(string filePath)
    {
        var result = new PriceBookImportResult();
        var importedPrices = new List<ImportedPrice>();
        
        try
        {
            using var reader = new StreamReader(filePath);
            using var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true,
                BadDataFound = null,
                MissingFieldFound = null
            });
            
            // Read the CSV records
            var records = csv.GetRecords<PriceBookRecord>().ToList();
            
            foreach (var record in records)
            {
                try
                {
                    // Skip records without product code or price
                    if (string.IsNullOrWhiteSpace(record.Product) || 
                        string.IsNullOrWhiteSpace(record.UnitPrice))
                    {
                        continue;
                    }
                    
                    // Extract product code from the product field
                    // Format: "000021 - Product Name [Supplier][Customer]"
                    var productCode = ExtractProductCode(record.Product);
                    if (string.IsNullOrEmpty(productCode))
                    {
                        result.Errors.Add($"Could not extract product code from: {record.Product}");
                        continue;
                    }
                    
                    // Parse the price
                    if (!TryParsePrice(record.UnitPrice, out decimal price))
                    {
                        continue; // Skip if no valid price
                    }
                    
                    // Parse the date
                    DateTime effectiveDate = DateTime.Now;
                    if (!string.IsNullOrWhiteSpace(record.Date))
                    {
                        if (DateTime.TryParse(record.Date, out DateTime parsedDate))
                        {
                            effectiveDate = parsedDate;
                        }
                    }
                    
                    // Determine currency
                    string currency = record.Currency ?? "USD";
                    if (currency.Equals("Euro", StringComparison.OrdinalIgnoreCase))
                    {
                        currency = "EUR";
                    }
                    
                    importedPrices.Add(new ImportedPrice
                    {
                        ProductCode = productCode,
                        Price = price,
                        Currency = currency,
                        EffectiveDate = effectiveDate,
                        Incoterms = record.Incoterms,
                        AutoNumber = record.AutoNumber,
                        CreatedBy = ExtractUser(record.FirstCreated),
                        UpdatedBy = ExtractUser(record.LastUpdated)
                    });
                }
                catch (Exception ex)
                {
                    result.Errors.Add($"Error processing record: {record.Product} - {ex.Message}");
                }
            }
            
            // Now update the database with the imported prices
            foreach (var importedPrice in importedPrices)
            {
                try
                {
                    // Find the product by code
                    var product = await _context.Products
                        .FirstOrDefaultAsync(p => p.ProductCode == importedPrice.ProductCode);
                    
                    if (product == null)
                    {
                        result.Warnings.Add($"Product not found: {importedPrice.ProductCode}");
                        continue;
                    }
                    
                    // Check if we already have this price in history
                    var existingPrice = await _context.ProductPriceHistory
                        .FirstOrDefaultAsync(ph => 
                            ph.ProductId == product.Id && 
                            ph.UnitPrice == importedPrice.Price &&
                            ph.EffectiveDate.Date == importedPrice.EffectiveDate.Date);
                    
                    if (existingPrice != null)
                    {
                        result.SkippedCount++;
                        continue; // Skip duplicate
                    }
                    
                    // Deactivate current prices for this product
                    var currentPrices = await _context.ProductPriceHistory
                        .Where(ph => ph.ProductId == product.Id && ph.IsActive)
                        .ToListAsync();
                    
                    foreach (var currentPrice in currentPrices)
                    {
                        currentPrice.IsActive = false;
                    }
                    
                    // Add new price history record
                    var priceHistory = new ProductPriceHistory
                    {
                        ProductId = product.Id,
                        SupplierId = product.SupplierId,
                        UnitPrice = importedPrice.Price,
                        Currency = importedPrice.Currency,
                        EffectiveDate = importedPrice.EffectiveDate,
                        CreatedBy = importedPrice.UpdatedBy ?? "Price Book Import",
                        CreatedAt = DateTime.Now,
                        ChangeReason = $"Imported from Price Book - {importedPrice.Incoterms} - {importedPrice.AutoNumber}",
                        IsActive = true
                    };
                    
                    _context.ProductPriceHistory.Add(priceHistory);
                    
                    // Update the product's current price
                    product.UnitWholesalePrice = importedPrice.Price;
                    product.Currency = importedPrice.Currency;
                    product.Incoterms = importedPrice.Incoterms;
                    product.UpdatedAt = DateTime.Now;
                    
                    result.ImportedCount++;
                }
                catch (Exception ex)
                {
                    result.Errors.Add($"Error updating product {importedPrice.ProductCode}: {ex.Message}");
                }
            }
            
            // Save all changes
            await _context.SaveChangesAsync();
            
            result.Success = true;
            result.Message = $"Successfully imported {result.ImportedCount} prices from Price Book";
        }
        catch (Exception ex)
        {
            result.Success = false;
            result.Message = $"Failed to import Price Book: {ex.Message}";
            result.Errors.Add(ex.ToString());
        }
        
        return result;
    }
    
    private string ExtractProductCode(string productField)
    {
        if (string.IsNullOrWhiteSpace(productField))
            return null;
        
        // Try to extract product code (e.g., "000021" from "000021 - Product Name")
        var match = Regex.Match(productField, @"^(\d{6})\s*-");
        if (match.Success)
        {
            return match.Groups[1].Value;
        }
        
        // Try alternative format
        match = Regex.Match(productField, @"^(\w+)\s*-");
        if (match.Success)
        {
            return match.Groups[1].Value;
        }
        
        return null;
    }
    
    private bool TryParsePrice(string priceStr, out decimal price)
    {
        price = 0;
        
        if (string.IsNullOrWhiteSpace(priceStr))
            return false;
        
        // Clean the price string
        priceStr = priceStr.Replace("$", "").Replace("€", "").Replace(",", "").Trim();
        
        return decimal.TryParse(priceStr, NumberStyles.Any, CultureInfo.InvariantCulture, out price) && price > 0;
    }
    
    private string ExtractUser(string userField)
    {
        if (string.IsNullOrWhiteSpace(userField))
            return "System";
        
        // Extract user name from "By UserName on Date"
        var match = Regex.Match(userField, @"By\s+(.+?)\s+on");
        if (match.Success)
        {
            return match.Groups[1].Value;
        }
        
        return userField;
    }
}

// CSV Mapping Classes
public class PriceBookRecord
{
    public string Title { get; set; }
    
    [CsvHelper.Configuration.Attributes.Name("Open Comments")]
    public string OpenComments { get; set; }
    
    public string Product { get; set; }
    public string Date { get; set; }
    public string Incoterms { get; set; }
    public string Currency { get; set; }
    
    [CsvHelper.Configuration.Attributes.Name("Auto Number")]
    public string AutoNumber { get; set; }
    
    public string Description { get; set; }
    
    [CsvHelper.Configuration.Attributes.Name("First Created")]
    public string FirstCreated { get; set; }
    
    [CsvHelper.Configuration.Attributes.Name("Last Updated")]
    public string LastUpdated { get; set; }
    
    [CsvHelper.Configuration.Attributes.Name("Unit price (Purchase/Base price) $/€")]
    public string UnitPrice { get; set; }
}

public class ImportedPrice
{
    public string ProductCode { get; set; }
    public decimal Price { get; set; }
    public string Currency { get; set; }
    public DateTime EffectiveDate { get; set; }
    public string Incoterms { get; set; }
    public string AutoNumber { get; set; }
    public string CreatedBy { get; set; }
    public string UpdatedBy { get; set; }
}

public class PriceBookImportResult
{
    public bool Success { get; set; }
    public string Message { get; set; }
    public int ImportedCount { get; set; }
    public int SkippedCount { get; set; }
    public List<string> Errors { get; set; } = new List<string>();
    public List<string> Warnings { get; set; } = new List<string>();
}