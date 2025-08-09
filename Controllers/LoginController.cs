using Microsoft.AspNetCore.Mvc;
using FDX.Trading.Models;

namespace FDX.Trading.Controllers;

[ApiController]
[Route("api/[controller]")]
public class LoginController : ControllerBase
{
    // Simple in-memory user storage
    private static List<User> users = new List<User>
    {
        new User { 
            Id = 1, 
            Username = "udi@fdx.trading", 
            Password = "FDX2030!", 
            Email = "udi@fdx.trading",
            CompanyName = "FDX Trading",
            Type = UserType.Admin,
            Country = "Israel",
            IsActive = true
        }
    };
    private static int nextId = 2;

    [HttpPost("register")]
    public IActionResult Register([FromBody] LoginRequest request)
    {
        // Check if user exists
        if (users.Any(u => u.Username == request.Username))
            return Ok(new { success = false, message = "User already exists" });

        // Create new user
        var user = new User
        {
            Id = nextId++,
            Username = request.Username,
            Password = request.Password,
            Email = $"{request.Username}@example.com"
        };

        users.Add(user);

        return Ok(new { 
            success = true, 
            message = "Registration successful",
            userId = user.Id,
            username = user.Username
        });
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest request)
    {
        // Find user
        var user = users.FirstOrDefault(u => 
            u.Username == request.Username && 
            u.Password == request.Password);

        if (user == null)
            return Ok(new { success = false, message = "Invalid username or password" });

        // Update last login
        user.LastLogin = DateTime.Now;

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
    
    // Make users accessible to UsersController
    public static List<User> GetUsers() => users;
    public static int GetNextId() => nextId++;
}