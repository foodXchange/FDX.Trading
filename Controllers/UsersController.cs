using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Models;
using FDX.Trading.Services;
using FDX.Trading.Data;
using System.Text;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly FdxTradingContext _context;
    
    public UsersController(FdxTradingContext context)
    {
        _context = context;
    }

    [HttpGet]
    public async Task<IActionResult> GetAllUsers([FromQuery] UserType? type = null)
    {
        var query = _context.FdxUsers.AsQueryable();
        
        if (type.HasValue)
        {
            query = query.Where(u => u.Type == type.Value);
        }
        
        var users = await query.ToListAsync();
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

    [HttpGet("suppliers/search")]
    public async Task<IActionResult> SearchSuppliers(
        [FromQuery] string? q = null,
        [FromQuery] string? country = null,
        [FromQuery] bool? hasProducts = null)
    {
        // Start with suppliers only
        var query = _context.FdxUsers
            .Where(u => u.Type == UserType.Supplier);
        
        // Search by company name
        if (!string.IsNullOrWhiteSpace(q))
        {
            query = query.Where(u => u.CompanyName.ToLower().Contains(q.ToLower()));
        }
        
        // Filter by country
        if (!string.IsNullOrWhiteSpace(country))
        {
            query = query.Where(u => u.Country == country);
        }
        
        // Filter by having products
        if (hasProducts.HasValue)
        {
            if (hasProducts.Value)
            {
                query = query.Where(u => _context.Products.Any(p => p.SupplierId == u.Id));
            }
            else
            {
                query = query.Where(u => !_context.Products.Any(p => p.SupplierId == u.Id));
            }
        }
        
        // Get results with product count
        var suppliers = await query
            .Select(u => new
            {
                id = u.Id,
                companyName = u.CompanyName,
                country = u.Country,
                email = u.Email,
                website = u.Website,
                phoneNumber = u.PhoneNumber,
                isActive = u.IsActive,
                productCount = _context.Products.Count(p => p.SupplierId == u.Id),
                verification = u.Verification,
                category = u.Category,
                businessType = u.BusinessType
            })
            .OrderByDescending(s => s.productCount)
            .ThenBy(s => s.companyName)
            .ToListAsync();
        
        return Ok(suppliers);
    }
    
    [HttpGet("suppliers/countries")]
    public async Task<IActionResult> GetSupplierCountries()
    {
        var countries = await _context.FdxUsers
            .Where(u => u.Type == UserType.Supplier)
            .Where(u => !string.IsNullOrEmpty(u.Country))
            .Select(u => u.Country)
            .Distinct()
            .OrderBy(c => c)
            .ToListAsync();
        
        return Ok(countries);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetUser(int id)
    {
        var user = await _context.FdxUsers.FindAsync(id);
        if (user == null)
            return NotFound(new { message = "User not found" });

        var userDto = new UserDto
        {
            Id = user.Id,
            Username = user.Username,
            Email = user.Email,
            FirstName = user.FirstName,
            LastName = user.LastName,
            CompanyName = user.CompanyName,
            Type = user.Type,
            TypeName = user.Type switch
            {
                UserType.Admin => "Admin",
                UserType.Expert => "Expert/Contractor",
                UserType.Buyer => "Buyer",
                UserType.Supplier => "Supplier",
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
            IsActive = user.IsActive,
            ProfileImage = user.ProfileImage
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
                        var username = await GenerateUsername(companyName);

                        var user = new User
                        {
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
                            BusinessType = "",
                            FullDescription = "",
                            SubCategories = "",
                            CreatedAt = DateTime.Now,
                            IsActive = true,
                            DataComplete = false,
                            RequiresPasswordChange = true,
                            Verification = VerificationStatus.Pending
                        };

                        _context.FdxUsers.Add(user);
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
                        var username = await GenerateUsername(companyName);

                        var user = new User
                        {
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
                            BusinessType = "",
                            FullDescription = "",
                            SubCategories = "",
                            CreatedAt = DateTime.Now,
                            IsActive = true,
                            DataComplete = false,
                            RequiresPasswordChange = true,
                            Verification = VerificationStatus.Pending
                        };

                        _context.FdxUsers.Add(user);
                        importedUsers.Add(user);
                    }
                }
                catch (Exception ex)
                {
                    errors.Add($"Line {lineNumber}: {ex.Message}");
                }
            }
        }

        await _context.SaveChangesAsync();

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

    [HttpPut("{id}/supplier-details")]
    public async Task<IActionResult> UpdateSupplierDetails(int id, [FromBody] SupplierUpdateDto updateDto)
    {
        var user = await _context.FdxUsers.FindAsync(id);
        if (user == null || user.Type != UserType.Supplier)
            return NotFound(new { message = "Supplier not found" });
        
        // Update supplier details
        if (!string.IsNullOrWhiteSpace(updateDto.CompanyName))
            user.CompanyName = updateDto.CompanyName;
        if (!string.IsNullOrWhiteSpace(updateDto.Email))
            user.Email = updateDto.Email;
        if (updateDto.PhoneNumber != null)
            user.PhoneNumber = updateDto.PhoneNumber;
        if (updateDto.Website != null)
            user.Website = updateDto.Website;
        if (updateDto.Address != null)
            user.Address = updateDto.Address;
        if (updateDto.Country != null)
            user.Country = updateDto.Country;
        if (updateDto.BusinessType != null)
            user.BusinessType = updateDto.BusinessType;
        if (updateDto.Category != null)
            user.Category = updateDto.Category;
        if (updateDto.ProfileImage != null)
            user.ProfileImage = updateDto.ProfileImage;
            
        await _context.SaveChangesAsync();
        
        return Ok(new
        {
            success = true,
            message = "Supplier details updated successfully",
            supplier = new
            {
                id = user.Id,
                companyName = user.CompanyName,
                email = user.Email,
                phoneNumber = user.PhoneNumber,
                website = user.Website,
                address = user.Address,
                country = user.Country,
                businessType = user.BusinessType,
                category = user.Category,
                profileImage = user.ProfileImage
            }
        });
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateUser(int id, [FromBody] UserUpdateDto updateDto)
    {
        var user = await _context.FdxUsers.FindAsync(id);
        if (user == null)
            return NotFound(new { message = "User not found" });

        // Update user properties
        user.Email = updateDto.Email ?? user.Email;
        user.FirstName = updateDto.FirstName ?? user.FirstName;
        user.LastName = updateDto.LastName ?? user.LastName;
        user.DisplayName = updateDto.DisplayName ?? user.DisplayName;
        user.CompanyName = updateDto.CompanyName ?? user.CompanyName;
        user.Type = (UserType)updateDto.Type;
        user.IsActive = updateDto.IsActive;
        user.PhoneNumber = updateDto.PhoneNumber ?? user.PhoneNumber;
        user.Country = updateDto.Country ?? user.Country;
        user.Address = updateDto.Address ?? user.Address;
        user.Website = updateDto.Website ?? user.Website;
        user.ProfileImage = updateDto.ProfileImage ?? user.ProfileImage;
        user.AlternateEmails = updateDto.AlternateEmails ?? user.AlternateEmails;
        user.Category = updateDto.Category ?? user.Category;
        user.BusinessType = updateDto.BusinessType ?? user.BusinessType;
        user.SubCategories = updateDto.SubCategories ?? user.SubCategories;
        user.FullDescription = updateDto.FullDescription ?? user.FullDescription;
        user.RequiresPasswordChange = updateDto.RequiresPasswordChange;
        user.DataComplete = updateDto.DataComplete;
        user.Verification = (VerificationStatus)updateDto.Verification;
        user.ImportNotes = updateDto.ImportNotes ?? user.ImportNotes;

        await _context.SaveChangesAsync();
        
        // Return the updated user data
        return Ok(new
        {
            id = user.Id,
            username = user.Username,
            email = user.Email,
            firstName = user.FirstName,
            lastName = user.LastName,
            displayName = user.DisplayName,
            companyName = user.CompanyName,
            typeName = user.Type switch
            {
                UserType.Admin => "Admin",
                UserType.Expert => "Expert/Contractor",
                UserType.Buyer => "Buyer",
                UserType.Supplier => "Supplier",
                _ => "Unknown"
            },
            type = (int)user.Type,
            country = user.Country,
            phoneNumber = user.PhoneNumber,
            website = user.Website,
            address = user.Address,
            profileImage = user.ProfileImage,
            isActive = user.IsActive,
            createdAt = user.CreatedAt,
            success = true,
            message = "User updated successfully"
        });
    }

    [HttpPost("{id}/reset-password")]
    public async Task<IActionResult> ResetPassword(int id, [FromBody] ResetPasswordDto dto)
    {
        var user = await _context.FdxUsers.FindAsync(id);
        if (user == null)
            return NotFound(new { message = "User not found" });

        if (string.IsNullOrWhiteSpace(dto.NewPassword))
            return BadRequest(new { message = "Password cannot be empty" });

        user.Password = dto.NewPassword;
        user.RequiresPasswordChange = true;
        await _context.SaveChangesAsync();
        
        return Ok(new { success = true, message = "Password reset successfully" });
    }

    [HttpPut("{id}/toggle-active")]
    public async Task<IActionResult> ToggleUserActive(int id)
    {
        var user = await _context.FdxUsers.FindAsync(id);
        if (user == null)
            return NotFound(new { message = "User not found" });

        user.IsActive = !user.IsActive;
        await _context.SaveChangesAsync();
        
        return Ok(new { success = true, isActive = user.IsActive });
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteUser(int id)
    {
        var user = await _context.FdxUsers.FindAsync(id);
        if (user == null)
            return NotFound(new { message = "User not found" });

        // Don't delete admin users
        if (user.Type == UserType.Admin)
            return BadRequest(new { message = "Cannot delete admin users" });

        _context.FdxUsers.Remove(user);
        await _context.SaveChangesAsync();
        
        return Ok(new { success = true, message = "User deleted" });
    }

    [HttpPost("import-default-files")]
    public async Task<IActionResult> ImportDefaultFiles([FromQuery] bool testMode = false)
    {
        var contractorsFile = @"C:\Users\fdxadmin\Downloads\Contractors 9_8_2025.csv";
        var buyersFile = @"C:\Users\fdxadmin\Downloads\Buyers 9_8_2025.csv";
        
        var results = new List<ImportResult>();
        
        // Import contractors
        var contractorsResult = await ImportFromFile(contractorsFile, UserType.Expert, testMode, 5);
        results.Add(contractorsResult);
        
        // Import buyers  
        var buyersResult = await ImportFromFile(buyersFile, UserType.Buyer, testMode, 5);
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
    
    private async Task<ImportResult> ImportFromFile(string filePath, UserType userType, bool testMode, int testLimit)
    {
        var result = new ImportResult 
        { 
            FileName = Path.GetFileName(filePath),
            UserType = userType.ToString()
        };

        if (!System.IO.File.Exists(filePath))
        {
            result.Errors.Add($"File not found: {filePath}");
            return result;
        }

        // Use EnhancedImportService for the actual import logic
        if (userType == UserType.Expert)
        {
            var importResult = await EnhancedImportService.ImportContractorsFromFile(filePath, testMode, testLimit);
            
            // Add imported users to database one by one
            foreach (var user in importResult.ImportedUsers)
            {
                try
                {
                    // Check if user already exists
                    if (!await _context.FdxUsers.AnyAsync(u => u.Username == user.Username))
                    {
                        _context.FdxUsers.Add(user);
                        await _context.SaveChangesAsync(); // Save each user individually
                    }
                }
                catch (Exception ex)
                {
                    // Log error but continue with other users
                    var innerMessage = ex.InnerException?.Message ?? ex.Message;
                    importResult.Errors.Add($"Failed to save user {user.Username}: {innerMessage}");
                    
                    // Check if it's a duplicate username error
                    if (innerMessage.Contains("duplicate") || innerMessage.Contains("unique"))
                    {
                        importResult.SkippedReasons.Add($"User {user.Username} already exists");
                        importResult.Skipped++;
                    }
                }
            }
            
            return importResult;
        }
        else
        {
            var importResult = await EnhancedImportService.ImportBuyersFromFile(filePath, testMode, testLimit);
            
            // Add imported users to database one by one
            foreach (var user in importResult.ImportedUsers)
            {
                try
                {
                    // Check if user already exists
                    if (!await _context.FdxUsers.AnyAsync(u => u.Username == user.Username))
                    {
                        _context.FdxUsers.Add(user);
                        await _context.SaveChangesAsync(); // Save each user individually
                    }
                }
                catch (Exception ex)
                {
                    // Log error but continue with other users
                    var innerMessage = ex.InnerException?.Message ?? ex.Message;
                    importResult.Errors.Add($"Failed to save user {user.Username}: {innerMessage}");
                    
                    // Check if it's a duplicate username error
                    if (innerMessage.Contains("duplicate") || innerMessage.Contains("unique"))
                    {
                        importResult.SkippedReasons.Add($"User {user.Username} already exists");
                        importResult.Skipped++;
                    }
                }
            }
            
            return importResult;
        }
    }
    
    [HttpPost("clear-imported-users")]
    public async Task<IActionResult> ClearImportedUsers()
    {
        var importedUsers = await _context.FdxUsers
            .Where(u => u.ImportedAt != null && u.Type != UserType.Admin)
            .ToListAsync();
        
        _context.FdxUsers.RemoveRange(importedUsers);
        await _context.SaveChangesAsync();
        
        return Ok(new
        {
            success = true,
            message = $"Removed {importedUsers.Count} imported users",
            removedCount = importedUsers.Count
        });
    }
    
    [HttpGet("export-credentials")]
    public async Task<IActionResult> ExportCredentials()
    {
        var users = await _context.FdxUsers
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
            })
            .ToListAsync();
        
        var csv = "Username,Password,CompanyName,Email,Phone,Type,Status,DataComplete\n";
        foreach (var user in users)
        {
            csv += $"\"{user.Username}\",\"{user.Password}\",\"{user.CompanyName}\",\"{user.Email}\",\"{user.PhoneNumber}\",\"{user.Type}\",\"{user.Status}\",\"{user.DataComplete}\"\n";
        }
        
        return File(Encoding.UTF8.GetBytes(csv), "text/csv", $"user_credentials_{DateTime.Now:yyyyMMdd_HHmmss}.csv");
    }

    private async Task<string> GenerateUsername(string companyName)
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
        while (await _context.FdxUsers.AnyAsync(u => u.Username == username))
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

public class SupplierUpdateDto
{
    public string? CompanyName { get; set; }
    public string? Email { get; set; }
    public string? PhoneNumber { get; set; }
    public string? Website { get; set; }
    public string? Address { get; set; }
    public string? Country { get; set; }
    public string? BusinessType { get; set; }
    public string? Category { get; set; }
    public string? ProfileImage { get; set; }  // URL or base64 image
}

public class UserUpdateDto
{
    public string? Email { get; set; }
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string? DisplayName { get; set; }
    public string? CompanyName { get; set; }
    public int Type { get; set; }
    public bool IsActive { get; set; }
    public string? PhoneNumber { get; set; }
    public string? Country { get; set; }
    public string? Address { get; set; }
    public string? Website { get; set; }
    public string? ProfileImage { get; set; }
    public string? AlternateEmails { get; set; }
    public string? Category { get; set; }
    public string? BusinessType { get; set; }
    public string? SubCategories { get; set; }
    public string? FullDescription { get; set; }
    public bool RequiresPasswordChange { get; set; }
    public bool DataComplete { get; set; }
    public int Verification { get; set; }
    public string? ImportNotes { get; set; }
}

public class ResetPasswordDto
{
    public string NewPassword { get; set; } = "";
}