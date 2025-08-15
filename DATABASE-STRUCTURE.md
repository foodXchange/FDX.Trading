# FDX Trading Database Structure Documentation

## Overview
This document describes the current database structure of the FDX Trading procurement platform as of August 2025.

## Core Tables

### 1. FdxUsers (Multi-Purpose User Table)
Stores all user types including buyers, suppliers, and admins.

| Column | Type | Description |
|--------|------|-------------|
| Id | int | Primary key |
| Username | nvarchar(100) | Unique username |
| Password | nvarchar(100) | Encrypted password |
| Email | nvarchar(100) | Email address |
| Type | int | User type (1=Admin, 2=Buyer, 3=Supplier) |
| CompanyName | nvarchar(200) | Company name |
| Country | nvarchar(100) | Country location |
| Address | nvarchar(500) | Physical address |
| Website | nvarchar(500) | Company website (required for suppliers) |
| PhoneNumber | nvarchar(50) | Contact phone |
| Category | nvarchar(100) | Business category |
| FullDescription | nvarchar(2000) | Detailed description |
| IsActive | bit | Active status |
| CreatedAt | datetime2 | Creation timestamp |
| DataComplete | bit | Profile completion status |
| ImportedAt | datetime2 | Import timestamp |
| ImportNotes | nvarchar(max) | Import metadata |

### 2. SupplierProductCatalogs
Contains all supplier products with categorization and search capabilities.

| Column | Type | Description |
|--------|------|-------------|
| Id | int | Primary key |
| SupplierId | int | Foreign key to FdxUsers |
| ProductName | nvarchar(200) | Product name |
| Description | nvarchar(1000) | Product description |
| Category | nvarchar(100) | Basic category |
| SubCategory | nvarchar(100) | Sub-category |
| ProductCategoryId | int | Foreign key to ProductCategories |
| SKU | nvarchar(50) | Stock keeping unit |
| Brand | nvarchar(100) | Brand name |
| Unit | nvarchar(50) | Unit of measure |
| PackSize | nvarchar(50) | Package size |
| MinOrderQuantity | int | Minimum order quantity |
| Price | decimal(18,2) | Unit price |
| Currency | nvarchar(10) | Price currency |
| IsAvailable | bit | Availability status |
| Certifications | nvarchar(500) | Product certifications |
| Origin | nvarchar(100) | Country of origin |
| LeadTime | nvarchar(50) | Delivery lead time |
| ImageUrl | nvarchar(500) | Product image URL |
| SearchTags | nvarchar(500) | Search optimization tags |
| Source | nvarchar(50) | Data source |
| CreatedAt | datetime2 | Creation timestamp |
| UpdatedAt | datetime2 | Last update timestamp |

### 3. ProductCategories
4-level hierarchical product categorization system.

| Column | Type | Description |
|--------|------|-------------|
| Id | int | Primary key |
| Category | nvarchar(100) | Level 1 - Main category |
| SubCategory | nvarchar(100) | Level 2 - Sub-category |
| Family | nvarchar(100) | Level 3 - Product family |
| SubFamily | nvarchar(200) | Level 4 - Sub-family |
| ProductFamilyId | nvarchar(20) | External reference ID |
| FullPath | nvarchar(500) | Complete category path |
| CreatedAt | datetime2 | Creation timestamp |
| UpdatedAt | datetime2 | Last update timestamp |

### 4. Requests
Procurement requests from buyers.

| Column | Type | Description |
|--------|------|-------------|
| Id | int | Primary key |
| Title | nvarchar(200) | Request title |
| Description | nvarchar(max) | Detailed description |
| BuyerId | int | Foreign key to FdxUsers |
| Status | nvarchar(50) | Request status |
| Priority | nvarchar(50) | Priority level |
| Category | nvarchar(100) | Request category |
| Budget | decimal(18,2) | Budget amount |
| Currency | nvarchar(10) | Budget currency |
| DeliveryDate | datetime2 | Required delivery date |
| DeliveryAddress | nvarchar(500) | Delivery location |
| CreatedAt | datetime2 | Creation timestamp |
| UpdatedAt | datetime2 | Last update timestamp |

### 5. RequestItems
Individual items within procurement requests.

| Column | Type | Description |
|--------|------|-------------|
| Id | int | Primary key |
| RequestId | int | Foreign key to Requests |
| ProductName | nvarchar(200) | Item name |
| Description | nvarchar(500) | Item description |
| Quantity | decimal(18,2) | Required quantity |
| Unit | nvarchar(50) | Unit of measure |
| TargetPrice | decimal(18,2) | Target unit price |
| Specifications | nvarchar(max) | Technical specifications |

### 6. SourcingBriefs
Advanced procurement briefs with supplier matching.

| Column | Type | Description |
|--------|------|-------------|
| Id | int | Primary key |
| Title | nvarchar(200) | Brief title |
| BuyerId | int | Foreign key to FdxUsers |
| Status | nvarchar(50) | Brief status |
| CreatedAt | datetime2 | Creation timestamp |
| QualityScore | decimal(5,2) | Quality assessment score |
| ResponseRate | decimal(5,2) | Supplier response rate |
| SuccessRate | decimal(5,2) | Success metric |

### 7. BriefProducts
Products within sourcing briefs.

| Column | Type | Description |
|--------|------|-------------|
| Id | int | Primary key |
| BriefId | int | Foreign key to SourcingBriefs |
| ProductName | nvarchar(200) | Product name |
| Category | nvarchar(100) | Product category |
| Quantity | int | Required quantity |
| Unit | nvarchar(50) | Unit of measure |
| Specifications | nvarchar(max) | Product specifications |
| TargetPrice | decimal(18,2) | Target price |
| ImageUrl | nvarchar(500) | Product image |

### 8. SupplierMatching
Matching results between briefs and suppliers.

| Column | Type | Description |
|--------|------|-------------|
| Id | int | Primary key |
| BriefId | int | Foreign key to SourcingBriefs |
| SupplierId | int | Foreign key to FdxUsers |
| MatchScore | decimal(5,2) | Matching score (0-100) |
| MatchedProducts | nvarchar(max) | JSON array of matched products |
| MatchDetails | nvarchar(max) | Detailed matching information |
| CreatedAt | datetime2 | Match timestamp |

## Relationships

```
FdxUsers (Suppliers)
    └── SupplierProductCatalogs (1:N)
            └── ProductCategories (N:1)
    
FdxUsers (Buyers)
    ├── Requests (1:N)
    │      └── RequestItems (1:N)
    └── SourcingBriefs (1:N)
           ├── BriefProducts (1:N)
           └── SupplierMatching (1:N)
                  └── FdxUsers (Suppliers) (N:1)
```

## Indexes & Optimization

### Primary Indexes
- All Id columns are clustered primary keys
- Foreign key indexes on all relationship columns

### Search Optimization
- Full-text index on SupplierProductCatalogs (ProductName, Description, SearchTags)
- Index on Category and SubCategory columns
- Composite index on (SupplierId, IsAvailable) for product queries

## Data Integrity Rules

### Supplier Requirements
- Must have valid website URL
- Must be categorized as food-related business
- Must have at least one product in catalog

### Product Requirements
- ProductName is required
- Must be linked to valid ProductCategory
- Price must be positive if specified

### Matching Rules
- MatchScore ranges from 0 to 100
- Only active suppliers are matched
- Product availability affects match score

## Recent Updates (Milestone 15)

1. **Enhanced Categorization**: Implemented 4-level product hierarchy from CSV import
2. **Supplier Validation**: Added comprehensive cleanup for non-food suppliers
3. **Product Extraction**: Automated extraction from supplier descriptions and websites
4. **Image Support**: Added ImageUrl fields for visual product representation
5. **Search Optimization**: Added SearchTags and improved full-text search capabilities

## Performance Considerations

- Database uses SQL Server with Azure hosting
- Connection pooling enabled for concurrent access
- Lazy loading disabled to prevent N+1 queries
- Batch operations for bulk imports (20-100 records per batch)

## Security

- Passwords are hashed (should be upgraded to bcrypt)
- SQL injection prevention via Entity Framework parameterization
- Row-level security for supplier data access
- Audit trail via CreatedAt/UpdatedAt timestamps

## Backup & Recovery

- Azure automated backups daily
- Point-in-time recovery available
- Development database separate from production

## Future Enhancements

1. Add multi-language support for product descriptions
2. Implement price history tracking
3. Add supplier rating and review system
4. Create materialized views for complex searches
5. Implement Redis caching for frequently accessed data