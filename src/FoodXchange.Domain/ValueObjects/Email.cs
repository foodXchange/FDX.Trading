using System.Text.RegularExpressions;

namespace FoodXchange.Domain.ValueObjects;

public record Email
{
    private static readonly Regex EmailRegex = new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", 
        RegexOptions.Compiled | RegexOptions.IgnoreCase);

    public string Value { get; }

    public Email(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException("Email address is required", nameof(value));
        
        if (!EmailRegex.IsMatch(value))
            throw new ArgumentException($"Invalid email address: {value}", nameof(value));
        
        Value = value.ToLowerInvariant();
    }

    public static implicit operator string(Email email) => email.Value;
    public override string ToString() => Value;
}