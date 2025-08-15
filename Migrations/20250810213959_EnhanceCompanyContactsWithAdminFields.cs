using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace FDX.Trading.Migrations
{
    /// <inheritdoc />
    public partial class EnhanceCompanyContactsWithAdminFields : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "ContactId",
                table: "FdxUsers",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "CanManageContacts",
                table: "CompanyContacts",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<int>(
                name: "CreatedByUserId",
                table: "CompanyContacts",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsOrganizationAdmin",
                table: "CompanyContacts",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<int>(
                name: "UpdatedByUserId",
                table: "CompanyContacts",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "UserId",
                table: "CompanyContacts",
                type: "int",
                nullable: true);

            migrationBuilder.UpdateData(
                table: "FdxUsers",
                keyColumn: "Id",
                keyValue: 1,
                column: "ContactId",
                value: null);

            migrationBuilder.CreateIndex(
                name: "IX_CompanyContacts_UserId",
                table: "CompanyContacts",
                column: "UserId");

            migrationBuilder.AddForeignKey(
                name: "FK_CompanyContacts_FdxUsers_UserId",
                table: "CompanyContacts",
                column: "UserId",
                principalTable: "FdxUsers",
                principalColumn: "Id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_CompanyContacts_FdxUsers_UserId",
                table: "CompanyContacts");

            migrationBuilder.DropIndex(
                name: "IX_CompanyContacts_UserId",
                table: "CompanyContacts");

            migrationBuilder.DropColumn(
                name: "ContactId",
                table: "FdxUsers");

            migrationBuilder.DropColumn(
                name: "CanManageContacts",
                table: "CompanyContacts");

            migrationBuilder.DropColumn(
                name: "CreatedByUserId",
                table: "CompanyContacts");

            migrationBuilder.DropColumn(
                name: "IsOrganizationAdmin",
                table: "CompanyContacts");

            migrationBuilder.DropColumn(
                name: "UpdatedByUserId",
                table: "CompanyContacts");

            migrationBuilder.DropColumn(
                name: "UserId",
                table: "CompanyContacts");
        }
    }
}
