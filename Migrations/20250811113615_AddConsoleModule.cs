using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace FDX.Trading.Migrations
{
    /// <inheritdoc />
    public partial class AddConsoleModule : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Consoles",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ConsoleCode = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    Title = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    Type = table.Column<int>(type: "int", nullable: false),
                    Priority = table.Column<int>(type: "int", nullable: false),
                    Status = table.Column<int>(type: "int", nullable: false),
                    SourceType = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    SourceId = table.Column<int>(type: "int", nullable: true),
                    OwnerId = table.Column<int>(type: "int", nullable: false),
                    CurrentStageNumber = table.Column<int>(type: "int", nullable: false),
                    Metadata = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CompletedAt = table.Column<DateTime>(type: "datetime2", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Consoles", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Consoles_FdxUsers_OwnerId",
                        column: x => x.OwnerId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_Consoles_Requests_SourceId",
                        column: x => x.SourceId,
                        principalTable: "Requests",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "ConsoleParticipants",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ConsoleId = table.Column<int>(type: "int", nullable: false),
                    UserId = table.Column<int>(type: "int", nullable: false),
                    Role = table.Column<int>(type: "int", nullable: false),
                    Permissions = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    AssignedStages = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    JoinedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    LastActivityAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    IsActive = table.Column<bool>(type: "bit", nullable: false),
                    CanEdit = table.Column<bool>(type: "bit", nullable: false),
                    CanApprove = table.Column<bool>(type: "bit", nullable: false),
                    CanReassign = table.Column<bool>(type: "bit", nullable: false),
                    Notes = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ConsoleParticipants", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ConsoleParticipants_Consoles_ConsoleId",
                        column: x => x.ConsoleId,
                        principalTable: "Consoles",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ConsoleParticipants_FdxUsers_UserId",
                        column: x => x.UserId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "WorkflowStages",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ConsoleId = table.Column<int>(type: "int", nullable: false),
                    StageNumber = table.Column<int>(type: "int", nullable: false),
                    StageName = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    StageType = table.Column<int>(type: "int", nullable: false),
                    Status = table.Column<int>(type: "int", nullable: false),
                    RequiredRole = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    AssignedUserId = table.Column<int>(type: "int", nullable: true),
                    DueDate = table.Column<DateTime>(type: "datetime2", nullable: true),
                    StartedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CompletedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ValidationRules = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    OutputData = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Dependencies = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsParallel = table.Column<bool>(type: "bit", nullable: false),
                    IsCritical = table.Column<bool>(type: "bit", nullable: false),
                    IsOptional = table.Column<bool>(type: "bit", nullable: false),
                    Description = table.Column<string>(type: "nvarchar(2000)", maxLength: 2000, nullable: true),
                    Instructions = table.Column<string>(type: "nvarchar(2000)", maxLength: 2000, nullable: true),
                    EstimatedMinutes = table.Column<int>(type: "int", nullable: false),
                    ActualMinutes = table.Column<int>(type: "int", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_WorkflowStages", x => x.Id);
                    table.ForeignKey(
                        name: "FK_WorkflowStages_Consoles_ConsoleId",
                        column: x => x.ConsoleId,
                        principalTable: "Consoles",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_WorkflowStages_FdxUsers_AssignedUserId",
                        column: x => x.AssignedUserId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "ConsoleActions",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ConsoleId = table.Column<int>(type: "int", nullable: false),
                    StageId = table.Column<int>(type: "int", nullable: true),
                    UserId = table.Column<int>(type: "int", nullable: false),
                    ActionType = table.Column<int>(type: "int", nullable: false),
                    ActionData = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Description = table.Column<string>(type: "nvarchar(2000)", maxLength: 2000, nullable: true),
                    Timestamp = table.Column<DateTime>(type: "datetime2", nullable: false),
                    IPAddress = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    IsSystemAction = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ConsoleActions", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ConsoleActions_Consoles_ConsoleId",
                        column: x => x.ConsoleId,
                        principalTable: "Consoles",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ConsoleActions_FdxUsers_UserId",
                        column: x => x.UserId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_ConsoleActions_WorkflowStages_StageId",
                        column: x => x.StageId,
                        principalTable: "WorkflowStages",
                        principalColumn: "Id");
                });

            migrationBuilder.CreateTable(
                name: "ConsoleDocuments",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ConsoleId = table.Column<int>(type: "int", nullable: false),
                    StageId = table.Column<int>(type: "int", nullable: true),
                    FileName = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    FilePath = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    DocumentType = table.Column<int>(type: "int", nullable: false),
                    FileSize = table.Column<long>(type: "bigint", nullable: false),
                    MimeType = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    UploadedByUserId = table.Column<int>(type: "int", nullable: false),
                    UploadedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    IsApproved = table.Column<bool>(type: "bit", nullable: false),
                    ApprovedByUserId = table.Column<int>(type: "int", nullable: true),
                    ApprovedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    Description = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: true),
                    Tags = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ConsoleDocuments", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ConsoleDocuments_Consoles_ConsoleId",
                        column: x => x.ConsoleId,
                        principalTable: "Consoles",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ConsoleDocuments_FdxUsers_UploadedByUserId",
                        column: x => x.UploadedByUserId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_ConsoleDocuments_WorkflowStages_StageId",
                        column: x => x.StageId,
                        principalTable: "WorkflowStages",
                        principalColumn: "Id");
                });

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleActions_ActionType",
                table: "ConsoleActions",
                column: "ActionType");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleActions_ConsoleId",
                table: "ConsoleActions",
                column: "ConsoleId");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleActions_StageId",
                table: "ConsoleActions",
                column: "StageId");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleActions_Timestamp",
                table: "ConsoleActions",
                column: "Timestamp");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleActions_UserId",
                table: "ConsoleActions",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleDocuments_ConsoleId",
                table: "ConsoleDocuments",
                column: "ConsoleId");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleDocuments_DocumentType",
                table: "ConsoleDocuments",
                column: "DocumentType");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleDocuments_StageId",
                table: "ConsoleDocuments",
                column: "StageId");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleDocuments_UploadedAt",
                table: "ConsoleDocuments",
                column: "UploadedAt");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleDocuments_UploadedByUserId",
                table: "ConsoleDocuments",
                column: "UploadedByUserId");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleParticipants_ConsoleId_UserId",
                table: "ConsoleParticipants",
                columns: new[] { "ConsoleId", "UserId" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleParticipants_IsActive",
                table: "ConsoleParticipants",
                column: "IsActive");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleParticipants_Role",
                table: "ConsoleParticipants",
                column: "Role");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleParticipants_UserId",
                table: "ConsoleParticipants",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_Consoles_ConsoleCode",
                table: "Consoles",
                column: "ConsoleCode",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Consoles_OwnerId",
                table: "Consoles",
                column: "OwnerId");

            migrationBuilder.CreateIndex(
                name: "IX_Consoles_Priority",
                table: "Consoles",
                column: "Priority");

            migrationBuilder.CreateIndex(
                name: "IX_Consoles_SourceId",
                table: "Consoles",
                column: "SourceId");

            migrationBuilder.CreateIndex(
                name: "IX_Consoles_Status",
                table: "Consoles",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_Consoles_Type",
                table: "Consoles",
                column: "Type");

            migrationBuilder.CreateIndex(
                name: "IX_WorkflowStages_AssignedUserId",
                table: "WorkflowStages",
                column: "AssignedUserId");

            migrationBuilder.CreateIndex(
                name: "IX_WorkflowStages_ConsoleId",
                table: "WorkflowStages",
                column: "ConsoleId");

            migrationBuilder.CreateIndex(
                name: "IX_WorkflowStages_ConsoleId_StageNumber",
                table: "WorkflowStages",
                columns: new[] { "ConsoleId", "StageNumber" });

            migrationBuilder.CreateIndex(
                name: "IX_WorkflowStages_StageType",
                table: "WorkflowStages",
                column: "StageType");

            migrationBuilder.CreateIndex(
                name: "IX_WorkflowStages_Status",
                table: "WorkflowStages",
                column: "Status");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "ConsoleActions");

            migrationBuilder.DropTable(
                name: "ConsoleDocuments");

            migrationBuilder.DropTable(
                name: "ConsoleParticipants");

            migrationBuilder.DropTable(
                name: "WorkflowStages");

            migrationBuilder.DropTable(
                name: "Consoles");
        }
    }
}
