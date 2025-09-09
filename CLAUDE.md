# CLAUDE.md - AI Context Memory

## Project Overview

**bringout-ofs-mockup-srv** is a FastAPI-based mockup server that simulates OFS (Open Fiscal Server) functionality for testing fiscal device integration in Bosnia and Herzegovina. It provides a complete API simulation for fiscal devices without requiring physical hardware.

### Key Technologies
- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation using Python type hints  
- **Uvicorn** - ASGI web server for production
- **Python 3.10+** - Modern Python features and type hints

## Architecture Summary

### Core Components

1. **FastAPI Application** (`main.py`)
   - Single-file application with all endpoints
   - API key authentication for all endpoints
   - Comprehensive fiscal API simulation
   - Multi-language support (Bosnian/Serbian Latin/Cyrillic, English)

2. **Data Models** (Embedded Pydantic models)
   - `TaxRate` / `TaxCategory` / `TaxRates` - Tax system definitions
   - `Status` - Device status and capabilities
   - `PaymentLine` / `ItemLine` - Invoice components
   - `InvoiceRequest` / `InvoiceData` - Invoice processing
   - `InvoiceResponse` - Fiscal receipt response
   - `TaxItems` - Tax breakdown information
   - `InvoiceSearch` - Search parameters with enums

3. **Configuration Constants**
   - API key authentication
   - Business information (name, address, district)
   - Security PIN for device authentication
   - Service availability status (current_api_attention)
   - Language and localization settings

## Key Business Logic

### Authentication System
- **API Key**: `api_key_0123456789abcdef0123456789abcdef` (hardcoded for testing)
- **PIN**: `4321` (for security element simulation)
- **Bearer Token**: Required for all endpoints except root

### Service Availability System
- **Attention Endpoint**: `/api/attention` returns HTTP 200 (available) or 404 (unavailable)
- **Default State**: 404 (unavailable) when server starts (or 200 with --available flag)
- **PIN Integration**: Successful PIN entry sets status to 200, failures set to 404
- **Mock Control**: `/mock/lock` sets to 404, `/mock/unlock` sets to 200

### Fiscal Device Simulation

#### Device Status Simulation
- **Attention System**: HTTP status-based service availability (200=available, 404=unavailable)
- **Service States**: Available (200) or unavailable (404) based on current_api_attention
- **Tax Rates**: Configurable VAT rates for different categories
- **Device Info**: Serial numbers, software versions, supported languages
- **Multi-language**: Bosnia/Serbia (Latin/Cyrillic), English support

#### Invoice Processing Flow
1. **Authentication** - API key validation
2. **Request Validation** - Pydantic model validation
3. **Business Logic** - Process invoice types (Normal, Copy, Refund, etc.)
4. **Response Generation** - Generate realistic fiscal receipt with all required fields
5. **Receipt Formatting** - Create formatted receipt journal with all details

### Supported Operations

#### Invoice Types
- **Normal** - Standard fiscal receipt
- **Copy** - Copy of existing receipt (requires referent document)
- **Proforma** - Proforma invoice
- **Training** - Training mode receipt
- **Advance** - Advance payment receipt

#### Transaction Types  
- **Sale** - Regular sale transaction
- **Refund** - Refund transaction (requires referent document)

#### Payment Types
- **Cash** - Cash payment
- **Card** - Credit/debit card
- **Check** - Check payment
- **WireTransfer** - Bank transfer  
- **Voucher** - Voucher payment
- **MobileMoney** - Mobile payment
- **Other** - Other payment methods

### Tax System Implementation

#### Bosnia and Herzegovina Tax Categories
- **E** - Standard VAT (10% in simulation, 17% in real system)
- **D** - Higher VAT rate (20%)
- **K** / **G** - Zero VAT (0%)
- **A** - VAT exempt
- **F** - Special rate (11%)

#### Tax Calculation
- Automatic tax calculation based on item labels
- Support for multiple tax categories per invoice
- Tax breakdown in response with amounts and percentages

## API Endpoints Summary

### Core Endpoints
- `GET /` - Health check (no auth required)
- `GET /api/attention` - Service availability check (returns HTTP 200 if available, 404 if unavailable)
- `GET /api/status` - Device status, tax rates, and capabilities
- `POST /api/pin` - PIN authentication (text/plain content-type)
- `POST /api/invoices` - Process fiscal invoices
- `POST /api/invoices/search` - Search processed invoices
- `GET /api/invoices/{invoiceNumber}` - Get specific invoice details
- `POST /mock/lock` - Set service to unavailable state (current_api_attention=404)
- `POST /mock/unlock` - Set service to available state (current_api_attention=200)
- `GET /mock/current_api_attention` - Get current service availability status

### Authentication Pattern
```python
def check_api_key(req: Request):
    token = req.headers["Authorization"].replace("Bearer ", "").strip()
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
```

### Response Generation Pattern
```python
# Generate realistic fiscal receipt numbers
cInvoiceNumber = str(randint(1,999)).zfill(3)
cFullInvoiceNumber = "AX4F7Y5L-BX4F7Y5L-" + cInvoiceNumber

# Create formatted receipt journal
journal = "=========== FISKALNI RAČUN ===========\n" + detailed_content
```

## Configuration and Customization

### Configurable Constants
```python
API_KEY = "api_key_0123456789abcdef0123456789abcdef"  # Authentication
PIN = "0A10015"                          # Security PIN
current_api_attention = 404               # Service availability (404=unavailable, 200=available)
BUSINESS_NAME = "Sigma-com doo Zenica"       # Company info
BUSINESS_ADDRESS = "Ulica 7. Muslimanske brigade 77"
DISTRICT = "Zenica"
SEND_CIRILICA = True                         # Enable Cyrillic responses
```

### Multi-language Support
```python
# Language-dependent responses
if SEND_CIRILICA:
    taxCategory = TaxCategory(name="Без ПДВ", ...)  # Cyrillic
else:
    taxCategory = TaxCategory(name="Bez PDV", ...)   # Latin
```

## Development Context

### Code Patterns
- Single-file FastAPI application for simplicity
- Embedded Pydantic models for type safety
- Hardcoded realistic test data for reliable simulation
- Comprehensive error handling with HTTP status codes
- Detailed console logging for development/debugging

### Testing Features
- **Configurable Responses** - Easy modification of business data
- **Error Simulation** - Special invoice number "ERROR" triggers error response
- **Realistic Data** - Proper formatting of fiscal receipts and QR codes
- **Complete API Coverage** - All major fiscal operations supported

### Response Realism
- Proper fiscal receipt formatting with headers/footers
- Realistic QR codes and verification URLs  
- Accurate tax calculations and breakdowns
- Proper timestamp formatting (ISO 8601)
- Authentic-looking serial numbers and signatures

## Integration Points

### ERP System Integration
- Standard OFS API compliance for easy ERP integration
- Proper HTTP status codes and error responses
- JSON request/response format matching real fiscal devices
- Support for all common fiscal operations

### Testing Scenarios
- **Development Testing** - Local development without fiscal hardware
- **CI/CD Integration** - Automated testing in pipelines
- **Demo Environments** - Client demonstrations
- **Load Testing** - Performance testing with fiscal operations
- **Integration Testing** - ERP-to-fiscal integration validation

## Important Notes for Future Development

1. **Single File Architecture** - Everything in main.py for simplicity
2. **Hardcoded Configuration** - Easy to modify constants for different test scenarios  
3. **No Persistence** - Stateless server, no database required
4. **Authentication** - Simple API key, suitable for testing environments
5. **Multi-language** - Built-in support for Balkan languages and scripts
6. **Tax Compliance** - Accurate simulation of Bosnia/Serbia tax systems
7. **Receipt Formatting** - Detailed fiscal receipt generation
8. **Error Handling** - Comprehensive error responses with proper HTTP codes

## Common Operations

### Starting the Server
```python
# Development mode
uvicorn ofs_mockup_srv.main:app --reload --port 8200

# Production mode (default: unavailable)
ofs-mockup-srv

# Start as available
ofs-mockup-srv --available

# Start as unavailable (explicit)
ofs-mockup-srv --unavailable
```

### Testing Invoice Processing
```bash
curl --location 'http://localhost:8200/api/invoices' \
--header 'Authorization: Bearer api_key_0123456789abcdef0123456789abcdef' \
--header 'Content-Type: application/json' \
--data '{...invoice_data...}'
```

### PIN Authentication Testing
```bash
curl --location 'http://localhost:8200/api/pin' \
--header 'Authorization: Bearer api_key_0123456789abcdef0123456789abcdef' \
--header 'Content-Type: text/plain' \
--data '0A10015'
```

### Custom Configuration
Modify constants in `main.py` to customize:
- Business information
- Tax rates and categories
- Device status simulation
- Language preferences
- Error scenarios
- all scripts go to scripts/

## Instructions
- `update` and `push`  for this project use `git` commit/push

## NextCloud Package Distribution

### Credentials and Configuration
- **NextCloud User**: `hernad`
- **NextCloud API Key**: `HrCjG-jRpJy-QGErA-dKtri-mZH4k`
- **Upload URL**: `https://next.cloud.out.ba/remote.php/dav/files/hernad@bring.out.ba/packages/`

### Windows-Compatible Upload Utilities

#### 1. Main Windows Utility: `scripts/nextcloud_upload_windows.py`
**Features:**
- Handles Windows environment variables reliably
- Multiple upload modes (wheel, wheelhouse)
- Can generate batch/PowerShell wrapper scripts
- Built-in credentials (can be overridden)
- Comprehensive help and examples

**Common Usage:**
```bash
# Direct wheelhouse upload (Windows-compatible)
python scripts/nextcloud_upload_windows.py --wheelhouse

# Direct wheel upload
python scripts/nextcloud_upload_windows.py --wheel

# Dry run for testing
python scripts/nextcloud_upload_windows.py --wheelhouse --dry-run

# Create reusable batch file
python scripts/nextcloud_upload_windows.py --wheelhouse --create-batch

# Create PowerShell script
python scripts/nextcloud_upload_windows.py --wheelhouse --create-powershell

# Custom credentials
python scripts/nextcloud_upload_windows.py --wheelhouse --user myuser --api-key mykey
```

#### 2. Quick Upload Scripts
- **`scripts/upload_wheelhouse.bat`** - Ready-to-use batch file for wheelhouse uploads
- **`scripts/upload_wheelhouse.ps1`** - PowerShell version with colored output

#### 3. Original Script: `scripts/push_to_nextcloud.py`
**Note**: Requires manual environment variable setup on Windows
```bash
# Environment variables required:
set NC_USER=hernad
set NC_API_KEY=HrCjG-jRpJy-QGErA-dKtri-mZH4k

# Upload wheelhouse
python scripts/push_to_nextcloud.py --wheelhouse

# Upload wheel
python scripts/push_to_nextcloud.py --wheel
```

### Package Types

#### Wheelhouse (Recommended for Windows)
- Contains all dependencies for offline installation
- Generated filename: `ofs_mockup_srv_wheelhouse_windows_v{version}_py{version}_{arch}.zip`
- Includes: `wheelhouse/` directory + `requirements.txt`

#### Standard Wheel
- Single wheel file for online installation
- Generated filename: `bringout_ofs_mockup_srv-{version}-py3-none-any.whl`
- Requires internet connection for dependency installation

### Memory Aid for Future Use

**Quick Commands:**
```bash
# RECOMMENDED: Use Windows-compatible utility
python scripts/nextcloud_upload_windows.py --wheelhouse

# OR: Use quick batch file
scripts\upload_wheelhouse.bat

# OR: Use PowerShell
powershell -ExecutionPolicy Bypass -File scripts\upload_wheelhouse.ps1
```

**Environment Variable Issues on Windows:**
- Use `nextcloud_upload_windows.py` instead of direct environment variable setting
- The utility handles environment variables internally
- Can generate wrapper scripts for repeated use
