namespace FoodXchange.Domain.Entities;

public class Category : BaseEntity
{
    public string Name { get; private set; }
    public string? Description { get; private set; }
    public string? IconClass { get; private set; }
    public int DisplayOrder { get; private set; }
    public bool IsActive { get; private set; }
    
    // Navigation properties
    private readonly List<Product> _products = new();
    public virtual IReadOnlyCollection<Product> Products => _products.AsReadOnly();

    protected Category() 
    { 
        Name = string.Empty;
    }

    public Category(string name, string? description = null, int displayOrder = 0)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Category name is required", nameof(name));

        Name = name;
        Description = description;
        DisplayOrder = displayOrder;
        IsActive = true;
    }

    public void UpdateDetails(string name, string? description, int displayOrder)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Category name is required", nameof(name));

        Name = name;
        Description = description;
        DisplayOrder = displayOrder;
        SetUpdated();
    }

    public void SetIcon(string iconClass)
    {
        IconClass = iconClass;
        SetUpdated();
    }

    public void Activate()
    {
        IsActive = true;
        SetUpdated();
    }

    public void Deactivate()
    {
        if (_products.Any(p => p.IsActive))
            throw new InvalidOperationException("Cannot deactivate category with active products");
        
        IsActive = false;
        SetUpdated();
    }
}