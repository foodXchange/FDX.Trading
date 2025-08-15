using FoodXchange.Domain.Abstractions;
using FoodXchange.Domain.Common;

namespace FoodXchange.Domain.Suppliers;

public class Supplier : Entity<Guid>, IAggregateRoot
{
    private readonly List<SupplierContact> _contacts = new();
    private readonly List<SupplierProduct> _products = new();
    private readonly List<SupplierDocument> _documents = new();
    
    protected Supplier() { }
    
    public Supplier(
        string name,
        string code,
        Email contactEmail,
        PhoneNumber? contactPhone = null,
        string? createdBy = null)
    {
        Id = Guid.NewGuid();
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Code = code ?? throw new ArgumentNullException(nameof(code));
        ContactEmail = contactEmail ?? throw new ArgumentNullException(nameof(contactEmail));
        ContactPhone = contactPhone;
        Status = SupplierStatus.Active;
        SetCreationDetails(createdBy);
    }
    
    public string Name { get; private set; } = default!;
    public string Code { get; private set; } = default!;
    public string? Description { get; private set; }
    public string? Website { get; private set; }
    public Email ContactEmail { get; private set; } = default!;
    public PhoneNumber? ContactPhone { get; private set; }
    public Address? PrimaryAddress { get; private set; }
    public string? TaxId { get; private set; }
    public string? LogoUrl { get; private set; }
    public SupplierStatus Status { get; private set; }
    public decimal? Rating { get; private set; }
    public DateTimeOffset? ApprovedAt { get; private set; }
    public string? ApprovedBy { get; private set; }
    
    public IReadOnlyCollection<SupplierContact> Contacts => _contacts.AsReadOnly();
    public IReadOnlyCollection<SupplierProduct> Products => _products.AsReadOnly();
    public IReadOnlyCollection<SupplierDocument> Documents => _documents.AsReadOnly();
    
    public void UpdateDetails(string name, string? description, string? modifiedBy = null)
    {
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Description = description;
        SetModificationDetails(modifiedBy);
    }
    
    public void UpdateContactInfo(Email email, PhoneNumber? phone, string? modifiedBy = null)
    {
        ContactEmail = email ?? throw new ArgumentNullException(nameof(email));
        ContactPhone = phone;
        SetModificationDetails(modifiedBy);
    }
    
    public void SetPrimaryAddress(Address address, string? modifiedBy = null)
    {
        PrimaryAddress = address ?? throw new ArgumentNullException(nameof(address));
        SetModificationDetails(modifiedBy);
    }
    
    public void SetWebsite(string? website, string? modifiedBy = null)
    {
        Website = website;
        SetModificationDetails(modifiedBy);
    }
    
    public void SetTaxId(string? taxId, string? modifiedBy = null)
    {
        TaxId = taxId;
        SetModificationDetails(modifiedBy);
    }
    
    public void SetLogo(string? logoUrl, string? modifiedBy = null)
    {
        LogoUrl = logoUrl;
        SetModificationDetails(modifiedBy);
    }
    
    public void UpdateRating(decimal rating, string? modifiedBy = null)
    {
        if (rating < 0 || rating > 5)
            throw new ArgumentException("Rating must be between 0 and 5", nameof(rating));
        
        Rating = rating;
        SetModificationDetails(modifiedBy);
    }
    
    public void Approve(string approvedBy)
    {
        if (Status != SupplierStatus.Pending)
            throw new InvalidOperationException("Only pending suppliers can be approved");
        
        Status = SupplierStatus.Active;
        ApprovedAt = DateTimeOffset.UtcNow;
        ApprovedBy = approvedBy;
        SetModificationDetails(approvedBy);
    }
    
    public void Suspend(string? modifiedBy = null)
    {
        Status = SupplierStatus.Suspended;
        SetModificationDetails(modifiedBy);
    }
    
    public void Reactivate(string? modifiedBy = null)
    {
        if (Status == SupplierStatus.Suspended)
        {
            Status = SupplierStatus.Active;
            SetModificationDetails(modifiedBy);
        }
    }
    
    public void AddContact(
        string firstName,
        string lastName,
        Email email,
        PhoneNumber? phone = null,
        string? title = null,
        bool isPrimary = false,
        string? modifiedBy = null)
    {
        if (isPrimary)
        {
            foreach (var contact in _contacts)
                contact.SetPrimary(false);
        }
        
        _contacts.Add(new SupplierContact(
            Id, firstName, lastName, email, phone, title, isPrimary));
        SetModificationDetails(modifiedBy);
    }
    
    public void RemoveContact(Guid contactId, string? modifiedBy = null)
    {
        _contacts.RemoveAll(c => c.Id == contactId);
        SetModificationDetails(modifiedBy);
    }
    
    public void AddProduct(Guid productId, string? supplierSku = null, Money? price = null, string? modifiedBy = null)
    {
        if (_products.Any(p => p.ProductId == productId))
            return;
        
        _products.Add(new SupplierProduct(Id, productId, supplierSku, price));
        SetModificationDetails(modifiedBy);
    }
    
    public void RemoveProduct(Guid productId, string? modifiedBy = null)
    {
        _products.RemoveAll(p => p.ProductId == productId);
        SetModificationDetails(modifiedBy);
    }
    
    public void AddDocument(
        string name,
        string url,
        DocumentType type,
        string? description = null,
        string? modifiedBy = null)
    {
        _documents.Add(new SupplierDocument(Id, name, url, type, description));
        SetModificationDetails(modifiedBy);
    }
    
    public void RemoveDocument(Guid documentId, string? modifiedBy = null)
    {
        _documents.RemoveAll(d => d.Id == documentId);
        SetModificationDetails(modifiedBy);
    }
}

public class SupplierContact : Entity<Guid>
{
    protected SupplierContact() { }
    
    public SupplierContact(
        Guid supplierId,
        string firstName,
        string lastName,
        Email email,
        PhoneNumber? phone = null,
        string? title = null,
        bool isPrimary = false)
    {
        Id = Guid.NewGuid();
        SupplierId = supplierId;
        FirstName = firstName ?? throw new ArgumentNullException(nameof(firstName));
        LastName = lastName ?? throw new ArgumentNullException(nameof(lastName));
        Email = email ?? throw new ArgumentNullException(nameof(email));
        Phone = phone;
        Title = title;
        IsPrimary = isPrimary;
    }
    
    public Guid SupplierId { get; private set; }
    public string FirstName { get; private set; } = default!;
    public string LastName { get; private set; } = default!;
    public Email Email { get; private set; } = default!;
    public PhoneNumber? Phone { get; private set; }
    public string? Title { get; private set; }
    public bool IsPrimary { get; private set; }
    
    public string FullName => $"{FirstName} {LastName}";
    
    public void SetPrimary(bool isPrimary)
    {
        IsPrimary = isPrimary;
    }
}

public class SupplierProduct : Entity<Guid>
{
    protected SupplierProduct() { }
    
    public SupplierProduct(
        Guid supplierId,
        Guid productId,
        string? supplierSku = null,
        Money? price = null)
    {
        Id = Guid.NewGuid();
        SupplierId = supplierId;
        ProductId = productId;
        SupplierSku = supplierSku;
        Price = price;
    }
    
    public Guid SupplierId { get; private set; }
    public Guid ProductId { get; private set; }
    public string? SupplierSku { get; private set; }
    public Money? Price { get; private set; }
    public int? LeadTimeDays { get; private set; }
    public int? MinOrderQuantity { get; private set; }
    
    public void UpdatePrice(Money? price)
    {
        Price = price;
    }
    
    public void SetLeadTime(int days)
    {
        if (days < 0)
            throw new ArgumentException("Lead time cannot be negative", nameof(days));
        LeadTimeDays = days;
    }
    
    public void SetMinOrderQuantity(int quantity)
    {
        if (quantity < 1)
            throw new ArgumentException("Minimum order quantity must be at least 1", nameof(quantity));
        MinOrderQuantity = quantity;
    }
}

public class SupplierDocument : Entity<Guid>
{
    protected SupplierDocument() { }
    
    public SupplierDocument(
        Guid supplierId,
        string name,
        string url,
        DocumentType type,
        string? description = null)
    {
        Id = Guid.NewGuid();
        SupplierId = supplierId;
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Url = url ?? throw new ArgumentNullException(nameof(url));
        Type = type;
        Description = description;
        UploadedAt = DateTimeOffset.UtcNow;
    }
    
    public Guid SupplierId { get; private set; }
    public string Name { get; private set; } = default!;
    public string Url { get; private set; } = default!;
    public DocumentType Type { get; private set; }
    public string? Description { get; private set; }
    public DateTimeOffset UploadedAt { get; private set; }
}

public enum SupplierStatus
{
    Pending,
    Active,
    Suspended,
    Inactive
}

public enum DocumentType
{
    Certificate,
    License,
    Insurance,
    Contract,
    PriceList,
    Catalog,
    Other
}