# FoodXchange Database Architecture

## Overview

This document describes the complete database architecture for FoodXchange, a B2B food supply chain platform. The schema is designed for PostgreSQL with support for advanced features like JSONB, full-text search, and row-level security.

## Database Schema Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Companies  │────<│    Users     │>────│ActivityLogs │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                     
       │                    v                     
       │            ┌──────────────┐             
       │            │Notifications │             
       │            └──────────────┘             
       │                                         
       v                                         
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Contacts   │     │  Suppliers   │────<│  Products   │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                     
       v                    v                     
┌─────────────┐     ┌──────────────┐             
│Communication│     │     RFQs     │             
│    Logs     │     └──────────────┘             
└─────────────┘            │                     
                           v                     
                    ┌──────────────┐             
                    │    Quotes    │             
                    └──────────────┘             
                           │                     
                           v                     
                    ┌──────────────┐     ┌─────────────┐
                    │    Orders    │────>│ OrderItems  │
                    └──────────────┘     └─────────────┘
                           │                     
                           v                     
                    ┌──────────────┐     ┌─────────────┐
                    │   Invoices   │────<│  Payments   │
                    └──────────────┘     └─────────────┘
```

## Table Descriptions

### Core Business Entities

#### 1. **companies**
Central entity for all organizations (buyers/suppliers).
- **Purpose**: Single source of truth for company information
- **Key Fields**: 
  - `company_type` (ENUM): buyer, supplier, both
  - `is_verified`: Verification status
  - `certifications` (JSONB): Food safety certifications
- **Relationships**: Links to users, contacts, orders, etc.

#### 2. **users**
System users with authentication and authorization.
- **Purpose**: User accounts and access control
- **Key Fields**:
  - `company_id`: Links to company
  - `role`: User role (buyer, supplier, admin)
  - `is_active`: Account status
- **Security**: Stores hashed passwords, supports 2FA

#### 3. **contacts**
Individual people within companies.
- **Purpose**: Multiple contacts per company
- **Key Fields**:
  - `is_primary`: Primary contact flag
  - `can_place_orders`: Permission flag
  - `communication_preferences` (JSONB)

### Supply Chain Management

#### 4. **suppliers**
Extended supplier information (legacy compatibility).
- **Purpose**: Supplier-specific data
- **Key Fields**:
  - `rating`: Performance rating
  - `response_rate`: Quote response metrics
  - Links to company table for future migration

#### 5. **products**
Product catalog from suppliers.
- **Purpose**: Searchable product database
- **Key Fields**:
  - `certifications` (JSONB): Product-specific certs
  - `price`: Current pricing
  - `moq`: Minimum order quantity
- **Features**: Full-text search on name/description

#### 6. **rfqs** (Request for Quotes)
Buyer requests for quotations.
- **Purpose**: Initiate procurement process
- **Key Fields**:
  - `rfq_number`: Unique identifier
  - `delivery_date`: Required by date
  - `requirements`: Detailed specifications

#### 7. **quotes**
Supplier responses to RFQs.
- **Purpose**: Price proposals from suppliers
- **Key Fields**:
  - `total_price`: Quote amount
  - `delivery_time`: Proposed delivery
  - `payment_terms`: Payment conditions

### Order Management

#### 8. **orders**
Confirmed purchase orders.
- **Purpose**: Track confirmed transactions
- **Key Fields**:
  - `order_number`: Unique PO number
  - `status` (ENUM): Order lifecycle
  - `payment_status` (ENUM): Payment tracking
- **Features**: Status history tracking

#### 9. **order_items**
Line items within orders.
- **Purpose**: Detailed order breakdown
- **Key Fields**:
  - `quantity`: Ordered amount
  - `unit_price`: Price per unit
  - `specifications` (JSONB): Item specs

#### 10. **order_status_history**
Audit trail for order changes.
- **Purpose**: Complete order history
- **Key Fields**:
  - `from_status`, `to_status`: State transition
  - `changed_by_user_id`: Who made change
  - `reason`: Change justification

### Financial Management

#### 11. **invoices**
Billing documents.
- **Purpose**: Financial records
- **Key Fields**:
  - `invoice_number`: Unique identifier
  - `due_date`: Payment deadline
  - `status` (ENUM): Invoice status
- **Features**: Automatic overdue detection

#### 12. **payments**
Payment transactions.
- **Purpose**: Track all payments
- **Key Fields**:
  - `payment_method` (ENUM): Payment type
  - `processor_transaction_id`: External reference
  - `is_reconciled`: Accounting status

### Communication & Notifications

#### 13. **notifications**
System alerts and messages.
- **Purpose**: Multi-channel notifications
- **Key Fields**:
  - `type` (ENUM): Notification category
  - `channels` (JSONB): Delivery methods
  - `is_read`: Read status

#### 14. **communication_logs**
All interactions history.
- **Purpose**: Complete communication audit
- **Key Fields**:
  - `type` (ENUM): Communication method
  - `sentiment`: AI-analyzed sentiment
  - `key_points` (JSONB): Extracted insights

#### 15. **emails**
Email processing queue.
- **Purpose**: AI email analysis
- **Key Fields**:
  - `classification`: Email category
  - `processed`: Processing status
  - `tasks_created` (JSONB): Actions taken

### System & Audit

#### 16. **activity_logs**
System-wide audit trail.
- **Purpose**: Track all system activities
- **Key Fields**:
  - `entity_type`, `entity_id`: Polymorphic reference
  - `action`: What was done
  - `details` (JSONB): Additional context

## Key Design Decisions

### 1. Company-Centric Model
- All entities link to companies, not individual users
- Supports B2B relationships
- Enables company-wide analytics

### 2. Flexible Attributes (JSONB)
- Used for: certifications, preferences, metadata
- Allows schema evolution without migrations
- Supports varied supplier/product attributes

### 3. Status Tracking
- Enums for standardized statuses
- History tables for audit trails
- Timestamp tracking throughout

### 4. Financial Precision
- Money stored as integers (cents)
- Prevents floating-point errors
- Currency field for internationalization

### 5. Soft Deletes
- is_active flags instead of deletions
- Preserves historical data
- Supports data recovery

## PostgreSQL-Specific Features

### 1. JSONB Columns
```sql
-- Query certifications
SELECT * FROM companies 
WHERE certifications @> '{"ISO22000": {"valid": true}}';
```

### 2. Full-Text Search
```sql
-- Add search vectors
ALTER TABLE products ADD COLUMN search_vector tsvector;
CREATE INDEX idx_products_search ON products USING GIN(search_vector);
```

### 3. Partial Indexes
```sql
-- Index only active records
CREATE INDEX idx_active_orders ON orders(created_at) 
WHERE status NOT IN ('completed', 'cancelled');
```

### 4. Row-Level Security
```sql
-- Company data isolation
CREATE POLICY company_isolation ON orders
FOR ALL TO application_role
USING (buyer_company_id = current_setting('app.company_id')::int);
```

## Migration to PostgreSQL

### From SQLite to PostgreSQL

1. **Update DATABASE_URL**:
   ```
   postgresql://foodxchange_app:password@server:5432/foodxchange_db?sslmode=require
   ```

2. **Run Migrations**:
   ```bash
   # Generate PostgreSQL-specific migration
   alembic upgrade head
   ```

3. **Data Migration**:
   ```python
   # Use included migration script
   python scripts/migrate_to_postgres.py
   ```

## Performance Optimizations

### 1. Indexes
- Foreign key indexes (automatic)
- Search indexes on frequently queried fields
- Composite indexes for common queries

### 2. Partitioning
- Orders table by created_at (monthly)
- Activity logs by created_at (monthly)
- Archived data to separate schema

### 3. Materialized Views
```sql
-- Supplier performance metrics
CREATE MATERIALIZED VIEW supplier_metrics AS
SELECT ...
WITH DATA;

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY supplier_metrics;
```

## Security Considerations

### 1. Data Encryption
- Sensitive fields encrypted at rest
- SSL/TLS for connections
- Encrypted backups

### 2. Access Control
- Row-level security by company
- Column-level permissions
- API rate limiting

### 3. Audit Trail
- All changes logged
- IP tracking for sensitive operations
- Immutable audit logs

## Backup & Recovery

### 1. Backup Strategy
- Daily full backups
- Hourly incremental backups
- 30-day retention

### 2. Recovery Procedures
- Point-in-time recovery
- Cross-region replication
- Automated failover

## Future Enhancements

### Phase 3 Tables (Planned)
- `inventory`: Real-time stock tracking
- `warehouses`: Multi-location support
- `shipments`: Logistics tracking
- `quality_checks`: Inspection records

### Phase 4 Features (Planned)
- Multi-tenant architecture
- Event sourcing for orders
- GraphQL API layer
- Real-time analytics

## Maintenance

### Regular Tasks
1. **Daily**: Check slow query log
2. **Weekly**: Update table statistics
3. **Monthly**: Review indexes, archive old data
4. **Quarterly**: Performance audit

### Monitoring
- Query performance (pg_stat_statements)
- Table bloat
- Connection pool usage
- Lock contention

## Conclusion

This architecture provides a solid foundation for FoodXchange's B2B operations while maintaining flexibility for future growth. The design prioritizes data integrity, performance, and scalability while supporting the complex relationships inherent in food supply chain management.