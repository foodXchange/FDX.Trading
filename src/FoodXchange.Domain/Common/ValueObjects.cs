using System.Text.RegularExpressions;
using FoodXchange.Domain.Abstractions;

namespace FoodXchange.Domain.Common;

public sealed class Money(decimal amount, string currency = "USD") : ValueObject
{
    public decimal Amount { get; } = Math.Round(amount, 2);
    public string Currency { get; } = currency.ToUpperInvariant();
    
    public static Money Zero => new(0);
    
    public static Money operator +(Money left, Money right)
    {
        if (left.Currency != right.Currency)
            throw new InvalidOperationException($"Cannot add different currencies: {left.Currency} and {right.Currency}");
        return new Money(left.Amount + right.Amount, left.Currency);
    }
    
    public static Money operator -(Money left, Money right)
    {
        if (left.Currency != right.Currency)
            throw new InvalidOperationException($"Cannot subtract different currencies: {left.Currency} and {right.Currency}");
        return new Money(left.Amount - right.Amount, left.Currency);
    }
    
    public static Money operator *(Money money, decimal multiplier) =>
        new(money.Amount * multiplier, money.Currency);
    
    protected override IEnumerable<object?> GetEqualityComponents()
    {
        yield return Amount;
        yield return Currency;
    }
    
    public override string ToString() => $"{Currency} {Amount:F2}";
}

public sealed class Email : ValueObject
{
    private static readonly Regex EmailRegex = new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", 
        RegexOptions.Compiled | RegexOptions.IgnoreCase);
    
    public string Value { get; }
    
    private Email(string value) => Value = value.Trim().ToLowerInvariant();
    
    public static Email Create(string value)
    {
        if (string.IsNullOrWhiteSpace(value) || !EmailRegex.IsMatch(value))
            throw new ArgumentException($"Invalid email: {value}");
        return new Email(value);
    }
    
    protected override IEnumerable<object?> GetEqualityComponents()
    {
        yield return Value;
    }
    
    public static implicit operator string(Email email) => email.Value;
    public override string ToString() => Value;
}

public sealed class Address(string line1, string city, string country, string? zip = null) : ValueObject
{
    public string Line1 { get; } = line1 ?? throw new ArgumentNullException(nameof(line1));
    public string City { get; } = city ?? throw new ArgumentNullException(nameof(city));
    public string Country { get; } = country ?? throw new ArgumentNullException(nameof(country));
    public string? Zip { get; } = zip;
    
    protected override IEnumerable<object?> GetEqualityComponents()
    {
        yield return Line1;
        yield return City;
        yield return Country;
        yield return Zip;
    }
    
    public override string ToString()
    {
        var parts = new List<string> { Line1, City, Country };
        if (!string.IsNullOrWhiteSpace(Zip))
            parts.Add(Zip);
        return string.Join(", ", parts);
    }
}

public sealed class PhoneNumber : ValueObject
{
    private static readonly Regex PhoneRegex = new(@"^\+?[1-9]\d{1,14}$", 
        RegexOptions.Compiled);
    
    public string Value { get; }
    
    private PhoneNumber(string value) => Value = value;
    
    public static PhoneNumber Create(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException("Phone number is required");
        
        var cleaned = value.Replace(" ", "")
                          .Replace("-", "")
                          .Replace("(", "")
                          .Replace(")", "")
                          .Replace(".", "");
        
        if (!PhoneRegex.IsMatch(cleaned))
            throw new ArgumentException($"Invalid phone number: {value}");
        
        return new PhoneNumber(cleaned);
    }
    
    protected override IEnumerable<object?> GetEqualityComponents()
    {
        yield return Value;
    }
    
    public static implicit operator string(PhoneNumber phone) => phone.Value;
    public override string ToString() => Value;
}