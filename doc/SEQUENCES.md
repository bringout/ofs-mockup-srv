# Sequence Diagrams

Below workflows illustrate the new HTTP status-based service availability system and PIN handling in the mock server. Diagrams use Mermaid syntax; render in a compatible viewer or GitHub.

## Service Availability Check Flow, system available
```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server (FastAPI)
    participant ST as State (app.state)

    C->>S: GET /api/attention (Bearer API_KEY)
    Note over S: current_api_attention = 200 (started with --available)
    S-->>C: 200 OK (no body)
    Note over C: Service is available
```

## Service Availability Check, system request PIN
```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server (FastAPI)
    participant ST as State (app.state)


    C->>S: GET /api/attention (Bearer)
    S-->>C: 404 Not Found
    Note over C: Service unavailable - PIN required

    C->>S: POST /api/pin (text/plain: "4321")
    S->>ST: PIN correct → current_api_attention = 200
    S->>ST: pin_fail_count = 0
    S-->>C: 200 "0100"

    C->>S: GET /api/attention (Bearer)
    S-->>C: 200 OK (no body)
    Note over C: Service is now available
```

## Service Lock/Unlock Flow
```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server (FastAPI)
    participant ST as State (app.state)

    C->>S: GET/POST /mock/lock (no auth required)
    S->>ST: current_api_attention = 404
    S-->>C: 200 {"current_api_attention": 404}

    C->>S: GET /api/attention (Bearer)
    Note over S: current_api_attention = 404
    S-->>C: 404 Not Found
    Note over C: Service is unavailable

    C->>S: GET/POST /mock/unlock (no auth required)
    S->>ST: current_api_attention = 200
    S-->>C: 200 {"current_api_attention": 200}

    C->>S: GET /api/attention (Bearer)
    Note over S: current_api_attention = 200
    S-->>C: 200 OK (no body)
    Note over C: Service is available
```

## PIN Integration Flow
```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server (FastAPI)
    participant ST as State (app.state)

    C->>S: GET/POST /mock/lock (no auth required)
    S->>ST: current_api_attention = 404
    S-->>C: 200 {"current_api_attention": 404}

    C->>S: GET /api/attention (Bearer)
    S-->>C: 404 Not Found
    Note over C: Service unavailable - PIN required

    C->>S: POST /api/pin (text/plain: "4321")
    S->>ST: PIN correct → current_api_attention = 200
    S->>ST: pin_fail_count = 0
    S-->>C: 200 "0100"

    C->>S: GET /api/attention (Bearer)
    S-->>C: 200 OK (no body)
    Note over C: Service is now available
```

## PIN Failure Flow
```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server
    participant ST as State

    C->>S: GET/POST /mock/lock (no auth required)
    S->>ST: current_api_attention = 404
    S-->>C: 200 {"current_api_attention": 404}

    C->>S: POST /api/pin ("0000")
    S->>ST: PIN wrong → current_api_attention = 404
    S->>ST: pin_fail_count = 1
    S-->>C: 200 "2400"

    C->>S: GET /api/attention
    S-->>C: 404 Not Found
    Note over C: Service still unavailable

    C->>S: POST /api/pin ("1111")
    S->>ST: PIN wrong → current_api_attention = 404
    S->>ST: pin_fail_count = 2
    S-->>C: 200 "2400"

    C->>S: POST /api/pin ("2222")
    S->>ST: pin_fail_count = 3
    S->>ST: current_api_attention = 404
    S-->>C: 200 "1300"

    C->>S: GET /api/attention
    S-->>C: 404 Not Found
    Note over C: Service unavailable (locked)

    C->>S: POST /api/pin (any)
    S-->>C: 200 "1300" (ignored while in error state)
```

## Server Startup Flow
```mermaid
sequenceDiagram
    participant CLI as CLI
    participant S as Server
    participant ST as State

    CLI->>S: start with --gsc=9999 (default)
    S->>ST: gsc = 9999
    S->>ST: current_api_attention = 200 (available)

    Note over S: Service starts in available state

    participant C as Client
    C->>S: GET /api/attention
    S-->>C: 200 OK (no body)

    alt CLI with --gsc=1500
        CLI->>S: start with --gsc=1500
        S->>ST: gsc = 1500
        S->>ST: current_api_attention = 404 (unavailable)
        C->>S: GET /api/attention
        S-->>C: 404 Not Found
    end
```

## Regular Invoice Processing
```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server (FastAPI)
    participant V as Validator
    participant B as Business Logic
    participant R as Response Generator

    C->>S: POST /api/invoices (Bearer API_KEY)
    Note over C,S: Invoice data with Normal/Sale transaction

    S->>S: check_api_key(req)
    alt API key valid
        S->>V: validate InvoiceData
        V->>V: check invoiceType, transactionType, items, payment
        
        alt validation successful
            V->>B: process Normal sale
            B->>B: calculate totalValue from items
            B->>B: validate payment amounts
            B->>B: process tax calculations (labels E,D,G,A,F)
            
            B->>R: generate fiscal response
            R->>R: create invoice number (AX4F7Y5L-BX4F7Y5L-XXX)
            R->>R: format receipt journal
            R->>R: generate tax breakdown
            
            R->>S: InvoiceResponse with receipt data
            S-->>C: 200 InvoiceResponse
            Note over S,C: Contains invoiceNumber, journal, taxItems, totalAmount
        else validation failed
            S-->>C: 400 Bad Request
        end
    else API key invalid
        S-->>C: 401 Unauthorized
    end
```

## Refund Invoice Processing
```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server (FastAPI)
    participant V as Validator
    participant B as Business Logic
    participant R as Response Generator

    C->>S: POST /api/invoices (Bearer API_KEY)
    Note over C,S: Invoice data with Normal/Refund transaction + referent document

    S->>S: check_api_key(req)
    alt API key valid
        S->>V: validate InvoiceData
        V->>V: check transactionType == "Refund"
        V->>V: validate referentDocumentNumber exists
        V->>V: validate referentDocumentDT exists
        
        alt validation successful
            V->>B: process Refund transaction
            B->>B: verify referent document (referentDocumentNumber, referentDocumentDT)
            Note over B: Print referent document info to console
            
            B->>B: calculate totalValue from refund items
            B->>B: validate refund payment amounts
            B->>B: process tax calculations for refund
            
            B->>R: generate fiscal refund response
            R->>R: create refund invoice number (AX4F7Y5L-BX4F7Y5L-XXX)
            R->>R: format refund receipt journal
            R->>R: generate tax breakdown for refund
            
            R->>S: InvoiceResponse with refund receipt data
            S-->>C: 200 InvoiceResponse
            Note over S,C: Contains refund receipt with original document reference
        else missing referent document
            S-->>C: 400 "Copy ne sadrzi referentDocumentNumber and DT"
        end
    else API key invalid
        S-->>C: 401 Unauthorized
    end
```

## Key Changes from Previous Version

### Service Availability System
- **New Approach**: HTTP status codes (200/404) instead of GSC text responses
- **current_api_attention**: New state variable controlling `/api/attention` responses
- **Default State**: 200 (available) when GSC=9999, 404 otherwise

### API Behavior Changes
- **`/api/attention`**: Returns HTTP 200 (available) or 404 (unavailable) with no response body
- **`/mock/lock`**: Sets `current_api_attention=404` and returns `{"current_api_attention": 404}`
- **`/mock/unlock`**: Sets `current_api_attention=200` and returns `{"current_api_attention": 200}`
- **`/api/pin`**: Success sets `current_api_attention=200`, failure sets `current_api_attention=404`

### Notes
- **PIN Format**: 4321 (exactly 4 digits)
- **GSC Codes**: Still used internally for device status (1300=security error, 1500=PIN required, 9999=OK)
- **API Status**: `/api/status` still returns GSC in the `gsc` array for device status information
- **PIN Authentication**: Accepts `text/plain` content-type only
- **Invoice Processing**: Requires valid Bearer token authentication
- **Refund Transactions**: Must include referentDocumentNumber and referentDocumentDT
- **Tax Calculations**: Based on item labels: E (10%), D (20%), G/K (0%), A (exempt), F (11%)