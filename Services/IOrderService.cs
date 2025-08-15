using FDX.Trading.Models.Orders;

namespace FDX.Trading.Services;

public interface IOrderService
{
    // Order Creation (with compliance gating)
    Task<Order> CreateOrderFromContractAsync(Guid contractId, Guid projectId, Guid? buyerUserId = null, string? orderCode = null, DateTime? requestedDelivery = null);
    Task<bool> CanCreateOrderAsync(Guid contractId);
    
    // Order Management
    Task<Order?> GetOrderAsync(Guid orderId);
    Task<IEnumerable<Order>> GetOrdersByProjectAsync(Guid projectId);
    Task<IEnumerable<Order>> GetOrdersByStatusAsync(string status);
    Task<bool> UpdateOrderStatusAsync(Guid orderId, string newStatus);
    Task<Order> AddOrderLineAsync(Guid orderId, OrderLine line);
    Task<bool> RemoveOrderLineAsync(Guid orderLineId);
    
    // Shipment Management
    Task<Shipment> CreateShipmentAsync(Guid orderId, string mode, string? carrier = null);
    Task<Shipment?> GetShipmentAsync(Guid shipmentId);
    Task<IEnumerable<Shipment>> GetShipmentsByOrderAsync(Guid orderId);
    Task<ShipmentMilestone> AddShipmentMilestoneAsync(Guid shipmentId, string code, DateTimeOffset? occurredAt = null, string? location = null, string? notes = null);
    Task<bool> UpdateShipmentStatusAsync(Guid shipmentId, string status);
    Task<ShipmentDocument> AddShipmentDocumentAsync(Guid shipmentId, string docType, string fileName, string blobUri, Guid? uploadedBy = null);
    
    // Container Management
    Task<Container> AddContainerAsync(Guid shipmentId, string containerType, string? containerNumber = null, string? sealNumber = null);
    Task<ShipmentLineAllocation> AllocateOrderLineToShipmentAsync(Guid shipmentId, Guid orderLineId, decimal quantity, Guid? containerId = null);
    
    // Commission Management
    Task<CommissionAccrual?> AccrueCommissionOnShipmentAsync(Guid shipmentId, string trigger);
    Task<IEnumerable<CommissionAccrual>> GetCommissionAccrualsAsync(Guid orderId);
    Task<CommissionRate?> GetApplicableCommissionRateAsync(Guid orderId, Guid? supplierId = null, string? mode = null);
    Task<IEnumerable<CommissionRate>> GetActiveCommissionRatesAsync();
    Task<CommissionRate> CreateCommissionRateAsync(CommissionRate rate);
    
    // Invoice Management
    Task<Invoice?> GenerateCommissionInvoiceAsync(Guid orderId);
    Task<Invoice?> GetInvoiceAsync(Guid invoiceId);
    Task<IEnumerable<Invoice>> GetInvoicesByOrderAsync(Guid orderId);
    Task<Payment> RecordPaymentAsync(Guid invoiceId, decimal amount, string currency, string? method = null, string? reference = null);
    Task<bool> UpdateInvoiceStatusAsync(Guid invoiceId, string status);
    
    // Order Participants
    Task<OrderParticipant> AssignParticipantAsync(Guid orderId, string role, Guid? userId = null, Guid? externalUserId = null);
    Task<IEnumerable<OrderParticipant>> GetOrderParticipantsAsync(Guid orderId);
    Task<bool> RemoveParticipantAsync(Guid participantId);
    
    // Payment Terms
    Task<OrderPaymentTerm> AddPaymentTermAsync(Guid orderId, string termCode, decimal amount, string currency, DateTime? dueDate = null);
    Task<IEnumerable<OrderPaymentTerm>> GetPaymentTermsAsync(Guid orderId);
    Task<bool> UpdatePaymentTermStatusAsync(Guid paymentTermId, string status);
}