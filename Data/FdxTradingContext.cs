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
    public DbSet<SupplierProductCatalog> SupplierProductCatalogs { get; set; }
    public DbSet<SupplierProductCatalogMatch> SupplierProductCatalogMatches { get; set; }
    public DbSet<ProductCategory> ProductCategories { get; set; }
    public DbSet<ProductRequest> ProductRequests { get; set; }
    public DbSet<ProductRequestItem> ProductRequestItems { get; set; }
    public DbSet<PriceProposal> PriceProposals { get; set; }
    public DbSet<PriceHistory> PriceHistories { get; set; }
    public DbSet<ProductPriceHistory> ProductPriceHistories { get; set; } = null!;
    //public DbSet<PriceBook> PriceBooks { get; set; } = null!;
    //public DbSet<PriceBookEntry> PriceBookEntries { get; set; } = null!;
    public DbSet<Request> Requests { get; set; }
    public DbSet<RequestItem> RequestItems { get; set; }
    public DbSet<RequestItemImage> RequestItemImages { get; set; }
    public DbSet<CompanyContact> CompanyContacts { get; set; }
    
    // New normalized entity structure
    //public DbSet<Company> Companies { get; set; }
    //public DbSet<Buyer> Buyers { get; set; }
    //public DbSet<Supplier> Suppliers { get; set; }
    //public DbSet<Expert> Experts { get; set; }
    //public DbSet<Agent> Agents { get; set; }
    //public DbSet<UserCompanyRole> UserCompanyRoles { get; set; }
    
    // Console module entities
    public DbSet<ProjectConsole> Consoles { get; set; }
    public DbSet<WorkflowStage> WorkflowStages { get; set; }
    public DbSet<ConsoleParticipant> ConsoleParticipants { get; set; }
    public DbSet<ConsoleAction> ConsoleActions { get; set; }
    public DbSet<ConsoleDocument> ConsoleDocuments { get; set; }
    
    // Communication foundation
    public DbSet<ConsoleMessage> ConsoleMessages { get; set; }
    public DbSet<NotificationQueue> NotificationQueues { get; set; }
    public DbSet<CommunicationTemplate> CommunicationTemplates { get; set; }
    
    // Sourcing Brief System
    public DbSet<SourcingBrief> SourcingBriefs { get; set; }
    
    // Proposal System
    //public DbSet<Proposal> Proposals { get; set; } = null!;
    //public DbSet<ProposalLineItem> ProposalLineItems { get; set; } = null!;
    //public DbSet<SamplingRequest> SamplingRequests { get; set; } = null!;
    
    // Category System
    //public DbSet<ProductCategoryHierarchy> ProductCategoryHierarchies { get; set; } = null!;
    //public DbSet<ProductCategoryMapping> ProductCategoryMappings { get; set; } = null!;
    
    // Contract System
    //public DbSet<Contract> Contracts { get; set; } = null!;
    //public DbSet<ContractDocument> ContractDocuments { get; set; } = null!;
    //public DbSet<ContractComment> ContractComments { get; set; } = null!;
    //public DbSet<ContractProduct> ContractProducts { get; set; } = null!;
    //public DbSet<ContractMilestone> ContractMilestones { get; set; } = null!;
    public DbSet<BriefRequest> BriefRequests { get; set; }
    public DbSet<BriefProduct> BriefProducts { get; set; }
    public DbSet<BriefProductImage> BriefProductImages { get; set; }
    public DbSet<BriefSupplier> BriefSuppliers { get; set; }
    public DbSet<BriefResponse> BriefResponses { get; set; }
    public DbSet<BriefResponseItem> BriefResponseItems { get; set; }
    public DbSet<BriefActivity> BriefActivities { get; set; }
    public DbSet<BriefAnalytics> BriefAnalytics { get; set; }
    public DbSet<BriefDocument> BriefDocuments { get; set; }
    public DbSet<BriefResponseDocument> BriefResponseDocuments { get; set; }

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
            entity.Property(e => e.MinimumOrderQuantity).HasColumnType("decimal(18,2)");
            
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

        // Configure Console entity
        modelBuilder.Entity<ProjectConsole>(entity =>
        {
            entity.ToTable("Consoles");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.ConsoleCode)
                .IsRequired()
                .HasMaxLength(50);
            
            entity.Property(e => e.Title)
                .IsRequired()
                .HasMaxLength(500);
            
            entity.HasOne(c => c.Owner)
                .WithMany()
                .HasForeignKey(c => c.OwnerId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(c => c.SourceRequest)
                .WithMany()
                .HasForeignKey(c => c.SourceId)
                .HasPrincipalKey(r => r.Id)
                .OnDelete(DeleteBehavior.SetNull);
            
            entity.HasIndex(e => e.ConsoleCode).IsUnique();
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.Type);
            entity.HasIndex(e => e.Priority);
            entity.HasIndex(e => e.OwnerId);
        });

        // Configure WorkflowStage entity
        modelBuilder.Entity<WorkflowStage>(entity =>
        {
            entity.ToTable("WorkflowStages");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.StageName)
                .IsRequired()
                .HasMaxLength(200);
            
            entity.HasOne(ws => ws.Console)
                .WithMany(c => c.WorkflowStages)
                .HasForeignKey(ws => ws.ConsoleId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(ws => ws.AssignedUser)
                .WithMany()
                .HasForeignKey(ws => ws.AssignedUserId)
                .OnDelete(DeleteBehavior.SetNull);
            
            entity.HasIndex(e => e.ConsoleId);
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.StageType);
            entity.HasIndex(e => new { e.ConsoleId, e.StageNumber });
        });

        // Configure ConsoleParticipant entity
        modelBuilder.Entity<ConsoleParticipant>(entity =>
        {
            entity.ToTable("ConsoleParticipants");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(cp => cp.Console)
                .WithMany(c => c.ConsoleParticipants)
                .HasForeignKey(cp => cp.ConsoleId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(cp => cp.User)
                .WithMany()
                .HasForeignKey(cp => cp.UserId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => new { e.ConsoleId, e.UserId }).IsUnique();
            entity.HasIndex(e => e.Role);
            entity.HasIndex(e => e.IsActive);
        });

        // Configure ConsoleAction entity
        modelBuilder.Entity<ConsoleAction>(entity =>
        {
            entity.ToTable("ConsoleActions");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(ca => ca.Console)
                .WithMany(c => c.ConsoleActions)
                .HasForeignKey(ca => ca.ConsoleId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(ca => ca.Stage)
                .WithMany()
                .HasForeignKey(ca => ca.StageId)
                .OnDelete(DeleteBehavior.NoAction);
            
            entity.HasOne(ca => ca.User)
                .WithMany()
                .HasForeignKey(ca => ca.UserId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => e.ConsoleId);
            entity.HasIndex(e => e.ActionType);
            entity.HasIndex(e => e.Timestamp);
        });

        // Configure ConsoleDocument entity
        modelBuilder.Entity<ConsoleDocument>(entity =>
        {
            entity.ToTable("ConsoleDocuments");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.FileName)
                .IsRequired()
                .HasMaxLength(500);
            
            entity.HasOne(cd => cd.Console)
                .WithMany(c => c.ConsoleDocuments)
                .HasForeignKey(cd => cd.ConsoleId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(cd => cd.Stage)
                .WithMany()
                .HasForeignKey(cd => cd.StageId)
                .OnDelete(DeleteBehavior.NoAction);
            
            entity.HasOne(cd => cd.UploadedBy)
                .WithMany()
                .HasForeignKey(cd => cd.UploadedByUserId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => e.ConsoleId);
            entity.HasIndex(e => e.DocumentType);
            entity.HasIndex(e => e.UploadedAt);
        });
        
        // Configure SourcingBrief entity
        modelBuilder.Entity<SourcingBrief>(entity =>
        {
            entity.ToTable("SourcingBriefs");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.BriefCode)
                .IsRequired()
                .HasMaxLength(50);
            
            entity.HasOne(sb => sb.Console)
                .WithOne()
                .HasForeignKey<SourcingBrief>(sb => sb.ConsoleId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(sb => sb.CreatedBy)
                .WithMany()
                .HasForeignKey(sb => sb.CreatedByUserId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => e.BriefCode).IsUnique();
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.CreatedAt);
        });
        
        // Configure BriefProduct entity
        modelBuilder.Entity<BriefProduct>(entity =>
        {
            entity.ToTable("BriefProducts");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.ProductName)
                .IsRequired()
                .HasMaxLength(500);
            
            entity.Property(e => e.TotalQuantity)
                .HasColumnType("decimal(18,3)");
            
            entity.Property(e => e.TargetPrice)
                .HasColumnType("decimal(18,2)");
            
            entity.Property(e => e.MaxPrice)
                .HasColumnType("decimal(18,2)");
            
            entity.Property(e => e.HistoricalPrice)
                .HasColumnType("decimal(18,2)");
            
            entity.HasOne(bp => bp.SourcingBrief)
                .WithMany(sb => sb.Products)
                .HasForeignKey(bp => bp.SourcingBriefId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasIndex(e => e.SourcingBriefId);
            entity.HasIndex(e => e.Category);
        });
        
        // Configure BriefSupplier entity
        modelBuilder.Entity<BriefSupplier>(entity =>
        {
            entity.ToTable("BriefSuppliers");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.MatchScore)
                .HasColumnType("decimal(5,2)");
            
            entity.HasOne(bs => bs.SourcingBrief)
                .WithMany(sb => sb.TargetSuppliers)
                .HasForeignKey(bs => bs.SourcingBriefId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(bs => bs.Supplier)
                .WithMany()
                .HasForeignKey(bs => bs.SupplierId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => new { e.SourcingBriefId, e.SupplierId }).IsUnique();
            entity.HasIndex(e => e.Status);
        });
        
        // Configure BriefResponse entity
        modelBuilder.Entity<BriefResponse>(entity =>
        {
            entity.ToTable("BriefResponses");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.TechnicalScore)
                .HasColumnType("decimal(5,2)");
            
            entity.Property(e => e.CommercialScore)
                .HasColumnType("decimal(5,2)");
            
            entity.Property(e => e.OverallScore)
                .HasColumnType("decimal(5,2)");
            
            entity.HasOne(br => br.SourcingBrief)
                .WithMany(sb => sb.Responses)
                .HasForeignKey(br => br.SourcingBriefId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(br => br.Supplier)
                .WithMany()
                .HasForeignKey(br => br.SupplierId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => e.ResponseCode).IsUnique();
            entity.HasIndex(e => new { e.SourcingBriefId, e.SupplierId }).IsUnique();
        });
        
        // Configure BriefResponseItem entity
        modelBuilder.Entity<BriefResponseItem>(entity =>
        {
            entity.ToTable("BriefResponseItems");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.UnitPrice)
                .HasColumnType("decimal(18,2)");
            
            entity.Property(e => e.VolumeDiscount)
                .HasColumnType("decimal(18,2)");
            
            entity.Property(e => e.AvailableQuantity)
                .HasColumnType("decimal(18,3)");
            
            entity.HasOne(bri => bri.BriefResponse)
                .WithMany(br => br.Items)
                .HasForeignKey(bri => bri.BriefResponseId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(bri => bri.BriefProduct)
                .WithMany()
                .HasForeignKey(bri => bri.BriefProductId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        // Configure SupplierProductCatalog entity
        modelBuilder.Entity<SupplierProductCatalog>(entity =>
        {
            entity.ToTable("SupplierProductCatalogs");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.ProductName)
                .IsRequired()
                .HasMaxLength(500);
            
            entity.Property(e => e.MinOrderQuantity)
                .HasColumnType("decimal(18,3)");
            
            entity.Property(e => e.PricePerUnit)
                .HasColumnType("decimal(18,2)");
            
            entity.Property(e => e.StockQuantity)
                .HasColumnType("decimal(18,3)");
            
            entity.Property(e => e.QualityScore)
                .HasColumnType("decimal(5,2)");
            
            entity.HasOne(e => e.Supplier)
                .WithMany()
                .HasForeignKey(e => e.SupplierId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        // Configure SupplierProductCatalogMatch entity
        modelBuilder.Entity<SupplierProductCatalogMatch>(entity =>
        {
            entity.ToTable("SupplierProductCatalogMatches");
            entity.HasKey(e => e.Id);
            
            entity.Property(e => e.MatchScore)
                .HasColumnType("decimal(5,2)");
            
            entity.HasOne(e => e.SupplierProductCatalog)
                .WithMany(sp => sp.ProductMatches)
                .HasForeignKey(e => e.SupplierProductCatalogId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(e => e.BriefProduct)
                .WithMany()
                .HasForeignKey(e => e.BriefProductId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasIndex(e => new { e.SupplierProductCatalogId, e.BriefProductId })
                .IsUnique();
        });
        
        /* Commented out entities that don't have corresponding models
        // Configure Proposal entity
        modelBuilder.Entity<Proposal>(entity =>
        {
            entity.ToTable("Proposals");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(p => p.Request)
                .WithMany()
                .HasForeignKey(p => p.RequestId)
                .OnDelete(DeleteBehavior.SetNull);
            
            entity.HasOne(p => p.Buyer)
                .WithMany()
                .HasForeignKey(p => p.BuyerId)
                .OnDelete(DeleteBehavior.SetNull);
            
            entity.HasOne(p => p.Supplier)
                .WithMany()
                .HasForeignKey(p => p.SupplierId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => e.ProposalId).IsUnique();
            entity.HasIndex(e => e.Status);
        });
        
        // Configure ProposalLineItem entity
        modelBuilder.Entity<ProposalLineItem>(entity =>
        {
            entity.ToTable("ProposalLineItems");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(pli => pli.Proposal)
                .WithMany(p => p.LineItems)
                .HasForeignKey(pli => pli.ProposalId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(pli => pli.Product)
                .WithMany()
                .HasForeignKey(pli => pli.ProductId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => e.Status);
        });
        
        // Configure SamplingRequest entity
        modelBuilder.Entity<SamplingRequest>(entity =>
        {
            entity.ToTable("SamplingRequests");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(sr => sr.Buyer)
                .WithMany()
                .HasForeignKey(sr => sr.BuyerId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(sr => sr.Supplier)
                .WithMany()
                .HasForeignKey(sr => sr.SupplierId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(sr => sr.Product)
                .WithMany()
                .HasForeignKey(sr => sr.ProductId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(sr => sr.Proposal)
                .WithMany(p => p.SamplingRequests)
                .HasForeignKey(sr => sr.ProposalId)
                .OnDelete(DeleteBehavior.SetNull);
            
            entity.HasOne(sr => sr.Request)
                .WithMany()
                .HasForeignKey(sr => sr.RequestId)
                .OnDelete(DeleteBehavior.SetNull);
            
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.RequestNumber);
        });
        
        // Configure ProductCategoryHierarchy entity
        modelBuilder.Entity<ProductCategoryHierarchy>(entity =>
        {
            entity.ToTable("ProductCategoryHierarchies");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(c => c.Parent)
                .WithMany(c => c.Children)
                .HasForeignKey(c => c.ParentId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => e.CategoryId);
            entity.HasIndex(e => e.Level);
            entity.HasIndex(e => e.IsActive);
            entity.HasIndex(e => new { e.Category, e.SubCategory, e.Family, e.SubFamily });
        });
        
        // Configure ProductCategoryMapping entity
        modelBuilder.Entity<ProductCategoryMapping>(entity =>
        {
            entity.ToTable("ProductCategoryMappings");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(pcm => pcm.Product)
                .WithMany()
                .HasForeignKey(pcm => pcm.ProductId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(pcm => pcm.Category)
                .WithMany()
                .HasForeignKey(pcm => pcm.CategoryId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasIndex(e => new { e.ProductId, e.CategoryId }).IsUnique();
        });
        
        // Configure Contract entity
        modelBuilder.Entity<Contract>(entity =>
        {
            entity.ToTable("Contracts");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(c => c.Buyer)
                .WithMany()
                .HasForeignKey(c => c.BuyerId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(c => c.Supplier)
                .WithMany()
                .HasForeignKey(c => c.SupplierId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(c => c.Proposal)
                .WithMany()
                .HasForeignKey(c => c.ProposalId)
                .OnDelete(DeleteBehavior.SetNull);
            
            entity.HasIndex(e => e.ContractNumber).IsUnique();
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.Type);
            entity.HasIndex(e => e.EndDate);
        });
        
        // Configure ContractDocument entity
        modelBuilder.Entity<ContractDocument>(entity =>
        {
            entity.ToTable("ContractDocuments");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(cd => cd.Contract)
                .WithMany(c => c.Documents)
                .HasForeignKey(cd => cd.ContractId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasIndex(e => e.ContractId);
            entity.HasIndex(e => e.Category);
        });
        
        // Configure ContractComment entity
        modelBuilder.Entity<ContractComment>(entity =>
        {
            entity.ToTable("ContractComments");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(cc => cc.Contract)
                .WithMany(c => c.Comments)
                .HasForeignKey(cc => cc.ContractId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(cc => cc.User)
                .WithMany()
                .HasForeignKey(cc => cc.UserId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(cc => cc.ParentComment)
                .WithMany()
                .HasForeignKey(cc => cc.ParentCommentId)
                .OnDelete(DeleteBehavior.NoAction);
            
            entity.HasIndex(e => e.ContractId);
            entity.HasIndex(e => e.Status);
        });
        
        // Configure ContractProduct entity
        modelBuilder.Entity<ContractProduct>(entity =>
        {
            entity.ToTable("ContractProducts");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(cp => cp.Contract)
                .WithMany(c => c.Products)
                .HasForeignKey(cp => cp.ContractId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(cp => cp.Product)
                .WithMany()
                .HasForeignKey(cp => cp.ProductId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => new { e.ContractId, e.ProductId }).IsUnique();
        });
        
        // Configure ContractMilestone entity
        modelBuilder.Entity<ContractMilestone>(entity =>
        {
            entity.ToTable("ContractMilestones");
            entity.HasKey(e => e.Id);
            
            entity.HasOne(cm => cm.Contract)
                .WithMany(c => c.Milestones)
                .HasForeignKey(cm => cm.ContractId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(cm => cm.DependsOnMilestone)
                .WithMany()
                .HasForeignKey(cm => cm.DependsOnMilestoneId)
                .OnDelete(DeleteBehavior.NoAction);
            
            entity.HasIndex(e => e.ContractId);
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.DueDate);
        });
        
        // Configure decimal precision for entities to fix warnings
        
        // Configure Company entity decimal properties
        modelBuilder.Entity<Company>(entity =>
        {
            entity.Property(e => e.AnnualRevenue).HasPrecision(18, 2);
        });
        
        // Configure Buyer entity decimal properties
        modelBuilder.Entity<Buyer>(entity =>
        {
            entity.Property(e => e.AnnualPurchasingVolume).HasPrecision(18, 2);
            entity.Property(e => e.CreditLimit).HasPrecision(18, 2);
            entity.Property(e => e.MinOrderValue).HasPrecision(18, 2);
            entity.Property(e => e.MaxOrderValue).HasPrecision(18, 2);
        });
        
        // Configure Supplier entity decimal properties
        modelBuilder.Entity<Supplier>(entity =>
        {
            entity.Property(e => e.MinOrderQuantity).HasPrecision(18, 2);
            entity.Property(e => e.AnnualProductionValue).HasPrecision(18, 2);
            entity.Property(e => e.SampleCost).HasPrecision(18, 2);
        });
        
        // Configure Expert entity decimal properties
        modelBuilder.Entity<Expert>(entity =>
        {
            entity.Property(e => e.HourlyRate).HasPrecision(18, 2);
            entity.Property(e => e.DailyRate).HasPrecision(18, 2);
            entity.Property(e => e.ProjectMinimum).HasPrecision(18, 2);
            entity.Property(e => e.InsuranceCoverage).HasPrecision(18, 2);
        });
        
        // Configure Agent entity decimal properties
        modelBuilder.Entity<Agent>(entity =>
        {
            entity.Property(e => e.CommissionRate).HasPrecision(5, 2);
            entity.Property(e => e.FixedFee).HasPrecision(18, 2);
            entity.Property(e => e.AverageOrderValue).HasPrecision(18, 2);
            entity.Property(e => e.AnnualSalesVolume).HasPrecision(18, 2);
        });
        
        // Configure SourcingBrief entity decimal properties
        modelBuilder.Entity<SourcingBrief>(entity =>
        {
            entity.Property(e => e.QualityScore).HasPrecision(5, 2);
            entity.Property(e => e.ResponseRate).HasPrecision(5, 2);
            entity.Property(e => e.SuccessRate).HasPrecision(5, 2);
        });
        
        // Configure BriefAnalytics entity decimal properties
        modelBuilder.Entity<BriefAnalytics>(entity =>
        {
            entity.Property(e => e.RequirementClarity).HasPrecision(5, 2);
            entity.Property(e => e.SpecificationCompleteness).HasPrecision(5, 2);
            entity.Property(e => e.VolumeAttractiveness).HasPrecision(5, 2);
            entity.Property(e => e.AverageResponseTime).HasPrecision(10, 2);
            entity.Property(e => e.SupplierSatisfactionScore).HasPrecision(5, 2);
            entity.Property(e => e.AchievedPriceReduction).HasPrecision(5, 2);
        });
        
        // Configure UserCompanyRole entity decimal properties
        modelBuilder.Entity<UserCompanyRole>(entity =>
        {
            entity.Property(e => e.PurchaseAuthority).HasPrecision(18, 2);
        });
        
        // Add performance indexes for frequently queried fields
        
        // Add indexes for Request entity
        modelBuilder.Entity<Request>(entity =>
        {
            entity.HasIndex(e => e.BuyerId);
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.CreatedAt);
            entity.HasIndex(e => e.UpdatedAt);
            entity.HasIndex(e => new { e.Status, e.CreatedAt })
                .HasDatabaseName("IX_Request_Status_CreatedAt");
        });
        
        // Add indexes for RequestItem entity
        modelBuilder.Entity<RequestItem>(entity =>
        {
            entity.HasIndex(e => e.RequestId);
            entity.HasIndex(e => e.ProductName);
            entity.HasIndex(e => new { e.RequestId, e.ProductName })
                .HasDatabaseName("IX_RequestItem_RequestId_ProductName");
        });
        
        // Add indexes for Company entity
        modelBuilder.Entity<Company>(entity =>
        {
            entity.HasIndex(e => e.CompanyName);
            entity.HasIndex(e => e.RegistrationNumber).IsUnique().HasFilter("[RegistrationNumber] IS NOT NULL");
            entity.HasIndex(e => e.Country);
            entity.HasIndex(e => e.VatNumber);
        });
        
        // Add indexes for SourcingBrief entity
        modelBuilder.Entity<SourcingBrief>(entity =>
        {
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.CreatedAt);
            entity.HasIndex(e => new { e.Status, e.CreatedAt })
                .HasDatabaseName("IX_SourcingBrief_Status_CreatedAt");
        });
        
        // Add indexes for BriefResponse entity
        modelBuilder.Entity<BriefResponse>(entity =>
        {
            entity.HasIndex(e => e.Status);
            entity.HasIndex(e => e.CreatedAt);
        });
        
        // Add indexes for Contract entity
        modelBuilder.Entity<Contract>(entity =>
        {
            entity.HasIndex(e => e.StartDate);
            entity.HasIndex(e => new { e.Status, e.EndDate })
                .HasDatabaseName("IX_Contract_Status_EndDate");
        });*/
        
        // Configure CompanyContact relationships
        modelBuilder.Entity<CompanyContact>(entity =>
        {
            entity.HasOne(cc => cc.User)
                .WithMany()
                .HasForeignKey(cc => cc.UserId)
                .OnDelete(DeleteBehavior.SetNull);
            
            entity.HasIndex(e => e.CompanyName);
            entity.HasIndex(e => e.UserId);
            entity.HasIndex(e => e.IsActive);
        });
        
        // Configure NotificationQueue relationships
        modelBuilder.Entity<NotificationQueue>(entity =>
        {
            entity.HasOne(n => n.RecipientUser)
                .WithMany()
                .HasForeignKey(n => n.RecipientUserId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(n => n.Console)
                .WithMany()
                .HasForeignKey(n => n.ConsoleId)
                .OnDelete(DeleteBehavior.NoAction);
            
            entity.HasOne(n => n.Message)
                .WithMany()
                .HasForeignKey(n => n.MessageId)
                .OnDelete(DeleteBehavior.NoAction);
            
            entity.HasIndex(e => e.RecipientUserId);
            entity.HasIndex(e => e.IsProcessed);
            entity.HasIndex(e => e.ScheduledFor);
            entity.HasIndex(e => new { e.IsProcessed, e.ScheduledFor })
                .HasDatabaseName("IX_NotificationQueue_Processing");
        });
    }
}