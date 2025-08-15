using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace FDX.Trading.Migrations
{
    /// <inheritdoc />
    public partial class ConvertToOneToManySupplierProduct : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<decimal>(
                name: "CartonWholesalePrice",
                table: "Products",
                type: "decimal(18,2)",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "CartonsPerContainer20ft",
                table: "Products",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "CartonsPerContainer40ft",
                table: "Products",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Currency",
                table: "Products",
                type: "nvarchar(10)",
                maxLength: 10,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Incoterms",
                table: "Products",
                type: "nvarchar(50)",
                maxLength: 50,
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "LeadTimeDays",
                table: "Products",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "MOQ",
                table: "Products",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "MOQCartons",
                table: "Products",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "PalletsPerContainer20ft",
                table: "Products",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "PalletsPerContainer40ft",
                table: "Products",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "PaymentTerms",
                table: "Products",
                type: "nvarchar(100)",
                maxLength: 100,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "PreferredPort",
                table: "Products",
                type: "nvarchar(200)",
                maxLength: 200,
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "SupplierId",
                table: "Products",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "SupplierProductCode",
                table: "Products",
                type: "nvarchar(100)",
                maxLength: 100,
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "UnitWholesalePrice",
                table: "Products",
                type: "decimal(18,2)",
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_Products_SupplierId",
                table: "Products",
                column: "SupplierId");

            migrationBuilder.AddForeignKey(
                name: "FK_Products_FdxUsers_SupplierId",
                table: "Products",
                column: "SupplierId",
                principalTable: "FdxUsers",
                principalColumn: "Id",
                onDelete: ReferentialAction.SetNull);
            
            // Migrate existing data from SupplierProducts to Products
            migrationBuilder.Sql(@"
                UPDATE p
                SET p.SupplierId = sd.UserId,
                    p.UnitWholesalePrice = sp.UnitWholesalePrice,
                    p.CartonWholesalePrice = sp.CartonWholesalePrice,
                    p.Currency = sp.Currency,
                    p.Incoterms = sp.Incoterms,
                    p.PaymentTerms = sp.PaymentTerms,
                    p.MOQ = sp.MinimumOrderQuantity,
                    p.MOQCartons = sp.MinimumOrderCartons,
                    p.CartonsPerContainer20ft = sp.CartonsPerContainer20ft,
                    p.CartonsPerContainer40ft = sp.CartonsPerContainer40ft,
                    p.PalletsPerContainer20ft = sp.PalletsPerContainer20ft,
                    p.PalletsPerContainer40ft = sp.PalletsPerContainer40ft,
                    p.PreferredPort = sp.ShippingPort,
                    p.LeadTimeDays = sp.LeadTimeDays,
                    p.SupplierProductCode = sp.SupplierProductCode
                FROM Products p
                INNER JOIN SupplierProducts sp ON p.Id = sp.ProductId
                INNER JOIN SupplierDetails sd ON sp.SupplierDetailsId = sd.Id
                WHERE sp.Id IN (
                    SELECT MIN(sp2.Id)
                    FROM SupplierProducts sp2
                    WHERE sp2.ProductId = p.Id
                    GROUP BY sp2.ProductId
                )
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Products_FdxUsers_SupplierId",
                table: "Products");

            migrationBuilder.DropIndex(
                name: "IX_Products_SupplierId",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "CartonWholesalePrice",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "CartonsPerContainer20ft",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "CartonsPerContainer40ft",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "Currency",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "Incoterms",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "LeadTimeDays",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "MOQ",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "MOQCartons",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "PalletsPerContainer20ft",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "PalletsPerContainer40ft",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "PaymentTerms",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "PreferredPort",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "SupplierId",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "SupplierProductCode",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "UnitWholesalePrice",
                table: "Products");
        }
    }
}
