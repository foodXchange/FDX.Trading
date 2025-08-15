using System.Linq.Expressions;
using Microsoft.EntityFrameworkCore;
using FoodXchange.Domain.Abstractions;
using FoodXchange.Domain.Products;
using FoodXchange.Domain.Suppliers;

namespace FoodXchange.Infrastructure.Data;

public sealed class AppDbContext : DbContext
{
    private readonly string _currentUser;
    
    public DbSet<Product> Products => Set<Product>();
    public DbSet<Category> Categories => Set<Category>();
    public DbSet<Supplier> Suppliers => Set<Supplier>();
    public DbSet<ProductCategory> ProductCategories => Set<ProductCategory>();
    public DbSet<ProductImage> ProductImages => Set<ProductImage>();
    public DbSet<ProductPrice> ProductPrices => Set<ProductPrice>();
    public DbSet<SupplierContact> SupplierContacts => Set<SupplierContact>();
    public DbSet<SupplierProduct> SupplierProducts => Set<SupplierProduct>();
    public DbSet<SupplierDocument> SupplierDocuments => Set<SupplierDocument>();
    
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
        _currentUser = "system"; // TODO: Get from IHttpContextAccessor or similar
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Apply configurations from assembly
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
        
        // Global soft-delete filter for all entities
        foreach (var entityType in modelBuilder.Model.GetEntityTypes())
        {
            if (entityType.ClrType.IsSubclassOfRawGeneric(typeof(Entity<>)))
            {
                var method = typeof(AppDbContext)
                    .GetMethod(nameof(ConfigureSoftDeleteFilter), 
                        System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)?
                    .MakeGenericMethod(entityType.ClrType);
                
                method?.Invoke(null, new object[] { modelBuilder });
            }
        }
        
        base.OnModelCreating(modelBuilder);
    }

    private static void ConfigureSoftDeleteFilter<T>(ModelBuilder modelBuilder) where T : Entity<Guid>
    {
        modelBuilder.Entity<T>().HasQueryFilter(e => !e.IsDeleted);
    }

    public override async Task<int> SaveChangesAsync(CancellationToken ct = default)
    {
        HandleAuditableEntities();
        HandleDomainEvents();
        return await base.SaveChangesAsync(ct);
    }

    private void HandleAuditableEntities()
    {
        var entries = ChangeTracker.Entries()
            .Where(e => e.Entity is Entity<Guid> && 
                       (e.State == EntityState.Added || e.State == EntityState.Modified));

        foreach (var entry in entries)
        {
            var entity = (Entity<Guid>)entry.Entity;
            
            if (entry.State == EntityState.Added)
            {
                entity.MarkCreated(_currentUser);
            }
            else if (entry.State == EntityState.Modified)
            {
                entity.MarkModified(_currentUser);
            }
        }
    }

    private void HandleDomainEvents()
    {
        var entities = ChangeTracker.Entries<Entity<Guid>>()
            .Where(e => e.Entity.DomainEvents.Any())
            .Select(e => e.Entity)
            .ToList();

        // TODO: Dispatch domain events via MediatR or similar
        foreach (var entity in entities)
        {
            entity.ClearDomainEvents();
        }
    }
}

internal static class TypeExtensions
{
    internal static bool IsSubclassOfRawGeneric(this Type toCheck, Type generic)
    {
        while (toCheck != null && toCheck != typeof(object))
        {
            var cur = toCheck.IsGenericType ? toCheck.GetGenericTypeDefinition() : toCheck;
            if (generic == cur)
                return true;
            toCheck = toCheck.BaseType!;
        }
        return false;
    }
}