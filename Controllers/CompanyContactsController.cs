using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models;
using System.Linq;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace FDX.Trading.Controllers
{
    [Route("api/company-contacts")]
    [ApiController]
    public class CompanyContactsController : ControllerBase
    {
        private readonly FdxTradingContext _context;

        public CompanyContactsController(FdxTradingContext context)
        {
            _context = context;
        }

        // GET: api/company-contacts
        [HttpGet]
        public async Task<ActionResult<IEnumerable<CompanyContactDto>>> GetAllContacts()
        {
            var contacts = await _context.CompanyContacts
                .Where(c => c.IsActive)
                .OrderBy(c => c.CompanyName)
                .ThenBy(c => c.ContactName)
                .Select(c => new CompanyContactDto
                {
                    Id = c.Id,
                    CompanyName = c.CompanyName,
                    ContactName = c.ContactName,
                    ContactEmail = c.ContactEmail,
                    ContactPhone = c.ContactPhone,
                    ContactRole = c.ContactRole,
                    IsActive = c.IsActive,
                    IsOrganizationAdmin = c.IsOrganizationAdmin,
                    CanManageContacts = c.CanManageContacts,
                    UserId = c.UserId,
                    CreatedAt = c.CreatedAt
                })
                .ToListAsync();

            return Ok(contacts);
        }

        // GET: api/company-contacts/by-company/{companyName}
        [HttpGet("by-company/{companyName}")]
        public async Task<ActionResult<IEnumerable<CompanyContactDto>>> GetContactsByCompany(string companyName)
        {
            var contacts = await _context.CompanyContacts
                .Where(c => c.CompanyName.ToLower() == companyName.ToLower() && c.IsActive)
                .OrderBy(c => c.ContactName)
                .Select(c => new CompanyContactDto
                {
                    Id = c.Id,
                    CompanyName = c.CompanyName,
                    ContactName = c.ContactName,
                    ContactEmail = c.ContactEmail,
                    ContactPhone = c.ContactPhone,
                    ContactRole = c.ContactRole,
                    IsActive = c.IsActive,
                    IsOrganizationAdmin = c.IsOrganizationAdmin,
                    CanManageContacts = c.CanManageContacts,
                    UserId = c.UserId,
                    CreatedAt = c.CreatedAt
                })
                .ToListAsync();

            return Ok(contacts);
        }

        // GET: api/company-contacts/{id}
        [HttpGet("{id}")]
        public async Task<ActionResult<CompanyContactDto>> GetContact(int id)
        {
            var contact = await _context.CompanyContacts.FindAsync(id);

            if (contact == null)
            {
                return NotFound();
            }

            return Ok(new CompanyContactDto
            {
                Id = contact.Id,
                CompanyName = contact.CompanyName,
                ContactName = contact.ContactName,
                ContactEmail = contact.ContactEmail,
                ContactPhone = contact.ContactPhone,
                ContactRole = contact.ContactRole,
                IsActive = contact.IsActive,
                IsOrganizationAdmin = contact.IsOrganizationAdmin,
                CanManageContacts = contact.CanManageContacts,
                UserId = contact.UserId,
                CreatedAt = contact.CreatedAt
            });
        }

        // POST: api/company-contacts
        [HttpPost]
        public async Task<ActionResult<CompanyContactDto>> CreateContact(CreateCompanyContactDto dto)
        {
            // Check if contact already exists
            var existingContact = await _context.CompanyContacts
                .FirstOrDefaultAsync(c => 
                    c.CompanyName.ToLower() == dto.CompanyName.ToLower() && 
                    c.ContactName.ToLower() == dto.ContactName.ToLower());

            if (existingContact != null)
            {
                if (!existingContact.IsActive)
                {
                    // Reactivate existing contact
                    existingContact.IsActive = true;
                    existingContact.ContactEmail = dto.ContactEmail;
                    existingContact.ContactPhone = dto.ContactPhone;
                    existingContact.ContactRole = dto.ContactRole;
                    existingContact.UpdatedAt = System.DateTime.Now;
                    
                    await _context.SaveChangesAsync();
                    
                    return Ok(new CompanyContactDto
                    {
                        Id = existingContact.Id,
                        CompanyName = existingContact.CompanyName,
                        ContactName = existingContact.ContactName,
                        ContactEmail = existingContact.ContactEmail,
                        ContactPhone = existingContact.ContactPhone,
                        ContactRole = existingContact.ContactRole,
                        IsActive = existingContact.IsActive,
                        CreatedAt = existingContact.CreatedAt
                    });
                }
                
                return BadRequest("Contact already exists for this company");
            }

            var contact = new CompanyContact
            {
                CompanyName = dto.CompanyName,
                ContactName = dto.ContactName,
                ContactEmail = dto.ContactEmail,
                ContactPhone = dto.ContactPhone,
                ContactRole = dto.ContactRole,
                IsActive = true,
                CreatedAt = System.DateTime.Now,
                UpdatedAt = System.DateTime.Now
            };

            _context.CompanyContacts.Add(contact);
            await _context.SaveChangesAsync();

            return CreatedAtAction(nameof(GetContact), new { id = contact.Id }, new CompanyContactDto
            {
                Id = contact.Id,
                CompanyName = contact.CompanyName,
                ContactName = contact.ContactName,
                ContactEmail = contact.ContactEmail,
                ContactPhone = contact.ContactPhone,
                ContactRole = contact.ContactRole,
                IsActive = contact.IsActive,
                CreatedAt = contact.CreatedAt
            });
        }

        // PUT: api/company-contacts/{id}
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateContact(int id, CreateCompanyContactDto dto)
        {
            var contact = await _context.CompanyContacts.FindAsync(id);
            
            if (contact == null)
            {
                return NotFound();
            }

            contact.ContactName = dto.ContactName;
            contact.ContactEmail = dto.ContactEmail;
            contact.ContactPhone = dto.ContactPhone;
            contact.ContactRole = dto.ContactRole;
            contact.UpdatedAt = System.DateTime.Now;

            await _context.SaveChangesAsync();

            return NoContent();
        }
        
        // PUT: api/company-contacts/{id}/permissions
        [HttpPut("{id}/permissions")]
        public async Task<IActionResult> UpdateContactPermissions(int id, UpdatePermissionsDto dto)
        {
            var contact = await _context.CompanyContacts.FindAsync(id);
            
            if (contact == null)
            {
                return NotFound();
            }

            contact.IsOrganizationAdmin = dto.IsOrganizationAdmin;
            contact.CanManageContacts = dto.CanManageContacts;
            contact.UpdatedAt = System.DateTime.Now;

            await _context.SaveChangesAsync();

            return Ok(new { success = true, message = "Permissions updated successfully" });
        }
        
        // PUT: api/company-contacts/{id}/full-update
        [HttpPut("{id}/full-update")]
        public async Task<IActionResult> UpdateContactFull(int id, UpdateContactFullDto dto)
        {
            var contact = await _context.CompanyContacts.FindAsync(id);
            
            if (contact == null)
            {
                return NotFound();
            }

            // Update all contact details
            contact.ContactName = dto.ContactName;
            contact.ContactRole = dto.ContactRole;
            contact.ContactEmail = dto.ContactEmail;
            contact.ContactPhone = dto.ContactPhone;
            contact.IsActive = dto.IsActive;
            contact.IsOrganizationAdmin = dto.IsOrganizationAdmin;
            contact.CanManageContacts = dto.CanManageContacts;
            contact.UpdatedAt = System.DateTime.Now;

            await _context.SaveChangesAsync();

            return Ok(new { success = true, message = "Contact updated successfully" });
        }

        // DELETE: api/company-contacts/{id}
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeactivateContact(int id)
        {
            var contact = await _context.CompanyContacts.FindAsync(id);
            
            if (contact == null)
            {
                return NotFound();
            }

            // Soft delete - just mark as inactive
            contact.IsActive = false;
            contact.UpdatedAt = System.DateTime.Now;

            await _context.SaveChangesAsync();

            return NoContent();
        }

        // POST: api/company-contacts/import-all-contacts
        [HttpPost("import-all-contacts")]
        public async Task<IActionResult> ImportAllContacts()
        {
            var importResults = new List<object>();
            var totalImported = 0;
            var totalSkipped = 0;
            var totalErrors = 0;

            // Import Buyer Contacts
            var buyerResult = await ImportBuyerContacts();
            importResults.Add(new { source = "Buyer Contacts", result = buyerResult });
            
            // Import Supplier Contacts
            var supplierResult = await ImportSupplierContacts();
            importResults.Add(new { source = "Supplier Contacts", result = supplierResult });

            return Ok(new
            {
                success = true,
                message = "Contact import completed",
                results = importResults
            });
        }

        private async Task<object> ImportBuyerContacts()
        {
            var filePath = @"C:\Users\fdxadmin\Downloads\Buyer Contacts 10_8_2025.csv";
            if (!System.IO.File.Exists(filePath))
                return new { error = "Buyer contacts file not found" };

            var imported = 0;
            var skipped = 0;
            var errors = new List<string>();

            try
            {
                using (var reader = new System.IO.StreamReader(filePath))
                {
                    var header = await reader.ReadLineAsync(); // Skip header
                    string? line;
                    var lineNumber = 1;

                    while ((line = await reader.ReadLineAsync()) != null)
                    {
                        lineNumber++;
                        if (string.IsNullOrWhiteSpace(line)) continue;

                        try
                        {
                            var values = ParseCsvLine(line);
                            if (values.Length >= 8)
                            {
                                var fullName = values[1]?.Trim();
                                var email = values[2]?.Trim();
                                var companyName = values[3]?.Trim();
                                var jobPosition = values[4]?.Trim();
                                var phone = values[5]?.Trim();
                                var mobile = values[6]?.Trim();
                                var isActive = values[7]?.Trim().ToLower() == "yes";

                                if (!string.IsNullOrEmpty(fullName) && !string.IsNullOrEmpty(companyName))
                                {
                                    // Check if exists
                                    var exists = await _context.CompanyContacts
                                        .AnyAsync(c => c.CompanyName == companyName && c.ContactName == fullName);

                                    if (!exists)
                                    {
                                        var contact = new CompanyContact
                                        {
                                            CompanyName = companyName.Length > 200 ? companyName.Substring(0, 200) : companyName,
                                            ContactName = fullName.Length > 200 ? fullName.Substring(0, 200) : fullName,
                                            ContactEmail = email?.Length > 100 ? email.Substring(0, 100) : email,
                                            ContactPhone = !string.IsNullOrEmpty(mobile) ? mobile : phone,
                                            ContactRole = jobPosition?.Length > 100 ? jobPosition.Substring(0, 100) : jobPosition,
                                            IsActive = isActive,
                                            IsOrganizationAdmin = false,
                                            CanManageContacts = false,
                                            CreatedAt = System.DateTime.Now,
                                            UpdatedAt = System.DateTime.Now
                                        };

                                        _context.CompanyContacts.Add(contact);
                                        imported++;
                                    }
                                    else
                                    {
                                        skipped++;
                                    }
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            errors.Add($"Line {lineNumber}: {ex.Message}");
                        }
                    }
                }

                await _context.SaveChangesAsync();
            }
            catch (Exception ex)
            {
                errors.Add($"General error: {ex.Message}");
            }

            return new { imported, skipped, errors = errors.Count, errorDetails = errors.Take(5) };
        }

        private async Task<object> ImportSupplierContacts()
        {
            var filePath = @"C:\Users\fdxadmin\Downloads\Supplier Contacts 10_8_2025 (1).csv";
            if (!System.IO.File.Exists(filePath))
                return new { error = "Supplier contacts file not found" };

            var imported = 0;
            var skipped = 0;
            var errors = new List<string>();

            try
            {
                using (var reader = new System.IO.StreamReader(filePath))
                {
                    var header = await reader.ReadLineAsync(); // Skip header
                    string? line;
                    var lineNumber = 1;

                    while ((line = await reader.ReadLineAsync()) != null)
                    {
                        lineNumber++;
                        if (string.IsNullOrWhiteSpace(line)) continue;

                        try
                        {
                            var values = ParseCsvLine(line);
                            if (values.Length >= 10)
                            {
                                var companyName = values[1]?.Trim(); // Contact's Company
                                var contactName = values[3]?.Trim(); // Contact person's name
                                var jobTitle = values[4]?.Trim();
                                var email = values[5]?.Trim();
                                var mobile = values[7]?.Trim();
                                var office = values[8]?.Trim();
                                var isActive = values[9]?.Trim().ToLower() == "yes";

                                // If company name is empty or "0", try to extract from contact ID field
                                if (string.IsNullOrEmpty(companyName) || companyName == "0")
                                {
                                    var idField = values[0]?.Trim();
                                    if (!string.IsNullOrEmpty(idField) && idField.Contains(","))
                                    {
                                        var parts = idField.Split(',');
                                        if (parts.Length > 2)
                                        {
                                            // Extract company from pattern like "Name, Company, Role"
                                            companyName = parts[1]?.Trim();
                                        }
                                    }
                                }

                                if (!string.IsNullOrEmpty(contactName) && !string.IsNullOrEmpty(companyName) && companyName != "0")
                                {
                                    // Clean up contact name
                                    contactName = System.Text.RegularExpressions.Regex.Replace(contactName, @"^(Mr\.|Mrs\.|Ms\.)\s*", "").Trim();

                                    // Check if exists
                                    var exists = await _context.CompanyContacts
                                        .AnyAsync(c => c.CompanyName == companyName && c.ContactName == contactName);

                                    if (!exists)
                                    {
                                        var contact = new CompanyContact
                                        {
                                            CompanyName = companyName.Length > 200 ? companyName.Substring(0, 200) : companyName,
                                            ContactName = contactName.Length > 200 ? contactName.Substring(0, 200) : contactName,
                                            ContactEmail = email?.Length > 100 ? email.Substring(0, 100) : email,
                                            ContactPhone = !string.IsNullOrEmpty(mobile) ? mobile : office,
                                            ContactRole = jobTitle?.Length > 100 ? jobTitle.Substring(0, 100) : jobTitle,
                                            IsActive = isActive,
                                            IsOrganizationAdmin = false,
                                            CanManageContacts = false,
                                            CreatedAt = System.DateTime.Now,
                                            UpdatedAt = System.DateTime.Now
                                        };

                                        _context.CompanyContacts.Add(contact);
                                        imported++;
                                    }
                                    else
                                    {
                                        skipped++;
                                    }
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            errors.Add($"Line {lineNumber}: {ex.Message}");
                        }
                    }
                }

                await _context.SaveChangesAsync();
            }
            catch (Exception ex)
            {
                errors.Add($"General error: {ex.Message}");
            }

            return new { imported, skipped, errors = errors.Count, errorDetails = errors.Take(5) };
        }

        // POST: api/company-contacts/import-from-buyers-csv
        [HttpPost("import-from-buyers-csv")]
        public async Task<IActionResult> ImportContactsFromBuyersCsv()
        {
            try
            {
                var filePath = @"C:\Users\fdxadmin\Downloads\Buyers 10_8_2025.csv";
                if (!System.IO.File.Exists(filePath))
                {
                    return BadRequest("Buyers CSV file not found");
                }

                var importedContacts = new List<CompanyContact>();
                var errors = new List<string>();
                var skipped = new List<string>();

                using (var reader = new System.IO.StreamReader(filePath))
                {
                    var line = await reader.ReadLineAsync(); // Skip header
                    var lineNumber = 1;

                    while ((line = await reader.ReadLineAsync()) != null)
                    {
                        lineNumber++;
                        try
                        {
                            var values = ParseCsvLine(line);
                            if (values.Length < 6) continue;

                            var companyName = values[4]?.Trim(); // Company name column
                            var contactsField = values[5]?.Trim(); // Link to Buyer Contacts column

                            if (string.IsNullOrEmpty(companyName) || string.IsNullOrEmpty(contactsField))
                                continue;

                            // Parse contacts from the field
                            var contactsList = ParseContacts(contactsField, companyName);
                            
                            foreach (var contactData in contactsList)
                            {
                                // Check if contact already exists
                                var existingContact = await _context.CompanyContacts
                                    .FirstOrDefaultAsync(c => 
                                        c.CompanyName == contactData.CompanyName && 
                                        c.ContactName == contactData.ContactName);

                                if (existingContact != null)
                                {
                                    skipped.Add($"{contactData.ContactName} from {contactData.CompanyName} - already exists");
                                    continue;
                                }

                                var contact = new CompanyContact
                                {
                                    CompanyName = contactData.CompanyName.Length > 200 ? contactData.CompanyName.Substring(0, 200) : contactData.CompanyName,
                                    ContactName = contactData.ContactName.Length > 200 ? contactData.ContactName.Substring(0, 200) : contactData.ContactName,
                                    ContactRole = contactData.ContactRole != null && contactData.ContactRole.Length > 100 ? contactData.ContactRole.Substring(0, 100) : contactData.ContactRole,
                                    IsActive = true,
                                    IsOrganizationAdmin = contactData.IsFirstContact, // First contact is admin
                                    CanManageContacts = contactData.IsFirstContact,
                                    CreatedAt = System.DateTime.Now,
                                    UpdatedAt = System.DateTime.Now
                                };

                                _context.CompanyContacts.Add(contact);
                                importedContacts.Add(contact);
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
                    message = $"Imported {importedContacts.Count} contacts",
                    imported = importedContacts.Count,
                    skipped = skipped.Count,
                    errors = errors.Count,
                    details = new
                    {
                        importedContacts = importedContacts.Select(c => new
                        {
                            c.CompanyName,
                            c.ContactName,
                            c.ContactRole,
                            c.IsOrganizationAdmin
                        }),
                        skippedReasons = skipped.Take(10),
                        errorMessages = errors.Take(10)
                    }
                });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }

        private List<(string CompanyName, string ContactName, string? ContactRole, bool IsFirstContact)> ParseContacts(string contactsField, string companyName)
        {
            var contacts = new List<(string, string, string, bool)>();
            
            // Improved parsing using regex to extract name and role pairs
            var pattern = @"(Mr\.|Mrs\.|Ms\.)?\s*([^,]+),\s*([^,]+)(?:,|$)";
            var matches = System.Text.RegularExpressions.Regex.Matches(contactsField, pattern);
            
            if (matches.Count > 0)
            {
                for (int i = 0; i < matches.Count; i++)
                {
                    var match = matches[i];
                    var contactName = match.Groups[2].Value.Trim();
                    var role = match.Groups[3].Value.Trim();
                    
                    // Clean up role - stop at next contact or company name
                    if (role.Contains(companyName))
                    {
                        var roleEnd = role.IndexOf(companyName);
                        role = role.Substring(0, roleEnd).Trim().TrimEnd(',', '.');
                    }
                    
                    // Limit role length
                    if (role.Length > 100) role = role.Substring(0, 100);
                    
                    if (!string.IsNullOrEmpty(contactName) && contactName.Length > 2)
                    {
                        contacts.Add((companyName, contactName, role, i == 0));
                    }
                }
            }
            else
            {
                // Fallback: if no pattern matches, try simple parsing
                var simpleParts = contactsField.Split(',');
                for (int i = 0; i < simpleParts.Length; i += 2)
                {
                    if (i >= simpleParts.Length) break;
                    
                    var name = simpleParts[i].Trim();
                    name = System.Text.RegularExpressions.Regex.Replace(name, @"^(Mr\.|Mrs\.|Ms\.)\s*", "");
                    
                    var role = i + 1 < simpleParts.Length ? simpleParts[i + 1].Trim() : "";
                    
                    // Stop if we hit description text
                    if (role.Length > 50 || role.Contains("**") || role.Contains("\n"))
                    {
                        role = role.Split(new[] { '\n', '*' }, StringSplitOptions.RemoveEmptyEntries)[0].Trim();
                    }
                    
                    if (role.Length > 100) role = role.Substring(0, 100);
                    
                    if (!string.IsNullOrEmpty(name) && name.Length > 2 && !name.Contains(companyName))
                    {
                        contacts.Add((companyName, name, role, contacts.Count == 0));
                    }
                }
            }

            return contacts;
        }

        private string[] ParseCsvLine(string line)
        {
            var values = new List<string>();
            var currentValue = new System.Text.StringBuilder();
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
}