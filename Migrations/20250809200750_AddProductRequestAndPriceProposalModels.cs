using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace FDX.Trading.Migrations
{
    /// <inheritdoc />
    public partial class AddProductRequestAndPriceProposalModels : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "BuyerCompany",
                table: "Products",
                type: "nvarchar(100)",
                maxLength: 100,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "BuyerProductCode",
                table: "Products",
                type: "nvarchar(50)",
                maxLength: 50,
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "InitialBuyerId",
                table: "Products",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "OpenComments",
                table: "Products",
                type: "nvarchar(500)",
                maxLength: 500,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "ProductImages",
                table: "Products",
                type: "nvarchar(500)",
                maxLength: 500,
                nullable: true);

            migrationBuilder.CreateTable(
                name: "ProductRequests",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    BuyerId = table.Column<int>(type: "int", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    Description = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: false),
                    Status = table.Column<int>(type: "int", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    ClosedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Deadline = table.Column<DateTime>(type: "datetime2", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ProductRequests", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ProductRequests_FdxUsers_BuyerId",
                        column: x => x.BuyerId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "PriceProposals",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ProductRequestId = table.Column<int>(type: "int", nullable: false),
                    SupplierId = table.Column<int>(type: "int", nullable: false),
                    ProductId = table.Column<int>(type: "int", nullable: false),
                    InitialPrice = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    CurrentPrice = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    Currency = table.Column<string>(type: "nvarchar(3)", maxLength: 3, nullable: false),
                    PricePerCarton = table.Column<decimal>(type: "decimal(18,2)", nullable: true),
                    MinimumOrderQuantity = table.Column<int>(type: "int", nullable: false),
                    Unit = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    Status = table.Column<int>(type: "int", nullable: false),
                    Incoterms = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    PaymentTerms = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    PreferredPort = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    LeadTimeDays = table.Column<int>(type: "int", nullable: false),
                    UnitsPerCarton = table.Column<int>(type: "int", nullable: true),
                    CartonsPerContainer20ft = table.Column<int>(type: "int", nullable: true),
                    CartonsPerContainer40ft = table.Column<int>(type: "int", nullable: true),
                    PalletsPerContainer20ft = table.Column<int>(type: "int", nullable: true),
                    PalletsPerContainer40ft = table.Column<int>(type: "int", nullable: true),
                    Notes = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    ConfirmedAt = table.Column<DateTime>(type: "datetime2", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PriceProposals", x => x.Id);
                    table.ForeignKey(
                        name: "FK_PriceProposals_FdxUsers_SupplierId",
                        column: x => x.SupplierId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_PriceProposals_ProductRequests_ProductRequestId",
                        column: x => x.ProductRequestId,
                        principalTable: "ProductRequests",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_PriceProposals_Products_ProductId",
                        column: x => x.ProductId,
                        principalTable: "Products",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "ProductRequestItems",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ProductRequestId = table.Column<int>(type: "int", nullable: false),
                    ProductId = table.Column<int>(type: "int", nullable: false),
                    RequestedQuantity = table.Column<int>(type: "int", nullable: false),
                    Unit = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    SpecialRequirements = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ProductRequestItems", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ProductRequestItems_ProductRequests_ProductRequestId",
                        column: x => x.ProductRequestId,
                        principalTable: "ProductRequests",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ProductRequestItems_Products_ProductId",
                        column: x => x.ProductId,
                        principalTable: "Products",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "PriceHistories",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    PriceProposalId = table.Column<int>(type: "int", nullable: false),
                    OldPrice = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    NewPrice = table.Column<decimal>(type: "decimal(18,2)", nullable: false),
                    ChangeReason = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    ChangedBy = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    ChangedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PriceHistories", x => x.Id);
                    table.ForeignKey(
                        name: "FK_PriceHistories_PriceProposals_PriceProposalId",
                        column: x => x.PriceProposalId,
                        principalTable: "PriceProposals",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Products_InitialBuyerId",
                table: "Products",
                column: "InitialBuyerId");

            migrationBuilder.CreateIndex(
                name: "IX_PriceHistories_ChangedAt",
                table: "PriceHistories",
                column: "ChangedAt");

            migrationBuilder.CreateIndex(
                name: "IX_PriceHistories_PriceProposalId",
                table: "PriceHistories",
                column: "PriceProposalId");

            migrationBuilder.CreateIndex(
                name: "IX_PriceProposals_ProductId",
                table: "PriceProposals",
                column: "ProductId");

            migrationBuilder.CreateIndex(
                name: "IX_PriceProposals_ProductRequestId_SupplierId_ProductId",
                table: "PriceProposals",
                columns: new[] { "ProductRequestId", "SupplierId", "ProductId" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_PriceProposals_Status",
                table: "PriceProposals",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_PriceProposals_SupplierId",
                table: "PriceProposals",
                column: "SupplierId");

            migrationBuilder.CreateIndex(
                name: "IX_ProductRequestItems_ProductId",
                table: "ProductRequestItems",
                column: "ProductId");

            migrationBuilder.CreateIndex(
                name: "IX_ProductRequestItems_ProductRequestId_ProductId",
                table: "ProductRequestItems",
                columns: new[] { "ProductRequestId", "ProductId" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_ProductRequests_BuyerId",
                table: "ProductRequests",
                column: "BuyerId");

            migrationBuilder.CreateIndex(
                name: "IX_ProductRequests_CreatedAt",
                table: "ProductRequests",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_ProductRequests_Status",
                table: "ProductRequests",
                column: "Status");

            migrationBuilder.AddForeignKey(
                name: "FK_Products_FdxUsers_InitialBuyerId",
                table: "Products",
                column: "InitialBuyerId",
                principalTable: "FdxUsers",
                principalColumn: "Id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Products_FdxUsers_InitialBuyerId",
                table: "Products");

            migrationBuilder.DropTable(
                name: "PriceHistories");

            migrationBuilder.DropTable(
                name: "ProductRequestItems");

            migrationBuilder.DropTable(
                name: "PriceProposals");

            migrationBuilder.DropTable(
                name: "ProductRequests");

            migrationBuilder.DropIndex(
                name: "IX_Products_InitialBuyerId",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "BuyerCompany",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "BuyerProductCode",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "InitialBuyerId",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "OpenComments",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "ProductImages",
                table: "Products");
        }
    }
}
