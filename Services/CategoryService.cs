using FDX.Trading.Models;
using System.Text.RegularExpressions;

namespace FDX.Trading.Services;

public class CategoryService
{
    /// <summary>
    /// Detects category type based on text content (company name, description, category field)
    /// </summary>
    public static CategoryType DetectCategory(string companyName, string description, string category, bool isBuyer)
    {
        // TODO: Fix this method when CategoryData structure is updated
        return CategoryType.Other;
        
        /*var searchText = $"{companyName} {description} {category}".ToLower();
        
        // Check each category's keywords
        foreach (var cat in CategoryData.Categories.Values)
        {
            // Skip contractor categories if buyer, and vice versa
            if (isBuyer && cat.IsContractor) continue;
            if (!isBuyer && !cat.IsContractor && cat.Type != CategoryType.Other) continue;
            
            foreach (var keyword in cat.Keywords)
            {
                if (searchText.Contains(keyword.ToLower()))
                {
                    return cat.Type;
                }
            }
        }
        
        // Special cases for known companies
        var companyLower = companyName.ToLower();
        
        // Buyers
        if (companyLower.Contains("carrefour")) return CategoryType.SupermarketChain;
        if (companyLower.Contains("dor alon") || companyLower.Contains("alonit")) return CategoryType.ConvenienceStore;
        if (companyLower.Contains("shufersal")) return CategoryType.SupermarketChain;
        if (companyLower.Contains("cohen") && searchText.Contains("wholesale")) return CategoryType.WholesaleDistributor;
        if (companyLower.Contains("foodz")) return CategoryType.RetailChain;
        if (companyLower.Contains("organic") || companyLower.Contains("ha'sade")) return CategoryType.SpecialtyStore;
        
        // Contractors
        if (companyLower.Contains("ups") || companyLower.Contains("dhl") || 
            companyLower.Contains("fedex") || companyLower.Contains("tnt")) return CategoryType.CourierLogistics;
        if (companyLower.Contains("kosher") || companyLower.Contains("rabbi")) return CategoryType.KosherCertification;
        
        return CategoryType.Other;*/
    }
    
    /// <summary>
    /// Extracts a short business type from long description
    /// </summary>
    public static string ExtractBusinessType(string description, CategoryType category)
    {
        if (string.IsNullOrWhiteSpace(description))
        {
            return category.ToString();
        }
        
        // Try to extract first sentence or key phrase
        var sentences = description.Split(new[] { '.', '!', '?' }, StringSplitOptions.RemoveEmptyEntries);
        if (sentences.Length > 0)
        {
            var firstSentence = sentences[0].Trim();
            
            // Look for "is a" pattern
            var isAPattern = @"is\s+a[n]?\s+([^,\.]+)";
            var match = Regex.Match(firstSentence, isAPattern, RegexOptions.IgnoreCase);
            if (match.Success)
            {
                var extracted = match.Groups[1].Value.Trim();
                if (extracted.Length <= 50)
                {
                    return CapitalizeWords(extracted);
                }
            }
            
            // Look for "specializing in" pattern
            var specializingPattern = @"specializing\s+in\s+([^,\.]+)";
            match = Regex.Match(firstSentence, specializingPattern, RegexOptions.IgnoreCase);
            if (match.Success)
            {
                return "Specialist in " + CapitalizeWords(match.Groups[1].Value.Trim());
            }
            
            // If first sentence is short enough, use it
            if (firstSentence.Length <= 50)
            {
                return firstSentence;
            }
        }
        
        // Fallback to category name
        return category.ToString();
    }
    
    /// <summary>
    /// Cleans and shortens category/description text
    /// </summary>
    public static string CleanCategoryText(string text, int maxLength = 30)
    {
        if (string.IsNullOrWhiteSpace(text))
            return "";
        
        // Remove special characters and extra spaces
        text = Regex.Replace(text, @"[*\n\r\t]", " ");
        text = Regex.Replace(text, @"\s+", " ");
        text = text.Trim();
        
        // If it's a list (contains commas), take first item
        if (text.Contains(','))
        {
            var parts = text.Split(',');
            text = parts[0].Trim();
        }
        
        // Truncate if too long
        if (text.Length > maxLength)
        {
            text = text.Substring(0, maxLength - 3) + "...";
        }
        
        return text;
    }
    
    private static string CapitalizeWords(string text)
    {
        if (string.IsNullOrEmpty(text))
            return text;
        
        var words = text.Split(' ');
        for (int i = 0; i < words.Length; i++)
        {
            if (words[i].Length > 0)
            {
                words[i] = char.ToUpper(words[i][0]) + words[i].Substring(1).ToLower();
            }
        }
        return string.Join(" ", words);
    }
    
    /// <summary>
    /// Process and categorize imported user data
    /// </summary>
    public static void ProcessUserCategory(User user, string originalCategory, string originalDescription)
    {
        // Detect category
        user.CategoryId = DetectCategory(
            user.CompanyName, 
            originalDescription ?? originalCategory ?? "", 
            originalCategory ?? "",
            user.Type == UserType.Buyer
        );
        
        // Extract business type
        user.BusinessType = ExtractBusinessType(
            originalDescription ?? originalCategory ?? "", 
            user.CategoryId.Value
        );
        
        // Store full description if it's long
        if (!string.IsNullOrWhiteSpace(originalDescription) && originalDescription.Length > 100)
        {
            user.FullDescription = originalDescription;
            user.Category = CleanCategoryText(originalCategory ?? user.BusinessType);
        }
        else if (!string.IsNullOrWhiteSpace(originalCategory))
        {
            // Short category - just clean it
            user.Category = CleanCategoryText(originalCategory);
            user.FullDescription = "";
        }
        else
        {
            // No data - use category name
            user.Category = ((CategoryType)user.CategoryId.Value).ToString();
            user.FullDescription = "";
        }
    }
}