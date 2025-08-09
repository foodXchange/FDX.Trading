using System.Text;
using FDX.Trading.Models;
using FDX.Trading.Controllers;

namespace FDX.Trading.Services;

public class CsvImportService
{
    public static async Task<(int imported, List<string> errors)> ImportContractorsFromFile(string filePath)
    {
        var importedCount = 0;
        var errors = new List<string>();
        var users = LoginController.GetUsers();

        if (!File.Exists(filePath))
        {
            errors.Add($"File not found: {filePath}");
            return (0, errors);
        }

        using (var reader = new StreamReader(filePath, Encoding.UTF8))
        {
            var lineNumber = 0;
            string? line;
            
            // Skip header
            await reader.ReadLineAsync();
            lineNumber++;

            while ((line = await reader.ReadLineAsync()) != null)
            {
                lineNumber++;
                try
                {
                    var values = ParseCsvLine(line);
                    
                    if (values.Length >= 12) // Contractors CSV
                    {
                        var companyName = values[2]; // Company name column
                        var email = values[5]; // Company email address
                        var country = values[6]; // Country
                        var phoneNumber = values[9]; // Company phone number(s)
                        var address = values[11]; // Contractor's Address
                        var category = values[3]; // Category
                        var website = values[4]; // Contractor's Website

                        if (string.IsNullOrWhiteSpace(companyName))
                            continue;

                        // Skip if already exists
                        if (users.Any(u => u.CompanyName == companyName))
                            continue;

                        // Generate username from company name
                        var username = GenerateUsername(companyName, users);

                        var user = new User
                        {
                            Id = LoginController.GetNextId(),
                            Username = username,
                            Password = "FDX2025!", // Default password
                            Email = email ?? $"{username}@fdx.trading",
                            CompanyName = companyName,
                            Type = UserType.Expert,
                            Country = country ?? "",
                            PhoneNumber = phoneNumber ?? "",
                            Website = website ?? "",
                            Address = address ?? "",
                            Category = category ?? "",
                            CreatedAt = DateTime.Now,
                            IsActive = true
                        };

                        users.Add(user);
                        importedCount++;
                    }
                }
                catch (Exception ex)
                {
                    errors.Add($"Line {lineNumber}: {ex.Message}");
                }
            }
        }

        return (importedCount, errors);
    }

    public static async Task<(int imported, List<string> errors)> ImportBuyersFromFile(string filePath)
    {
        var importedCount = 0;
        var errors = new List<string>();
        var users = LoginController.GetUsers();

        if (!File.Exists(filePath))
        {
            errors.Add($"File not found: {filePath}");
            return (0, errors);
        }

        using (var reader = new StreamReader(filePath, Encoding.UTF8))
        {
            var lineNumber = 0;
            string? line;
            
            // Skip header
            await reader.ReadLineAsync();
            lineNumber++;

            while ((line = await reader.ReadLineAsync()) != null)
            {
                lineNumber++;
                try
                {
                    var values = ParseCsvLine(line);
                    
                    if (values.Length >= 14) // Buyers CSV
                    {
                        var companyName = values[4]; // Company name
                        var email = values[8]; // Email address
                        var phoneNumber = values[9]; // Phone Number
                        var address = values[11]; // Buyer's company address
                        var country = values[13]; // Company Country
                        var website = values[7]; // Company website
                        var description = values[6]; // Buyer's Description & Bus. Sector

                        if (string.IsNullOrWhiteSpace(companyName))
                            continue;

                        // Skip if already exists
                        if (users.Any(u => u.CompanyName == companyName))
                            continue;

                        // Generate username from company name
                        var username = GenerateUsername(companyName, users);

                        var user = new User
                        {
                            Id = LoginController.GetNextId(),
                            Username = username,
                            Password = "FDX2025!", // Default password
                            Email = email ?? $"{username}@fdx.trading",
                            CompanyName = companyName,
                            Type = UserType.Buyer,
                            Country = country ?? "",
                            PhoneNumber = phoneNumber ?? "",
                            Website = website ?? "",
                            Address = address ?? "",
                            Category = description ?? "",
                            CreatedAt = DateTime.Now,
                            IsActive = true
                        };

                        users.Add(user);
                        importedCount++;
                    }
                }
                catch (Exception ex)
                {
                    errors.Add($"Line {lineNumber}: {ex.Message}");
                }
            }
        }

        return (importedCount, errors);
    }

    private static string GenerateUsername(string companyName, List<User> existingUsers)
    {
        // Clean company name for username
        var baseUsername = companyName.ToLower()
            .Replace(" ", "")
            .Replace(",", "")
            .Replace(".", "")
            .Replace("/", "")
            .Replace("\\", "");

        if (baseUsername.Length > 20)
            baseUsername = baseUsername.Substring(0, 20);

        var username = baseUsername;
        var counter = 1;

        // Ensure unique username
        while (existingUsers.Any(u => u.Username == username))
        {
            username = $"{baseUsername}{counter}";
            counter++;
        }

        return username;
    }

    private static string[] ParseCsvLine(string line)
    {
        var values = new List<string>();
        var currentValue = new StringBuilder();
        var inQuotes = false;

        for (int i = 0; i < line.Length; i++)
        {
            var ch = line[i];

            if (ch == '"')
            {
                if (inQuotes && i + 1 < line.Length && line[i + 1] == '"')
                {
                    currentValue.Append('"');
                    i++; // Skip next quote
                }
                else
                {
                    inQuotes = !inQuotes;
                }
            }
            else if (ch == ',' && !inQuotes)
            {
                values.Add(currentValue.ToString());
                currentValue.Clear();
            }
            else
            {
                currentValue.Append(ch);
            }
        }

        values.Add(currentValue.ToString());
        return values.ToArray();
    }
}