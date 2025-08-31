# Sequence Diagrams

Below workflows illustrate GSC-driven authentication and PIN handling in the mock server. Diagrams use Mermaid syntax; render in a compatible viewer or GitHub.

## PIN Unlock Flow
```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server (FastAPI)
    participant ST as State (app.state)

    C->>S: POST /mock/lock (Bearer API_KEY)
    S->>ST: gsc = 1500, pin_fail_count = 0
    S-->>C: 200 {"gsc":"1500"}

    C->>S: GET /api/attention (Bearer)
    S-->>C: 200 "1500"

    C->>S: POST /api/pin (text/plain: PIN)
    S->>ST: if PIN ok → gsc = 9999, pin_fail_count = 0
    S-->>C: 200 "0100"

    C->>S: GET /api/attention (Bearer)
    S-->>C: 200 "9999"
```

## Wrong PIN Lockout (3 strikes → 1300)
```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server
    participant ST as State

    C->>S: POST /mock/lock (Bearer)
    S->>ST: gsc = 1500, pin_fail_count = 0
    S-->>C: 200 {"gsc":"1500"}

    C->>S: POST /api/pin ("0000")
    S->>ST: pin_fail_count = 1
    S-->>C: 200 "2400"

    C->>S: POST /api/pin ("1111")
    S->>ST: pin_fail_count = 2
    S-->>C: 200 "2400"

    C->>S: POST /api/pin ("2222")
    S->>ST: pin_fail_count = 3
    S->>ST:  gsc = 1300
    S-->>C: 200 "1300"

    C->>S: GET /api/attention
    S-->>C: 200 "1300"

    C->>S: POST /api/pin (any)
    S-->>C: 200 "1300" (ignored while in error state)
```

## Init Parameter (--gsc)
```mermaid
sequenceDiagram
    participant CLI as CLI
    participant S as Server
    participant ST as State

    CLI->>S: start with --gsc=1500
    S->>ST: gsc = 1500 at startup

    Note over S: /api/status includes gsc in array [gsc, "0210"]

    participant C as Client
    C->>S: GET /api/attention
    S-->>C: 200 "1500"
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

```
Notes
- GSC codes: 1300 = security error; 1500 = PIN required; 9999 = OK (PIN entered).
- /api/status mirrors current GSC in `gsc` list along with other status codes.
- /api/pin accepts `text/plain` only.
- Invoice processing requires valid Bearer token authentication.
- Refund transactions must include referentDocumentNumber and referentDocumentDT.
- Tax calculations based on item labels: E (10%), D (20%), G/K (0%), A (exempt), F (11%).
```
