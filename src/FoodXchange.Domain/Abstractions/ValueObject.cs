namespace FoodXchange.Domain.Abstractions;

public abstract class ValueObject
{
    protected abstract IEnumerable<object?> GetEqualityComponents();
    
    public override bool Equals(object? obj) =>
        obj is ValueObject other && 
        GetEqualityComponents().SequenceEqual(other.GetEqualityComponents());
    
    public override int GetHashCode() =>
        GetEqualityComponents()
            .Aggregate(0, (current, obj) => HashCode.Combine(current, obj));
    
    public static bool operator ==(ValueObject? left, ValueObject? right) =>
        left?.Equals(right) ?? right is null;
    
    public static bool operator !=(ValueObject? left, ValueObject? right) =>
        !(left == right);
}