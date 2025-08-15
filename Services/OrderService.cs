using Microsoft.EntityFrameworkCore;
using Microsoft.Data.SqlClient;
using FDX.Trading.Data;
using FDX.Trading.Models.Orders;
using FDX.Trading.Models.Compliance;
using System.Data;

namespace FDX.Trading.Services;

public class OrderService : IOrderService
{
    private readonly FdxTradingContext _context;
    private readonly ILogger<OrderService> _logger;
    private readonly IComplianceService _complianceService;

    public OrderService(FdxTradingContext context, ILogger<OrderService> logger, IComplianceService complianceService)
    {
        _context = context;
        _logger = logger;
        _complianceService = complianceService;
    }

    // Order Creation with Compliance Gating
    public async Task<Order> CreateOrderFromContractAsync(Guid contractId, Guid projectId, Guid? buyerUserId = null, string? orderCode = null, DateTime? requestedDelivery = null)
    {
        // Check compliance gate
        var canCreate = await CanCreateOrderAsync(contractId);
        if (!canCreate)
        {
            throw new InvalidOperationException($"Cannot create order: Compliance not approved for contract {contractId}");
        }

        // Generate order code if not provided
        if (string.IsNullOrEmpty(orderCode))
        {
            var dateStr = DateTime.UtcNow.ToString("yyyy-MM-dd");
            var sequence = await _context.Orders.CountAsync() + 1;
            orderCode = $"ORD-{dateStr}-{sequence:D5}";
        }

        // Create order (simplified - in production would copy from contract)
        var order = new Order
        {
            OrderId = Guid.NewGuid(),
            ProjectId = projectId,
            ContractId = contractId,
            BuyerUserId = buyerUserId,
            SupplierId = Guid.NewGuid(), // In production, get from contract
            OrderCode = orderCode,
            Status = "placed",
            Currency = "USD",
            Incoterms = "FOB",
            RequestedDelivery = requestedDelivery?.ToUniversalTime(),
            CreatedAt = DateTimeOffset.UtcNow,
            UpdatedAt = DateTimeOffset.UtcNow
        };

        _context.Orders.Add(order);
        
        // Add sample order lines (in production, copy from contract lines)
        for (int i = 1; i <= 3; i++)
        {
            var line = new OrderLine
            {
                OrderLineId = Guid.NewGuid(),
                OrderId = order.OrderId,
                ProductName = $"Sample Product {i}",
                Unit = "KG",
                Quantity = 100,
                UnitPrice = 10.50m * i,
                Currency = order.Currency,
                Incoterms = order.Incoterms,
                RequestedDelivery = order.RequestedDelivery,
                CreatedAt = DateTimeOffset.UtcNow
            };
            _context.OrderLines.Add(line);
        }

        // Calculate totals
        await _context.SaveChangesAsync();
        
        var subtotal = await _context.OrderLines
            .Where(ol => ol.OrderId == order.OrderId)
            .SumAsync(ol => ol.Quantity * ol.UnitPrice);
            
        order.SubtotalAmount = subtotal;
        order.TotalAmount = subtotal + (order.FreightAmount ?? 0) + (order.InsuranceAmount ?? 0) + (order.TaxAmount ?? 0);
        order.UpdatedAt = DateTimeOffset.UtcNow;
        
        await _context.SaveChangesAsync();
        
        _logger.LogInformation("Created order {OrderCode} from contract {ContractId}", order.OrderCode, contractId);
        
        return order;
    }

    public async Task<bool> CanCreateOrderAsync(Guid contractId)
    {
        // Check if compliance is approved for this contract
        var complianceProcess = await _context.ComplianceProcesses
            .FirstOrDefaultAsync(cp => cp.ContractId == contractId);
            
        return complianceProcess != null && complianceProcess.Status == "approved";
    }

    // Order Management
    public async Task<Order?> GetOrderAsync(Guid orderId)
    {
        return await _context.Orders
            .Include(o => o.OrderLines)
            .Include(o => o.Shipments)
            .Include(o => o.OrderParticipants)
            .FirstOrDefaultAsync(o => o.OrderId == orderId);
    }

    public async Task<IEnumerable<Order>> GetOrdersByProjectAsync(Guid projectId)
    {
        return await _context.Orders
            .Where(o => o.ProjectId == projectId)
            .OrderByDescending(o => o.CreatedAt)
            .ToListAsync();
    }

    public async Task<IEnumerable<Order>> GetOrdersByStatusAsync(string status)
    {
        return await _context.Orders
            .Where(o => o.Status == status)
            .OrderByDescending(o => o.CreatedAt)
            .ToListAsync();
    }

    public async Task<bool> UpdateOrderStatusAsync(Guid orderId, string newStatus)
    {
        var order = await _context.Orders.FindAsync(orderId);
        if (order == null) return false;

        // Basic validation
        if (order.Status == "closed" && newStatus != "closed")
        {
            throw new InvalidOperationException("Cannot change status of a closed order");
        }

        if (order.Status == "cancelled")
        {
            throw new InvalidOperationException("Cannot change status of a cancelled order");
        }

        order.Status = newStatus;
        order.UpdatedAt = DateTimeOffset.UtcNow;
        
        await _context.SaveChangesAsync();
        return true;
    }

    public async Task<Order> AddOrderLineAsync(Guid orderId, OrderLine line)
    {
        var order = await GetOrderAsync(orderId);
        if (order == null)
            throw new ArgumentException($"Order {orderId} not found");

        line.OrderId = orderId;
        line.CreatedAt = DateTimeOffset.UtcNow;
        
        _context.OrderLines.Add(line);
        await _context.SaveChangesAsync();

        // Recalculate totals
        order.SubtotalAmount = await _context.OrderLines
            .Where(ol => ol.OrderId == orderId)
            .SumAsync(ol => ol.Quantity * ol.UnitPrice);
        order.TotalAmount = order.SubtotalAmount + (order.FreightAmount ?? 0) + (order.InsuranceAmount ?? 0) + (order.TaxAmount ?? 0);
        order.UpdatedAt = DateTimeOffset.UtcNow;
        
        await _context.SaveChangesAsync();
        
        return order;
    }

    public async Task<bool> RemoveOrderLineAsync(Guid orderLineId)
    {
        var line = await _context.OrderLines.FindAsync(orderLineId);
        if (line == null) return false;

        _context.OrderLines.Remove(line);
        await _context.SaveChangesAsync();
        
        return true;
    }

    // Shipment Management
    public async Task<Shipment> CreateShipmentAsync(Guid orderId, string mode, string? carrier = null)
    {
        var order = await GetOrderAsync(orderId);
        if (order == null)
            throw new ArgumentException($"Order {orderId} not found");

        var shipmentCount = await _context.Shipments.CountAsync(s => s.OrderId == orderId);
        var shipmentCode = $"{order.OrderCode}-SHP-{shipmentCount + 1:D3}";

        var shipment = new Shipment
        {
            ShipmentId = Guid.NewGuid(),
            OrderId = orderId,
            ShipmentCode = shipmentCode,
            Mode = mode,
            Carrier = carrier,
            Status = "planning",
            CreatedAt = DateTimeOffset.UtcNow,
            UpdatedAt = DateTimeOffset.UtcNow
        };

        _context.Shipments.Add(shipment);
        await _context.SaveChangesAsync();
        
        return shipment;
    }

    public async Task<Shipment?> GetShipmentAsync(Guid shipmentId)
    {
        return await _context.Shipments
            .Include(s => s.Containers)
            .Include(s => s.Documents)
            .Include(s => s.Milestones)
            .FirstOrDefaultAsync(s => s.ShipmentId == shipmentId);
    }

    public async Task<IEnumerable<Shipment>> GetShipmentsByOrderAsync(Guid orderId)
    {
        return await _context.Shipments
            .Where(s => s.OrderId == orderId)
            .OrderByDescending(s => s.CreatedAt)
            .ToListAsync();
    }

    public async Task<ShipmentMilestone> AddShipmentMilestoneAsync(Guid shipmentId, string code, DateTimeOffset? occurredAt = null, string? location = null, string? notes = null)
    {
        var shipment = await GetShipmentAsync(shipmentId);
        if (shipment == null)
            throw new ArgumentException($"Shipment {shipmentId} not found");

        var milestone = new ShipmentMilestone
        {
            MilestoneId = Guid.NewGuid(),
            ShipmentId = shipmentId,
            Code = code,
            OccurredAt = occurredAt ?? DateTimeOffset.UtcNow,
            Location = location,
            Notes = notes,
            CreatedAt = DateTimeOffset.UtcNow
        };

        _context.ShipmentMilestones.Add(milestone);

        // Update shipment status based on milestone
        var newStatus = code switch
        {
            "BOOKED" => "booked",
            "DEPARTED" => "in_transit",
            "ARRIVED" => "arrived",
            "CUSTOMS_CLEARED" => "customs_cleared",
            "DELIVERED" => "delivered",
            _ => null
        };

        if (newStatus != null)
        {
            shipment.Status = newStatus;
            shipment.UpdatedAt = DateTimeOffset.UtcNow;
        }

        await _context.SaveChangesAsync();

        // Trigger commission accrual if applicable
        if (code == "ARRIVED" || code == "CUSTOMS_CLEARED")
        {
            await AccrueCommissionOnShipmentAsync(shipmentId, code);
        }

        return milestone;
    }

    public async Task<bool> UpdateShipmentStatusAsync(Guid shipmentId, string status)
    {
        var shipment = await _context.Shipments.FindAsync(shipmentId);
        if (shipment == null) return false;

        shipment.Status = status;
        shipment.UpdatedAt = DateTimeOffset.UtcNow;
        
        await _context.SaveChangesAsync();
        return true;
    }

    public async Task<ShipmentDocument> AddShipmentDocumentAsync(Guid shipmentId, string docType, string fileName, string blobUri, Guid? uploadedBy = null)
    {
        var document = new ShipmentDocument
        {
            ShipmentDocumentId = Guid.NewGuid(),
            ShipmentId = shipmentId,
            DocType = docType,
            FileName = fileName,
            BlobUri = blobUri,
            UploadedBy = uploadedBy,
            UploadedAt = DateTimeOffset.UtcNow
        };

        _context.ShipmentDocuments.Add(document);
        await _context.SaveChangesAsync();
        
        return document;
    }

    // Container Management
    public async Task<Container> AddContainerAsync(Guid shipmentId, string containerType, string? containerNumber = null, string? sealNumber = null)
    {
        var container = new Container
        {
            ContainerId = Guid.NewGuid(),
            ShipmentId = shipmentId,
            ContainerType = containerType,
            ContainerNumber = containerNumber,
            SealNumber = sealNumber,
            CreatedAt = DateTimeOffset.UtcNow
        };

        _context.Containers.Add(container);
        await _context.SaveChangesAsync();
        
        return container;
    }

    public async Task<ShipmentLineAllocation> AllocateOrderLineToShipmentAsync(Guid shipmentId, Guid orderLineId, decimal quantity, Guid? containerId = null)
    {
        var allocation = new ShipmentLineAllocation
        {
            AllocationId = Guid.NewGuid(),
            ShipmentId = shipmentId,
            OrderLineId = orderLineId,
            ContainerId = containerId,
            Quantity = quantity,
            CreatedAt = DateTimeOffset.UtcNow
        };

        _context.ShipmentLineAllocations.Add(allocation);
        await _context.SaveChangesAsync();
        
        return allocation;
    }

    // Commission Management
    public async Task<CommissionAccrual?> AccrueCommissionOnShipmentAsync(Guid shipmentId, string trigger)
    {
        var shipment = await GetShipmentAsync(shipmentId);
        if (shipment == null) return null;

        // Check if milestone exists
        var milestoneExists = await _context.ShipmentMilestones
            .AnyAsync(m => m.ShipmentId == shipmentId && m.Code == trigger);
        if (!milestoneExists) return null;

        // Check if already accrued
        var existingAccrual = await _context.CommissionAccruals
            .FirstOrDefaultAsync(a => a.ShipmentId == shipmentId && a.Status != "cancelled");
        if (existingAccrual != null) return existingAccrual;

        var order = await GetOrderAsync(shipment.OrderId);
        if (order == null) return null;

        // Calculate base amount
        var baseAmount = await _context.OrderLines
            .Where(ol => ol.OrderId == order.OrderId)
            .SumAsync(ol => ol.Quantity * ol.UnitPrice);

        // Find applicable rate
        var rate = await GetApplicableCommissionRateAsync(order.OrderId, order.SupplierId, shipment.Mode);
        if (rate == null) return null;

        // Calculate commission
        decimal calculatedAmount = 0;
        if (rate.RatePct.HasValue && rate.RatePct > 0)
        {
            calculatedAmount = Math.Round(baseAmount * (rate.RatePct.Value / 100m), 4);
        }
        else if (rate.FlatAmount.HasValue)
        {
            calculatedAmount = rate.FlatAmount.Value;
        }

        // Apply min/max limits
        if (rate.MinFee.HasValue && calculatedAmount < rate.MinFee.Value)
            calculatedAmount = rate.MinFee.Value;
        if (rate.MaxFee.HasValue && calculatedAmount > rate.MaxFee.Value)
            calculatedAmount = rate.MaxFee.Value;

        // Create accrual
        var accrual = new CommissionAccrual
        {
            AccrualId = Guid.NewGuid(),
            OrderId = order.OrderId,
            ShipmentId = shipmentId,
            RateId = rate.RateId,
            Basis = "order_value",
            BaseAmount = baseAmount,
            Currency = order.Currency,
            CalculatedAmount = calculatedAmount,
            Status = "accrued",
            AccruedAt = DateTimeOffset.UtcNow
        };

        _context.CommissionAccruals.Add(accrual);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Accrued commission of {Amount} {Currency} for shipment {ShipmentId}", 
            calculatedAmount, order.Currency, shipmentId);

        return accrual;
    }

    public async Task<IEnumerable<CommissionAccrual>> GetCommissionAccrualsAsync(Guid orderId)
    {
        return await _context.CommissionAccruals
            .Include(a => a.Rate)
            .Where(a => a.OrderId == orderId)
            .OrderByDescending(a => a.AccruedAt)
            .ToListAsync();
    }

    public async Task<CommissionRate?> GetApplicableCommissionRateAsync(Guid orderId, Guid? supplierId = null, string? mode = null)
    {
        var query = _context.CommissionRates
            .Where(r => r.IsActive && r.EffectiveFrom <= DateTime.UtcNow);

        if (r.EffectiveTo.HasValue)
            query = query.Where(r => r.EffectiveTo >= DateTime.UtcNow);

        // Apply filters with wildcards
        var rates = await query.ToListAsync();
        
        // Sort by specificity and priority
        var orderedRates = rates
            .OrderBy(r => r.SupplierId == null ? 2 : (r.SupplierId == supplierId ? 0 : 3))
            .ThenBy(r => r.Mode == null ? 2 : (r.Mode == mode ? 0 : 3))
            .ThenBy(r => r.Priority);

        return orderedRates.FirstOrDefault();
    }

    public async Task<IEnumerable<CommissionRate>> GetActiveCommissionRatesAsync()
    {
        return await _context.CommissionRates
            .Where(r => r.IsActive)
            .OrderBy(r => r.Priority)
            .ToListAsync();
    }

    public async Task<CommissionRate> CreateCommissionRateAsync(CommissionRate rate)
    {
        rate.RateId = Guid.NewGuid();
        rate.CreatedAt = DateTimeOffset.UtcNow;
        
        _context.CommissionRates.Add(rate);
        await _context.SaveChangesAsync();
        
        return rate;
    }

    // Invoice Management
    public async Task<Invoice?> GenerateCommissionInvoiceAsync(Guid orderId)
    {
        // Check for non-invoiced accruals
        var accruals = await _context.CommissionAccruals
            .Include(a => a.Rate)
            .Include(a => a.Shipment)
            .Where(a => a.OrderId == orderId && a.Status == "accrued")
            .ToListAsync();

        if (!accruals.Any()) return null;

        var order = await GetOrderAsync(orderId);
        if (order == null) return null;

        // Determine payer from first accrual's rate
        var firstRate = accruals.First().Rate;
        var payer = firstRate.Payer;

        // Set invoice type and counterparty
        string invoiceType = "AR";
        string counterpartyType = payer == "supplier" ? "supplier" : "buyer";
        Guid counterpartyId = payer == "supplier" ? order.SupplierId : order.BuyerUserId ?? Guid.Empty;

        // Generate invoice code
        var invoiceCode = $"INV-COM-{order.OrderCode}-{DateTime.UtcNow:yyyyMMdd}";

        // Create invoice
        var invoice = new Invoice
        {
            InvoiceId = Guid.NewGuid(),
            Type = invoiceType,
            OrderId = orderId,
            CounterpartyType = counterpartyType,
            CounterpartyId = counterpartyId,
            InvoiceCode = invoiceCode,
            Currency = order.Currency,
            Status = "issued",
            IssueDate = DateTime.UtcNow,
            CreatedAt = DateTimeOffset.UtcNow,
            UpdatedAt = DateTimeOffset.UtcNow
        };

        _context.Invoices.Add(invoice);

        // Create invoice lines from accruals
        decimal subtotal = 0;
        foreach (var accrual in accruals)
        {
            var line = new InvoiceLine
            {
                InvoiceLineId = Guid.NewGuid(),
                InvoiceId = invoice.InvoiceId,
                Kind = "commission",
                Description = $"Commission for shipment {accrual.Shipment.ShipmentCode}",
                Quantity = 1,
                UnitPrice = accrual.CalculatedAmount,
                ShipmentId = accrual.ShipmentId,
                CreatedAt = DateTimeOffset.UtcNow
            };
            
            _context.InvoiceLines.Add(line);
            subtotal += accrual.CalculatedAmount;

            // Mark accrual as invoiced
            accrual.Status = "invoiced";
            accrual.InvoiceId = invoice.InvoiceId;
        }

        invoice.Subtotal = subtotal;
        await _context.SaveChangesAsync();

        _logger.LogInformation("Generated commission invoice {InvoiceCode} for order {OrderId}", 
            invoice.InvoiceCode, orderId);

        return invoice;
    }

    public async Task<Invoice?> GetInvoiceAsync(Guid invoiceId)
    {
        return await _context.Invoices
            .Include(i => i.InvoiceLines)
            .Include(i => i.Payments)
            .FirstOrDefaultAsync(i => i.InvoiceId == invoiceId);
    }

    public async Task<IEnumerable<Invoice>> GetInvoicesByOrderAsync(Guid orderId)
    {
        return await _context.Invoices
            .Where(i => i.OrderId == orderId)
            .OrderByDescending(i => i.CreatedAt)
            .ToListAsync();
    }

    public async Task<Payment> RecordPaymentAsync(Guid invoiceId, decimal amount, string currency, string? method = null, string? reference = null)
    {
        var payment = new Payment
        {
            PaymentId = Guid.NewGuid(),
            InvoiceId = invoiceId,
            Amount = amount,
            Currency = currency,
            Method = method,
            Reference = reference,
            PaidAt = DateTimeOffset.UtcNow,
            CreatedAt = DateTimeOffset.UtcNow
        };

        _context.Payments.Add(payment);

        // Check if invoice is fully paid
        var invoice = await GetInvoiceAsync(invoiceId);
        if (invoice != null)
        {
            var totalPaid = invoice.Payments.Sum(p => p.Amount) + amount;
            if (totalPaid >= invoice.Total)
            {
                invoice.Status = "paid";
                invoice.UpdatedAt = DateTimeOffset.UtcNow;
            }
        }

        await _context.SaveChangesAsync();
        
        return payment;
    }

    public async Task<bool> UpdateInvoiceStatusAsync(Guid invoiceId, string status)
    {
        var invoice = await _context.Invoices.FindAsync(invoiceId);
        if (invoice == null) return false;

        invoice.Status = status;
        invoice.UpdatedAt = DateTimeOffset.UtcNow;
        
        await _context.SaveChangesAsync();
        return true;
    }

    // Order Participants
    public async Task<OrderParticipant> AssignParticipantAsync(Guid orderId, string role, Guid? userId = null, Guid? externalUserId = null)
    {
        if (userId == null && externalUserId == null)
            throw new ArgumentException("Either userId or externalUserId must be provided");

        var participant = new OrderParticipant
        {
            OrderParticipantId = Guid.NewGuid(),
            OrderId = orderId,
            Role = role,
            UserId = userId,
            ExternalUserId = externalUserId,
            AssignedAt = DateTimeOffset.UtcNow
        };

        _context.OrderParticipants.Add(participant);
        await _context.SaveChangesAsync();
        
        return participant;
    }

    public async Task<IEnumerable<OrderParticipant>> GetOrderParticipantsAsync(Guid orderId)
    {
        return await _context.OrderParticipants
            .Include(p => p.User)
            .Where(p => p.OrderId == orderId)
            .ToListAsync();
    }

    public async Task<bool> RemoveParticipantAsync(Guid participantId)
    {
        var participant = await _context.OrderParticipants.FindAsync(participantId);
        if (participant == null) return false;

        _context.OrderParticipants.Remove(participant);
        await _context.SaveChangesAsync();
        
        return true;
    }

    // Payment Terms
    public async Task<OrderPaymentTerm> AddPaymentTermAsync(Guid orderId, string termCode, decimal amount, string currency, DateTime? dueDate = null)
    {
        var term = new OrderPaymentTerm
        {
            OrderPaymentTermId = Guid.NewGuid(),
            OrderId = orderId,
            TermCode = termCode,
            Amount = amount,
            Currency = currency,
            DueDate = dueDate,
            Status = "pending",
            CreatedAt = DateTimeOffset.UtcNow
        };

        _context.OrderPaymentTerms.Add(term);
        await _context.SaveChangesAsync();
        
        return term;
    }

    public async Task<IEnumerable<OrderPaymentTerm>> GetPaymentTermsAsync(Guid orderId)
    {
        return await _context.OrderPaymentTerms
            .Where(t => t.OrderId == orderId)
            .OrderBy(t => t.DueDate)
            .ToListAsync();
    }

    public async Task<bool> UpdatePaymentTermStatusAsync(Guid paymentTermId, string status)
    {
        var term = await _context.OrderPaymentTerms.FindAsync(paymentTermId);
        if (term == null) return false;

        term.Status = status;
        await _context.SaveChangesAsync();
        
        return true;
    }
}