namespace FoodXchange.Domain.Abstractions;

public abstract class Entity<TKey> where TKey : notnull
{
    public TKey Id { get; protected set; } = default!;
    public DateTimeOffset CreatedAt { get; private set; } = DateTimeOffset.UtcNow;
    public string? CreatedBy { get; private set; }
    public DateTimeOffset? ModifiedAt { get; private set; }
    public string? ModifiedBy { get; private set; }
    public bool IsDeleted { get; private set; }
    public DateTimeOffset? DeletedAt { get; private set; }
    public string? DeletedBy { get; private set; }

    // Domain events (for future CQRS/Event Sourcing)
    private readonly List<IDomainEvent> _domainEvents = new();
    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    public void MarkCreated(string? by = null)
    {
        CreatedBy = by;
        CreatedAt = DateTimeOffset.UtcNow;
    }

    public void MarkModified(string? by = null)
    {
        ModifiedAt = DateTimeOffset.UtcNow;
        ModifiedBy = by;
    }

    public void SoftDelete(string? by = null)
    {
        IsDeleted = true;
        DeletedAt = DateTimeOffset.UtcNow;
        DeletedBy = by;
        MarkModified(by);
    }

    public void Restore(string? by = null)
    {
        IsDeleted = false;
        DeletedAt = null;
        DeletedBy = null;
        MarkModified(by);
    }
    
    protected void SetCreationDetails(string? createdBy = null)
    {
        MarkCreated(createdBy);
    }
    
    protected void SetModificationDetails(string? modifiedBy = null)
    {
        MarkModified(modifiedBy);
    }

    protected void AddDomainEvent(IDomainEvent domainEvent)
    {
        _domainEvents.Add(domainEvent);
    }

    public void ClearDomainEvents()
    {
        _domainEvents.Clear();
    }

    public override bool Equals(object? obj)
    {
        if (obj is not Entity<TKey> other)
            return false;

        if (ReferenceEquals(this, other))
            return true;

        if (GetType() != other.GetType())
            return false;

        return Id.Equals(other.Id);
    }

    public override int GetHashCode() => Id.GetHashCode();

    public static bool operator ==(Entity<TKey>? left, Entity<TKey>? right) =>
        left?.Equals(right) ?? right is null;

    public static bool operator !=(Entity<TKey>? left, Entity<TKey>? right) =>
        !(left == right);
}

public interface IDomainEvent
{
    DateTimeOffset OccurredAt { get; }
}