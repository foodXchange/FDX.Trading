using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace FDX.Trading.Migrations
{
    /// <inheritdoc />
    public partial class AddRequestAttributes : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "ContainerLoading",
                table: "Requests",
                type: "nvarchar(50)",
                maxLength: 50,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "FreeFromOptions",
                table: "Requests",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Incoterms",
                table: "Requests",
                type: "nvarchar(50)",
                maxLength: 50,
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsFreeFrom",
                table: "Requests",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<bool>(
                name: "IsKosher",
                table: "Requests",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<string>(
                name: "KosherPreference",
                table: "Requests",
                type: "nvarchar(50)",
                maxLength: 50,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "PalletSize",
                table: "Requests",
                type: "nvarchar(100)",
                maxLength: 100,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "PreferredCountries",
                table: "Requests",
                type: "nvarchar(max)",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "ContainerLoading",
                table: "Requests");

            migrationBuilder.DropColumn(
                name: "FreeFromOptions",
                table: "Requests");

            migrationBuilder.DropColumn(
                name: "Incoterms",
                table: "Requests");

            migrationBuilder.DropColumn(
                name: "IsFreeFrom",
                table: "Requests");

            migrationBuilder.DropColumn(
                name: "IsKosher",
                table: "Requests");

            migrationBuilder.DropColumn(
                name: "KosherPreference",
                table: "Requests");

            migrationBuilder.DropColumn(
                name: "PalletSize",
                table: "Requests");

            migrationBuilder.DropColumn(
                name: "PreferredCountries",
                table: "Requests");
        }
    }
}
