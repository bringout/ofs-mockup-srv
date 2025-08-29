# OFS Mockup Server

A FastAPI-based mockup server that simulates OFS (Open Fiscal Server) functionality for testing fiscal device integration in Bosnia and Herzegovina, Serbia, and other Balkans regions.

## Overview

This server provides a complete mockup implementation of the OFS API specification, enabling developers to test fiscal integration without requiring physical fiscal devices or real fiscal infrastructure. It simulates the behavior of fiscal devices commonly used in Bosnia and Herzegovina and Serbia.

## Features

- **Complete OFS API Implementation** - Full simulation of fiscal device endpoints
- **Multi-language Support** - Supports Bosnian (Latin/Cyrillic), Serbian (Latin/Cyrillic), and English
- **Tax Category Simulation** - Configurable VAT rates and tax categories
- **Invoice Processing** - Normal sales, refunds, copies, advances, and training receipts  
- **Receipt Search** - Search invoices by date range, amount, type, and payment method
- **Status Simulation** - Realistic device status responses including GSC codes
- **PIN Authentication** - Simulates security element PIN entry
- **Configurable Responses** - Easy customization of business data and responses

## Quick Start

### Installation

```bash
pip install bringout-ofs-mockup-srv
```

### Development Installation

```bash
git clone https://github.com/bring-out/0.git
cd packages/bringout-ofs-mockup-srv
pip install -e .[dev]
```

### Running the Server

```bash
# Using the installed command
ofs-mockup-srv

# Or directly with Python
python -m ofs_mockup_srv.main

# Or with uvicorn
uvicorn ofs_mockup_srv.main:app --reload --port 8200

# Optional: set initial GSC and port via CLI
ofs-mockup-srv --gsc 1500 --port 8200
```

### Makefile Shortcuts

```bash
# Install dev deps
make install-dev

# Run with initial GSC and port
make run-gsc GSC=1500 PORT=8200

# Run demos
make demo         # PIN + invoice flows
make demo-pin     # PIN flow only
make demo-invoice # invoice flow only
```

The server will start at `http://localhost:8200`

## API Endpoints

### Authentication
All endpoints (except root) require API key authentication:
```
Authorization: Bearer 0123456789abcdef0123456789abcdef
```

### Core Endpoints

- `GET /` - Health check
- `GET /api/attention` - Returns current GSC state: `"1300" | "1500" | "9999"`
- `GET /api/status` - Device status and tax rates
- `POST /api/pin` - PIN authentication for security element
- `POST /api/invoices` - Process fiscal invoices
- `POST /api/invoices/search` - Search processed invoices  
- `GET /api/invoices/{invoiceNumber}` - Get specific invoice details

### Mock Controls

- `POST /mock/lock` (Bearer): Force PIN-required state (sets GSC to `"1500"` and resets fail counter).
- `POST /api/pin` (text/plain):
  - Correct PIN → response `"0100"`, sets GSC `"9999"`, resets counter.
  - Wrong 4-digit PIN → response `"2400"`, counts toward lockout.
  - After 3 wrong 4-digit attempts → response `"1300"`, sets GSC `"1300"` (subsequent PINs return `"1300"`).

### PIN & Lockout Walkthrough (curl)

```bash
# Assume server at http://localhost:8200 and default API key
API=0123456789abcdef0123456789abcdef

# 1) Force PIN-required state
curl -s -X POST \
  -H "Authorization: Bearer $API" \
  http://localhost:8200/mock/lock

# 2) Attention shows 1500 (PIN required)
curl -s -H "Authorization: Bearer $API" \
  http://localhost:8200/api/attention

# 3) Enter correct PIN (text/plain) → "0100" and unlock to 9999
curl -s -X POST \
  -H "Authorization: Bearer $API" \
  -H "Content-Type: text/plain" \
  --data '1234' \
  http://localhost:8200/api/pin

# 4) Attention now shows 9999
curl -s -H "Authorization: Bearer $API" \
  http://localhost:8200/api/attention

# Lockout demo: 3 wrong 4-digit attempts → 1300
curl -s -X POST -H "Authorization: Bearer $API" http://localhost:8200/mock/lock
for P in 0000 1111 2222; do
  curl -s -X POST \
    -H "Authorization: Bearer $API" \
    -H "Content-Type: text/plain" \
    --data "$P" \
    http://localhost:8200/api/pin; echo
done

# Attention now shows 1300; further /api/pin returns 1300
curl -s -H "Authorization: Bearer $API" http://localhost:8200/api/attention
curl -s -X POST -H "Authorization: Bearer $API" -H "Content-Type: text/plain" \
  --data '1234' http://localhost:8200/api/pin
```

Quick script: `bash scripts/demo_flows.sh all` (or `pin` / `invoice`).

### Configuration

- API key and PIN defaults live in `ofs_mockup_srv/main.py` for local use.
- GSC is dynamic at runtime. Set initial value with `--gsc {1300|1500|9999}`.
- Business metadata can be adjusted in `main.py` for demos.

## Usage Examples

### Basic Invoice Processing

```bash
curl --location 'http://localhost:8200/api/invoices' \
--header 'Authorization: Bearer 0123456789abcdef0123456789abcdef' \
--header 'Content-Type: application/json' \
--data '{
    "invoiceRequest": {
        "invoiceType": "Normal",
        "transactionType": "Sale",
        "payment": [{
            "amount": 100.00,
            "paymentType": "Cash"
        }],
        "items": [{
            "name": "Test Product",
            "labels": ["E"],
            "totalAmount": 100.00,
            "unitPrice": 50.00,
            "quantity": 2.000
        }],
        "cashier": "Test Cashier"
    }
}'
```

### PIN Authentication

```bash
curl --location 'http://localhost:8200/api/pin' \
--header 'Authorization: Bearer 0123456789abcdef0123456789abcdef' \
--header 'Content-Type: text/plain' \
--data '1234'
```

### Invoice Search

```bash
curl --location 'http://localhost:8200/api/invoices/search' \
--header 'Authorization: Bearer 0123456789abcdef0123456789abcdef' \
--header 'Content-Type: application/json' \
--data '{
    "fromDate": "2024-03-01",
    "toDate": "2024-03-31",
    "amountFrom": 10.00,
    "amountTo": 10000.00,
    "invoiceTypes": ["Normal"],
    "transactionTypes": ["Sale"],
    "paymentTypes": ["Cash"]
}'
```

## Supported Features

### Invoice Types
- **Normal** - Standard fiscal receipt
- **Copy** - Copy of existing receipt  
- **Proforma** - Proforma invoice
- **Training** - Training mode receipt
- **Advance** - Advance payment receipt

### Transaction Types
- **Sale** - Regular sale transaction
- **Refund** - Refund transaction

### Payment Types
- **Cash** - Cash payment
- **Card** - Credit/debit card payment  
- **Check** - Check payment
- **WireTransfer** - Bank transfer
- **Voucher** - Voucher payment
- **MobileMoney** - Mobile payment
- **Other** - Other payment methods

### Tax Categories
Supports Bosnia and Herzegovina tax system:
- **E** - Standard VAT (17%)
- **K** - Zero VAT (0%)
- **A** - VAT exempt
- **F** - Special rate (11%)

## Testing Integration

This mockup server is perfect for:

- **Development Testing** - Test fiscal integration during development
- **CI/CD Pipelines** - Automated testing without real fiscal devices
- **Demo Environments** - Showcase fiscal functionality to clients
- **Load Testing** - Test system performance with fiscal operations
- **Integration Testing** - Validate ERP integration with fiscal systems

## Development

### Project Structure

```
ofs_mockup_srv/
├── __init__.py
├── main.py           # Main FastAPI application
└── models.py         # Pydantic data models (optional)
scripts/              # Helper scripts
patches/              # NixOS patches (for Nix development)
```

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=ofs_mockup_srv
```

### Sequence Diagrams

See `doc/SEQUENCES.md` for Mermaid diagrams of PIN unlock, 3-strike lockout, and `--gsc` initialization flows.

### Invoice Walkthrough (curl)

```bash
# Assume server at http://localhost:8200 and default API key
API=0123456789abcdef0123456789abcdef

# 1) Create a new invoice
curl -s -X POST \
  -H "Authorization: Bearer $API" \
  -H "Content-Type: application/json" \
  -d '{
        "invoiceRequest": {
          "invoiceType": "Normal",
          "transactionType": "Sale",
          "payment": [{"amount": 100.0, "paymentType": "Cash"}],
          "items": [
            {"name": "Test Product", "labels": ["F"], "totalAmount": 60.0, "unitPrice": 30.0, "quantity": 2.0},
            {"name": "Another", "labels": ["F"], "totalAmount": 40.0, "unitPrice": 20.0, "quantity": 2.0}
          ],
          "cashier": "Tester"
        }
      }' \
  http://localhost:8200/api/invoices | tee /tmp/invoice.json

# 2) Extract the invoice number
INV=$(jq -r .invoiceNumber /tmp/invoice.json)
echo "Invoice Number: $INV"

# 3) Fetch invoice details (optional query params)
curl -s \
  -H "Authorization: Bearer $API" \
  "http://localhost:8200/api/invoices/$INV?receiptLayout=Slip&imageFormat=Png&includeHeaderAndFooter=true" | jq .

# 4) Search invoices (CSV-like response)
FROM=$(date -I -d "-30 days")
TO=$(date -I)
curl -s -X POST \
  -H "Authorization: Bearer $API" \
  -H "Content-Type: application/json" \
  -d "{\n    \"fromDate\": \"$FROM\",\n    \"toDate\": \"$TO\",\n    \"amountFrom\": 0,\n    \"amountTo\": 100000,\n    \"invoiceTypes\": [\"Normal\"],\n    \"transactionTypes\": [\"Sale\"],\n    \"paymentTypes\": [\"Cash\"]\n  }" \
  http://localhost:8200/api/invoices/search

# 5) Error example (reserved value)
curl -s -H "Authorization: Bearer $API" \
  http://localhost:8200/api/invoices/ERROR
```

### Code Quality

```bash
# Format code
black ofs_mockup_srv/
isort ofs_mockup_srv/

# Lint code  
flake8 ofs_mockup_srv/
mypy ofs_mockup_srv/
```

## License

MIT License

## Support

For issues and questions:
- Create an issue on GitHub
- Contact: info@bring.out.ba

This mockup server helps accelerate fiscal integration development by providing a reliable testing environment that closely mimics real fiscal device behavior.
