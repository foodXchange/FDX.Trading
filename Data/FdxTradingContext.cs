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
    }
}