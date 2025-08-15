using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace FDX.Trading.Migrations
{
    /// <inheritdoc />
    public partial class PopulateInitialPriceHistory : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // Populate ProductPriceHistory with existing prices from Products table
            migrationBuilder.Sql(@"
                INSERT INTO ProductPriceHistory (ProductId, SupplierId, UnitPrice, Currency, EffectiveDate, CreatedBy, CreatedAt, ChangeReason, IsActive)
                SELECT 
                    p.Id as ProductId,
                    p.SupplierId,
                    p.UnitWholesalePrice as UnitPrice,
                    ISNULL(p.Currency, 'USD') as Currency,
                    ISNULL(p.CreatedAt, GETDATE()) as EffectiveDate,
                    'Initial Import' as CreatedBy,
                    GETDATE() as CreatedAt,
                    'Initial price from product catalog' as ChangeReason,
                    1 as IsActive
                FROM Products p
                WHERE p.UnitWholesalePrice IS NOT NULL
                    AND p.UnitWholesalePrice > 0
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Remove the initial import prices
            migrationBuilder.Sql(@"
                DELETE FROM ProductPriceHistory 
                WHERE CreatedBy = 'Initial Import' 
                    AND ChangeReason = 'Initial price from product catalog'
            ");
        }
    }
}
