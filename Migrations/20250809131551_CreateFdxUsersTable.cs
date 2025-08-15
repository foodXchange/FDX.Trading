using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace FDX.Trading.Migrations
{
    /// <inheritdoc />
    public partial class CreateFdxUsersTable : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "FdxUsers",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    Username = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    Password = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    Email = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    CompanyName = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    Type = table.Column<int>(type: "int", nullable: false),
                    Country = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    PhoneNumber = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    Website = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    Address = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    Category = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    CategoryId = table.Column<int>(type: "int", nullable: true),
                    BusinessType = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    FullDescription = table.Column<string>(type: "nvarchar(2000)", maxLength: 2000, nullable: false),
                    SubCategories = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    LastLogin = table.Column<DateTime>(type: "datetime2", nullable: true),
                    IsActive = table.Column<bool>(type: "bit", nullable: false),
                    RequiresPasswordChange = table.Column<bool>(type: "bit", nullable: false),
                    DataComplete = table.Column<bool>(type: "bit", nullable: false),
                    Verification = table.Column<int>(type: "int", nullable: false),
                    AlternateEmails = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    DisplayName = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    ImportNotes = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ImportedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    OriginalId = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_FdxUsers", x => x.Id);
                });

            migrationBuilder.InsertData(
                table: "FdxUsers",
                columns: new[] { "Id", "Address", "AlternateEmails", "BusinessType", "Category", "CategoryId", "CompanyName", "Country", "CreatedAt", "DataComplete", "DisplayName", "Email", "FullDescription", "ImportNotes", "ImportedAt", "IsActive", "LastLogin", "OriginalId", "Password", "PhoneNumber", "RequiresPasswordChange", "SubCategories", "Type", "Username", "Verification", "Website" },
                values: new object[] { 1, "", null, "", "", null, "FDX Trading", "Israel", new DateTime(2025, 1, 9, 12, 0, 0, 0, DateTimeKind.Unspecified), true, null, "udi@fdx.trading", "", null, null, true, new DateTime(2025, 1, 9, 12, 0, 0, 0, DateTimeKind.Unspecified), null, "FDX2030!", "", false, "", 0, "udi@fdx.trading", 0, "" });

            migrationBuilder.CreateIndex(
                name: "IX_FdxUsers_Email",
                table: "FdxUsers",
                column: "Email");

            migrationBuilder.CreateIndex(
                name: "IX_FdxUsers_IsActive",
                table: "FdxUsers",
                column: "IsActive");

            migrationBuilder.CreateIndex(
                name: "IX_FdxUsers_Type",
                table: "FdxUsers",
                column: "Type");

            migrationBuilder.CreateIndex(
                name: "IX_FdxUsers_Username",
                table: "FdxUsers",
                column: "Username",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "FdxUsers");
        }
    }
}
