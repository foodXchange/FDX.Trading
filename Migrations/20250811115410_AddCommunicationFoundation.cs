using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace FDX.Trading.Migrations
{
    /// <inheritdoc />
    public partial class AddCommunicationFoundation : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "CommunicationTemplates",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    TemplateName = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    Type = table.Column<int>(type: "int", nullable: false),
                    Subject = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    Body = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    AvailableVariables = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    DefaultValues = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    AllowedRoles = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Language = table.Column<string>(type: "nvarchar(10)", maxLength: 10, nullable: false),
                    Category = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: true),
                    IsActive = table.Column<bool>(type: "bit", nullable: false),
                    IsSystem = table.Column<bool>(type: "bit", nullable: false),
                    CreatedByUserId = table.Column<int>(type: "int", nullable: true),
                    CreatedById = table.Column<int>(type: "int", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UsageCount = table.Column<int>(type: "int", nullable: false),
                    LastUsedAt = table.Column<DateTime>(type: "datetime2", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_CommunicationTemplates", x => x.Id);
                    table.ForeignKey(
                        name: "FK_CommunicationTemplates_FdxUsers_CreatedById",
                        column: x => x.CreatedById,
                        principalTable: "FdxUsers",
                        principalColumn: "Id");
                });

            migrationBuilder.CreateTable(
                name: "ConsoleMessages",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    ConsoleId = table.Column<int>(type: "int", nullable: false),
                    StageId = table.Column<int>(type: "int", nullable: true),
                    SenderId = table.Column<int>(type: "int", nullable: false),
                    RecipientId = table.Column<int>(type: "int", nullable: true),
                    ParentMessageId = table.Column<int>(type: "int", nullable: true),
                    MessageType = table.Column<int>(type: "int", nullable: false),
                    Priority = table.Column<int>(type: "int", nullable: false),
                    Status = table.Column<int>(type: "int", nullable: false),
                    Subject = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    Content = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Metadata = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    AttachmentPath = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    AttachmentName = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    ReadAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    RepliedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    RequiresEmail = table.Column<bool>(type: "bit", nullable: false),
                    EmailSent = table.Column<bool>(type: "bit", nullable: false),
                    EmailSentAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    MentionedUsers = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ConsoleMessages", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ConsoleMessages_ConsoleMessages_ParentMessageId",
                        column: x => x.ParentMessageId,
                        principalTable: "ConsoleMessages",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_ConsoleMessages_Consoles_ConsoleId",
                        column: x => x.ConsoleId,
                        principalTable: "Consoles",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ConsoleMessages_FdxUsers_RecipientId",
                        column: x => x.RecipientId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_ConsoleMessages_FdxUsers_SenderId",
                        column: x => x.SenderId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ConsoleMessages_WorkflowStages_StageId",
                        column: x => x.StageId,
                        principalTable: "WorkflowStages",
                        principalColumn: "Id");
                });

            migrationBuilder.CreateTable(
                name: "NotificationQueues",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    RecipientUserId = table.Column<int>(type: "int", nullable: false),
                    ConsoleId = table.Column<int>(type: "int", nullable: true),
                    MessageId = table.Column<int>(type: "int", nullable: true),
                    Channel = table.Column<int>(type: "int", nullable: false),
                    Category = table.Column<int>(type: "int", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    Body = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: false),
                    Data = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsProcessed = table.Column<bool>(type: "bit", nullable: false),
                    RetryCount = table.Column<int>(type: "int", nullable: false),
                    ProcessedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ErrorMessage = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    ScheduledFor = table.Column<DateTime>(type: "datetime2", nullable: false),
                    ExpiresAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    EmailTo = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    EmailCc = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    EmailTemplate = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Priority = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_NotificationQueues", x => x.Id);
                    table.ForeignKey(
                        name: "FK_NotificationQueues_ConsoleMessages_MessageId",
                        column: x => x.MessageId,
                        principalTable: "ConsoleMessages",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_NotificationQueues_Consoles_ConsoleId",
                        column: x => x.ConsoleId,
                        principalTable: "Consoles",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_NotificationQueues_FdxUsers_RecipientUserId",
                        column: x => x.RecipientUserId,
                        principalTable: "FdxUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_CommunicationTemplates_CreatedById",
                table: "CommunicationTemplates",
                column: "CreatedById");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleMessages_ConsoleId",
                table: "ConsoleMessages",
                column: "ConsoleId");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleMessages_ParentMessageId",
                table: "ConsoleMessages",
                column: "ParentMessageId");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleMessages_RecipientId",
                table: "ConsoleMessages",
                column: "RecipientId");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleMessages_SenderId",
                table: "ConsoleMessages",
                column: "SenderId");

            migrationBuilder.CreateIndex(
                name: "IX_ConsoleMessages_StageId",
                table: "ConsoleMessages",
                column: "StageId");

            migrationBuilder.CreateIndex(
                name: "IX_NotificationQueues_ConsoleId",
                table: "NotificationQueues",
                column: "ConsoleId");

            migrationBuilder.CreateIndex(
                name: "IX_NotificationQueues_MessageId",
                table: "NotificationQueues",
                column: "MessageId");

            migrationBuilder.CreateIndex(
                name: "IX_NotificationQueues_RecipientUserId",
                table: "NotificationQueues",
                column: "RecipientUserId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "CommunicationTemplates");

            migrationBuilder.DropTable(
                name: "NotificationQueues");

            migrationBuilder.DropTable(
                name: "ConsoleMessages");
        }
    }
}
