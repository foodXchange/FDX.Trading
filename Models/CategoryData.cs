using System.Collections.Generic;

namespace FDX.Trading.Models;

public static class CategoryData
{
    public static string GetDisplayName(CategoryType category)
    {
        return category.ToString();
    }

    public static string GetDisplayName(string category)
    {
        return category ?? "Unknown";
    }

    public static string GetColorCode(CategoryType category)
    {
        // Return a color code based on category type
        return category switch
        {
            CategoryType.SupermarketChain => "#4A90E2",
            CategoryType.WholesaleDistributor => "#7B68EE",
            CategoryType.Manufacturer => "#FF6B6B",
            CategoryType.Importer => "#4ECDC4",
            CategoryType.Exporter => "#45B7D1",
            CategoryType.Distributor => "#96CEB4",
            CategoryType.LogisticsProvider => "#FECA57",
            _ => "#B2BEC3"
        };
    }

    public static string GetColorCode(string category)
    {
        // Return a color code based on category
        return category switch
        {
            "Edible Oils" => "#FFB366",
            "Fresh Produce" => "#66FF66",
            "Frozen Foods" => "#66B3FF",
            "Dairy Products" => "#FFE666",
            "Meat & Poultry" => "#FF6666",
            _ => "#999999"
        };
    }

    public static string GetCategory(string categoryName)
    {
        return categoryName ?? "Other";
    }
    public static List<string> Categories { get; } = new List<string>
    {
        "Edible Oils",
        "Fresh Produce",
        "Frozen Foods",
        "Dairy Products",
        "Meat & Poultry",
        "Seafood",
        "Grains & Cereals",
        "Beverages",
        "Snacks & Confectionery",
        "Spices & Seasonings",
        "Bakery Products",
        "Canned Goods",
        "Pasta & Noodles",
        "Sauces & Condiments",
        "Health Foods",
        "Organic Products",
        "Other"
    };

    public static List<string> SubCategories { get; } = new List<string>
    {
        "Vegetable Oils",
        "Olive Oils",
        "Specialty Oils",
        "Vegetables",
        "Fruits",
        "Frozen Vegetables",
        "Frozen Fruits",
        "Frozen Meals",
        "Milk Products",
        "Cheese",
        "Yogurt",
        "Beef",
        "Chicken",
        "Pork",
        "Fresh Fish",
        "Frozen Fish",
        "Shellfish",
        "Rice",
        "Wheat",
        "Corn",
        "Soft Drinks",
        "Juices",
        "Water",
        "Tea & Coffee",
        "Chips",
        "Cookies",
        "Candy",
        "Herbs",
        "Spices",
        "Salt & Pepper",
        "Bread",
        "Cakes",
        "Pastries",
        "Canned Vegetables",
        "Canned Fruits",
        "Canned Meat",
        "Pasta",
        "Instant Noodles",
        "Rice Noodles",
        "Ketchup",
        "Mayonnaise",
        "Mustard",
        "Vitamins",
        "Supplements",
        "Protein Products",
        "Organic Vegetables",
        "Organic Fruits",
        "Organic Grains"
    };
}