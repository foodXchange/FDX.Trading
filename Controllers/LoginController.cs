using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using FDX.Trading.Models;
using FDX.Trading.Data;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class LoginController : ControllerBase
{
    private readonly FdxTradingContext _context;
    
    public LoginController(FdxTradingContext context)
    {
        _context = context;
    }

    [HttpPost("register")]
    public async Task<IActionResult> Register([FromBody] LoginRequest request)
    {
        // Check if user exists
        if (await _context.FdxUsers.AnyAsync(u => u.Username == request.Username))
            return Ok(new { success = false, message = "User already exists" });

        // Create new user
        var user = new User
        {
            Username = request.Username,
            Password = request.Password,
            Email = $"{request.Username}@example.com",
            CompanyName = "",
            Type = UserType.Buyer,
            Country = "",
            PhoneNumber = "",
            Website = "",
            Address = "",
            Category = "",
            BusinessType = "",
            FullDescription = "",
            SubCategories = "",
            CreatedAt = DateTime.Now,
            IsActive = true,
            DataComplete = false,
            RequiresPasswordChange = true,
            Verification = VerificationStatus.Pending
        };

        _context.FdxUsers.Add(user);
        await _context.SaveChangesAsync();

        return Ok(new { 
            success = true, 
            message = "Registration successful",
            userId = user.Id,
            username = user.Username
        });
    }

    [HttpPost("login")]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        // Find user
        var user = await _context.FdxUsers.FirstOrDefaultAsync(u => 
            u.Username == request.Username && 
            u.Password == request.Password);

        if (user == null)
            return Ok(new { success = false, message = "Invalid username or password" });

        // Update last login
        user.LastLogin = DateTime.Now;
        await _context.SaveChangesAsync();

        return Ok(new { 
            success = true, 
            message = "Login successful",
            userId = user.Id,
            username = user.Username,
            userType = user.Type.ToString(),
            companyName = user.CompanyName
        });
    }

    [HttpGet("test")]
    public IActionResult Test()
    {
        return Ok(new { message = "API is working!", time = DateTime.Now });
    }
}