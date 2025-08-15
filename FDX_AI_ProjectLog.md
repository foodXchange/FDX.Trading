# FDX AI Project Log

## A. Project State

### Platform Overview
**FoodXchange (FDX)** — Enterprise workflow-driven food trade management platform for sourcing, compliance, labeling, logistics, and collaboration.

### Tech Stack
- **Backend**: 
  - .NET 9 with Blazor United (Clean Architecture)
  - Azure SQL Database (fdx-sql-prod.database.windows.net/fdxdb)
  - Entity Framework Core with migrations
  - Minimal APIs with endpoint groups
  - Domain-Driven Design with aggregates
  
- **Frontend**: 
  - Blazor United (Server-side rendering default)
  - Interactive Server mode enabled
  - WebAssembly-ready components
  - Bootstrap 5 + custom CSS
  - Gradient-based modern UI design
  
- **Azure Services**:
  - Azure SQL with Managed Identity
  - Azure Key Vault for secrets
  - Azure OpenAI (GPT-4) via Microsoft.Extensions.AI
  - Application Insights for monitoring
  - Azure Entra ID (Tenant: 53d5a7a1-e671-49ca-a0cb-03a0e822d023)
  
- **Real-time**: 
  - SignalR for live updates (planned)
  - WebSockets for notifications

### Current Architecture
```
src/
├── FoodXchange.Domain/          # Domain entities, value objects, aggregates
│   ├── Projects/                # Project, ProjectMember
│   ├── Requests/                # PurchaseRequest, RequestLineItem, RequestItemImage
│   ├── Products/                # Product, Category, ProductPrice
│   └── Suppliers/               # Supplier, SupplierContact, SupplierProduct
├── FoodXchange.Application/     # Use cases, services, DTOs
├── FoodXchange.Infrastructure/  # EF Core, repositories, external services
│   └── Data/
│       ├── AppDbContext.cs
│       └── Configurations/     # EF mappings
├── FoodXchange.Api/             # REST API endpoints
│   └── Endpoints/               # RequestEndpoints, ProjectEndpoints
└── FoodXchange.App/             # Blazor UI
    └── Components/
        ├── Projects/            # ProjectHeader.razor
        └── Pages/               # ProjectDashboard.razor
```

### Active Workflows
1. **Project/Console System**:
   - Every Request belongs to a Project (auto-created if needed)
   - ProjectCode format: `FDX-2024-100001` (year + sequence)
   - Buyers automatically added as ProjectMembers with "buyer" role
   
2. **Request Management**:
   - Requests (RFQs) with full procurement details
   - RequestLineItems for product specifications
   - RequestItemImages for visual references
   - Status workflow: Draft → Active → Closed
   
3. **Dual Identity Support**:
   - Legacy: BuyerId (INT) for existing users
   - Modern: UserId (GUID) for new Azure AD users
   - Seamless migration path built-in

### Database Schema (Current)
```sql
Projects (ProjectId, ProjectCode, Name, CreatedAt...)
ProjectMembers (ProjectMemberId, ProjectId, BuyerId, UserId, RoleInProject...)
Requests (Id, ProjectId, RequestNumber, Title, BuyerId, Status...)
RequestItems (Id, RequestId, ProductName, Quantity, Unit...)
RequestItemImages (Id, RequestItemId, ImageUrl, Caption...)
```

## B. Technical Decisions & Standards

### Naming Conventions
- **ProjectCode**: `FDX-{YYYY}-{6-digit-sequence}` (e.g., FDX-2024-100001)
- **RequestNumber**: `REQ-{YYYYMMDD}-{4-digit-sequence}`
- **Database Tables**: Plural names (Projects, Requests)
- **Entity Classes**: Singular PascalCase (Project, PurchaseRequest)
- **API Routes**: `/api/{resource}` (lowercase plural)

### Domain Patterns
- **Aggregate Roots**: Project (for workflow), PurchaseRequest (for RFQs)
- **Value Objects**: Address, Money (planned)
- **Domain Events**: Ready for CQRS implementation
- **Soft Delete**: Global query filters on all entities
- **Audit Fields**: CreatedAt, CreatedBy, ModifiedAt, ModifiedBy

### UI/UX Standards
- **Color Palette**:
  - Primary: Gradient `#667eea → #764ba2` (purple)
  - Success: `#10b981` (green)
  - Warning: `#f59e0b` (amber)
  - Info: `#3b82f6` (blue)
- **Typography**: System fonts with fallback stack
- **Component Style**: Card-based with subtle shadows
- **Animations**: Smooth transitions (0.2s ease)
- **Responsive**: Mobile-first, grid-based layouts

### Security Practices
- **Authentication**: Azure Entra ID (pending full integration)
- **Authorization**: Role-based (buyer, admin, supplier)
- **Database**: Managed Identity for passwordless access
- **Secrets**: Azure Key Vault for all sensitive data
- **API Security**: JWT tokens (planned)

### Code Quality Standards
- **No Comments**: Self-documenting code only
- **Error Handling**: Comprehensive try-catch with logging
- **Async/Await**: Throughout for all I/O operations
- **Dependency Injection**: Constructor injection pattern
- **Testing**: Unit tests for domain logic (pending)

## C. Milestones Log

### 2025-01-15 — Session 1: Azure SQL & Health Checks
- Configured Azure SQL connection with connection string
- Added health checks for SQL Server with retry logic
- Created `/db/verify` endpoint for database diagnostics
- Implemented `/ai/status` endpoint for Azure OpenAI monitoring
- Set up Azure Key Vault integration for secure password storage
- Created PowerShell script for Key Vault setup

### 2025-01-15 — Session 2: Project/Console Foundation
- **Database Schema**:
  - Created Projects table with sequence-based ProjectCode generation
  - Created ProjectMembers table with dual identity support (BuyerId/UserId)
  - Added ProjectId foreign key to existing Requests table
  - SQL migration script with automatic backfill for existing requests
  
- **Domain Models**:
  - Implemented Project aggregate root with member management
  - Created PurchaseRequest entity mapping to Requests table
  - Added RequestLineItem and RequestItemImage entities
  - Business methods for status transitions and updates
  
- **EF Core Configuration**:
  - Full mappings for Project, ProjectMember, PurchaseRequest
  - Relationships configured with proper cascading
  - Unique constraints and indexes optimized
  - Global soft-delete filters applied
  
- **API Endpoints**:
  - POST `/api/requests` with auto-Project creation
  - Automatic buyer assignment as ProjectMember
  - Full CRUD for Projects and Requests
  - GET `/api/requests/by-project/{projectCode}` for filtering
  
- **Blazor Components**:
  - ProjectHeader component with gradient design
  - Live member count and request statistics
  - Slide-in panel for member management
  - ProjectDashboard page with request filtering (All/Active/Draft/Closed)
  - Responsive grid layout for request cards

**Key Achievement**: Zero-friction workflow where creating a Request automatically creates a Project/Console and assigns the buyer as a member.

## D. Next Steps / TODO

[To be determined based on current priorities]

## E. Known Issues & Blockers

### Current Issues
- None critical at this time

### Technical Debt
- Hardcoded "system" user in AppDbContext (needs IHttpContextAccessor)
- Missing comprehensive error handling in API endpoints
- No caching layer for frequently accessed Projects
- SignalR hub not yet implemented

## F. Environment & Configuration

### Local Development
```json
{
  "ConnectionStrings": {
    "Sql": "Server=fdx-sql-prod.database.windows.net;Database=fdxdb;User Id=fdxadmin;Password=***;TrustServerCertificate=true"
  },
  "Azure": {
    "OpenAI": {
      "Endpoint": "https://fdx-openai.openai.azure.com",
      "DeploymentName": "gpt-4-turbo"
    }
  }
}
```

### Azure Resources
- **SQL Server**: fdx-sql-prod.database.windows.net
- **Database**: fdxdb
- **Key Vault**: fdx-keyvault-prod (planned)
- **App Service**: fdx-app-prod (planned)

### Git Repository State
- **Branch**: main
- **Latest Commit**: "Milestone 16: Modern UI Transformation & Azure AI Integration"
- **Modified Files**: Multiple pending (Components/, Controllers/, Services/)

## G. Session Instructions for AI

### When Starting a New Session
1. Read this entire document first
2. Check section D for immediate TODOs
3. Review section E for any blockers
4. Ask user: "Ready to continue with [next HIGH priority item]?"

### When Ending a Session
1. Update section C with work completed
2. Move completed items from section D
3. Add any new discoveries to section E
4. Commit this file with session summary

### Context Priorities
1. Always preserve ProjectCode format `FDX-YYYY-NNNNNN`
2. Maintain auto-console creation on Request POST
3. Keep dual identity support (BuyerId + UserId)
4. Follow gradient purple theme for primary actions
5. No comments in code unless explicitly requested

---

*Last Updated: 2025-01-15 | Session 2 | Assistant: Claude*
*Next Session: Continue with SignalR implementation for live Project updates*