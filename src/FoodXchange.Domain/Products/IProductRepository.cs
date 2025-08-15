using FoodXchange.Domain.Abstractions;

namespace FoodXchange.Domain.Products;

public interface IProductRepository : IRepository<Product>
{
    Task<Product?> GetBySkuAsync(string sku, CancellationToken ct = default);
    Task<List<Product>> GetByCategoryAsync(Guid categoryId, CancellationToken ct = default);
    Task<List<Product>> GetByBrandAsync(string brand, CancellationToken ct = default);
    Task<List<Product>> SearchAsync(string searchTerm, CancellationToken ct = default);
    Task<bool> SkuExistsAsync(string sku, CancellationToken ct = default);
}

public interface ICategoryRepository : IRepository<Category>
{
    Task<List<Category>> GetRootCategoriesAsync(CancellationToken ct = default);
    Task<List<Category>> GetChildCategoriesAsync(Guid parentId, CancellationToken ct = default);
    Task<Category?> GetWithChildrenAsync(Guid id, CancellationToken ct = default);
}