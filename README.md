# FoodXchange Trading Platform

A modern B2B food trading platform built with .NET 9, Blazor United, and Clean Architecture principles.

## Architecture Overview

```
FoodXchange/
├── FoodXchange.Domain/          # Core business logic & entities
│   ├── Entities/               # Domain entities (Product, Supplier, etc.)
│   └── ValueObjects/           # Value objects (Money, Email, Address)
│
├── FoodXchange.Application/     # Application services & use cases
│   ├── Services/               # Application services
│   ├── DTOs/                   # Data transfer objects
│   └── Interfaces/             # Service interfaces
│
├── FoodXchange.Infrastructure/  # Data access & external services
│   ├── Data/                   # EF Core DbContext & configurations
│   ├── Repositories/           # Repository implementations
│   └── Services/               # External service integrations
│
├── FoodXchange.Api/            # REST API with minimal APIs
│   ├── Endpoints/              # API endpoint definitions
│   ├── Middleware/             # Custom middleware
│   └── Program.cs              # API configuration
│
└── FoodXchange.App/            # Blazor Web App (UI)
    ├── Components/             # Blazor components
    ├── Pages/                  # Blazor pages
    └── Program.cs              # Web app configuration
```

## Technology Stack

- **.NET 9** - Latest framework version
- **Blazor United** - Unified web app model with SSR and interactivity
- **Entity Framework Core 9** - Data access
- **Azure SQL Database** - Primary data store
- **Azure OpenAI** - AI capabilities via Microsoft.Extensions.AI
- **Application Insights** - Monitoring and observability
- **Clean Architecture** - Separation of concerns

## Render Modes

- **Default**: Server-Side Rendering (SSR) for fastest initial load
- **Interactive Server**: For real-time features (dashboards, chat)
- **WebAssembly**: For offline-capable features (future)

## Key Features

- Product catalog management
- Supplier management
- Order processing
- AI-powered search and recommendations
- Real-time analytics dashboard
- Multi-tenant support (future)

## Getting Started

### Prerequisites

- .NET 9 SDK
- SQL Server or Azure SQL Database
- Azure OpenAI resource (optional)

### Configuration

1. Update connection string in `appsettings.json`
2. Configure Azure OpenAI endpoint and key
3. Set up Application Insights connection

### Running the Application

```bash
# Run the API
cd FoodXchange.Api
dotnet run

# Run the Blazor App
cd FoodXchange.App
dotnet run
```

## Development Principles

1. **Domain-Driven Design** - Rich domain models with business logic
2. **CQRS** - Separate read and write operations (future)
3. **Repository Pattern** - Abstract data access
4. **Dependency Injection** - Loose coupling
5. **Value Objects** - Type safety for domain concepts
6. **Soft Deletes** - Data retention for audit trails

## Security

- Azure AD / Entra ID integration (planned)
- Managed Identity for Azure resources
- Key Vault for secrets management
- Row-level security in database

## Performance Optimizations

- Response caching for static content
- Distributed caching with Redis (future)
- Lazy loading for related entities
- Pagination for large datasets
- CDN for static assets

## Monitoring

- Application Insights for telemetry
- Health checks endpoint (`/health`)
- Structured logging with Serilog
- Custom metrics and dashboards