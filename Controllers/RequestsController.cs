using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Models;
using FDX.Trading.Data;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Globalization;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class RequestsController : ControllerBase
{
    private readonly FdxTradingContext _context;
    
    public RequestsController(FdxTradingContext context)
    {
        _context = context;
    }

    // GET: api/requests
    [HttpGet]
    public async Task<IActionResult> GetRequests([FromQuery] ProcurementRequestStatus? status = null, [FromQuery] int? buyerId = null)
    {
        var query = _context.Requests
            .Include(r => r.Buyer)
            .Include(r => r.RequestItems)
            .AsQueryable();

        if (status.HasValue)
            query = query.Where(r => r.Status == status.Value);

        if (buyerId.HasValue)
            query = query.Where(r => r.BuyerId == buyerId.Value);

        var requests = await query
            .OrderByDescending(r => r.CreatedAt)
            .Select(r => new RequestDto
            {
                Id = r.Id,
                RequestNumber = r.RequestNumber,
                Title = r.Title,
                Description = r.Description,
                BuyerId = r.BuyerId,
                BuyerName = r.BuyerName ?? (r.Buyer.FirstName != null && r.Buyer.LastName != null 
                    ? $"{r.Buyer.FirstName} {r.Buyer.LastName}"
                    : r.Buyer.Username),
                BuyerCompany = r.BuyerCompany ?? r.Buyer.CompanyName,
                Status = r.Status,
                ItemCount = r.RequestItems.Count,
                CreatedAt = r.CreatedAt,
                UpdatedAt = r.UpdatedAt
            })
            .ToListAsync();

        return Ok(requests);
    }

    // GET: api/requests/{id}
    [HttpGet("{id}")]
    public async Task<IActionResult> GetRequest(int id)
    {
        var request = await _context.Requests
            .Include(r => r.Buyer)
            .Include(r => r.RequestItems)
            .FirstOrDefaultAsync(r => r.Id == id);

        if (request == null)
            return NotFound(new { message = "Request not found" });

        var requestDto = new RequestDto
        {
            Id = request.Id,
            RequestNumber = request.RequestNumber,
            Title = request.Title,
            Description = request.Description,
            BuyerId = request.BuyerId,
            BuyerName = request.BuyerName ?? (request.Buyer.FirstName != null && request.Buyer.LastName != null 
                ? $"{request.Buyer.FirstName} {request.Buyer.LastName}"
                : request.Buyer.Username),
            BuyerCompany = request.BuyerCompany ?? request.Buyer.CompanyName,
            Status = request.Status,
            ItemCount = request.RequestItems.Count,
            CreatedAt = request.CreatedAt,
            UpdatedAt = request.UpdatedAt,
            Items = request.RequestItems.Select(i => new RequestItemDto
            {
                Id = i.Id,
                RequestId = i.RequestId,
                ProductName = i.ProductName,
                Quantity = i.Quantity,
                Unit = i.Unit,
                Description = i.Description,
                TargetPrice = i.TargetPrice,
                CreatedAt = i.CreatedAt
            }).ToList()
        };

        return Ok(requestDto);
    }

    // POST: api/requests
    [HttpPost]
    public async Task<IActionResult> CreateRequest([FromBody] CreateRequestDto dto)
    {
        // For now, use buyer ID 1 as default (you can later get this from session/auth)
        // In production, get from authenticated user context
        var buyerId = 1; // Default to admin user for testing
        
        // Check if user is a buyer
        var buyer = await _context.FdxUsers.FindAsync(buyerId);
        if (buyer == null || buyer.Type != UserType.Buyer && buyer.Type != UserType.Admin)
            return BadRequest(new { message = "Only buyers can create requests" });
        
        // Update buyer's company if provided
        if (!string.IsNullOrEmpty(dto.BuyerCompany) && buyer.CompanyName != dto.BuyerCompany)
        {
            buyer.CompanyName = dto.BuyerCompany;
            _context.FdxUsers.Update(buyer);
        }

        // Generate request number
        var year = DateTime.Now.Year;
        var lastRequest = await _context.Requests
            .Where(r => r.RequestNumber.StartsWith($"REQ-{year}-"))
            .OrderByDescending(r => r.RequestNumber)
            .FirstOrDefaultAsync();

        int nextNumber = 1;
        if (lastRequest != null)
        {
            var lastNumberStr = lastRequest.RequestNumber.Split('-').Last();
            if (int.TryParse(lastNumberStr, out int lastNumber))
                nextNumber = lastNumber + 1;
        }

        var requestNumber = $"REQ-{year}-{nextNumber:D4}";

        var request = new Request
        {
            RequestNumber = requestNumber,
            Title = dto.Title,
            Description = dto.Description,
            BuyerId = buyerId,
            BuyerName = dto.BuyerName ?? buyer.DisplayName ?? buyer.Username,
            BuyerCompany = dto.BuyerCompany ?? buyer.CompanyName,
            Status = ProcurementRequestStatus.Draft,
            CreatedAt = DateTime.Now,
            UpdatedAt = DateTime.Now
        };

        // Add request items
        foreach (var itemDto in dto.Items)
        {
            request.RequestItems.Add(new RequestItem
            {
                ProductName = itemDto.ProductName,
                Quantity = itemDto.Quantity,
                Unit = itemDto.Unit,
                Description = itemDto.Description,
                TargetPrice = itemDto.TargetPrice,
                CreatedAt = DateTime.Now
            });
        }

        _context.Requests.Add(request);
        await _context.SaveChangesAsync();

        return Ok(new
        {
            success = true,
            message = "Request created successfully",
            requestId = request.Id,
            requestNumber = request.RequestNumber
        });
    }

    // PUT: api/requests/{id}
    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateRequest(int id, [FromBody] CreateRequestDto dto)
    {
        var request = await _context.Requests
            .Include(r => r.RequestItems)
            .FirstOrDefaultAsync(r => r.Id == id);

        if (request == null)
            return NotFound(new { message = "Request not found" });

        // Only allow editing draft requests
        if (request.Status != ProcurementRequestStatus.Draft)
            return BadRequest(new { message = "Can only edit draft requests" });

        request.Title = dto.Title;
        request.Description = dto.Description;
        request.BuyerName = dto.BuyerName;
        request.BuyerCompany = dto.BuyerCompany;
        request.UpdatedAt = DateTime.Now;

        // Remove existing items
        _context.RequestItems.RemoveRange(request.RequestItems);

        // Add new items
        foreach (var itemDto in dto.Items)
        {
            request.RequestItems.Add(new RequestItem
            {
                ProductName = itemDto.ProductName,
                Quantity = itemDto.Quantity,
                Unit = itemDto.Unit,
                Description = itemDto.Description,
                TargetPrice = itemDto.TargetPrice,
                CreatedAt = DateTime.Now
            });
        }

        await _context.SaveChangesAsync();

        return Ok(new
        {
            success = true,
            message = "Request updated successfully"
        });
    }

    // PATCH: api/requests/{id}
    [HttpPatch("{id}")]
    public async Task<IActionResult> PatchRequest(int id, [FromBody] JsonElement patchData)
    {
        var request = await _context.Requests.FindAsync(id);

        if (request == null)
            return NotFound(new { message = "Request not found" });

        // Update only the fields that are provided
        if (patchData.TryGetProperty("buyerName", out JsonElement buyerNameElement))
        {
            request.BuyerName = buyerNameElement.GetString();
            request.UpdatedAt = DateTime.Now;
        }

        if (patchData.TryGetProperty("buyerCompany", out JsonElement buyerCompanyElement))
        {
            request.BuyerCompany = buyerCompanyElement.GetString();
            request.UpdatedAt = DateTime.Now;
        }

        if (patchData.TryGetProperty("updatedAt", out JsonElement updatedAtElement))
        {
            request.UpdatedAt = DateTime.Now;
        }

        await _context.SaveChangesAsync();

        return Ok(new
        {
            success = true,
            message = "Request updated successfully"
        });
    }

    // PUT: api/requests/{id}/status
    [HttpPut("{id}/status")]
    public async Task<IActionResult> UpdateRequestStatus(int id, [FromBody] UpdateRequestStatusDto dto)
    {
        var request = await _context.Requests.FindAsync(id);

        if (request == null)
            return NotFound(new { message = "Request not found" });

        request.Status = dto.Status;
        request.UpdatedAt = DateTime.Now;

        await _context.SaveChangesAsync();

        return Ok(new
        {
            success = true,
            message = $"Request status updated to {dto.Status}",
            newStatus = dto.Status.ToString()
        });
    }

    // DELETE: api/requests/{id}
    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteRequest(int id)
    {
        var request = await _context.Requests.FindAsync(id);

        if (request == null)
            return NotFound(new { message = "Request not found" });

        // Only allow deleting draft requests
        if (request.Status != ProcurementRequestStatus.Draft)
            return BadRequest(new { message = "Can only delete draft requests" });

        _context.Requests.Remove(request);
        await _context.SaveChangesAsync();

        return Ok(new
        {
            success = true,
            message = "Request deleted successfully"
        });
    }

    // POST: api/requests/{id}/items
    [HttpPost("{id}/items")]
    public async Task<IActionResult> AddRequestItem(int id, [FromBody] CreateRequestItemDto dto)
    {
        var request = await _context.Requests.FindAsync(id);

        if (request == null)
            return NotFound(new { message = "Request not found" });

        if (request.Status != ProcurementRequestStatus.Draft)
            return BadRequest(new { message = "Can only add items to draft requests" });

        var item = new RequestItem
        {
            RequestId = id,
            ProductName = dto.ProductName,
            Quantity = dto.Quantity,
            Unit = dto.Unit,
            Description = dto.Description,
            TargetPrice = dto.TargetPrice,
            CreatedAt = DateTime.Now
        };

        _context.RequestItems.Add(item);
        request.UpdatedAt = DateTime.Now;
        
        await _context.SaveChangesAsync();

        return Ok(new
        {
            success = true,
            message = "Item added successfully",
            itemId = item.Id
        });
    }

    // DELETE: api/requests/{id}/items/{itemId}
    [HttpDelete("{id}/items/{itemId}")]
    public async Task<IActionResult> DeleteRequestItem(int id, int itemId)
    {
        var item = await _context.RequestItems
            .Include(i => i.Request)
            .FirstOrDefaultAsync(i => i.Id == itemId && i.RequestId == id);

        if (item == null)
            return NotFound(new { message = "Item not found" });

        if (item.Request.Status != ProcurementRequestStatus.Draft)
            return BadRequest(new { message = "Can only remove items from draft requests" });

        _context.RequestItems.Remove(item);
        item.Request.UpdatedAt = DateTime.Now;
        
        await _context.SaveChangesAsync();

        return Ok(new
        {
            success = true,
            message = "Item removed successfully"
        });
    }

    // GET: api/requests/stats
    [HttpGet("stats")]
    public async Task<IActionResult> GetRequestStats()
    {
        var stats = new
        {
            total = await _context.Requests.CountAsync(),
            draft = await _context.Requests.CountAsync(r => r.Status == ProcurementRequestStatus.Draft),
            active = await _context.Requests.CountAsync(r => r.Status == ProcurementRequestStatus.Active),
            closed = await _context.Requests.CountAsync(r => r.Status == ProcurementRequestStatus.Closed),
            totalItems = await _context.RequestItems.CountAsync()
        };

        return Ok(stats);
    }

    // POST: api/requests/import-csv
    [HttpPost("import-csv")]
    public async Task<IActionResult> ImportFromCsv([FromForm] IFormFile requestsFile, [FromForm] IFormFile? itemsFile)
    {
        if (requestsFile == null || requestsFile.Length == 0)
            return BadRequest(new { message = "Requests file is required" });

        var importedRequests = new List<Request>();
        var requestItems = new Dictionary<string, List<RequestItem>>();
        var errors = new List<string>();
        
        try
        {
            // First, parse the request items file if provided
            if (itemsFile != null && itemsFile.Length > 0)
            {
                using (var reader = new StreamReader(itemsFile.OpenReadStream(), Encoding.UTF8))
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
                            if (values.Length >= 4) // At least: Product Name, Quantity, Unit, Link to Request
                            {
                                var productName = values[0]?.Trim() ?? "";
                                var requestLink = values[3]?.Trim() ?? ""; // Link to Requests column
                                
                                if (!string.IsNullOrEmpty(productName) && !string.IsNullOrEmpty(requestLink))
                                {
                                    // Extract quantity and unit
                                    decimal quantity = 1;
                                    string unit = "pcs";
                                    
                                    if (values.Length > 6 && decimal.TryParse(values[6], out decimal q))
                                        quantity = q;
                                    if (values.Length > 7 && !string.IsNullOrEmpty(values[7]))
                                        unit = values[7].Trim();
                                    
                                    // Truncate product name if too long
                                    if (productName.Length > 500)
                                        productName = productName.Substring(0, 497) + "...";
                                    
                                    var item = new RequestItem
                                    {
                                        ProductName = productName,
                                        Quantity = quantity,
                                        Unit = unit,
                                        Description = values.Length > 9 ? values[9]?.Trim() : null,
                                        CreatedAt = DateTime.Now
                                    };
                                    
                                    if (!requestItems.ContainsKey(requestLink))
                                        requestItems[requestLink] = new List<RequestItem>();
                                    
                                    requestItems[requestLink].Add(item);
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            errors.Add($"Items file line {lineNumber}: {ex.Message}");
                        }
                    }
                }
            }
            
            // Now parse the requests file
            using (var reader = new StreamReader(requestsFile.OpenReadStream(), Encoding.UTF8))
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
                        
                        if (values.Length >= 3) // At least: Request name, status, brief/description
                        {
                            var requestName = values[0]?.Trim() ?? "";
                            var status = values[2]?.Trim() ?? "New";
                            var brief = values.Length > 6 ? values[6]?.Trim() : "";
                            var buyerName = values.Length > 9 ? values[9]?.Trim() : "Unknown Buyer";
                            var requestId = values.Length > 33 ? values[33]?.Trim() : ""; // Request ID column
                            
                            if (string.IsNullOrEmpty(requestName))
                                continue;
                            
                            // Map status
                            var requestStatus = status.ToLower() switch
                            {
                                "new" => ProcurementRequestStatus.Draft,
                                "active" => ProcurementRequestStatus.Active,
                                "cancelled" => ProcurementRequestStatus.Closed,
                                "closed" => ProcurementRequestStatus.Closed,
                                _ => ProcurementRequestStatus.Draft
                            };
                            
                            // Find or create buyer
                            var buyer = await _context.FdxUsers
                                .FirstOrDefaultAsync(u => u.CompanyName == buyerName || u.Username == buyerName);
                            
                            if (buyer == null)
                            {
                                // Use admin as default if buyer not found
                                buyer = await _context.FdxUsers.FirstOrDefaultAsync(u => u.Id == 1);
                            }
                            
                            // Generate request number
                            var year = DateTime.Now.Year;
                            var lastRequest = await _context.Requests
                                .OrderByDescending(r => r.RequestNumber)
                                .FirstOrDefaultAsync();
                            
                            int nextNumber = importedRequests.Count + 1;
                            if (lastRequest != null)
                            {
                                var lastNumberStr = lastRequest.RequestNumber.Split('-').Last();
                                if (int.TryParse(lastNumberStr, out int lastNumber))
                                    nextNumber = lastNumber + importedRequests.Count + 1;
                            }
                            
                            // Truncate title if too long
                            if (requestName.Length > 500)
                                requestName = requestName.Substring(0, 497) + "...";
                            
                            // Truncate description if too long
                            if (!string.IsNullOrEmpty(brief) && brief.Length > 4000)
                                brief = brief.Substring(0, 3997) + "...";
                            
                            var request = new Request
                            {
                                RequestNumber = $"REQ-{year}-{nextNumber:D4}",
                                Title = requestName,
                                Description = brief,
                                BuyerId = buyer?.Id ?? 1,
                                Status = requestStatus,
                                CreatedAt = DateTime.Now,
                                UpdatedAt = DateTime.Now
                            };
                            
                            // Add items if they exist for this request
                            if (requestItems.ContainsKey(requestName))
                            {
                                foreach (var item in requestItems[requestName])
                                {
                                    request.RequestItems.Add(item);
                                }
                            }
                            // Also check by request ID if available
                            else if (!string.IsNullOrEmpty(requestId) && requestItems.ContainsKey(requestId))
                            {
                                foreach (var item in requestItems[requestId])
                                {
                                    request.RequestItems.Add(item);
                                }
                            }
                            
                            _context.Requests.Add(request);
                            importedRequests.Add(request);
                        }
                    }
                    catch (Exception ex)
                    {
                        errors.Add($"Requests file line {lineNumber}: {ex.Message}");
                    }
                }
            }
            
            await _context.SaveChangesAsync();
            
            return Ok(new
            {
                success = true,
                message = $"Imported {importedRequests.Count} requests with {importedRequests.Sum(r => r.RequestItems.Count)} items",
                importedCount = importedRequests.Count,
                totalItems = importedRequests.Sum(r => r.RequestItems.Count),
                errors = errors,
                importedRequests = importedRequests.Select(r => new
                {
                    r.RequestNumber,
                    r.Title,
                    ItemCount = r.RequestItems.Count,
                    Status = r.Status.ToString()
                })
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new
            {
                success = false,
                message = "Failed to import CSV files",
                error = ex.Message,
                errors = errors
            });
        }
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