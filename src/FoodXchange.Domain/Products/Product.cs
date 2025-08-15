using FoodXchange.Domain.Abstractions;
using FoodXchange.Domain.Common;

namespace FoodXchange.Domain.Products;

public class Product : Entity<Guid>, IAggregateRoot
{
    private readonly List<ProductCategory> _categories = new();
    private readonly List<ProductImage> _images = new();
    private readonly List<ProductPrice> _prices = new();

    protected Product() { }

    public Product(
        string sku,
        string name,
        string description,
        string brand,
        Money price,
        string? createdBy = null)
    {
        Id = Guid.NewGuid();
        Sku = sku ?? throw new ArgumentNullException(nameof(sku));
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Description = description ?? throw new ArgumentNullException(nameof(description));
        Brand = brand ?? throw new ArgumentNullException(nameof(brand));
        
        if (price == null || price.Amount < 0)
            throw new ArgumentException("Price must be non-negative", nameof(price));
        
        SetBasePrice(price, createdBy);
        SetCreationDetails(createdBy);
    }

    public string Sku { get; private set; } = default!;
    public string Name { get; private set; } = default!;
    public string Description { get; private set; } = default!;
    public string Brand { get; private set; } = default!;
    public string? Barcode { get; private set; }
    public decimal Weight { get; private set; }
    public string? WeightUnit { get; private set; }
    public string? PackSize { get; private set; }
    public int MinOrderQuantity { get; private set; } = 1;
    public bool IsActive { get; private set; } = true;
    
    public IReadOnlyCollection<ProductCategory> Categories => _categories.AsReadOnly();
    public IReadOnlyCollection<ProductImage> Images => _images.AsReadOnly();
    public IReadOnlyCollection<ProductPrice> Prices => _prices.AsReadOnly();

    public void UpdateDetails(string name, string description, string? modifiedBy = null)
    {
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Description = description ?? throw new ArgumentNullException(nameof(description));
        SetModificationDetails(modifiedBy);
    }

    public void UpdateBrand(string brand, string? modifiedBy = null)
    {
        Brand = brand ?? throw new ArgumentNullException(nameof(brand));
        SetModificationDetails(modifiedBy);
    }

    public void SetBarcode(string barcode, string? modifiedBy = null)
    {
        Barcode = barcode;
        SetModificationDetails(modifiedBy);
    }

    public void SetWeight(decimal weight, string unit, string? modifiedBy = null)
    {
        if (weight < 0) throw new ArgumentException("Weight must be non-negative", nameof(weight));
        Weight = weight;
        WeightUnit = unit;
        SetModificationDetails(modifiedBy);
    }

    public void SetPackSize(string packSize, string? modifiedBy = null)
    {
        PackSize = packSize;
        SetModificationDetails(modifiedBy);
    }

    public void SetMinOrderQuantity(int quantity, string? modifiedBy = null)
    {
        if (quantity < 1) throw new ArgumentException("Minimum order quantity must be at least 1", nameof(quantity));
        MinOrderQuantity = quantity;
        SetModificationDetails(modifiedBy);
    }

    public void Activate(string? modifiedBy = null)
    {
        IsActive = true;
        SetModificationDetails(modifiedBy);
    }

    public void Deactivate(string? modifiedBy = null)
    {
        IsActive = false;
        SetModificationDetails(modifiedBy);
    }

    public void AddCategory(Guid categoryId, string? modifiedBy = null)
    {
        if (_categories.Any(c => c.CategoryId == categoryId))
            return;
        
        _categories.Add(new ProductCategory(Id, categoryId));
        SetModificationDetails(modifiedBy);
    }

    public void RemoveCategory(Guid categoryId, string? modifiedBy = null)
    {
        _categories.RemoveAll(c => c.CategoryId == categoryId);
        SetModificationDetails(modifiedBy);
    }

    public void AddImage(string url, string? caption = null, bool isPrimary = false, string? modifiedBy = null)
    {
        if (isPrimary)
        {
            foreach (var img in _images)
                img.SetPrimary(false);
        }
        
        _images.Add(new ProductImage(Id, url, caption, isPrimary));
        SetModificationDetails(modifiedBy);
    }

    public void RemoveImage(Guid imageId, string? modifiedBy = null)
    {
        _images.RemoveAll(i => i.Id == imageId);
        SetModificationDetails(modifiedBy);
    }

    public void SetBasePrice(Money price, string? modifiedBy = null)
    {
        if (price == null || price.Amount < 0)
            throw new ArgumentException("Price must be non-negative", nameof(price));
        
        var existingBase = _prices.FirstOrDefault(p => p.PriceType == PriceType.Base);
        if (existingBase != null)
        {
            existingBase.UpdatePrice(price);
        }
        else
        {
            _prices.Add(new ProductPrice(Id, price, PriceType.Base));
        }
        
        SetModificationDetails(modifiedBy);
    }

    public void AddTierPrice(Money price, int minQuantity, string? modifiedBy = null)
    {
        if (price == null || price.Amount < 0)
            throw new ArgumentException("Price must be non-negative", nameof(price));
        if (minQuantity < 1)
            throw new ArgumentException("Minimum quantity must be at least 1", nameof(minQuantity));
        
        _prices.Add(new ProductPrice(Id, price, PriceType.Tiered, minQuantity));
        SetModificationDetails(modifiedBy);
    }

    public Money? GetPrice(int quantity = 1)
    {
        var tierPrices = _prices
            .Where(p => p.PriceType == PriceType.Tiered && p.MinQuantity <= quantity)
            .OrderByDescending(p => p.MinQuantity);
        
        var tierPrice = tierPrices.FirstOrDefault();
        if (tierPrice != null)
            return tierPrice.Price;
        
        var basePrice = _prices.FirstOrDefault(p => p.PriceType == PriceType.Base);
        return basePrice?.Price;
    }
}

public class ProductCategory : Entity<Guid>
{
    protected ProductCategory() { }
    
    public ProductCategory(Guid productId, Guid categoryId)
    {
        Id = Guid.NewGuid();
        ProductId = productId;
        CategoryId = categoryId;
    }
    
    public Guid ProductId { get; private set; }
    public Guid CategoryId { get; private set; }
}

public class ProductImage : Entity<Guid>
{
    protected ProductImage() { }
    
    public ProductImage(Guid productId, string url, string? caption = null, bool isPrimary = false)
    {
        Id = Guid.NewGuid();
        ProductId = productId;
        Url = url ?? throw new ArgumentNullException(nameof(url));
        Caption = caption;
        IsPrimary = isPrimary;
    }
    
    public Guid ProductId { get; private set; }
    public string Url { get; private set; } = default!;
    public string? Caption { get; private set; }
    public bool IsPrimary { get; private set; }
    
    public void SetPrimary(bool isPrimary)
    {
        IsPrimary = isPrimary;
    }
}

public class ProductPrice : Entity<Guid>
{
    protected ProductPrice() { }
    
    public ProductPrice(Guid productId, Money price, PriceType priceType, int minQuantity = 1)
    {
        Id = Guid.NewGuid();
        ProductId = productId;
        Price = price ?? throw new ArgumentNullException(nameof(price));
        PriceType = priceType;
        MinQuantity = minQuantity;
    }
    
    public Guid ProductId { get; private set; }
    public Money Price { get; private set; } = default!;
    public PriceType PriceType { get; private set; }
    public int MinQuantity { get; private set; }
    
    public void UpdatePrice(Money price)
    {
        Price = price ?? throw new ArgumentNullException(nameof(price));
    }
}

public enum PriceType
{
    Base,
    Tiered,
    Promotional
}