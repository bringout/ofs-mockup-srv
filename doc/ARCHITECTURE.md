# Architecture Documentation

## System Overview

The OFS Mockup Server is a lightweight FastAPI-based application that simulates the complete OFS (Open Fiscal Server) API for testing fiscal device integration without requiring physical hardware. It provides realistic responses for all fiscal operations commonly used in Bosnia and Herzegovina, Serbia, and other Balkan regions.

## High-Level Architecture

```mermaid
graph TB
    subgraph "External Systems"
        ERP["ERP System (Odoo, SAP, etc.)"]
        TESTING["Testing Framework"]
        CI["CI/CD Pipeline"]
    end
    
    subgraph "OFS Mockup Server"
        API[FastAPI Application]
        AUTH[API Key Authentication]
        FISCAL[Fiscal Operations Engine]
        LANG[Multi-language Support]
    end
    
    ERP -->|"REST API Requests"| API
    TESTING -->|"Test Scenarios"| API
    CI -->|"Automated Tests"| API
    API -->|"Validate"| AUTH
    AUTH -->|"Process"| FISCAL
    FISCAL -->|"Localize"| LANG
    LANG -->|"JSON Response"| API
    API -->|"Fiscal Receipt Data"| ERP
```

## Component Architecture

```mermaid
graph TB
    subgraph "Request Processing Layer"
        ENDPOINT[API Endpoints]
        VALIDATION[Request Validation]
        AUTH_LAYER[Authentication Layer]
    end
    
    subgraph "Business Logic Layer"
        INVOICE_PROC[Invoice Processing]
        TAX_CALC[Tax Calculations]
        RECEIPT_GEN[Receipt Generation]
        SEARCH_ENGINE[Invoice Search]
        STATUS_SIM[Status Simulation]
    end
    
    subgraph "Data Layer"
        MODELS[Pydantic Data Models]
        CONFIG[Configuration Constants]
        TEMPLATES[Response Templates]
    end
    
    subgraph "Output Layer"
        FORMATTER[Response Formatter]
        LOCALIZER[Language Localizer]
        ENCODER[JSON Encoder]
    end
    
    ENDPOINT --> VALIDATION
    VALIDATION --> AUTH_LAYER
    AUTH_LAYER --> INVOICE_PROC
    AUTH_LAYER --> TAX_CALC
    AUTH_LAYER --> RECEIPT_GEN
    AUTH_LAYER --> SEARCH_ENGINE
    AUTH_LAYER --> STATUS_SIM
    
    INVOICE_PROC --> MODELS
    TAX_CALC --> MODELS
    RECEIPT_GEN --> TEMPLATES
    SEARCH_ENGINE --> CONFIG
    STATUS_SIM --> CONFIG
    
    MODELS --> FORMATTER
    TEMPLATES --> FORMATTER
    CONFIG --> LOCALIZER
    FORMATTER --> ENCODER
    LOCALIZER --> ENCODER
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant C as Client (ERP/Test)
    participant A as API Layer
    participant Au as Authentication
    participant B as Business Logic
    participant F as Response Formatter
    
    C->>A: HTTP Request with API Key
    A->>Au: Validate API Key
    Au-->>A: Authentication Result
    
    alt Valid API Key
        A->>A: Validate Request Data
        A->>B: Process Business Logic
        B->>B: Calculate Taxes
        B->>B: Generate Receipt
        B->>F: Format Response
        F->>F: Apply Localization
        F-->>A: Formatted Response
        A-->>C: HTTP 200 + JSON Response
    else Invalid API Key
        Au-->>C: HTTP 401 Unauthorized
    end
```

## Module Architecture

```mermaid
graph TB
    subgraph "Main Module (main.py)"
        APP_INIT[FastAPI App Initialization]
        CONSTANTS[Configuration Constants]
        AUTH_FUNC[Authentication Functions]
        ENDPOINTS[API Endpoint Handlers]
        MODELS_INLINE[Inline Pydantic Models]
        BUSINESS_LOGIC[Business Logic Functions]
    end
    
    subgraph "Supporting Files"
        SCRIPTS[Helper Scripts]
        NIX_CONFIG[Nix Development Environment]
        PATCHES[System Patches]
    end
    
    APP_INIT --> CONSTANTS
    CONSTANTS --> AUTH_FUNC
    AUTH_FUNC --> ENDPOINTS
    ENDPOINTS --> MODELS_INLINE
    ENDPOINTS --> BUSINESS_LOGIC
    BUSINESS_LOGIC --> MODELS_INLINE
```

## API Architecture

### Endpoint Categories

```mermaid
graph TB
    subgraph "Public Endpoints"
        ROOT[GET / - Health Check]
    end
    
    subgraph "Authenticated Endpoints"
        ATTENTION[GET /api/attention - Service Check]
        STATUS[GET /api/status - Device Status]
        PIN[POST /api/pin - PIN Authentication]
        INVOICES[POST /api/invoices - Process Invoices]
        SEARCH[POST /api/invoices/search - Search Invoices]
        DETAILS[GET /api/invoices/{id} - Invoice Details]
    end
    
    ROOT --> ATTENTION
    ATTENTION --> STATUS
    STATUS --> PIN
    PIN --> INVOICES
    INVOICES --> SEARCH
    SEARCH --> DETAILS
```

### Authentication Flow

```mermaid
graph TB
    subgraph "Authentication Process"
        REQUEST[HTTP Request]
        EXTRACT[Extract Bearer Token]
        VALIDATE[Validate Against API_KEY]
        DECISION{Valid?}
        ALLOW[Allow Request]
        REJECT[HTTP 401 Unauthorized]
    end
    
    REQUEST --> EXTRACT
    EXTRACT --> VALIDATE
    VALIDATE --> DECISION
    DECISION -->|Yes| ALLOW
    DECISION -->|No| REJECT
```

## Data Model Architecture

```mermaid
erDiagram
    InvoiceData {
        object invoiceRequest
    }
    
    InvoiceRequest {
        string invoiceType
        string transactionType
        string cashier
        string referentDocumentNumber
        string referentDocumentDT
        array payment
        array items
    }
    
    PaymentLine {
        float amount
        string paymentType
    }
    
    ItemLine {
        string name
        array labels
        float totalAmount
        float unitPrice
        float quantity
        float discount
        float discountAmount
    }
    
    InvoiceResponse {
        string address
        string businessName
        string district
        string invoiceNumber
        string journal
        float totalAmount
        array taxItems
        string verificationUrl
    }
    
    Status {
        array allTaxRates
        array currentTaxRates
        string deviceSerialNumber
        array gsc
        string make
        string model
    }
    
    InvoiceData ||--|| InvoiceRequest : contains
    InvoiceRequest ||--o{ PaymentLine : has
    InvoiceRequest ||--o{ ItemLine : has
    InvoiceRequest ||--|| InvoiceResponse : generates
```

## Configuration Architecture

```mermaid
graph TB
    subgraph "Configuration Constants"
        API_CONFIG[API_KEY - Authentication]
        BUSINESS_CONFIG[BUSINESS_NAME, ADDRESS - Company Info]
        SECURITY_CONFIG[PIN - Security Element]
        DEVICE_CONFIG[GSC_CODE - Device Status]
        LANG_CONFIG[SEND_CIRILICA - Language Settings]
    end
    
    subgraph "Runtime Configuration"
        SERVER_CONFIG[Host, Port, Workers]
        UVICORN_CONFIG[Reload, Access Log]
    end
    
    API_CONFIG --> SERVER_CONFIG
    BUSINESS_CONFIG --> SERVER_CONFIG
    SECURITY_CONFIG --> SERVER_CONFIG
    DEVICE_CONFIG --> SERVER_CONFIG
    LANG_CONFIG --> SERVER_CONFIG
```

## Tax System Architecture

```mermaid
graph TB
    subgraph "Tax Categories"
        TAX_E[E - Standard VAT 10%]
        TAX_D[D - Higher VAT 20%]
        TAX_K[K/G - Zero VAT 0%]
        TAX_A[A - VAT Exempt]
        TAX_F[F - Special Rate 11%]
    end
    
    subgraph "Tax Processing"
        ITEM_LABEL[Item Tax Label]
        TAX_LOOKUP[Tax Rate Lookup]
        TAX_CALC[Tax Calculation]
        TAX_SUMMARY[Tax Summary Generation]
    end
    
    TAX_E --> TAX_LOOKUP
    TAX_D --> TAX_LOOKUP
    TAX_K --> TAX_LOOKUP
    TAX_A --> TAX_LOOKUP
    TAX_F --> TAX_LOOKUP
    
    ITEM_LABEL --> TAX_LOOKUP
    TAX_LOOKUP --> TAX_CALC
    TAX_CALC --> TAX_SUMMARY
```

## Multi-language Architecture

```mermaid
graph TB
    subgraph "Language Support"
        CYRILLIC[Cyrillic Script Support]
        LATIN[Latin Script Support]
        ENGLISH[English Support]
    end
    
    subgraph "Localization Process"
        LANG_DETECT[Language Detection]
        TEXT_SELECT[Text Selection]
        RESPONSE_FORMAT[Response Formatting]
    end
    
    subgraph "Supported Languages"
        BS_BA[bs-BA - Bosnian Latin]
        BS_CYRL[bs-Cyrl-BA - Bosnian Cyrillic]
        SR_BA[sr-BA - Serbian Latin]
        EN_US[en-US - English]
    end
    
    CYRILLIC --> LANG_DETECT
    LATIN --> LANG_DETECT
    ENGLISH --> LANG_DETECT
    
    LANG_DETECT --> TEXT_SELECT
    TEXT_SELECT --> RESPONSE_FORMAT
    
    BS_BA --> RESPONSE_FORMAT
    BS_CYRL --> RESPONSE_FORMAT
    SR_BA --> RESPONSE_FORMAT
    EN_US --> RESPONSE_FORMAT
```

## Error Handling Architecture

```mermaid
graph TB
    subgraph "Error Types"
        AUTH_ERR[Authentication Errors]
        VALIDATION_ERR[Validation Errors]
        BUSINESS_ERR[Business Logic Errors]
        SYSTEM_ERR[System Errors]
    end
    
    subgraph "Error Processing"
        ERROR_DETECT[Error Detection]
        ERROR_FORMAT[Error Formatting]
        HTTP_STATUS[HTTP Status Assignment]
        ERROR_RESPONSE[Error Response Generation]
    end
    
    AUTH_ERR --> ERROR_DETECT
    VALIDATION_ERR --> ERROR_DETECT
    BUSINESS_ERR --> ERROR_DETECT
    SYSTEM_ERR --> ERROR_DETECT
    
    ERROR_DETECT --> ERROR_FORMAT
    ERROR_FORMAT --> HTTP_STATUS
    HTTP_STATUS --> ERROR_RESPONSE
```

## Testing Architecture

```mermaid
graph TB
    subgraph "Test Types"
        UNIT_TESTS[Unit Tests]
        INTEGRATION_TESTS[Integration Tests]
        API_TESTS[API Endpoint Tests]
        LOAD_TESTS[Load Tests]
    end
    
    subgraph "Test Configuration"
        TEST_DATA[Test Data Sets]
        MOCK_SCENARIOS[Mock Scenarios]
        ERROR_SCENARIOS[Error Scenarios]
    end
    
    subgraph "Test Infrastructure"
        PYTEST[Pytest Framework]
        HTTPX[HTTP Client Testing]
        FASTAPI_TEST[FastAPI Test Client]
    end
    
    UNIT_TESTS --> TEST_DATA
    INTEGRATION_TESTS --> MOCK_SCENARIOS
    API_TESTS --> ERROR_SCENARIOS
    LOAD_TESTS --> TEST_DATA
    
    TEST_DATA --> PYTEST
    MOCK_SCENARIOS --> HTTPX
    ERROR_SCENARIOS --> FASTAPI_TEST
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        NIX_ENV[Nix Development Environment]
        LOCAL_SERVER[Local Uvicorn Server]
        DEV_CONFIG[Development Configuration]
    end
    
    subgraph "Testing Environment"
        CI_RUNNER[CI/CD Runner]
        TEST_SERVER[Test Server Instance]
        AUTOMATED_TESTS[Automated Test Suite]
    end
    
    subgraph "Production-like Environment"
        DOCKER_CONTAINER[Docker Container]
        LOAD_BALANCER[Load Balancer]
        MONITORING[Health Monitoring]
    end
    
    NIX_ENV --> LOCAL_SERVER
    LOCAL_SERVER --> DEV_CONFIG
    
    CI_RUNNER --> TEST_SERVER
    TEST_SERVER --> AUTOMATED_TESTS
    
    DOCKER_CONTAINER --> LOAD_BALANCER
    LOAD_BALANCER --> MONITORING
```

## Performance Characteristics

### Scalability Design
- **Stateless Architecture** - No session storage, fully stateless
- **Single Process** - Designed for testing, not high-load production
- **Fast Response Times** - In-memory processing, no database queries
- **Concurrent Requests** - FastAPI async support for concurrent testing

### Resource Usage
- **Minimal Memory** - Lightweight application with embedded data
- **Low CPU Usage** - Simple request processing without heavy computation
- **No External Dependencies** - Self-contained server with no external services
- **Fast Startup** - Quick server initialization for testing environments

This architecture provides a complete, realistic simulation of fiscal device functionality while maintaining simplicity and reliability for testing scenarios.