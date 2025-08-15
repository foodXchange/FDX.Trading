using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using FoodXchange.Domain.Products;

namespace FoodXchange.Infrastructure.Data.Configurations;

public class CategoryConfiguration : IEntityTypeConfiguration<Category>
{
    public void Configure(EntityTypeBuilder<Category> builder)
    {
        builder.ToTable("Categories");
        
        builder.HasKey(c => c.Id);
        
        builder.Property(c => c.Name)
            .HasMaxLength(100)
            .IsRequired();
        
        builder.Property(c => c.Description)
            .HasMaxLength(500);
        
        builder.Property(c => c.ImageUrl)
            .HasMaxLength(500);
        
        builder.HasOne(c => c.Parent)
            .WithMany(c => c.Children)
            .HasForeignKey(c => c.ParentId)
            .OnDelete(DeleteBehavior.Restrict);
        
        builder.HasIndex(c => c.Name);
        builder.HasIndex(c => c.ParentId);
        
        builder.HasQueryFilter(c => !c.IsDeleted);
    }
}