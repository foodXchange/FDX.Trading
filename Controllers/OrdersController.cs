using Microsoft.AspNetCore.Mvc;
using FDX.Trading.Models.Orders;
using FDX.Trading.Services;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{
    private readonly IOrderService _orderService;
    private readonly ILogger<OrdersController> _logger;

    public OrdersController(IOrderService orderService, ILogger<OrdersController> logger)
    {
        _orderService = orderService;
        _logger = logger;
    }

    // Order Creation with Compliance Gating
    [HttpPost("create-from-contract")]
    public async Task<IActionResult> CreateOrderFromContract([FromBody] CreateOrderRequest request)
    {
        try
        {
            // Check compliance gate first
            var canCreate = await _orderService.CanCreateOrderAsync(request.ContractId);
            if (!canCreate)
            {
                return BadRequest(new { 
                    success = false, 
                    message = "Cannot create order: Compliance not approved for this contract",
                    requiresCompliance = true 
                });
            }

            var order = await _orderService.CreateOrderFromContractAsync(
                request.ContractId,
                request.ProjectId,
                request.BuyerUserId,
                request.OrderCode,
                request.RequestedDelivery
            );

            return Ok(new { 
                success = true, 
                orderId = order.OrderId,
                orderCode = order.OrderCode,
                status = order.Status
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating order from contract");
            return StatusCode(500, new { success = false, message = "Error creating order" });
        }
    }

    [HttpGet("can-create/{contractId}")]
    public async Task<IActionResult> CanCreateOrder(Guid contractId)
    {
        try
        {
            var canCreate = await _orderService.CanCreateOrderAsync(contractId);
            return Ok(new { canCreate });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking if order can be created");
            return StatusCode(500, new { success = false, message = "Error checking order creation eligibility" });
        }
    }

    // Order Management
    [HttpGet("{orderId}")]
    public async Task<IActionResult> GetOrder(Guid orderId)
    {
        try
        {
            var order = await _orderService.GetOrderAsync(orderId);
            if (order == null)
            {
                return NotFound(new { success = false, message = "Order not found" });
            }

            return Ok(new { success = true, data = order });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting order {OrderId}", orderId);
            return StatusCode(500, new { success = false, message = "Error retrieving order" });
        }
    }

    [HttpGet("project/{projectId}")]
    public async Task<IActionResult> GetOrdersByProject(Guid projectId)
    {
        try
        {
            var orders = await _orderService.GetOrdersByProjectAsync(projectId);
            return Ok(new { success = true, data = orders });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting orders for project {ProjectId}", projectId);
            return StatusCode(500, new { success = false, message = "Error retrieving orders" });
        }
    }

    [HttpGet("status/{status}")]
    public async Task<IActionResult> GetOrdersByStatus(string status)
    {
        try
        {
            var orders = await _orderService.GetOrdersByStatusAsync(status);
            return Ok(new { success = true, data = orders });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting orders by status {Status}", status);
            return StatusCode(500, new { success = false, message = "Error retrieving orders" });
        }
    }

    [HttpPut("{orderId}/status")]
    public async Task<IActionResult> UpdateOrderStatus(Guid orderId, [FromBody] UpdateStatusRequest request)
    {
        try
        {
            var success = await _orderService.UpdateOrderStatusAsync(orderId, request.Status);
            if (!success)
            {
                return NotFound(new { success = false, message = "Order not found" });
            }

            return Ok(new { success = true, message = "Order status updated" });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { success = false, message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating order status");
            return StatusCode(500, new { success = false, message = "Error updating order status" });
        }
    }

    // Shipment Management
    [HttpPost("{orderId}/shipments")]
    public async Task<IActionResult> CreateShipment(Guid orderId, [FromBody] CreateShipmentRequest request)
    {
        try
        {
            var shipment = await _orderService.CreateShipmentAsync(
                orderId,
                request.Mode,
                request.Carrier
            );

            return Ok(new { 
                success = true, 
                shipmentId = shipment.ShipmentId,
                shipmentCode = shipment.ShipmentCode
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating shipment");
            return StatusCode(500, new { success = false, message = "Error creating shipment" });
        }
    }

    [HttpGet("shipments/{shipmentId}")]
    public async Task<IActionResult> GetShipment(Guid shipmentId)
    {
        try
        {
            var shipment = await _orderService.GetShipmentAsync(shipmentId);
            if (shipment == null)
            {
                return NotFound(new { success = false, message = "Shipment not found" });
            }

            return Ok(new { success = true, data = shipment });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting shipment");
            return StatusCode(500, new { success = false, message = "Error retrieving shipment" });
        }
    }

    [HttpGet("{orderId}/shipments")]
    public async Task<IActionResult> GetShipmentsByOrder(Guid orderId)
    {
        try
        {
            var shipments = await _orderService.GetShipmentsByOrderAsync(orderId);
            return Ok(new { success = true, data = shipments });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting shipments");
            return StatusCode(500, new { success = false, message = "Error retrieving shipments" });
        }
    }

    [HttpPost("shipments/{shipmentId}/milestones")]
    public async Task<IActionResult> AddShipmentMilestone(Guid shipmentId, [FromBody] AddMilestoneRequest request)
    {
        try
        {
            var milestone = await _orderService.AddShipmentMilestoneAsync(
                shipmentId,
                request.Code,
                request.OccurredAt,
                request.Location,
                request.Notes
            );

            return Ok(new { 
                success = true, 
                milestoneId = milestone.MilestoneId,
                commissionAccrued = request.Code == "ARRIVED" || request.Code == "CUSTOMS_CLEARED"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding shipment milestone");
            return StatusCode(500, new { success = false, message = "Error adding milestone" });
        }
    }

    [HttpPost("shipments/{shipmentId}/documents")]
    public async Task<IActionResult> AddShipmentDocument(Guid shipmentId, [FromBody] AddDocumentRequest request)
    {
        try
        {
            var document = await _orderService.AddShipmentDocumentAsync(
                shipmentId,
                request.DocType,
                request.FileName,
                request.BlobUri,
                request.UploadedBy
            );

            return Ok(new { 
                success = true, 
                documentId = document.ShipmentDocumentId
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding shipment document");
            return StatusCode(500, new { success = false, message = "Error adding document" });
        }
    }

    // Commission Management
    [HttpGet("{orderId}/commissions")]
    public async Task<IActionResult> GetCommissionAccruals(Guid orderId)
    {
        try
        {
            var accruals = await _orderService.GetCommissionAccrualsAsync(orderId);
            return Ok(new { success = true, data = accruals });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting commission accruals");
            return StatusCode(500, new { success = false, message = "Error retrieving commissions" });
        }
    }

    [HttpPost("{orderId}/commissions/generate-invoice")]
    public async Task<IActionResult> GenerateCommissionInvoice(Guid orderId)
    {
        try
        {
            var invoice = await _orderService.GenerateCommissionInvoiceAsync(orderId);
            if (invoice == null)
            {
                return BadRequest(new { 
                    success = false, 
                    message = "No accrued commissions to invoice" 
                });
            }

            return Ok(new { 
                success = true, 
                invoiceId = invoice.InvoiceId,
                invoiceCode = invoice.InvoiceCode,
                total = invoice.Total
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating commission invoice");
            return StatusCode(500, new { success = false, message = "Error generating invoice" });
        }
    }

    [HttpGet("commission-rates")]
    public async Task<IActionResult> GetActiveCommissionRates()
    {
        try
        {
            var rates = await _orderService.GetActiveCommissionRatesAsync();
            return Ok(new { success = true, data = rates });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting commission rates");
            return StatusCode(500, new { success = false, message = "Error retrieving commission rates" });
        }
    }

    [HttpPost("commission-rates")]
    public async Task<IActionResult> CreateCommissionRate([FromBody] CommissionRate rate)
    {
        try
        {
            var created = await _orderService.CreateCommissionRateAsync(rate);
            return Ok(new { 
                success = true, 
                rateId = created.RateId
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating commission rate");
            return StatusCode(500, new { success = false, message = "Error creating commission rate" });
        }
    }

    // Invoice Management
    [HttpGet("invoices/{invoiceId}")]
    public async Task<IActionResult> GetInvoice(Guid invoiceId)
    {
        try
        {
            var invoice = await _orderService.GetInvoiceAsync(invoiceId);
            if (invoice == null)
            {
                return NotFound(new { success = false, message = "Invoice not found" });
            }

            return Ok(new { success = true, data = invoice });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting invoice");
            return StatusCode(500, new { success = false, message = "Error retrieving invoice" });
        }
    }

    [HttpGet("{orderId}/invoices")]
    public async Task<IActionResult> GetInvoicesByOrder(Guid orderId)
    {
        try
        {
            var invoices = await _orderService.GetInvoicesByOrderAsync(orderId);
            return Ok(new { success = true, data = invoices });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting invoices");
            return StatusCode(500, new { success = false, message = "Error retrieving invoices" });
        }
    }

    [HttpPost("invoices/{invoiceId}/payments")]
    public async Task<IActionResult> RecordPayment(Guid invoiceId, [FromBody] RecordPaymentRequest request)
    {
        try
        {
            var payment = await _orderService.RecordPaymentAsync(
                invoiceId,
                request.Amount,
                request.Currency,
                request.Method,
                request.Reference
            );

            return Ok(new { 
                success = true, 
                paymentId = payment.PaymentId
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error recording payment");
            return StatusCode(500, new { success = false, message = "Error recording payment" });
        }
    }

    // Order Participants
    [HttpPost("{orderId}/participants")]
    public async Task<IActionResult> AssignParticipant(Guid orderId, [FromBody] AssignParticipantRequest request)
    {
        try
        {
            var participant = await _orderService.AssignParticipantAsync(
                orderId,
                request.Role,
                request.UserId,
                request.ExternalUserId
            );

            return Ok(new { 
                success = true, 
                participantId = participant.OrderParticipantId
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error assigning participant");
            return StatusCode(500, new { success = false, message = "Error assigning participant" });
        }
    }

    [HttpGet("{orderId}/participants")]
    public async Task<IActionResult> GetOrderParticipants(Guid orderId)
    {
        try
        {
            var participants = await _orderService.GetOrderParticipantsAsync(orderId);
            return Ok(new { success = true, data = participants });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting participants");
            return StatusCode(500, new { success = false, message = "Error retrieving participants" });
        }
    }
}

// Request DTOs
public class CreateOrderRequest
{
    public Guid ContractId { get; set; }
    public Guid ProjectId { get; set; }
    public Guid? BuyerUserId { get; set; }
    public string? OrderCode { get; set; }
    public DateTime? RequestedDelivery { get; set; }
}

public class UpdateStatusRequest
{
    public string Status { get; set; } = string.Empty;
}

public class CreateShipmentRequest
{
    public string Mode { get; set; } = "sea";
    public string? Carrier { get; set; }
}

public class AddMilestoneRequest
{
    public string Code { get; set; } = string.Empty;
    public DateTimeOffset? OccurredAt { get; set; }
    public string? Location { get; set; }
    public string? Notes { get; set; }
}

public class AddDocumentRequest
{
    public string DocType { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
    public string BlobUri { get; set; } = string.Empty;
    public Guid? UploadedBy { get; set; }
}

public class RecordPaymentRequest
{
    public decimal Amount { get; set; }
    public string Currency { get; set; } = "USD";
    public string? Method { get; set; }
    public string? Reference { get; set; }
}

public class AssignParticipantRequest
{
    public string Role { get; set; } = string.Empty;
    public Guid? UserId { get; set; }
    public Guid? ExternalUserId { get; set; }
}