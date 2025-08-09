using Microsoft.AspNetCore.Mvc;
using FDX.Trading.Models;
using FDX.Trading.Services;
using System.Text;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    [HttpGet]
    public IActionResult GetAllUsers()
    {
        var users = LoginController.GetUsers();
        var userDtos = users.Select(u => new UserDto
        {
            Id = u.Id,
            Username = u.Username,
            Email = u.Email,
            CompanyName = u.CompanyName,
            Type = u.Type,
            TypeName = u.Type switch
            {
                UserType.Admin => "Admin",
                UserType.Expert => "Expert/Contractor",
                UserType.Buyer => "Buyer",
                _ => "Unknown"
            },
            Country = u.Country,
            PhoneNumber = u.PhoneNumber,
            Website = u.Website,
            Address = u.Address,
            Category = !string.IsNullOrEmpty(u.BusinessType) ? u.BusinessType : u.Category,
            CategoryId = u.CategoryId,
            BusinessType = u.BusinessType,
            CategoryDisplayName = u.CategoryId.HasValue ? CategoryData.GetDisplayName(u.CategoryId.Value) : "",
            CategoryColor = u.CategoryId.HasValue ? CategoryData.GetColorCode(u.CategoryId.Value) : "#B2BEC3",
            CreatedAt = u.CreatedAt,
            LastLogin = u.LastLogin,
            IsActive = u.IsActive,
            RequiresPasswordChange = u.RequiresPasswordChange,
            DataComplete = u.DataComplete,
            Verification = u.Verification,
            AlternateEmails = u.AlternateEmails,
            DisplayName = u.DisplayName,
            ImportedAt = u.ImportedAt
        }).ToList();

        return Ok(userDtos);
    }

    [HttpGet("{id}")]
    public IActionResult GetUser(int id)
    {
        var user = LoginController.GetUsers().FirstOrDefault(u => u.Id == id);
        if (user == null)
            return NotFound(new { message = "User not found" });

        var userDto = new UserDto
        {
            Id = user.Id,
            Username = user.Username,
            Email = user.Email,
            CompanyName = user.CompanyName,
            Type = user.Type,
            TypeName = user.Type switch
            {
                UserType.Admin => "Admin",
                UserType.Expert => "Expert/Contractor",
                UserType.Buyer => "Buyer",
                _ => "Unknown"
            },
            Country = user.Country,
            PhoneNumber = user.PhoneNumber,
            Website = user.Website,
            Address = user.Address,
            Category = !string.IsNullOrEmpty(user.BusinessType) ? user.BusinessType : user.Category,
            CategoryId = user.CategoryId,
            BusinessType = user.BusinessType,
            CategoryDisplayName = user.CategoryId.HasValue ? CategoryData.GetDisplayName(user.CategoryId.Value) : "",
            CategoryColor = user.CategoryId.HasValue ? CategoryData.GetColorCode(user.CategoryId.Value) : "#B2BEC3",
            CreatedAt = user.CreatedAt,
            LastLogin = user.LastLogin,
            IsActive = user.IsActive
        };

        return Ok(userDto);
    }

    [HttpPost("import-csv")]
    public async Task<IActionResult> ImportCsv([FromForm] IFormFile file, [FromForm] string userType)
    {
        if (file == null || file.Length == 0)
            return BadRequest(new { message = "No file uploaded" });

        var type = userType.ToLower() switch
        {
            "buyer" => UserType.Buyer,
            "expert" => UserType.Expert,
            "contractor" => UserType.Expert,
            _ => UserType.Buyer
        };

        var importedUsers = new List<User>();
        var errors = new List<string>();
        var users = LoginController.GetUsers();

        using (var reader = new StreamReader(file.OpenReadStream(), Encoding.UTF8))
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
                    
                    if (type == UserType.Expert && values.Length >= 12) // Contractors CSV
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
                        importedUsers.Add(user);
                    }
                    else if (type == UserType.Buyer && values.Length >= 14) // Buyers CSV
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
                        importedUsers.Add(user);
                    }
                }
                catch (Exception ex)
                {
                    errors.Add($"Line {lineNumber}: {ex.Message}");
                }
            }
        }

        return Ok(new
        {
            success = true,
            message = $"Imported {importedUsers.Count} users",
            importedCount = importedUsers.Count,
            errors = errors,
            importedUsers = importedUsers.Select(u => new
            {
                u.Id,
                u.Username,
                u.CompanyName,
                u.Email,
                Type = u.Type.ToString()
            })
        });
    }

    [HttpPut("{id}/toggle-active")]
    public IActionResult ToggleUserActive(int id)
    {
        var user = LoginController.GetUsers().FirstOrDefault(u => u.Id == id);
        if (user == null)
            return NotFound(new { message = "User not found" });

        user.IsActive = !user.IsActive;
        return Ok(new { success = true, isActive = user.IsActive });
    }

    [HttpDelete("{id}")]
    public IActionResult DeleteUser(int id)
    {
        var users = LoginController.GetUsers();
        var user = users.FirstOrDefault(u => u.Id == id);
        if (user == null)
            return NotFound(new { message = "User not found" });

        // Don't delete admin users
        if (user.Type == UserType.Admin)
            return BadRequest(new { message = "Cannot delete admin users" });

        users.Remove(user);
        return Ok(new { success = true, message = "User deleted" });
    }

    [HttpPost("import-default-files")]
    public async Task<IActionResult> ImportDefaultFiles([FromQuery] bool testMode = false)
    {
        var contractorsFile = @"C:\Users\fdxadmin\Downloads\Contractors 9_8_2025.csv";
        var buyersFile = @"C:\Users\fdxadmin\Downloads\Buyers 9_8_2025.csv";
        
        var results = new List<ImportResult>();
        
        // Import contractors
        var contractorsResult = await EnhancedImportService.ImportContractorsFromFile(contractorsFile, testMode, 5);
        results.Add(contractorsResult);
        
        // Import buyers  
        var buyersResult = await EnhancedImportService.ImportBuyersFromFile(buyersFile, testMode, 5);
        results.Add(buyersResult);
        
        // Generate CSV report
        var csvReport = EnhancedImportService.GenerateImportReport(results);
        
        return Ok(new
        {
            success = true,
            testMode = testMode,
            message = testMode 
                ? $"Test import complete: {contractorsResult.SuccessfulImports + buyersResult.SuccessfulImports} users imported (max 10 for test)"
                : $"Full import complete: {contractorsResult.SuccessfulImports + buyersResult.SuccessfulImports} users imported",
            summary = new
            {
                totalProcessed = contractorsResult.TotalProcessed + buyersResult.TotalProcessed,
                totalImported = contractorsResult.SuccessfulImports + buyersResult.SuccessfulImports,
                totalSkipped = contractorsResult.Skipped + buyersResult.Skipped,
                totalErrors = contractorsResult.Errors.Count + buyersResult.Errors.Count
            },
            contractors = new
            {
                processed = contractorsResult.TotalProcessed,
                imported = contractorsResult.SuccessfulImports,
                skipped = contractorsResult.Skipped,
                errors = contractorsResult.Errors,
                skippedReasons = contractorsResult.SkippedReasons
            },
            buyers = new
            {
                processed = buyersResult.TotalProcessed,
                imported = buyersResult.SuccessfulImports,
                skipped = buyersResult.Skipped,
                errors = buyersResult.Errors,
                skippedReasons = buyersResult.SkippedReasons
            },
            importedUsers = results.SelectMany(r => r.ImportedUsers),
            csvReportData = csvReport
        });
    }
    
    [HttpPost("clear-imported-users")]
    public IActionResult ClearImportedUsers()
    {
        var users = LoginController.GetUsers();
        var removedCount = users.RemoveAll(u => u.ImportedAt != null && u.Type != UserType.Admin);
        
        return Ok(new
        {
            success = true,
            message = $"Removed {removedCount} imported users",
            removedCount = removedCount
        });
    }
    
    [HttpGet("export-credentials")]
    public IActionResult ExportCredentials()
    {
        var users = LoginController.GetUsers()
            .Where(u => u.ImportedAt != null)
            .Select(u => new
            {
                u.Username,
                Password = "FDX2025!", // Default password
                u.CompanyName,
                u.Email,
                u.PhoneNumber,
                Type = u.Type.ToString(),
                Status = u.IsActive ? "Active" : "Inactive",
                DataComplete = u.DataComplete ? "Complete" : "Incomplete"
            });
        
        var csv = "Username,Password,CompanyName,Email,Phone,Type,Status,DataComplete\n";
        foreach (var user in users)
        {
            csv += $"\"{user.Username}\",\"{user.Password}\",\"{user.CompanyName}\",\"{user.Email}\",\"{user.PhoneNumber}\",\"{user.Type}\",\"{user.Status}\",\"{user.DataComplete}\"\n";
        }
        
        return File(Encoding.UTF8.GetBytes(csv), "text/csv", $"user_credentials_{DateTime.Now:yyyyMMdd_HHmmss}.csv");
    }

    private string GenerateUsername(string companyName, List<User> existingUsers)
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

    private string[] ParseCsvLine(string line)
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