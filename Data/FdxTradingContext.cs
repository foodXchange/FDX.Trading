using Microsoft.EntityFrameworkCore;
using FDX.Trading.Models;

namespace FDX.Trading.Data;

public class FdxTradingContext : DbContext
{
    public FdxTradingContext(DbContextOptions<FdxTradingContext> options)
        : base(options)
    {
    }

    public DbSet<User> FdxUsers { get; set; }
    public DbSet<SupplierDetails> SupplierDetails { get; set; }
    public DbSet<Product> Products { get; set; }
    public DbSet<SupplierProduct> SupplierProducts { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure User entity
        modelBuilder.Entity<User>(entity =>
        {
            entity.ToTable("FdxUsers"); // Use different table name
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.Username)
                .IsRequired()
                .HasMaxLength(100);
            
            entity.Property(e => e.Password)
                .IsRequired()
                .HasMaxLength(200);
            
            entity.Property(e => e.Email)
                .IsRequired()
                .HasMaxLength(200);
            
            entity.Property(e => e.CompanyName)
                .HasMaxLength(200);
            
            entity.Property(e => e.Country)
                .HasMaxLength(100);
            
            entity.Property(e => e.PhoneNumber)
                .HasMaxLength(50);
            
            entity.Property(e => e.Website)
                .HasMaxLength(500);
            
            entity.Property(e => e.Address)
                .HasMaxLength(500);
            
            entity.Property(e => e.Category)
                .HasMaxLength(200);
            
            entity.Property(e => e.BusinessType)
                .HasMaxLength(500);
            
            entity.Property(e => e.FullDescription)
                .HasMaxLength(2000);
            
            entity.Property(e => e.SubCategories)
                .HasMaxLength(500);
            
            entity.Property(e => e.AlternateEmails)
                .HasMaxLength(500);
            
            entity.Property(e => e.DisplayName)
                .HasMaxLength(200);

            // Create unique index on username
            entity.HasIndex(e => e.Username)
                .IsUnique();

            // Create index on email for faster lookups
            entity.HasIndex(e => e.Email);

            // Create index on Type for filtering
            entity.HasIndex(e => e.Type);

            // Create index on IsActive for filtering
            entity.HasIndex(e => e.IsActive);

            // Seed admin user
            entity.HasData(new User
            {
                Id = 1,
                Username = "udi@fdx.trading",
                Password = "FDX2030!", // In production, this should be hashed
                Email = "udi@fdx.trading",
                CompanyName = "FDX Trading",
                Type = UserType.Admin,
                Country = "Israel",
                IsActive = true,
                CreatedAt = new DateTime(2025, 1, 9, 12, 0, 0),
                LastLogin = new DateTime(2025, 1, 9, 12, 0, 0),
                DataComplete = true,
                RequiresPasswordChange = false,
                Verification = VerificationStatus.Verified
            });
        });

        // Configure SupplierDetails entity
        modelBuilder.Entity<SupplierDetails>(entity =>
        {
            entity.ToTable("SupplierDetails");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(s => s.User)
                .WithOne()
                .HasForeignKey<SupplierDetails>(s => s.UserId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.Property(e => e.CompanyRegistrationNumber).HasMaxLength(100);
            entity.Property(e => e.TaxId).HasMaxLength(100);
            entity.Property(e => e.ProductCategories).HasMaxLength(500);
            entity.Property(e => e.Certifications).HasMaxLength(500);
            entity.Property(e => e.PreferredSeaPort).HasMaxLength(200);
            entity.Property(e => e.PaymentTerms).HasMaxLength(200);
            entity.Property(e => e.Incoterms).HasMaxLength(100);
            entity.Property(e => e.Currency).HasMaxLength(10);
            entity.Property(e => e.WarehouseLocations).HasMaxLength(500);
            entity.Property(e => e.SalesContactName).HasMaxLength(200);
            entity.Property(e => e.SalesContactEmail).HasMaxLength(200);
            entity.Property(e => e.SalesContactPhone).HasMaxLength(50);
            entity.Property(e => e.VerifiedBy).HasMaxLength(200);
            
            entity.Property(e => e.Rating).HasColumnType("decimal(3,2)");
            entity.Property(e => e.MinimumOrderValue).HasColumnType("decimal(18,2)");
            
            entity.HasIndex(e => e.UserId).IsUnique();
            entity.HasIndex(e => e.IsVerified);
        });

        // Configure Product entity
        modelBuilder.Entity<Product>(entity =>
        {
            entity.ToTable("Products");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.ProductCode)
                .IsRequired()
                .HasMaxLength(50);
            
            entity.Property(e => e.ProductName)
                .IsRequired()
                .HasMaxLength(500);
            
            entity.Property(e => e.NetWeight).HasColumnType("decimal(18,3)");
            entity.Property(e => e.GrossWeight).HasColumnType("decimal(18,3)");
            entity.Property(e => e.MinTemperature).HasColumnType("decimal(5,2)");
            entity.Property(e => e.MaxTemperature).HasColumnType("decimal(5,2)");
            
            entity.HasIndex(e => e.ProductCode).IsUnique();
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.Category);
            entity.HasIndex(e => e.IsKosher);
            entity.HasIndex(e => e.IsOrganic);
        });

        // Configure SupplierProduct entity
        modelBuilder.Entity<SupplierProduct>(entity =>
        {
            entity.ToTable("SupplierProducts");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(sp => sp.SupplierDetails)
                .WithMany(s => s.SupplierProducts)
                .HasForeignKey(sp => sp.SupplierDetailsId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(sp => sp.Product)
                .WithMany(p => p.SupplierProducts)
                .HasForeignKey(sp => sp.ProductId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.Property(e => e.UnitWholesalePrice).HasColumnType("decimal(18,2)");
            entity.Property(e => e.CartonWholesalePrice).HasColumnType("decimal(18,2)");
            entity.Property(e => e.DiscountPercentage).HasColumnType("decimal(5,2)");
            entity.Property(e => e.MinimumOrderValue).HasColumnType("decimal(18,2)");
            entity.Property(e => e.PromotionalPrice).HasColumnType("decimal(18,2)");
            entity.Property(e => e.LastPurchasePrice).HasColumnType("decimal(18,2)");
            
            entity.HasIndex(e => new { e.SupplierDetailsId, e.ProductId }).IsUnique();
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.Currency);
        });
    }
}