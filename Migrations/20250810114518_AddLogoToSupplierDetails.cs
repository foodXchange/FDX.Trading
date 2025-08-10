using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace FDX.Trading.Migrations
{
    /// <inheritdoc />
    public partial class AddLogoToSupplierDetails : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "Logo",
                table: "SupplierDetails",
                type: "nvarchar(max)",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Logo",
                table: "SupplierDetails");
        }
    }
}
