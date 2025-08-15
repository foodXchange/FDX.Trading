using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using FoodXchange.Domain.Products;
using FoodXchange.Domain.Common;

namespace FoodXchange.Infrastructure.Data.Configurations;

public class ProductConfiguration : IEntityTypeConfiguration<Product>
{
    public void Configure(EntityTypeBuilder<Product> builder)
    {
        builder.ToTable("Products");
        
        builder.HasKey(p => p.Id);
        
        builder.Property(p => p.Sku)
            .HasMaxLength(100)
            .IsRequired();
        
        builder.HasIndex(p => p.Sku)
            .IsUnique();
        
        builder.Property(p => p.Name)
            .HasMaxLength(200)
            .IsRequired();
        
        builder.Property(p => p.Description)
            .HasMaxLength(2000);
        
        builder.Property(p => p.Brand)
            .HasMaxLength(100)
            .IsRequired();
        
        builder.Property(p => p.Barcode)
            .HasMaxLength(50);
        
        builder.Property(p => p.WeightUnit)
            .HasMaxLength(20);
        
        builder.Property(p => p.PackSize)
            .HasMaxLength(50);
        
        builder.HasMany(p => p.Categories)
            .WithOne()
            .HasForeignKey(pc => pc.ProductId)
            .OnDelete(DeleteBehavior.Cascade);
        
        builder.HasMany(p => p.Images)
            .WithOne()
            .HasForeignKey(pi => pi.ProductId)
            .OnDelete(DeleteBehavior.Cascade);
        
        builder.HasMany(p => p.Prices)
            .WithOne()
            .HasForeignKey(pp => pp.ProductId)
            .OnDelete(DeleteBehavior.Cascade);
        
        builder.HasQueryFilter(p => !p.IsDeleted);
    }
}

public class ProductCategoryConfiguration : IEntityTypeConfiguration<ProductCategory>
{
    public void Configure(EntityTypeBuilder<ProductCategory> builder)
    {
        builder.ToTable("ProductCategories");
        
        builder.HasKey(pc => pc.Id);
        
        builder.HasIndex(pc => new { pc.ProductId, pc.CategoryId })
            .IsUnique();
        
        builder.HasQueryFilter(pc => !pc.IsDeleted);
    }
}

public class ProductImageConfiguration : IEntityTypeConfiguration<ProductImage>
{
    public void Configure(EntityTypeBuilder<ProductImage> builder)
    {
        builder.ToTable("ProductImages");
        
        builder.HasKey(pi => pi.Id);
        
        builder.Property(pi => pi.Url)
            .HasMaxLength(500)
            .IsRequired();
        
        builder.Property(pi => pi.Caption)
            .HasMaxLength(200);
        
        builder.HasQueryFilter(pi => !pi.IsDeleted);
    }
}

public class ProductPriceConfiguration : IEntityTypeConfiguration<ProductPrice>
{
    public void Configure(EntityTypeBuilder<ProductPrice> builder)
    {
        builder.ToTable("ProductPrices");
        
        builder.HasKey(pp => pp.Id);
        
        builder.OwnsOne(pp => pp.Price, money =>
        {
            money.Property(m => m.Currency)
                .HasMaxLength(3)
                .HasColumnName("Currency");
            
            money.Property(m => m.Amount)
                .HasPrecision(18, 2)
                .HasColumnName("Amount");
        });
        
        builder.Property(pp => pp.PriceType)
            .HasConversion<string>()
            .HasMaxLength(20);
        
        builder.HasQueryFilter(pp => !pp.IsDeleted);
    }
}