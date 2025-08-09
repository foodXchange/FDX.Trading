using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace FDX.Trading.Migrations
{
    /// <inheritdoc />
    public partial class AddSupplierDetailsProductsTables : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Products",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ProductCode = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    ProductName = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    Category = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    SubCategory = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    ProductFamily = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Description = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    HSCode = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    Barcode = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    UnitOfMeasure = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: true),
                    NetWeight = table.Column<decimal>(type: "decimal(18,3)", nullable: true),
                    GrossWeight = table.Column<decimal>(type: "decimal(18,3)", nullable: true),
                    UnitsPerCarton = table.Column<int>(type: "int", nullable: true),
                    CartonsPerPallet = table.Column<int>(type: "int", nullable: true),
                    MinTemperature = table.Column<decimal>(type: "decimal(5,2)", nullable: true),
                    MaxTemperature = table.Column<decimal>(type: "decimal(5,2)", nullable: true),
                    ShelfLifeDays = table.Column<int>(type: "int", nullable: true),
                    StorageConditions = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsKosher = table.Column<bool>(type: "bit", nullable: false),
                    KosherCertificate = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsOrganic = table.Column<bool>(type: "bit", nullable: false),
                    OrganicCertificate = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsVegan = table.Column<bool>(type: "bit", nullable: false),
                    IsGlutenFree = table.Column<bool>(type: "bit", nullable: false),
                    OtherCertifications = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ProductImage = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    LabelImage = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    AdditionalImages = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    CountryOfOrigin = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    Manufacturer = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Brand = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Status = table.Column<int>(type: "int", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    OriginalProductId = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ImportedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ImportNotes = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Products", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "SupplierDetails",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    UserId = table.Column<int>(type: "int", nullable: false),
                    CompanyRegistrationNumber = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    TaxId = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    Description = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ProductCategories = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    Certifications = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    PreferredSeaPort = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    PaymentTerms = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Incoterms = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    Currency = table.Column<string>(type: "nvarchar(10)", maxLength: 10, nullable: true),
                    MinimumOrderValue = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    LeadTimeDays = table.Column<int>(type: "int", nullable: true),
                    WarehouseLocations = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    Rating = table.Column<decimal>(type: "decimal(3,2)", nullable: true),
                    TotalOrders = table.Column<int>(type: "int", nullable: true),
                    CompletedOrders = table.Column<int>(type: "int", nullable: true),
                    LastOrderDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    SalesContactName = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    SalesContactEmail = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    SalesContactPhone = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    IsVerified = table.Column<bool>(type: "bit", nullable: false),
                    VerifiedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    VerifiedBy = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_SupplierDetails", x => x.Id);
                    table.ForeignKey(
                        name: "FK_SupplierDetails_FdxUsers_UserId",
                        column: x => x.UserId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "SupplierProducts",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    SupplierDetailsId = table.Column<int>(type: "int", nullable: false),
                    ProductId = table.Column<int>(type: "int", nullable: false),
                    SupplierProductCode = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    SupplierProductName = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    UnitWholesalePrice = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    CartonWholesalePrice = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    Currency = table.Column<string>(type: "nvarchar(10)", maxLength: 10, nullable: false),
                    DiscountPercentage = table.Column<decimal>(type: "decimal(5,2)", nullable: true),
                    MinimumOrderQuantity = table.Column<int>(type: "int", nullable: true),
                    MinimumOrderCartons = table.Column<int>(type: "int", nullable: true),
                    MinimumOrderValue = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    UnitsPerContainer20ft = table.Column<int>(type: "int", nullable: true),
                    UnitsPerContainer40ft = table.Column<int>(type: "int", nullable: true),
                    CartonsPerContainer20ft = table.Column<int>(type: "int", nullable: true),
                    CartonsPerContainer40ft = table.Column<int>(type: "int", nullable: true),
                    PalletsPerContainer20ft = table.Column<int>(type: "int", nullable: true),
                    PalletsPerContainer40ft = table.Column<int>(type: "int", nullable: true),
                    LeadTimeDays = table.Column<int>(type: "int", nullable: true),
                    StockQuantity = table.Column<int>(type: "int", nullable: true),
                    StockLastUpdated = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Incoterms = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    PaymentTerms = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    ShippingPort = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    Status = table.Column<int>(type: "int", nullable: false),
                    AvailableFrom = table.Column<DateTime>(type: "datetime2", nullable: true),
                    AvailableUntil = table.Column<DateTime>(type: "datetime2", nullable: true),
                    IsPromotional = table.Column<bool>(type: "bit", nullable: false),
                    PromotionalPrice = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    PromotionalPriceEndDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    QualityGrade = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ComplianceNotes = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    CertificationExpiryDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    LastPurchasePrice = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    LastPurchaseDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    TotalUnitsSold = table.Column<int>(type: "int", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Notes = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ImportedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ImportSource = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_SupplierProducts", x => x.Id);
                    table.ForeignKey(
                        name: "FK_SupplierProducts_Products_ProductId",
                        column: x => x.ProductId,
                        principalTable: "Products",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_SupplierProducts_SupplierDetails_SupplierDetailsId",
                        column: x => x.SupplierDetailsId,
                        principalTable: "SupplierDetails",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Products_Category",
                table: "Products",
                column: "Category");

            migrationBuilder.CreateIndex(
                name: "IX_Products_IsKosher",
                table: "Products",
                column: "IsKosher");

            migrationBuilder.CreateIndex(
                name: "IX_Products_IsOrganic",
                table: "Products",
                column: "IsOrganic");

            migrationBuilder.CreateIndex(
                name: "IX_Products_ProductCode",
                table: "Products",
                column: "ProductCode",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Products_Status",
                table: "Products",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_SupplierDetails_IsVerified",
                table: "SupplierDetails",
                column: "IsVerified");

            migrationBuilder.CreateIndex(
                name: "IX_SupplierDetails_UserId",
                table: "SupplierDetails",
                column: "UserId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_SupplierProducts_Currency",
                table: "SupplierProducts",
                column: "Currency");

            migrationBuilder.CreateIndex(
                name: "IX_SupplierProducts_ProductId",
                table: "SupplierProducts",
                column: "ProductId");

            migrationBuilder.CreateIndex(
                name: "IX_SupplierProducts_Status",
                table: "SupplierProducts",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_SupplierProducts_SupplierDetailsId_ProductId",
                table: "SupplierProducts",
                columns: new[] { "SupplierDetailsId", "ProductId" },
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "SupplierProducts");

            migrationBuilder.DropTable(
                name: "Products");

            migrationBuilder.DropTable(
                name: "SupplierDetails");
        }
    }
}
