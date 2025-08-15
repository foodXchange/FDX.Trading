using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using FoodXchange.Domain.Suppliers;
using FoodXchange.Domain.Common;

namespace FoodXchange.Infrastructure.Data.Configurations;

public class SupplierConfiguration : IEntityTypeConfiguration<Supplier>
{
    public void Configure(EntityTypeBuilder<Supplier> builder)
    {
        builder.ToTable("Suppliers");
        
        builder.HasKey(s => s.Id);
        
        builder.Property(s => s.Name)
            .HasMaxLength(200)
            .IsRequired();
        
        builder.Property(s => s.Code)
            .HasMaxLength(50)
            .IsRequired();
        
        builder.HasIndex(s => s.Code)
            .IsUnique();
        
        builder.Property(s => s.Description)
            .HasMaxLength(2000);
        
        builder.Property(s => s.Website)
            .HasMaxLength(200);
        
        builder.OwnsOne(s => s.ContactEmail, email =>
        {
            email.Property(e => e.Value)
                .HasColumnName("ContactEmail")
                .HasMaxLength(200)
                .IsRequired();
        });
        
        builder.OwnsOne(s => s.ContactPhone, phone =>
        {
            phone.Property(p => p.Value)
                .HasColumnName("ContactPhone")
                .HasMaxLength(50);
        });
        
        builder.OwnsOne(s => s.PrimaryAddress, address =>
        {
            address.Property(a => a.Line1)
                .HasColumnName("AddressLine1")
                .HasMaxLength(200);
            
            address.Property(a => a.City)
                .HasColumnName("AddressCity")
                .HasMaxLength(100);
            
            address.Property(a => a.Country)
                .HasColumnName("AddressCountry")
                .HasMaxLength(100);
            
            address.Property(a => a.Zip)
                .HasColumnName("AddressZip")
                .HasMaxLength(20);
        });
        
        builder.Property(s => s.TaxId)
            .HasMaxLength(50);
        
        builder.Property(s => s.LogoUrl)
            .HasMaxLength(500);
        
        builder.Property(s => s.Status)
            .HasConversion<string>()
            .HasMaxLength(20);
        
        builder.Property(s => s.Rating)
            .HasPrecision(3, 2);
        
        builder.Property(s => s.ApprovedBy)
            .HasMaxLength(100);
        
        builder.HasMany(s => s.Contacts)
            .WithOne()
            .HasForeignKey(sc => sc.SupplierId)
            .OnDelete(DeleteBehavior.Cascade);
        
        builder.HasMany(s => s.Products)
            .WithOne()
            .HasForeignKey(sp => sp.SupplierId)
            .OnDelete(DeleteBehavior.Cascade);
        
        builder.HasMany(s => s.Documents)
            .WithOne()
            .HasForeignKey(sd => sd.SupplierId)
            .OnDelete(DeleteBehavior.Cascade);
        
        builder.HasQueryFilter(s => !s.IsDeleted);
    }
}

public class SupplierContactConfiguration : IEntityTypeConfiguration<SupplierContact>
{
    public void Configure(EntityTypeBuilder<SupplierContact> builder)
    {
        builder.ToTable("SupplierContacts");
        
        builder.HasKey(sc => sc.Id);
        
        builder.Property(sc => sc.FirstName)
            .HasMaxLength(100)
            .IsRequired();
        
        builder.Property(sc => sc.LastName)
            .HasMaxLength(100)
            .IsRequired();
        
        builder.OwnsOne(sc => sc.Email, email =>
        {
            email.Property(e => e.Value)
                .HasColumnName("Email")
                .HasMaxLength(200)
                .IsRequired();
        });
        
        builder.OwnsOne(sc => sc.Phone, phone =>
        {
            phone.Property(p => p.Value)
                .HasColumnName("Phone")
                .HasMaxLength(50);
        });
        
        builder.Property(sc => sc.Title)
            .HasMaxLength(100);
        
        builder.HasQueryFilter(sc => !sc.IsDeleted);
    }
}

public class SupplierProductConfiguration : IEntityTypeConfiguration<SupplierProduct>
{
    public void Configure(EntityTypeBuilder<SupplierProduct> builder)
    {
        builder.ToTable("SupplierProducts");
        
        builder.HasKey(sp => sp.Id);
        
        builder.HasIndex(sp => new { sp.SupplierId, sp.ProductId })
            .IsUnique();
        
        builder.Property(sp => sp.SupplierSku)
            .HasMaxLength(100);
        
        builder.OwnsOne(sp => sp.Price, money =>
        {
            money.Property(m => m.Currency)
                .HasMaxLength(3)
                .HasColumnName("PriceCurrency");
            
            money.Property(m => m.Amount)
                .HasPrecision(18, 2)
                .HasColumnName("PriceAmount");
        });
        
        builder.HasQueryFilter(sp => !sp.IsDeleted);
    }
}

public class SupplierDocumentConfiguration : IEntityTypeConfiguration<SupplierDocument>
{
    public void Configure(EntityTypeBuilder<SupplierDocument> builder)
    {
        builder.ToTable("SupplierDocuments");
        
        builder.HasKey(sd => sd.Id);
        
        builder.Property(sd => sd.Name)
            .HasMaxLength(200)
            .IsRequired();
        
        builder.Property(sd => sd.Url)
            .HasMaxLength(500)
            .IsRequired();
        
        builder.Property(sd => sd.Type)
            .HasConversion<string>()
            .HasMaxLength(20);
        
        builder.Property(sd => sd.Description)
            .HasMaxLength(500);
        
        builder.HasQueryFilter(sd => !sd.IsDeleted);
    }
}