using FoodXchange.Domain.Abstractions;

namespace FoodXchange.Domain.Products;

public class Category : Entity<Guid>
{
    private readonly List<Category> _children = new();
    
    protected Category() { }
    
    public Category(string name, string? description = null, Guid? parentId = null, string? createdBy = null)
    {
        Id = Guid.NewGuid();
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Description = description;
        ParentId = parentId;
        SetCreationDetails(createdBy);
    }
    
    public string Name { get; private set; } = default!;
    public string? Description { get; private set; }
    public Guid? ParentId { get; private set; }
    public string? ImageUrl { get; private set; }
    public int DisplayOrder { get; private set; }
    public bool IsActive { get; private set; } = true;
    
    public Category? Parent { get; private set; }
    public IReadOnlyCollection<Category> Children => _children.AsReadOnly();
    
    public void UpdateDetails(string name, string? description, string? modifiedBy = null)
    {
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Description = description;
        SetModificationDetails(modifiedBy);
    }
    
    public void SetParent(Guid? parentId, string? modifiedBy = null)
    {
        if (parentId == Id)
            throw new InvalidOperationException("Category cannot be its own parent");
        
        ParentId = parentId;
        SetModificationDetails(modifiedBy);
    }
    
    public void SetImage(string? imageUrl, string? modifiedBy = null)
    {
        ImageUrl = imageUrl;
        SetModificationDetails(modifiedBy);
    }
    
    public void SetDisplayOrder(int order, string? modifiedBy = null)
    {
        DisplayOrder = order;
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
    
    public string GetFullPath(string separator = " > ")
    {
        var path = new List<string> { Name };
        var current = Parent;
        
        while (current != null)
        {
            path.Insert(0, current.Name);
            current = current.Parent;
        }
        
        return string.Join(separator, path);
    }
}