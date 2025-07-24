# System Architecture & Workflows

## Overall System Architecture
```mermaid
flowchart TD
    A[User] -->|Login| B[Frontend React App]
    B -->|API Calls| C[FastAPI Backend]
    C -->|AI Analysis| D[Azure OpenAI]
    C -->|Supplier Data| E[Azure Cosmos DB]
    C -->|Email| F[SMTP Server]
    C -->|Analytics| G[AI Analytics Engine]
    C -->|Import/Export| H[Bulk Import Script]
    B -->|Dashboard| I[User Interface]
    I -->|Insights| G
    G -->|Recommendations| I
```

## Module Relationships
```mermaid
flowchart TD
    subgraph Backend
        A1[FastAPI App]
        A2[Database Module]
        A3[AI Analytics]
        A4[Email Service]
    end
    subgraph Frontend
        B1[React App]
        B2[Pages/Components]
        B3[API Service]
    end
    B1 --> B2
    B2 --> B3
    B3 --> A1
    A1 --> A2
    A1 --> A3
    A1 --> A4
    A3 --> A2
    A4 --> A2
```

## Supplier Import Workflow
```mermaid
flowchart TD
    A[Supplier CSV/Excel] --> B[Import Script]
    B -->|Batch API| C[FastAPI Bulk Import Endpoint]
    C --> D[Cosmos DB]
    D --> E[Dashboard]
    E --> F[Analytics]
    F --> G[AI Insights]
```

## Email Automation Flow
```mermaid
flowchart TD
    A[User] -->|Send Email| B[FastAPI Email Endpoint]
    B --> C[Email Service]
    C -->|SMTP| D[Gmail/SMTP Server]
    D --> E[Supplier]
    C --> F[Tracking/Analytics]
    F --> G[Dashboard]
    G --> H[User]
```

## AI Email Analysis Flow
```mermaid
flowchart TD
    A[User] -->|Analyze Email| B[FastAPI AI Endpoint]
    B --> C[Azure OpenAI]
    C -->|AI Result| B
    B --> D[Cosmos DB]
    D --> E[Dashboard]
    E --> F[User]
```

## Campaign Workflow
```mermaid
flowchart TD
    A[User] -->|Create Campaign| B[Dashboard]
    B -->|API| C[FastAPI Backend]
    C --> D[Email Service]
    D -->|Bulk Email| E[Suppliers]
    D --> F[Tracking]
    F --> G[Analytics]
    G --> H[Dashboard]
``` 