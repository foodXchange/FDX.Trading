using FoodXchange.Domain.ValueObjects;

namespace FoodXchange.Domain.Entities;

public class Supplier : BaseEntity
{
    public string CompanyName { get; private set; }
    public string ContactName { get; private set; }
    public Email Email { get; private set; }
    public PhoneNumber? Phone { get; private set; }
    public Address Address { get; private set; }
    public string? Website { get; private set; }
    public string? LogoUrl { get; private set; }
    public bool IsActive { get; private set; }
    public SupplierStatus Status { get; private set; }
    
    // Navigation properties
    private readonly List<Product> _products = new();
    public virtual IReadOnlyCollection<Product> Products => _products.AsReadOnly();

    protected Supplier() 
    { 
        CompanyName = string.Empty;
        ContactName = string.Empty;
        Email = new Email("placeholder@example.com");
        Address = Address.Empty;
    }

    public Supplier(string companyName, string contactName, Email email, Address address, PhoneNumber? phone = null)
    {
        if (string.IsNullOrWhiteSpace(companyName))
            throw new ArgumentException("Company name is required", nameof(companyName));
        
        if (string.IsNullOrWhiteSpace(contactName))
            throw new ArgumentException("Contact name is required", nameof(contactName));

        CompanyName = companyName;
        ContactName = contactName;
        Email = email ?? throw new ArgumentNullException(nameof(email));
        Address = address ?? throw new ArgumentNullException(nameof(address));
        Phone = phone;
        IsActive = true;
        Status = SupplierStatus.Pending;
    }

    public void UpdateContactInfo(string contactName, Email email, PhoneNumber? phone)
    {
        if (string.IsNullOrWhiteSpace(contactName))
            throw new ArgumentException("Contact name is required", nameof(contactName));

        ContactName = contactName;
        Email = email ?? throw new ArgumentNullException(nameof(email));
        Phone = phone;
        SetUpdated();
    }

    public void UpdateAddress(Address address)
    {
        Address = address ?? throw new ArgumentNullException(nameof(address));
        SetUpdated();
    }

    public void Approve()
    {
        Status = SupplierStatus.Approved;
        IsActive = true;
        SetUpdated();
    }

    public void Reject(string reason)
    {
        Status = SupplierStatus.Rejected;
        IsActive = false;
        SetUpdated();
    }

    public void Suspend()
    {
        Status = SupplierStatus.Suspended;
        IsActive = false;
        SetUpdated();
    }

    public void Reactivate()
    {
        if (Status == SupplierStatus.Rejected)
            throw new InvalidOperationException("Cannot reactivate a rejected supplier");
        
        Status = SupplierStatus.Approved;
        IsActive = true;
        SetUpdated();
    }
}

public enum SupplierStatus
{
    Pending,
    Approved,
    Rejected,
    Suspended
}