using FoodXchange.Domain.Abstractions;

namespace FoodXchange.Domain.Suppliers;

public interface ISupplierRepository : IRepository<Supplier>
{
    Task<Supplier?> GetByCodeAsync(string code, CancellationToken ct = default);
    Task<List<Supplier>> GetByStatusAsync(SupplierStatus status, CancellationToken ct = default);
    Task<List<Supplier>> SearchAsync(string searchTerm, CancellationToken ct = default);
    Task<bool> CodeExistsAsync(string code, CancellationToken ct = default);
    Task<List<Supplier>> GetSuppliersForProductAsync(Guid productId, CancellationToken ct = default);
}