using System.Text;
using FDX.Trading.Models;
using FDX.Trading.Controllers;
using FDX.Trading.Services;

namespace FDX.Trading.Services;

public class ImportResult
{
    public int TotalProcessed { get; set; }
    public int SuccessfulImports { get; set; }
    public int Skipped { get; set; }
    public List<string> Errors { get; set; } = new();
    public List<string> SkippedReasons { get; set; } = new();
    public List<ImportedUserInfo> ImportedUsers { get; set; } = new();
}

public class ImportedUserInfo
{
    public string Username { get; set; } = "";
    public string Password { get; set; } = "";
    public string CompanyName { get; set; } = "";
    public string Email { get; set; } = "";
    public string Status { get; set; } = "";
    public string Notes { get; set; } = "";
}

public class EnhancedImportService
{
    private const string DEFAULT_PASSWORD = "FDX2025!";
    
    public static async Task<ImportResult> ImportContractorsFromFile(string filePath, bool testMode = false, int testLimit = 5)
    {
        var result = new ImportResult();
        var users = LoginController.GetUsers();

        if (!File.Exists(filePath))
        {
            result.Errors.Add($"File not found: {filePath}");
            return result;
        }

        using (var reader = new StreamReader(filePath, Encoding.UTF8))
        {
            // Parse entire file to handle multi-line records
            var allRecords = ParseCsvFile(reader);
            
            // Skip header row
            var dataRecords = allRecords.Skip(1).ToList();
            
            foreach (var values in dataRecords)
            {
                if (testMode && result.SuccessfulImports >= testLimit)
                    break;
                    
                result.TotalProcessed++;
                
                try
                {
                    
                    if (values.Length >= 12) // Contractors CSV structure
                    {
                        var companyName = CleanValue(values[2]); // Company name
                        var email = CleanValue(values[5]); // Company email
                        var country = CleanValue(values[6]); // Country
                        var phoneNumber = CleanValue(values[9]); // Phone
                        var address = CleanValue(values[11]); // Address
                        var category = CleanValue(values[3]); // Category
                        var website = CleanValue(values[4]); // Website

                        if (string.IsNullOrWhiteSpace(companyName))
                        {
                            result.SkippedReasons.Add($"Record {result.TotalProcessed}: No company name");
                            result.Skipped++;
                            continue;
                        }

                        // Check for duplicates
                        if (users.Any(u => u.CompanyName.Equals(companyName, StringComparison.OrdinalIgnoreCase)))
                        {
                            result.SkippedReasons.Add($"Record {result.TotalProcessed}: Duplicate company '{companyName}'");
                            result.Skipped++;
                            continue;
                        }

                        // Handle multiple emails
                        string? alternateEmails = null;
                        if (!string.IsNullOrEmpty(email) && email.Contains(","))
                        {
                            var emails = email.Split(',').Select(e => e.Trim()).ToArray();
                            email = emails[0];
                            alternateEmails = string.Join(";", emails.Skip(1));
                        }

                        // Generate username with underscore format
                        var username = GenerateEnhancedUsername(companyName, users);

                        // Check data completeness
                        bool dataComplete = !string.IsNullOrEmpty(email) && !string.IsNullOrEmpty(phoneNumber);
                        var verificationStatus = dataComplete ? VerificationStatus.Pending : VerificationStatus.Incomplete;
                        
                        // Generate placeholder email if missing
                        if (string.IsNullOrEmpty(email))
                        {
                            email = $"{username}@pending.fdx";
                        }

                        // Determine if should be active (complete data only)
                        bool isActive = dataComplete;

                        var user = new User
                        {
                            Id = LoginController.GetNextId(),
                            Username = username,
                            Password = DEFAULT_PASSWORD,
                            Email = email,
                            CompanyName = companyName,
                            Type = UserType.Expert,
                            Country = country ?? "",
                            PhoneNumber = phoneNumber ?? "",
                            Website = website ?? "",
                            Address = address ?? "",
                            CreatedAt = DateTime.Now,
                            IsActive = isActive,
                            RequiresPasswordChange = true,
                            DataComplete = dataComplete,
                            Verification = verificationStatus,
                            AlternateEmails = alternateEmails,
                            ImportedAt = DateTime.Now,
                            ImportNotes = dataComplete ? "Imported successfully" : "Missing: " + 
                                (string.IsNullOrEmpty(values[5]) ? "email " : "") + 
                                (string.IsNullOrEmpty(phoneNumber) ? "phone" : "")
                        };
                        
                        // Process category using CategoryService
                        CategoryService.ProcessUserCategory(user, category, null);

                        // Check for Hebrew and set display name
                        if (ContainsHebrew(companyName))
                        {
                            user.DisplayName = username; // Use generated username as display
                        }

                        users.Add(user);
                        result.SuccessfulImports++;
                        
                        result.ImportedUsers.Add(new ImportedUserInfo
                        {
                            Username = username,
                            Password = DEFAULT_PASSWORD,
                            CompanyName = companyName,
                            Email = email,
                            Status = isActive ? "Active" : "Inactive (Incomplete)",
                            Notes = user.ImportNotes ?? ""
                        });
                    }
                }
                catch (Exception ex)
                {
                    result.Errors.Add($"Record {result.TotalProcessed}: {ex.Message}");
                }
            }
        }

        return result;
    }

    public static async Task<ImportResult> ImportBuyersFromFile(string filePath, bool testMode = false, int testLimit = 5)
    {
        var result = new ImportResult();
        var users = LoginController.GetUsers();

        if (!File.Exists(filePath))
        {
            result.Errors.Add($"File not found: {filePath}");
            return result;
        }

        using (var reader = new StreamReader(filePath, Encoding.UTF8))
        {
            // Parse entire file to handle multi-line records
            var allRecords = ParseCsvFile(reader);
            
            // Skip header row
            var dataRecords = allRecords.Skip(1).ToList();
            
            foreach (var values in dataRecords)
            {
                if (testMode && result.SuccessfulImports >= testLimit)
                    break;
                    
                result.TotalProcessed++;
                
                try
                {
                    if (values.Length >= 14) // Buyers CSV structure
                    {
                        var buyerId = CleanValue(values[2]); // ID
                        var companyName = CleanValue(values[4]); // Company name
                        var email = CleanValue(values[8]); // Email
                        var phoneNumber = CleanValue(values[9]); // Phone
                        var address = CleanValue(values[11]); // Address
                        var country = CleanValue(values[13]); // Country
                        var website = CleanValue(values[7]); // Website
                        var description = CleanValue(values[6]); // Description

                        if (string.IsNullOrWhiteSpace(companyName))
                        {
                            result.SkippedReasons.Add($"Record {result.TotalProcessed}: No company name");
                            result.Skipped++;
                            continue;
                        }

                        // Check for duplicates
                        if (users.Any(u => u.CompanyName.Equals(companyName, StringComparison.OrdinalIgnoreCase)))
                        {
                            result.SkippedReasons.Add($"Record {result.TotalProcessed}: Duplicate company '{companyName}'");
                            result.Skipped++;
                            continue;
                        }

                        // Handle multiple emails
                        string? alternateEmails = null;
                        if (!string.IsNullOrEmpty(email) && email.Contains(","))
                        {
                            var emails = email.Split(',').Select(e => e.Trim()).ToArray();
                            email = emails[0];
                            alternateEmails = string.Join(";", emails.Skip(1));
                        }

                        // Handle multiple phone numbers
                        if (!string.IsNullOrEmpty(phoneNumber) && phoneNumber.Contains(","))
                        {
                            phoneNumber = phoneNumber.Replace(",", ";");
                        }

                        // Generate username
                        var username = GenerateEnhancedUsername(companyName, users);

                        // Check data completeness
                        bool dataComplete = !string.IsNullOrEmpty(email) && !string.IsNullOrEmpty(phoneNumber);
                        var verificationStatus = dataComplete ? VerificationStatus.Pending : VerificationStatus.Incomplete;
                        
                        // Generate placeholder email if missing
                        if (string.IsNullOrEmpty(email))
                        {
                            email = $"{username}@pending.fdx";
                        }

                        // Buyers with complete data are active
                        bool isActive = dataComplete;

                        var user = new User
                        {
                            Id = LoginController.GetNextId(),
                            Username = username,
                            Password = DEFAULT_PASSWORD,
                            Email = email,
                            CompanyName = companyName,
                            Type = UserType.Buyer,
                            Country = country ?? "",
                            PhoneNumber = phoneNumber ?? "",
                            Website = website ?? "",
                            Address = address ?? "",
                            CreatedAt = DateTime.Now,
                            IsActive = isActive,
                            RequiresPasswordChange = true,
                            DataComplete = dataComplete,
                            Verification = verificationStatus,
                            AlternateEmails = alternateEmails,
                            ImportedAt = DateTime.Now,
                            OriginalId = buyerId,
                            ImportNotes = dataComplete ? "Imported successfully" : "Missing: " + 
                                (string.IsNullOrEmpty(values[8]) ? "email " : "") + 
                                (string.IsNullOrEmpty(values[9]) ? "phone" : "")
                        };
                        
                        // Process category using CategoryService - description field contains the business info
                        CategoryService.ProcessUserCategory(user, null, description);

                        // Check for Hebrew and set display name
                        if (ContainsHebrew(companyName))
                        {
                            user.DisplayName = username; // Use generated username as display
                        }

                        users.Add(user);
                        result.SuccessfulImports++;
                        
                        result.ImportedUsers.Add(new ImportedUserInfo
                        {
                            Username = username,
                            Password = DEFAULT_PASSWORD,
                            CompanyName = companyName,
                            Email = email,
                            Status = isActive ? "Active" : "Inactive (Incomplete)",
                            Notes = user.ImportNotes ?? ""
                        });
                    }
                }
                catch (Exception ex)
                {
                    result.Errors.Add($"Record {result.TotalProcessed}: {ex.Message}");
                }
            }
        }

        return result;
    }

    private static string GenerateEnhancedUsername(string companyName, List<User> existingUsers)
    {
        // Clean company name for username with underscore format
        var baseUsername = companyName.ToLower()
            .Replace(" ", "_")
            .Replace(",", "")
            .Replace(".", "")
            .Replace("/", "_")
            .Replace("\\", "_")
            .Replace("-", "_")
            .Replace("(", "")
            .Replace(")", "");

        // Remove multiple underscores
        while (baseUsername.Contains("__"))
        {
            baseUsername = baseUsername.Replace("__", "_");
        }

        // Trim underscores from ends
        baseUsername = baseUsername.Trim('_');

        if (baseUsername.Length > 20)
            baseUsername = baseUsername.Substring(0, 20);

        var username = baseUsername;
        var counter = 1;

        // Ensure unique username
        while (existingUsers.Any(u => u.Username.Equals(username, StringComparison.OrdinalIgnoreCase)))
        {
            username = $"{baseUsername}{counter}";
            counter++;
        }

        return username;
    }

    private static string CleanValue(string value)
    {
        if (string.IsNullOrEmpty(value))
            return "";
        
        return value.Trim().Replace("\"", "");
    }

    private static bool ContainsHebrew(string text)
    {
        if (string.IsNullOrEmpty(text))
            return false;
            
        return text.Any(c => c >= 0x0590 && c <= 0x05FF);
    }

    private static List<string[]> ParseCsvFile(StreamReader reader)
    {
        var records = new List<string[]>();
        var currentRecord = new List<string>();
        var currentValue = new StringBuilder();
        var inQuotes = false;
        string? line;

        while ((line = reader.ReadLine()) != null)
        {
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
                    currentRecord.Add(currentValue.ToString());
                    currentValue.Clear();
                }
                else
                {
                    currentValue.Append(ch);
                }
            }

            // If we're not in quotes, this line is complete
            if (!inQuotes)
            {
                // Add the last value
                currentRecord.Add(currentValue.ToString());
                currentValue.Clear();
                
                // Add the complete record if it has content
                if (currentRecord.Count > 0 && !string.IsNullOrWhiteSpace(string.Join("", currentRecord)))
                {
                    records.Add(currentRecord.ToArray());
                }
                currentRecord.Clear();
            }
            else
            {
                // We're still in quotes, add a newline and continue with next line
                currentValue.AppendLine();
            }
        }

        // Handle any remaining data
        if (currentRecord.Count > 0 || currentValue.Length > 0)
        {
            if (currentValue.Length > 0)
            {
                currentRecord.Add(currentValue.ToString());
            }
            if (currentRecord.Count > 0)
            {
                records.Add(currentRecord.ToArray());
            }
        }

        return records;
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

    public static string GenerateImportReport(List<ImportResult> results)
    {
        var sb = new StringBuilder();
        sb.AppendLine("Username,Password,CompanyName,Email,Status,Notes");
        
        foreach (var result in results)
        {
            foreach (var user in result.ImportedUsers)
            {
                sb.AppendLine($"\"{user.Username}\",\"{user.Password}\",\"{user.CompanyName}\",\"{user.Email}\",\"{user.Status}\",\"{user.Notes}\"");
            }
        }
        
        return sb.ToString();
    }
}