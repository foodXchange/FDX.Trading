using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Data;
using FDX.Trading.Models.Orders;
using FDX.Trading.Services;
using FDX.Trading.Utils;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class FinanceController : ControllerBase
{
    private readonly FdxTradingContext _context;
    private readonly IOrderService _orderService;
    private readonly ICsvImporter _csvImporter;
    private readonly ILogger<FinanceController> _logger;

    public FinanceController(
        FdxTradingContext context, 
        IOrderService orderService,
        ICsvImporter csvImporter,
        ILogger<FinanceController> logger)
    {
        _context = context;
        _orderService = orderService;
        _csvImporter = csvImporter;
        _logger = logger;
    }

    // Commission Management
    [HttpPost("commission/accrue/shipment/{shipmentId}")]
    public async Task<IActionResult> AccrueCommission(Guid shipmentId, [FromQuery] string trigger = "ARRIVED")
    {
        try
        {
            // Ensure milestone exists
            var milestoneExists = await _context.ShipmentMilestones
                .AnyAsync(m => m.ShipmentId == shipmentId && m.Code == trigger);
                
            if (!milestoneExists)
            {
                return Conflict(new { error = "Milestone not reached", shipmentId, trigger });
            }

            // Accrue commission
            var accrual = await _orderService.AccrueCommissionOnShipmentAsync(shipmentId, trigger);
            
            if (accrual == null)
            {
                return BadRequest(new { 
                    error = "Commission accrual failed or already exists", 
                    shipmentId, 
                    trigger 
                });
            }

            return Ok(new { 
                shipmentId, 
                trigger, 
                status = "accrued",
                accrualId = accrual.AccrualId,
                amount = accrual.CalculatedAmount,
                currency = accrual.Currency
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error accruing commission for shipment {ShipmentId}", shipmentId);
            return StatusCode(500, new { error = "Error accruing commission" });
        }
    }

    [HttpPost("commission/invoice/order/{orderId}")]
    public async Task<IActionResult> IssueCommissionInvoice(Guid orderId)
    {
        try
        {
            var invoice = await _orderService.GenerateCommissionInvoiceAsync(orderId);
            
            if (invoice == null)
            {
                return BadRequest(new { 
                    error = "No accrued commissions to invoice",
                    orderId 
                });
            }

            return Ok(new { 
                orderId, 
                status = "invoice_issued",
                invoiceId = invoice.InvoiceId,
                invoiceCode = invoice.InvoiceCode,
                total = invoice.Total
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error issuing commission invoice for order {OrderId}", orderId);
            return StatusCode(500, new { error = "Error issuing invoice" });
        }
    }

    // AP Invoice Management
    [HttpPost("ap/shipment/{shipmentId}/invoice")]
    public async Task<IActionResult> AddAPInvoice(Guid shipmentId, [FromBody] ApInvoiceDto dto)
    {
        try
        {
            // Verify shipment exists
            var shipmentExists = await _context.Shipments.AnyAsync(s => s.ShipmentId == shipmentId);
            if (!shipmentExists)
            {
                return NotFound(new { error = "Shipment not found" });
            }

            // Create invoice
            var invoice = new Invoice
            {
                InvoiceId = Guid.NewGuid(),
                Type = "AP",
                ShipmentId = shipmentId,
                CounterpartyType = "external_org",
                CounterpartyId = dto.ExternalOrgId,
                InvoiceCode = dto.InvoiceCode,
                IssueDate = DateTime.SpecifyKind(dto.IssueDate, DateTimeKind.Utc),
                DueDate = dto.DueDate.HasValue ? DateTime.SpecifyKind(dto.DueDate.Value, DateTimeKind.Utc) : null,
                Currency = dto.Currency,
                Status = "issued",
                Subtotal = dto.Lines.Sum(x => x.Quantity * x.UnitPrice),
                TaxAmount = 0,
                CreatedAt = DateTimeOffset.UtcNow,
                UpdatedAt = DateTimeOffset.UtcNow
            };

            _context.Invoices.Add(invoice);

            // Add invoice lines
            foreach (var line in dto.Lines)
            {
                _context.InvoiceLines.Add(new InvoiceLine
                {
                    InvoiceLineId = Guid.NewGuid(),
                    InvoiceId = invoice.InvoiceId,
                    Kind = line.Kind,
                    Description = line.Description,
                    Quantity = line.Quantity,
                    UnitPrice = line.UnitPrice,
                    CreatedAt = DateTimeOffset.UtcNow
                });
            }

            await _context.SaveChangesAsync();

            return Created($"/api/invoices/{invoice.InvoiceId}", new { 
                invoiceId = invoice.InvoiceId,
                invoiceCode = invoice.InvoiceCode,
                total = invoice.Total
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding AP invoice for shipment {ShipmentId}", shipmentId);
            return StatusCode(500, new { error = "Error adding AP invoice" });
        }
    }

    // Invoice Queries
    [HttpGet("invoices")]
    public async Task<IActionResult> GetInvoices([FromQuery] Guid? orderId, [FromQuery] Guid? shipmentId, [FromQuery] string? type)
    {
        try
        {
            var query = _context.Invoices.AsQueryable();

            if (orderId.HasValue)
                query = query.Where(i => i.OrderId == orderId);
            
            if (shipmentId.HasValue)
                query = query.Where(i => i.ShipmentId == shipmentId);
            
            if (!string.IsNullOrEmpty(type))
                query = query.Where(i => i.Type == type);

            var invoices = await query
                .OrderByDescending(i => i.IssueDate)
                .Select(i => new
                {
                    i.InvoiceId,
                    i.Type,
                    i.InvoiceCode,
                    i.Currency,
                    i.Subtotal,
                    i.TaxAmount,
                    Total = i.Total,
                    i.Status,
                    i.IssueDate,
                    i.DueDate,
                    i.OrderId,
                    i.ShipmentId
                })
                .ToListAsync();

            return Ok(invoices);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting invoices");
            return StatusCode(500, new { error = "Error retrieving invoices" });
        }
    }

    [HttpGet("invoices/{invoiceId}")]
    public async Task<IActionResult> GetInvoiceDetail(Guid invoiceId)
    {
        try
        {
            var invoice = await _context.Invoices
                .Where(i => i.InvoiceId == invoiceId)
                .Select(i => new
                {
                    i.InvoiceId,
                    i.Type,
                    i.InvoiceCode,
                    i.IssueDate,
                    i.DueDate,
                    i.Currency,
                    i.Status,
                    i.OrderId,
                    i.ShipmentId,
                    i.CounterpartyType,
                    i.CounterpartyId,
                    Lines = _context.InvoiceLines
                        .Where(l => l.InvoiceId == i.InvoiceId)
                        .Select(l => new
                        {
                            l.InvoiceLineId,
                            l.Kind,
                            l.Description,
                            l.Quantity,
                            l.UnitPrice,
                            Amount = l.Amount
                        })
                        .ToList(),
                    i.Subtotal,
                    Tax = i.TaxAmount,
                    Total = i.Total,
                    Payments = _context.Payments
                        .Where(p => p.InvoiceId == i.InvoiceId)
                        .Select(p => new
                        {
                            p.PaymentId,
                            p.PaidAt,
                            p.Currency,
                            p.Amount,
                            p.Method,
                            p.Reference
                        })
                        .ToList()
                })
                .FirstOrDefaultAsync();

            if (invoice == null)
                return NotFound(new { error = "Invoice not found" });

            return Ok(invoice);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting invoice {InvoiceId}", invoiceId);
            return StatusCode(500, new { error = "Error retrieving invoice" });
        }
    }

    // Payment Management
    [HttpPost("invoices/{invoiceId}/payments")]
    public async Task<IActionResult> RecordPayment(Guid invoiceId, [FromBody] PaymentDto dto)
    {
        try
        {
            var invoice = await _context.Invoices.FindAsync(invoiceId);
            if (invoice == null)
                return NotFound(new { error = "Invoice not found" });

            var payment = new Payment
            {
                PaymentId = Guid.NewGuid(),
                InvoiceId = invoiceId,
                PaidAt = dto.PaidAt ?? DateTimeOffset.UtcNow,
                Currency = dto.Currency,
                Amount = dto.Amount,
                Method = dto.Method,
                Reference = dto.Reference,
                CreatedAt = DateTimeOffset.UtcNow
            };

            _context.Payments.Add(payment);
            await _context.SaveChangesAsync();

            // Check if fully paid
            var totalPaid = await _context.Payments
                .Where(p => p.InvoiceId == invoiceId)
                .SumAsync(p => p.Amount);
            
            var invoiceTotal = invoice.Subtotal + invoice.TaxAmount;
            
            if (totalPaid >= invoiceTotal)
            {
                invoice.Status = "paid";
                invoice.UpdatedAt = DateTimeOffset.UtcNow;
                await _context.SaveChangesAsync();
            }

            return Created($"/api/invoices/{invoiceId}", new { 
                invoiceId, 
                paymentId = payment.PaymentId,
                totalPaid,
                invoiceTotal,
                status = invoice.Status
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error recording payment for invoice {InvoiceId}", invoiceId);
            return StatusCode(500, new { error = "Error recording payment" });
        }
    }

    // Aging Report
    [HttpGet("aging")]
    public async Task<IActionResult> GetAgingReport([FromQuery] string type = "AR")
    {
        try
        {
            var today = DateTime.UtcNow.Date;
            
            var invoices = await _context.Invoices
                .Where(i => i.Type == type && i.Status != "paid" && i.Status != "cancelled")
                .Select(i => new
                {
                    i.InvoiceId,
                    i.InvoiceCode,
                    i.CounterpartyType,
                    i.CounterpartyId,
                    i.Currency,
                    Amount = i.Subtotal + i.TaxAmount,
                    i.DueDate,
                    i.IssueDate
                })
                .ToListAsync();

            var aged = invoices.Select(i =>
            {
                var dueDate = i.DueDate ?? i.IssueDate.AddDays(30);
                var daysPastDue = (today - dueDate).Days;
                var bucket = daysPastDue <= 0 ? "current" :
                            daysPastDue <= 30 ? "1-30" :
                            daysPastDue <= 60 ? "31-60" :
                            daysPastDue <= 90 ? "61-90" : "90+";
                
                return new
                {
                    i.InvoiceId,
                    i.InvoiceCode,
                    i.Amount,
                    i.Currency,
                    DaysPastDue = daysPastDue,
                    Bucket = bucket
                };
            });

            var summary = aged.GroupBy(x => x.Bucket)
                .Select(g => new
                {
                    Bucket = g.Key,
                    Count = g.Count(),
                    Total = g.Sum(x => x.Amount),
                    Invoices = g.ToList()
                })
                .OrderBy(g => g.Bucket switch
                {
                    "current" => 0,
                    "1-30" => 1,
                    "31-60" => 2,
                    "61-90" => 3,
                    "90+" => 4,
                    _ => 5
                });

            return Ok(new
            {
                Type = type,
                AsOfDate = today,
                Summary = summary,
                TotalOutstanding = aged.Sum(x => x.Amount)
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating aging report");
            return StatusCode(500, new { error = "Error generating aging report" });
        }
    }

    // P&L by Order
    [HttpGet("pnl/order/{orderId}")]
    public async Task<IActionResult> GetOrderPnL(Guid orderId)
    {
        try
        {
            var order = await _context.Orders.FindAsync(orderId);
            if (order == null)
                return NotFound(new { error = "Order not found" });

            var arTotal = await _context.Invoices
                .Where(i => i.OrderId == orderId && i.Type == "AR" && i.Status != "cancelled")
                .SumAsync(i => i.Subtotal + i.TaxAmount);

            var apTotal = await _context.Invoices
                .Where(i => i.OrderId == orderId && i.Type == "AP" && i.Status != "cancelled")
                .SumAsync(i => i.Subtotal + i.TaxAmount);

            var commissionAccrued = await _context.CommissionAccruals
                .Where(a => a.OrderId == orderId && a.Status != "cancelled")
                .SumAsync(a => a.CalculatedAmount);

            var net = arTotal - apTotal;

            return Ok(new
            {
                OrderId = orderId,
                OrderCode = order.OrderCode,
                Currency = order.Currency,
                OrderValue = order.TotalAmount ?? 0,
                AR_Total = arTotal,
                AP_Total = apTotal,
                CommissionAccrued = commissionAccrued,
                Net = net,
                Margin = order.TotalAmount > 0 ? (net / order.TotalAmount.Value) * 100 : 0
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting P&L for order {OrderId}", orderId);
            return StatusCode(500, new { error = "Error calculating P&L" });
        }
    }

    // CSV Import
    [HttpPost("import/csv")]
    public async Task<IActionResult> ImportCsvData([FromQuery] string? basePath = null)
    {
        try
        {
            basePath ??= @"C:\FDX.Trading\Data\Import";
            
            _logger.LogInformation("Starting CSV import from {BasePath}", basePath);

            var results = new
            {
                CommissionRates = await _csvImporter.ImportCommissionRatesAsync(Path.Combine(basePath, "Commission Rates 15_8_2025.csv")),
                Invoices = await _csvImporter.ImportInvoicesAsync(Path.Combine(basePath, "Invoices 15_8_2025.csv")),
                Shipping = await _csvImporter.ImportShippingAsync(Path.Combine(basePath, "Shipping 15_8_2025.csv"))
            };

            await _csvImporter.NormalizeAllDataAsync();

            return Ok(new
            {
                success = true,
                message = "CSV import completed",
                imported = results
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error importing CSV data");
            return StatusCode(500, new { error = "Error importing CSV data", details = ex.Message });
        }
    }
}

// DTOs
public class ApInvoiceDto
{
    public Guid ExternalOrgId { get; set; }
    public string InvoiceCode { get; set; } = string.Empty;
    public DateTime IssueDate { get; set; } = DateTime.UtcNow;
    public DateTime? DueDate { get; set; }
    public string Currency { get; set; } = "USD";
    public List<ApInvoiceLineDto> Lines { get; set; } = new();
}

public class ApInvoiceLineDto
{
    public string Kind { get; set; } = "freight";
    public string Description { get; set; } = string.Empty;
    public decimal Quantity { get; set; } = 1;
    public decimal UnitPrice { get; set; }
}

public class PaymentDto
{
    public DateTimeOffset? PaidAt { get; set; }
    public string Currency { get; set; } = "USD";
    public decimal Amount { get; set; }
    public string? Method { get; set; }
    public string? Reference { get; set; }
}