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
    public DbSet<ProductRequest> ProductRequests { get; set; }
    public DbSet<ProductRequestItem> ProductRequestItems { get; set; }
    public DbSet<PriceProposal> PriceProposals { get; set; }
    public DbSet<PriceHistory> PriceHistories { get; set; }
    public DbSet<ProductPriceHistory> ProductPriceHistory { get; set; }
    public DbSet<Request> Requests { get; set; }
    public DbSet<RequestItem> RequestItems { get; set; }
    public DbSet<CompanyContact> CompanyContacts { get; set; }

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

        // Configure SupplierProduct entity - DEPRECATED: Moving to one-to-many relationship
        // Keeping for migration purposes only
        modelBuilder.Entity<SupplierProduct>(entity =>
        {
            entity.ToTable("SupplierProducts");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(sp => sp.SupplierDetails)
                .WithMany(s => s.SupplierProducts)
                .HasForeignKey(sp => sp.SupplierDetailsId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(sp => sp.Product)
                .WithMany() // Removed navigation property from Product
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
        
        // Configure Product-Supplier relationship (one-to-many)
        modelBuilder.Entity<Product>(entity =>
        {
            entity.HasOne(p => p.Supplier)
                .WithMany(u => u.Products)
                .HasForeignKey(p => p.SupplierId)
                .OnDelete(DeleteBehavior.SetNull);
                
            entity.Property(e => e.UnitWholesalePrice).HasColumnType("decimal(18,2)");
            entity.Property(e => e.CartonWholesalePrice).HasColumnType("decimal(18,2)");
        });

        // Configure ProductRequest entity
        modelBuilder.Entity<ProductRequest>(entity =>
        {
            entity.ToTable("ProductRequests");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(pr => pr.Buyer)
                .WithMany()
                .HasForeignKey(pr => pr.BuyerId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.Property(e => e.Title).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Description).HasMaxLength(1000);
            
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.BuyerId);
            entity.HasIndex(e => e.CreatedAt);
        });

        // Configure ProductRequestItem entity
        modelBuilder.Entity<ProductRequestItem>(entity =>
        {
            entity.ToTable("ProductRequestItems");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(pri => pri.ProductRequest)
                .WithMany(pr => pr.RequestItems)
                .HasForeignKey(pri => pri.ProductRequestId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(pri => pri.Product)
                .WithMany(p => p.RequestItems)
                .HasForeignKey(pri => pri.ProductId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.Property(e => e.Unit).HasMaxLength(50);
            entity.Property(e => e.SpecialRequirements).HasMaxLength(500);
            
            entity.HasIndex(e => new { e.ProductRequestId, e.ProductId }).IsUnique();
        });

        // Configure PriceProposal entity
        modelBuilder.Entity<PriceProposal>(entity =>
        {
            entity.ToTable("PriceProposals");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(pp => pp.ProductRequest)
                .WithMany(pr => pr.Proposals)
                .HasForeignKey(pp => pp.ProductRequestId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(pp => pp.Supplier)
                .WithMany()
                .HasForeignKey(pp => pp.SupplierId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(pp => pp.Product)
                .WithMany(p => p.PriceProposals)
                .HasForeignKey(pp => pp.ProductId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.Property(e => e.InitialPrice).HasColumnType("decimal(18,2)");
            entity.Property(e => e.CurrentPrice).HasColumnType("decimal(18,2)");
            entity.Property(e => e.PricePerCarton).HasColumnType("decimal(18,2)");
            entity.Property(e => e.Currency).IsRequired().HasMaxLength(3);
            entity.Property(e => e.Unit).HasMaxLength(50);
            entity.Property(e => e.Incoterms).HasMaxLength(50);
            entity.Property(e => e.PaymentTerms).HasMaxLength(100);
            entity.Property(e => e.PreferredPort).HasMaxLength(100);
            entity.Property(e => e.Notes).HasMaxLength(1000);
            
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.SupplierId);
            entity.HasIndex(e => e.ProductId);
            entity.HasIndex(e => new { e.ProductRequestId, e.SupplierId, e.ProductId }).IsUnique();
        });

        // Configure PriceHistory entity
        modelBuilder.Entity<PriceHistory>(entity =>
        {
            entity.ToTable("PriceHistories");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(ph => ph.PriceProposal)
                .WithMany(pp => pp.PriceHistories)
                .HasForeignKey(ph => ph.PriceProposalId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.Property(e => e.OldPrice).HasColumnType("decimal(18,2)");
            entity.Property(e => e.NewPrice).HasColumnType("decimal(18,2)");
            entity.Property(e => e.ChangeReason).HasMaxLength(500);
            entity.Property(e => e.ChangedBy).HasMaxLength(100);
            
            entity.HasIndex(e => e.PriceProposalId);
            entity.HasIndex(e => e.ChangedAt);
        });

        // Configure Request entity
        modelBuilder.Entity<Request>(entity =>
        {
            entity.ToTable("Requests");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.RequestNumber)
                .IsRequired()
                .HasMaxLength(50);
            
            entity.Property(e => e.Title)
                .IsRequired()
                .HasMaxLength(200);
            
            entity.Property(e => e.Description)
                .HasMaxLength(2000);
            
            entity.HasOne(r => r.Buyer)
                .WithMany()
                .HasForeignKey(r => r.BuyerId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => e.RequestNumber).IsUnique();
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.BuyerId);
            entity.HasIndex(e => e.CreatedAt);
        });

        // Configure RequestItem entity
        modelBuilder.Entity<RequestItem>(entity =>
        {
            entity.ToTable("RequestItems");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.ProductName)
                .IsRequired()
                .HasMaxLength(200);
            
            entity.Property(e => e.Quantity)
                .HasColumnType("decimal(18,3)");
            
            entity.Property(e => e.Unit)
                .IsRequired()
                .HasMaxLength(20);
            
            entity.Property(e => e.Description)
                .HasMaxLength(500);
            
            entity.Property(e => e.TargetPrice)
                .HasColumnType("decimal(18,2)");
            
            entity.HasOne(ri => ri.Request)
                .WithMany(r => r.RequestItems)
                .HasForeignKey(ri => ri.RequestId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasIndex(e => e.RequestId);
        });

        // Configure CompanyContact entity
        modelBuilder.Entity<CompanyContact>(entity =>
        {
            entity.ToTable("CompanyContacts");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.CompanyName)
                .IsRequired()
                .HasMaxLength(200);
            
            entity.Property(e => e.ContactName)
                .IsRequired()
                .HasMaxLength(200);
            
            entity.Property(e => e.ContactEmail)
                .HasMaxLength(100);
            
            entity.Property(e => e.ContactPhone)
                .HasMaxLength(50);
            
            entity.Property(e => e.ContactRole)
                .HasMaxLength(100);
            
            // Create index for faster lookups
            entity.HasIndex(e => e.CompanyName);
            entity.HasIndex(e => new { e.CompanyName, e.ContactName });
            entity.HasIndex(e => e.IsActive);
        });
    }
}