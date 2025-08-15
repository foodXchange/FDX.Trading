using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace FDX.Trading.Migrations
{
    /// <inheritdoc />
    public partial class AddProductCategories : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Products_ProductCategoryHierarchies_ProductCategoryHierarchyId",
                table: "Products");

            migrationBuilder.DropTable(
                name: "CompanyAgents");

            migrationBuilder.DropTable(
                name: "CompanyBuyers");

            migrationBuilder.DropTable(
                name: "CompanyExperts");

            migrationBuilder.DropTable(
                name: "CompanySuppliers");

            migrationBuilder.DropTable(
                name: "ContractComments");

            migrationBuilder.DropTable(
                name: "ContractDocuments");

            migrationBuilder.DropTable(
                name: "ContractMilestones");

            migrationBuilder.DropTable(
                name: "ContractProducts");

            migrationBuilder.DropTable(
                name: "PriceBookEntries");

            migrationBuilder.DropTable(
                name: "ProductCategoryMappings");

            migrationBuilder.DropTable(
                name: "ProposalLineItems");

            migrationBuilder.DropTable(
                name: "SamplingRequests");

            migrationBuilder.DropTable(
                name: "UserCompanyRoles");

            migrationBuilder.DropTable(
                name: "Contracts");

            migrationBuilder.DropTable(
                name: "PriceBooks");

            migrationBuilder.DropTable(
                name: "ProductCategoryHierarchies");

            migrationBuilder.DropTable(
                name: "Companies");

            migrationBuilder.DropTable(
                name: "Proposals");

            migrationBuilder.DropIndex(
                name: "IX_SourcingBrief_Status_CreatedAt",
                table: "SourcingBriefs");

            migrationBuilder.DropIndex(
                name: "IX_Request_Status_CreatedAt",
                table: "Requests");

            migrationBuilder.DropIndex(
                name: "IX_Requests_UpdatedAt",
                table: "Requests");

            migrationBuilder.DropIndex(
                name: "IX_RequestItem_RequestId_ProductName",
                table: "RequestItems");

            migrationBuilder.DropIndex(
                name: "IX_RequestItems_ProductName",
                table: "RequestItems");

            migrationBuilder.DropIndex(
                name: "IX_Products_ProductCategoryHierarchyId",
                table: "Products");

            migrationBuilder.DropIndex(
                name: "IX_BriefResponses_CreatedAt",
                table: "BriefResponses");

            migrationBuilder.DropIndex(
                name: "IX_BriefResponses_Status",
                table: "BriefResponses");

            migrationBuilder.DropColumn(
                name: "ProductCategoryHierarchyId",
                table: "Products");

            migrationBuilder.AddColumn<int>(
                name: "ProductCategoryId",
                table: "SupplierProductCatalogs",
                type: "int",
                nullable: true);

            migrationBuilder.AlterColumn<decimal>(
                name: "SuccessRate",
                table: "SourcingBriefs",
                type: "decimal(18,2)",
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(5,2)",
                oldPrecision: 5,
                oldScale: 2);

            migrationBuilder.AlterColumn<decimal>(
                name: "ResponseRate",
                table: "SourcingBriefs",
                type: "decimal(18,2)",
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(5,2)",
                oldPrecision: 5,
                oldScale: 2);

            migrationBuilder.AlterColumn<decimal>(
                name: "QualityScore",
                table: "SourcingBriefs",
                type: "decimal(18,2)",
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(5,2)",
                oldPrecision: 5,
                oldScale: 2);

            migrationBuilder.AlterColumn<string>(
                name: "ContentType",
                table: "RequestItemImages",
                type: "nvarchar(100)",
                maxLength: 100,
                nullable: false,
                defaultValue: "",
                oldClrType: typeof(string),
                oldType: "nvarchar(100)",
                oldMaxLength: 100,
                oldNullable: true);

            migrationBuilder.AlterColumn<decimal>(
                name: "VolumeAttractiveness",
                table: "BriefAnalytics",
                type: "decimal(18,2)",
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(5,2)",
                oldPrecision: 5,
                oldScale: 2);

            migrationBuilder.AlterColumn<decimal>(
                name: "SupplierSatisfactionScore",
                table: "BriefAnalytics",
                type: "decimal(18,2)",
                nullable: true,
                oldClrType: typeof(decimal),
                oldType: "decimal(5,2)",
                oldPrecision: 5,
                oldScale: 2,
                oldNullable: true);

            migrationBuilder.AlterColumn<decimal>(
                name: "SpecificationCompleteness",
                table: "BriefAnalytics",
                type: "decimal(18,2)",
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(5,2)",
                oldPrecision: 5,
                oldScale: 2);

            migrationBuilder.AlterColumn<decimal>(
                name: "RequirementClarity",
                table: "BriefAnalytics",
                type: "decimal(18,2)",
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(5,2)",
                oldPrecision: 5,
                oldScale: 2);

            migrationBuilder.AlterColumn<decimal>(
                name: "AverageResponseTime",
                table: "BriefAnalytics",
                type: "decimal(18,2)",
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(10,2)",
                oldPrecision: 10,
                oldScale: 2);

            migrationBuilder.AlterColumn<decimal>(
                name: "AchievedPriceReduction",
                table: "BriefAnalytics",
                type: "decimal(18,2)",
                nullable: true,
                oldClrType: typeof(decimal),
                oldType: "decimal(5,2)",
                oldPrecision: 5,
                oldScale: 2,
                oldNullable: true);

            migrationBuilder.CreateTable(
                name: "ProductCategories",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    Category = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    SubCategory = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    Family = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    SubFamily = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    ProductFamilyId = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: true),
                    FullPath = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ProductCategories", x => x.Id);
                });

            migrationBuilder.UpdateData(
                table: "FdxUsers",
                keyColumn: "Id",
                keyValue: 1,
                column: "Verification",
                value: 2);

            migrationBuilder.CreateIndex(
                name: "IX_SupplierProductCatalogs_ProductCategoryId",
                table: "SupplierProductCatalogs",
                column: "ProductCategoryId");

            migrationBuilder.AddForeignKey(
                name: "FK_SupplierProductCatalogs_ProductCategories_ProductCategoryId",
                table: "SupplierProductCatalogs",
                column: "ProductCategoryId",
                principalTable: "ProductCategories",
                principalColumn: "Id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_SupplierProductCatalogs_ProductCategories_ProductCategoryId",
                table: "SupplierProductCatalogs");

            migrationBuilder.DropTable(
                name: "ProductCategories");

            migrationBuilder.DropIndex(
                name: "IX_SupplierProductCatalogs_ProductCategoryId",
                table: "SupplierProductCatalogs");

            migrationBuilder.DropColumn(
                name: "ProductCategoryId",
                table: "SupplierProductCatalogs");

            migrationBuilder.AlterColumn<decimal>(
                name: "SuccessRate",
                table: "SourcingBriefs",
                type: "decimal(5,2)",
                precision: 5,
                scale: 2,
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(18,2)");

            migrationBuilder.AlterColumn<decimal>(
                name: "ResponseRate",
                table: "SourcingBriefs",
                type: "decimal(5,2)",
                precision: 5,
                scale: 2,
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(18,2)");

            migrationBuilder.AlterColumn<decimal>(
                name: "QualityScore",
                table: "SourcingBriefs",
                type: "decimal(5,2)",
                precision: 5,
                scale: 2,
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(18,2)");

            migrationBuilder.AlterColumn<string>(
                name: "ContentType",
                table: "RequestItemImages",
                type: "nvarchar(100)",
                maxLength: 100,
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(100)",
                oldMaxLength: 100);

            migrationBuilder.AddColumn<int>(
                name: "ProductCategoryHierarchyId",
                table: "Products",
                type: "int",
                nullable: true);

            migrationBuilder.AlterColumn<decimal>(
                name: "VolumeAttractiveness",
                table: "BriefAnalytics",
                type: "decimal(5,2)",
                precision: 5,
                scale: 2,
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(18,2)");

            migrationBuilder.AlterColumn<decimal>(
                name: "SupplierSatisfactionScore",
                table: "BriefAnalytics",
                type: "decimal(5,2)",
                precision: 5,
                scale: 2,
                nullable: true,
                oldClrType: typeof(decimal),
                oldType: "decimal(18,2)",
                oldNullable: true);

            migrationBuilder.AlterColumn<decimal>(
                name: "SpecificationCompleteness",
                table: "BriefAnalytics",
                type: "decimal(5,2)",
                precision: 5,
                scale: 2,
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(18,2)");

            migrationBuilder.AlterColumn<decimal>(
                name: "RequirementClarity",
                table: "BriefAnalytics",
                type: "decimal(5,2)",
                precision: 5,
                scale: 2,
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(18,2)");

            migrationBuilder.AlterColumn<decimal>(
                name: "AverageResponseTime",
                table: "BriefAnalytics",
                type: "decimal(10,2)",
                precision: 10,
                scale: 2,
                nullable: false,
                oldClrType: typeof(decimal),
                oldType: "decimal(18,2)");

            migrationBuilder.AlterColumn<decimal>(
                name: "AchievedPriceReduction",
                table: "BriefAnalytics",
                type: "decimal(5,2)",
                precision: 5,
                scale: 2,
                nullable: true,
                oldClrType: typeof(decimal),
                oldType: "decimal(18,2)",
                oldNullable: true);

            migrationBuilder.CreateTable(
                name: "Companies",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    Address = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    AnnualRevenue = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    Certifications = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    City = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    CompanyName = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    Country = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedByUserId = table.Column<int>(type: "int", nullable: true),
                    Currency = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    Description = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    Email = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    EmployeeCount = table.Column<int>(type: "int", nullable: true),
                    IsActive = table.Column<bool>(type: "bit", nullable: false),
                    IsVerified = table.Column<bool>(type: "bit", nullable: false),
                    LinkedInUrl = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Logo = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    PhoneNumber = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    PostalCode = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: true),
                    RegistrationNumber = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    Type = table.Column<int>(type: "int", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedByUserId = table.Column<int>(type: "int", nullable: true),
                    VatNumber = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    VerificationStatus = table.Column<int>(type: "int", nullable: false),
                    Website = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    WhatsAppBusiness = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    YearEstablished = table.Column<int>(type: "int", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Companies", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "PriceBooks",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ApprovedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ApprovedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Description = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    EffectiveDate = table.Column<DateTime>(type: "datetime2", nullable: false),
                    ExpiryDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ImportSource = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Name = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    NewProducts = table.Column<int>(type: "int", nullable: false),
                    Status = table.Column<int>(type: "int", nullable: false),
                    TotalEntries = table.Column<int>(type: "int", nullable: false),
                    UpdatedPrices = table.Column<int>(type: "int", nullable: false),
                    Version = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PriceBooks", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "ProductCategoryHierarchies",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ParentId = table.Column<int>(type: "int", nullable: true),
                    Category = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    CategoryId = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Description = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    DisplayName = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    Family = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    FullPath = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    ImportSource = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    ImportedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    IsActive = table.Column<bool>(type: "bit", nullable: false),
                    Keywords = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    LastUpdated = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Level = table.Column<int>(type: "int", nullable: false),
                    ProductCount = table.Column<int>(type: "int", nullable: false),
                    Slug = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    SortOrder = table.Column<int>(type: "int", nullable: false),
                    SubCategory = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    SubFamily = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ProductCategoryHierarchies", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ProductCategoryHierarchies_ProductCategoryHierarchies_ParentId",
                        column: x => x.ParentId,
                        principalTable: "ProductCategoryHierarchies",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Proposals",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    BuyerId = table.Column<int>(type: "int", nullable: true),
                    RequestId = table.Column<int>(type: "int", nullable: true),
                    SupplierId = table.Column<int>(type: "int", nullable: false),
                    BrandingLabel = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    Comments = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Currency = table.Column<string>(type: "nvarchar(10)", maxLength: 10, nullable: false),
                    ForecastFiles = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    ImportSource = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    ImportedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Incoterms = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    LastUpdated = table.Column<DateTime>(type: "datetime2", nullable: true),
                    PaymentTerms = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    PortOfLoading = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    ProductImages = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    ProposalDocument = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    ProposalId = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    Status = table.Column<int>(type: "int", nullable: false),
                    SupplierLogo = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    SupplierProfileImages = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    Title = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    TotalValue = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ValidFrom = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ValidTo = table.Column<DateTime>(type: "datetime2", nullable: true),
                    VatNumber = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Proposals", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Proposals_FdxUsers_BuyerId",
                        column: x => x.BuyerId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                    table.ForeignKey(
                        name: "FK_Proposals_FdxUsers_SupplierId",
                        column: x => x.SupplierId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Proposals_Requests_RequestId",
                        column: x => x.RequestId,
                        principalTable: "Requests",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "CompanyAgents",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    CompanyId = table.Column<int>(type: "int", nullable: false),
                    ActiveClients = table.Column<int>(type: "int", nullable: true),
                    AgentType = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    Airlines = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    AnnualSalesVolume = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    AverageOrderValue = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    ClientReferences = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    CommissionRate = table.Column<decimal>(type: "decimal(5,2)", precision: 5, scale: 2, nullable: true),
                    CommissionStructure = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    ContractDuration = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    CustomsLicenseNumber = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    CustomsPorts = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    DealsClosedLastYear = table.Column<int>(type: "int", nullable: true),
                    ExclusiveTerritories = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    FeeCurrency = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    FixedFee = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    FreightModes = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    HandlesExport = table.Column<bool>(type: "bit", nullable: false),
                    HandlesImport = table.Column<bool>(type: "bit", nullable: false),
                    HasWarehouseFacilities = table.Column<bool>(type: "bit", nullable: false),
                    IndustryConnections = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Languages = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    MarketSegments = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    NetworkSize = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    Notes = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: true),
                    NoticePeriod = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    PortfolioUrl = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    ProvidesCustomsClearance = table.Column<bool>(type: "bit", nullable: false),
                    ProvidesLeadGeneration = table.Column<bool>(type: "bit", nullable: false),
                    ProvidesLogisticsSupport = table.Column<bool>(type: "bit", nullable: false),
                    ProvidesMarketResearch = table.Column<bool>(type: "bit", nullable: false),
                    ProvidesNegotiation = table.Column<bool>(type: "bit", nullable: false),
                    ProvidesQualityInspection = table.Column<bool>(type: "bit", nullable: false),
                    ProvidesTranslation = table.Column<bool>(type: "bit", nullable: false),
                    RepresentedBrands = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    RepresentedSuppliers = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    RequiresExclusivity = table.Column<bool>(type: "bit", nullable: false),
                    ShippingLines = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Specialization = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    SuccessStories = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    TermsAndConditions = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    TerritoryCountries = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    TerritoryRegions = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    WarehouseLocations = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_CompanyAgents", x => x.Id);
                    table.ForeignKey(
                        name: "FK_CompanyAgents_Companies_CompanyId",
                        column: x => x.CompanyId,
                        principalTable: "Companies",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "CompanyBuyers",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    CompanyId = table.Column<int>(type: "int", nullable: false),
                    AcceptsPrivateLabel = table.Column<bool>(type: "bit", nullable: false),
                    AnnualPurchasingVolume = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    BuyerType = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    CreditLimit = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    CreditRating = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    DeliveryPreferences = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    DistributionChannels = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    MaxOrderValue = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    MinOrderValue = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    Notes = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    PaymentTerms = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    PreferredCategories = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    PreferredIncoterms = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    PurchasingCurrency = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    PurchasingFrequency = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    RequiredCertifications = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    RequiresHalal = table.Column<bool>(type: "bit", nullable: false),
                    RequiresKosher = table.Column<bool>(type: "bit", nullable: false),
                    RequiresOrganic = table.Column<bool>(type: "bit", nullable: false),
                    StoreCount = table.Column<int>(type: "int", nullable: true),
                    WarehouseLocations = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_CompanyBuyers", x => x.Id);
                    table.ForeignKey(
                        name: "FK_CompanyBuyers_Companies_CompanyId",
                        column: x => x.CompanyId,
                        principalTable: "Companies",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "CompanyExperts",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    CompanyId = table.Column<int>(type: "int", nullable: false),
                    Accreditations = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    AvailableCountries = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    CaseStudies = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Certifications = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ClientReferences = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    DailyRate = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    HasProfessionalInsurance = table.Column<bool>(type: "bit", nullable: false),
                    HourlyRate = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    IndustryExpertise = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    InsuranceCoverage = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    InsuranceProvider = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    IslamicAuthority = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    KeyPersonnel = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    Notes = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: true),
                    PaymentTerms = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    PortfolioUrl = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    PricingCurrency = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    ProjectMinimum = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    ProvidesEmergencyService = table.Column<bool>(type: "bit", nullable: false),
                    ProvidesRemoteService = table.Column<bool>(type: "bit", nullable: false),
                    RabbinicalAuthority = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    RequiresOnSite = table.Column<bool>(type: "bit", nullable: false),
                    ResponseTime = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    ServiceAreas = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ServiceCategories = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ServiceDescription = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: true),
                    ServiceLanguages = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    ServiceType = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    SpecialtyAreas = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    TeamSize = table.Column<int>(type: "int", nullable: true),
                    YearsOfExperience = table.Column<int>(type: "int", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_CompanyExperts", x => x.Id);
                    table.ForeignKey(
                        name: "FK_CompanyExperts_Companies_CompanyId",
                        column: x => x.CompanyId,
                        principalTable: "Companies",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "CompanySuppliers",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    CompanyId = table.Column<int>(type: "int", nullable: false),
                    AnnualProductionValue = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    BrandNames = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    CanShipDirect = table.Column<bool>(type: "bit", nullable: false),
                    CompanyProfile = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: true),
                    ExportCountries = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    FactoryEmployeeCount = table.Column<int>(type: "int", nullable: true),
                    HalalCertifier = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    HasHalalCertification = table.Column<bool>(type: "bit", nullable: false),
                    HasKosherCertification = table.Column<bool>(type: "bit", nullable: false),
                    HasOrganicCertification = table.Column<bool>(type: "bit", nullable: false),
                    Incoterms = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    KosherCertifier = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    LeadTime = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    MainMarkets = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    ManufacturingCapacity = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    MinOrderQuantity = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    MinOrderUnit = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    Notes = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    OffersCustomPackaging = table.Column<bool>(type: "bit", nullable: false),
                    OffersPrivateLabel = table.Column<bool>(type: "bit", nullable: false),
                    OffersProductDevelopment = table.Column<bool>(type: "bit", nullable: false),
                    OrganicCertifier = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    PaymentTerms = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    PortOfLoading = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    PricingCurrency = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    ProductCatalogUrl = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ProductCategories = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ProductionFacilities = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    QualityCertifications = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    SampleCost = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    SamplePolicy = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_CompanySuppliers", x => x.Id);
                    table.ForeignKey(
                        name: "FK_CompanySuppliers_Companies_CompanyId",
                        column: x => x.CompanyId,
                        principalTable: "Companies",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "UserCompanyRoles",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    CompanyId = table.Column<int>(type: "int", nullable: false),
                    UserId = table.Column<int>(type: "int", nullable: false),
                    AuthorityCurrency = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    BestContactTime = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    CanApprovePurchases = table.Column<bool>(type: "bit", nullable: false),
                    CanMakeDecisions = table.Column<bool>(type: "bit", nullable: false),
                    CanSignContracts = table.Column<bool>(type: "bit", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    Department = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    EndDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    IsActive = table.Column<bool>(type: "bit", nullable: false),
                    IsAvailable = table.Column<bool>(type: "bit", nullable: false),
                    IsMainContact = table.Column<bool>(type: "bit", nullable: false),
                    IsPrimary = table.Column<bool>(type: "bit", nullable: false),
                    JobTitle = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    Notes = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    PreferredContactMethod = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    PreferredLanguage = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    ProductCategories = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    PurchaseAuthority = table.Column<decimal>(type: "decimal(18,2)", precision: 18, scale: 2, nullable: true),
                    Responsibilities = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Role = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    StartDate = table.Column<DateTime>(type: "datetime2", nullable: false),
                    Territories = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UnavailableReason = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    UnavailableUntil = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UserCompanyRoles", x => x.Id);
                    table.ForeignKey(
                        name: "FK_UserCompanyRoles_Companies_CompanyId",
                        column: x => x.CompanyId,
                        principalTable: "Companies",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_UserCompanyRoles_FdxUsers_UserId",
                        column: x => x.UserId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "PriceBookEntries",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    PriceBookId = table.Column<int>(type: "int", nullable: false),
                    ProductId = table.Column<int>(type: "int", nullable: false),
                    SupplierId = table.Column<int>(type: "int", nullable: true),
                    CartonPrice = table.Column<decimal>(type: "decimal(18,4)", nullable: true),
                    Currency = table.Column<string>(type: "nvarchar(10)", maxLength: 10, nullable: false),
                    ImportedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    ImportedFrom = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    Incoterms = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: true),
                    LeadTimeDays = table.Column<int>(type: "int", nullable: true),
                    MOQ = table.Column<int>(type: "int", nullable: true),
                    Notes = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    PaymentTerms = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    PreviousUnitPrice = table.Column<decimal>(type: "decimal(18,4)", nullable: true),
                    PriceChangePercent = table.Column<decimal>(type: "decimal(10,2)", nullable: true),
                    Tier1Price = table.Column<decimal>(type: "decimal(18,4)", nullable: true),
                    Tier1Quantity = table.Column<int>(type: "int", nullable: true),
                    Tier2Price = table.Column<decimal>(type: "decimal(18,4)", nullable: true),
                    Tier2Quantity = table.Column<int>(type: "int", nullable: true),
                    Tier3Price = table.Column<decimal>(type: "decimal(18,4)", nullable: true),
                    Tier3Quantity = table.Column<int>(type: "int", nullable: true),
                    UnitPrice = table.Column<decimal>(type: "decimal(18,4)", nullable: false),
                    ValidFrom = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ValidTo = table.Column<DateTime>(type: "datetime2", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PriceBookEntries", x => x.Id);
                    table.ForeignKey(
                        name: "FK_PriceBookEntries_FdxUsers_SupplierId",
                        column: x => x.SupplierId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_PriceBookEntries_PriceBooks_PriceBookId",
                        column: x => x.PriceBookId,
                        principalTable: "PriceBooks",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_PriceBookEntries_Products_ProductId",
                        column: x => x.ProductId,
                        principalTable: "Products",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ProductCategoryMappings",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    CategoryId = table.Column<int>(type: "int", nullable: false),
                    ProductId = table.Column<int>(type: "int", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    IsPrimary = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ProductCategoryMappings", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ProductCategoryMappings_ProductCategoryHierarchies_CategoryId",
                        column: x => x.CategoryId,
                        principalTable: "ProductCategoryHierarchies",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ProductCategoryMappings_Products_ProductId",
                        column: x => x.ProductId,
                        principalTable: "Products",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Contracts",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    BuyerId = table.Column<int>(type: "int", nullable: true),
                    ProposalId = table.Column<int>(type: "int", nullable: true),
                    SupplierId = table.Column<int>(type: "int", nullable: true),
                    ActualSpend = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    ApprovalDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ApprovedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    AutoRenew = table.Column<bool>(type: "bit", nullable: false),
                    ComplianceRequirements = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    ContractNumber = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Currency = table.Column<string>(type: "nvarchar(10)", maxLength: 10, nullable: false),
                    DeliveryTerms = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Description = table.Column<string>(type: "nvarchar(2000)", maxLength: 2000, nullable: true),
                    DiscountPercentage = table.Column<decimal>(type: "decimal(5,2)", nullable: true),
                    EndDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ExpiryAlertSent = table.Column<bool>(type: "bit", nullable: false),
                    ImportSource = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    ImportedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Incoterms = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    LastAlertDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    LastUpdated = table.Column<DateTime>(type: "datetime2", nullable: true),
                    OpenComments = table.Column<int>(type: "int", nullable: false),
                    ParentContractNumber = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    PaymentTerms = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    PerformanceRating = table.Column<decimal>(type: "decimal(5,2)", nullable: true),
                    QualityStandards = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    RenewalDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    RenewalNoticeDays = table.Column<int>(type: "int", nullable: true),
                    RenewalType = table.Column<int>(type: "int", nullable: true),
                    ReviewDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ReviewedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    SignedDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    StartDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Status = table.Column<int>(type: "int", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    TotalValue = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    Type = table.Column<int>(type: "int", nullable: false),
                    UpdatedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Version = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Contracts", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Contracts_FdxUsers_BuyerId",
                        column: x => x.BuyerId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Contracts_FdxUsers_SupplierId",
                        column: x => x.SupplierId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Contracts_Proposals_ProposalId",
                        column: x => x.ProposalId,
                        principalTable: "Proposals",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "ProposalLineItems",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ProductId = table.Column<int>(type: "int", nullable: false),
                    ProposalId = table.Column<int>(type: "int", nullable: false),
                    CreateComplianceRecord = table.Column<bool>(type: "bit", nullable: false),
                    CreateGraphics = table.Column<bool>(type: "bit", nullable: false),
                    CreateOrderLineItem = table.Column<bool>(type: "bit", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Currency = table.Column<string>(type: "nvarchar(10)", maxLength: 10, nullable: false),
                    DiscountAmount = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    DiscountPercent = table.Column<decimal>(type: "decimal(5,2)", nullable: true),
                    ImportSource = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    ImportedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Incoterms = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    IsOrdered = table.Column<bool>(type: "bit", nullable: false),
                    LastUpdated = table.Column<DateTime>(type: "datetime2", nullable: true),
                    LeadTimeDays = table.Column<int>(type: "int", nullable: true),
                    LineItemId = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    MOQ = table.Column<int>(type: "int", nullable: true),
                    Notes = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    PaymentTerms = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    Quantity = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    RequiresAdaptation = table.Column<bool>(type: "bit", nullable: false),
                    ShippingPort = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    Status = table.Column<int>(type: "int", nullable: false),
                    SupplierNotes = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    TotalPrice = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    UnitOfMeasure = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    UnitPrice = table.Column<decimal>(type: "decimal(18,4)", nullable: false),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    WholesalePrice = table.Column<decimal>(type: "decimal(18,4)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ProposalLineItems", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ProposalLineItems_Products_ProductId",
                        column: x => x.ProductId,
                        principalTable: "Products",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_ProposalLineItems_Proposals_ProposalId",
                        column: x => x.ProposalId,
                        principalTable: "Proposals",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "SamplingRequests",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    BuyerId = table.Column<int>(type: "int", nullable: false),
                    ProductId = table.Column<int>(type: "int", nullable: false),
                    ProposalId = table.Column<int>(type: "int", nullable: true),
                    RequestId = table.Column<int>(type: "int", nullable: true),
                    SupplierId = table.Column<int>(type: "int", nullable: false),
                    BuyerFeedback = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    BuyerPaymentStatus = table.Column<int>(type: "int", nullable: false),
                    Comments = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    CourierCompany = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Decision = table.Column<int>(type: "int", nullable: true),
                    DeliveredDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    DeliveryAddress = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    DeliveryCost = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    DeliveryPhone = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    ImportSource = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    ImportedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    LastUpdated = table.Column<DateTime>(type: "datetime2", nullable: true),
                    OtherSamplesFromCompany = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    RequestNumber = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    SampleDescription = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    SampleImages = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    SampleQuantity = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    SellerComment = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    SellerEmail = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    SellerPaymentStatus = table.Column<int>(type: "int", nullable: false),
                    ShippedDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Status = table.Column<int>(type: "int", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    TrackingNumber = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UseCompanyAddress = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_SamplingRequests", x => x.Id);
                    table.ForeignKey(
                        name: "FK_SamplingRequests_FdxUsers_BuyerId",
                        column: x => x.BuyerId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_SamplingRequests_FdxUsers_SupplierId",
                        column: x => x.SupplierId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_SamplingRequests_Products_ProductId",
                        column: x => x.ProductId,
                        principalTable: "Products",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_SamplingRequests_Proposals_ProposalId",
                        column: x => x.ProposalId,
                        principalTable: "Proposals",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                    table.ForeignKey(
                        name: "FK_SamplingRequests_Requests_RequestId",
                        column: x => x.RequestId,
                        principalTable: "Requests",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "ContractComments",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ContractId = table.Column<int>(type: "int", nullable: false),
                    ParentCommentId = table.Column<int>(type: "int", nullable: true),
                    UserId = table.Column<int>(type: "int", nullable: false),
                    AssignedTo = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Comment = table.Column<string>(type: "nvarchar(2000)", maxLength: 2000, nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    DueDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    IsInternal = table.Column<bool>(type: "bit", nullable: false),
                    IsPinned = table.Column<bool>(type: "bit", nullable: false),
                    LastUpdated = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Priority = table.Column<int>(type: "int", nullable: false),
                    RequiresAction = table.Column<bool>(type: "bit", nullable: false),
                    ResolutionNote = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: true),
                    ResolvedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ResolvedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Status = table.Column<int>(type: "int", nullable: false),
                    Type = table.Column<int>(type: "int", nullable: false),
                    UpdatedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ContractComments", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ContractComments_ContractComments_ParentCommentId",
                        column: x => x.ParentCommentId,
                        principalTable: "ContractComments",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_ContractComments_Contracts_ContractId",
                        column: x => x.ContractId,
                        principalTable: "Contracts",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ContractComments_FdxUsers_UserId",
                        column: x => x.UserId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "ContractDocuments",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ContractId = table.Column<int>(type: "int", nullable: false),
                    AccessRestrictions = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Category = table.Column<int>(type: "int", nullable: false),
                    Description = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    FileName = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    FilePath = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    FileSize = table.Column<long>(type: "bigint", nullable: true),
                    FileType = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    IsConfidential = table.Column<bool>(type: "bit", nullable: false),
                    IsCurrentVersion = table.Column<bool>(type: "bit", nullable: false),
                    IsSigned = table.Column<bool>(type: "bit", nullable: false),
                    LastViewed = table.Column<DateTime>(type: "datetime2", nullable: true),
                    LastViewedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    SignatureHash = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    SignedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    SignedDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UploadedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    UploadedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Version = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ContractDocuments", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ContractDocuments_Contracts_ContractId",
                        column: x => x.ContractId,
                        principalTable: "Contracts",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ContractMilestones",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ContractId = table.Column<int>(type: "int", nullable: false),
                    DependsOnMilestoneId = table.Column<int>(type: "int", nullable: true),
                    AttachedDocuments = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    CompletedDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    DaysDelayed = table.Column<int>(type: "int", nullable: true),
                    DelayReason = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    Deliverables = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    Description = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: true),
                    DueDate = table.Column<DateTime>(type: "datetime2", nullable: false),
                    IsOnTime = table.Column<bool>(type: "bit", nullable: false),
                    LastUpdated = table.Column<DateTime>(type: "datetime2", nullable: true),
                    PaymentAmount = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    PaymentCurrency = table.Column<string>(type: "nvarchar(10)", maxLength: 10, nullable: true),
                    PaymentDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    PaymentTriggered = table.Column<bool>(type: "bit", nullable: false),
                    Quantity = table.Column<decimal>(type: "decimal(18,3)", nullable: true),
                    QuantityUnit = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    ReminderDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ReminderDaysBefore = table.Column<int>(type: "int", nullable: true),
                    ReminderSent = table.Column<bool>(type: "bit", nullable: false),
                    Status = table.Column<int>(type: "int", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    Type = table.Column<int>(type: "int", nullable: false),
                    UpdatedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    VerificationDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    VerificationNotes = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    VerifiedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ContractMilestones", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ContractMilestones_ContractMilestones_DependsOnMilestoneId",
                        column: x => x.DependsOnMilestoneId,
                        principalTable: "ContractMilestones",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_ContractMilestones_Contracts_ContractId",
                        column: x => x.ContractId,
                        principalTable: "Contracts",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ContractProducts",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ContractId = table.Column<int>(type: "int", nullable: false),
                    ProductId = table.Column<int>(type: "int", nullable: false),
                    CommittedQuantity = table.Column<decimal>(type: "decimal(18,3)", nullable: true),
                    ContractPrice = table.Column<decimal>(type: "decimal(18,4)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Currency = table.Column<string>(type: "nvarchar(10)", maxLength: 10, nullable: false),
                    DeliveredQuantity = table.Column<decimal>(type: "decimal(18,3)", nullable: true),
                    DeliveryTerms = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    DiscountConditions = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    DiscountPercentage = table.Column<decimal>(type: "decimal(5,2)", nullable: true),
                    EffectiveFrom = table.Column<DateTime>(type: "datetime2", nullable: true),
                    EffectiveTo = table.Column<DateTime>(type: "datetime2", nullable: true),
                    FulfillmentRate = table.Column<decimal>(type: "decimal(5,2)", nullable: true),
                    IsActive = table.Column<bool>(type: "bit", nullable: false),
                    LastUpdated = table.Column<DateTime>(type: "datetime2", nullable: true),
                    LeadTimeDays = table.Column<int>(type: "int", nullable: true),
                    MaximumQuantity = table.Column<decimal>(type: "decimal(18,3)", nullable: true),
                    MinimumQuantity = table.Column<decimal>(type: "decimal(18,3)", nullable: true),
                    Notes = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: true),
                    OrderedQuantity = table.Column<decimal>(type: "decimal(18,3)", nullable: true),
                    OriginalPrice = table.Column<decimal>(type: "decimal(18,4)", nullable: true),
                    PriceUnit = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    QualityScore = table.Column<decimal>(type: "decimal(5,2)", nullable: true),
                    QualitySpecification = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    VolumeRebate = table.Column<decimal>(type: "decimal(18,2)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ContractProducts", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ContractProducts_Contracts_ContractId",
                        column: x => x.ContractId,
                        principalTable: "Contracts",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ContractProducts_Products_ProductId",
                        column: x => x.ProductId,
                        principalTable: "Products",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.UpdateData(
                table: "FdxUsers",
                keyColumn: "Id",
                keyValue: 1,
                column: "Verification",
                value: 0);

            migrationBuilder.CreateIndex(
                name: "IX_SourcingBrief_Status_CreatedAt",
                table: "SourcingBriefs",
                columns: new[] { "Status", "CreatedAt" });

            migrationBuilder.CreateIndex(
                name: "IX_Request_Status_CreatedAt",
                table: "Requests",
                columns: new[] { "Status", "CreatedAt" });

            migrationBuilder.CreateIndex(
                name: "IX_Requests_UpdatedAt",
                table: "Requests",
                column: "UpdatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_RequestItem_RequestId_ProductName",
                table: "RequestItems",
                columns: new[] { "RequestId", "ProductName" });

            migrationBuilder.CreateIndex(
                name: "IX_RequestItems_ProductName",
                table: "RequestItems",
                column: "ProductName");

            migrationBuilder.CreateIndex(
                name: "IX_Products_ProductCategoryHierarchyId",
                table: "Products",
                column: "ProductCategoryHierarchyId");

            migrationBuilder.CreateIndex(
                name: "IX_BriefResponses_CreatedAt",
                table: "BriefResponses",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_BriefResponses_Status",
                table: "BriefResponses",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_Companies_CompanyName",
                table: "Companies",
                column: "CompanyName");

            migrationBuilder.CreateIndex(
                name: "IX_Companies_Country",
                table: "Companies",
                column: "Country");

            migrationBuilder.CreateIndex(
                name: "IX_Companies_RegistrationNumber",
                table: "Companies",
                column: "RegistrationNumber",
                unique: true,
                filter: "[RegistrationNumber] IS NOT NULL");

            migrationBuilder.CreateIndex(
                name: "IX_Companies_VatNumber",
                table: "Companies",
                column: "VatNumber");

            migrationBuilder.CreateIndex(
                name: "IX_CompanyAgents_CompanyId",
                table: "CompanyAgents",
                column: "CompanyId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_CompanyBuyers_CompanyId",
                table: "CompanyBuyers",
                column: "CompanyId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_CompanyExperts_CompanyId",
                table: "CompanyExperts",
                column: "CompanyId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_CompanySuppliers_CompanyId",
                table: "CompanySuppliers",
                column: "CompanyId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_ContractComments_ContractId",
                table: "ContractComments",
                column: "ContractId");

            migrationBuilder.CreateIndex(
                name: "IX_ContractComments_ParentCommentId",
                table: "ContractComments",
                column: "ParentCommentId");

            migrationBuilder.CreateIndex(
                name: "IX_ContractComments_Status",
                table: "ContractComments",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_ContractComments_UserId",
                table: "ContractComments",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_ContractDocuments_Category",
                table: "ContractDocuments",
                column: "Category");

            migrationBuilder.CreateIndex(
                name: "IX_ContractDocuments_ContractId",
                table: "ContractDocuments",
                column: "ContractId");

            migrationBuilder.CreateIndex(
                name: "IX_ContractMilestones_ContractId",
                table: "ContractMilestones",
                column: "ContractId");

            migrationBuilder.CreateIndex(
                name: "IX_ContractMilestones_DependsOnMilestoneId",
                table: "ContractMilestones",
                column: "DependsOnMilestoneId");

            migrationBuilder.CreateIndex(
                name: "IX_ContractMilestones_DueDate",
                table: "ContractMilestones",
                column: "DueDate");

            migrationBuilder.CreateIndex(
                name: "IX_ContractMilestones_Status",
                table: "ContractMilestones",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_ContractProducts_ContractId_ProductId",
                table: "ContractProducts",
                columns: new[] { "ContractId", "ProductId" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_ContractProducts_ProductId",
                table: "ContractProducts",
                column: "ProductId");

            migrationBuilder.CreateIndex(
                name: "IX_Contract_Status_EndDate",
                table: "Contracts",
                columns: new[] { "Status", "EndDate" });

            migrationBuilder.CreateIndex(
                name: "IX_Contracts_BuyerId",
                table: "Contracts",
                column: "BuyerId");

            migrationBuilder.CreateIndex(
                name: "IX_Contracts_ContractNumber",
                table: "Contracts",
                column: "ContractNumber",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Contracts_EndDate",
                table: "Contracts",
                column: "EndDate");

            migrationBuilder.CreateIndex(
                name: "IX_Contracts_ProposalId",
                table: "Contracts",
                column: "ProposalId");

            migrationBuilder.CreateIndex(
                name: "IX_Contracts_StartDate",
                table: "Contracts",
                column: "StartDate");

            migrationBuilder.CreateIndex(
                name: "IX_Contracts_Status",
                table: "Contracts",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_Contracts_SupplierId",
                table: "Contracts",
                column: "SupplierId");

            migrationBuilder.CreateIndex(
                name: "IX_Contracts_Type",
                table: "Contracts",
                column: "Type");

            migrationBuilder.CreateIndex(
                name: "IX_PriceBookEntries_PriceBookId",
                table: "PriceBookEntries",
                column: "PriceBookId");

            migrationBuilder.CreateIndex(
                name: "IX_PriceBookEntries_ProductId",
                table: "PriceBookEntries",
                column: "ProductId");

            migrationBuilder.CreateIndex(
                name: "IX_PriceBookEntries_SupplierId",
                table: "PriceBookEntries",
                column: "SupplierId");

            migrationBuilder.CreateIndex(
                name: "IX_ProductCategoryHierarchies_Category_SubCategory_Family_SubFamily",
                table: "ProductCategoryHierarchies",
                columns: new[] { "Category", "SubCategory", "Family", "SubFamily" });

            migrationBuilder.CreateIndex(
                name: "IX_ProductCategoryHierarchies_CategoryId",
                table: "ProductCategoryHierarchies",
                column: "CategoryId");

            migrationBuilder.CreateIndex(
                name: "IX_ProductCategoryHierarchies_IsActive",
                table: "ProductCategoryHierarchies",
                column: "IsActive");

            migrationBuilder.CreateIndex(
                name: "IX_ProductCategoryHierarchies_Level",
                table: "ProductCategoryHierarchies",
                column: "Level");

            migrationBuilder.CreateIndex(
                name: "IX_ProductCategoryHierarchies_ParentId",
                table: "ProductCategoryHierarchies",
                column: "ParentId");

            migrationBuilder.CreateIndex(
                name: "IX_ProductCategoryMappings_CategoryId",
                table: "ProductCategoryMappings",
                column: "CategoryId");

            migrationBuilder.CreateIndex(
                name: "IX_ProductCategoryMappings_ProductId_CategoryId",
                table: "ProductCategoryMappings",
                columns: new[] { "ProductId", "CategoryId" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_ProposalLineItems_ProductId",
                table: "ProposalLineItems",
                column: "ProductId");

            migrationBuilder.CreateIndex(
                name: "IX_ProposalLineItems_ProposalId",
                table: "ProposalLineItems",
                column: "ProposalId");

            migrationBuilder.CreateIndex(
                name: "IX_ProposalLineItems_Status",
                table: "ProposalLineItems",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_Proposals_BuyerId",
                table: "Proposals",
                column: "BuyerId");

            migrationBuilder.CreateIndex(
                name: "IX_Proposals_ProposalId",
                table: "Proposals",
                column: "ProposalId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Proposals_RequestId",
                table: "Proposals",
                column: "RequestId");

            migrationBuilder.CreateIndex(
                name: "IX_Proposals_Status",
                table: "Proposals",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_Proposals_SupplierId",
                table: "Proposals",
                column: "SupplierId");

            migrationBuilder.CreateIndex(
                name: "IX_SamplingRequests_BuyerId",
                table: "SamplingRequests",
                column: "BuyerId");

            migrationBuilder.CreateIndex(
                name: "IX_SamplingRequests_ProductId",
                table: "SamplingRequests",
                column: "ProductId");

            migrationBuilder.CreateIndex(
                name: "IX_SamplingRequests_ProposalId",
                table: "SamplingRequests",
                column: "ProposalId");

            migrationBuilder.CreateIndex(
                name: "IX_SamplingRequests_RequestId",
                table: "SamplingRequests",
                column: "RequestId");

            migrationBuilder.CreateIndex(
                name: "IX_SamplingRequests_RequestNumber",
                table: "SamplingRequests",
                column: "RequestNumber");

            migrationBuilder.CreateIndex(
                name: "IX_SamplingRequests_Status",
                table: "SamplingRequests",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_SamplingRequests_SupplierId",
                table: "SamplingRequests",
                column: "SupplierId");

            migrationBuilder.CreateIndex(
                name: "IX_UserCompanyRoles_CompanyId",
                table: "UserCompanyRoles",
                column: "CompanyId");

            migrationBuilder.CreateIndex(
                name: "IX_UserCompanyRoles_UserId",
                table: "UserCompanyRoles",
                column: "UserId");

            migrationBuilder.AddForeignKey(
                name: "FK_Products_ProductCategoryHierarchies_ProductCategoryHierarchyId",
                table: "Products",
                column: "ProductCategoryHierarchyId",
                principalTable: "ProductCategoryHierarchies",
                principalColumn: "Id");
        }
    }
}
