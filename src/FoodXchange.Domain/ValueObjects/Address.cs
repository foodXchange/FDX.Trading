namespace FoodXchange.Domain.ValueObjects;

public record Address
{
    public string Street { get; }
    public string City { get; }
    public string State { get; }
    public string Country { get; }
    public string PostalCode { get; }

    public Address(string street, string city, string state, string country, string postalCode)
    {
        if (string.IsNullOrWhiteSpace(city))
            throw new ArgumentException("City is required", nameof(city));
        
        if (string.IsNullOrWhiteSpace(country))
            throw new ArgumentException("Country is required", nameof(country));

        Street = street ?? string.Empty;
        City = city;
        State = state ?? string.Empty;
        Country = country;
        PostalCode = postalCode ?? string.Empty;
    }

    public static Address Empty => new(string.Empty, "Unknown", string.Empty, "Unknown", string.Empty);

    public override string ToString()
    {
        var parts = new List<string>();
        
        if (!string.IsNullOrWhiteSpace(Street))
            parts.Add(Street);
        
        parts.Add(City);
        
        if (!string.IsNullOrWhiteSpace(State))
            parts.Add(State);
        
        parts.Add(Country);
        
        if (!string.IsNullOrWhiteSpace(PostalCode))
            parts.Add(PostalCode);
        
        return string.Join(", ", parts);
    }
}