using System.Text.RegularExpressions;

namespace FoodXchange.Domain.ValueObjects;

public record PhoneNumber
{
    private static readonly Regex PhoneRegex = new(@"^\+?[1-9]\d{1,14}$", 
        RegexOptions.Compiled);

    public string Value { get; }

    public PhoneNumber(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException("Phone number is required", nameof(value));
        
        // Remove common formatting characters
        var cleaned = value.Replace(" ", "")
                          .Replace("-", "")
                          .Replace("(", "")
                          .Replace(")", "")
                          .Replace(".", "");
        
        if (!PhoneRegex.IsMatch(cleaned))
            throw new ArgumentException($"Invalid phone number: {value}", nameof(value));
        
        Value = cleaned;
    }

    public static implicit operator string(PhoneNumber phone) => phone.Value;
    public override string ToString() => Value;
}