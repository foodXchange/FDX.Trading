using FoodXchange.Domain.ValueObjects;

namespace FoodXchange.Domain.Entities;

public class Product : BaseEntity
{
    public string Name { get; private set; }
    public string SKU { get; private set; }
    public string? Description { get; private set; }
    public Money Price { get; private set; }
    public int StockQuantity { get; private set; }
    public Guid CategoryId { get; private set; }
    public Guid SupplierId { get; private set; }
    public string? ImageUrl { get; private set; }
    public bool IsActive { get; private set; }
    
    // Navigation properties
    public virtual Category? Category { get; private set; }
    public virtual Supplier? Supplier { get; private set; }

    protected Product() 
    { 
        Name = string.Empty;
        SKU = string.Empty;
        Price = Money.Zero;
    }

    public Product(string name, string sku, Money price, Guid categoryId, Guid supplierId, string? description = null)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Product name is required", nameof(name));
        
        if (string.IsNullOrWhiteSpace(sku))
            throw new ArgumentException("Product SKU is required", nameof(sku));
        
        if (price.Amount < 0)
            throw new ArgumentException("Product price cannot be negative", nameof(price));

        Name = name;
        SKU = sku;
        Price = price;
        CategoryId = categoryId;
        SupplierId = supplierId;
        Description = description;
        StockQuantity = 0;
        IsActive = true;
    }

    public void UpdateDetails(string name, string? description, Money price)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Product name is required", nameof(name));
        
        if (price.Amount < 0)
            throw new ArgumentException("Product price cannot be negative", nameof(price));

        Name = name;
        Description = description;
        Price = price;
        SetUpdated();
    }

    public void UpdateStock(int quantity)
    {
        if (quantity < 0)
            throw new ArgumentException("Stock quantity cannot be negative", nameof(quantity));
        
        StockQuantity = quantity;
        SetUpdated();
    }

    public void AdjustStock(int adjustment)
    {
        var newQuantity = StockQuantity + adjustment;
        if (newQuantity < 0)
            throw new InvalidOperationException($"Insufficient stock. Current: {StockQuantity}, Requested adjustment: {adjustment}");
        
        StockQuantity = newQuantity;
        SetUpdated();
    }

    public void Activate() 
    { 
        IsActive = true; 
        SetUpdated();
    }
    
    public void Deactivate() 
    { 
        IsActive = false; 
        SetUpdated();
    }
}