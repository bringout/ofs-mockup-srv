# Development Guide

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment tool (venv, conda, etc.)
- Optional: Nix (for reproducible development environment)

### Local Development Setup

#### Standard Python Setup

1. **Clone the repository:**
```bash
git clone https://github.com/bring-out/0.git
cd packages/bringout-ofs-mockup-srv
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
# Development installation
pip install -e .[dev]

# Or production installation
pip install -e .
```

4. **Run the server:**
```bash
# Using the installed command
ofs-mockup-srv

# Or directly with Python
python -m ofs_mockup_srv.main

# Or with uvicorn for development
uvicorn ofs_mockup_srv.main:app --reload --port 8200
```

#### Nix Development Setup (Recommended)

The project includes a complete Nix flake for reproducible development:

1. **Enter development environment:**
```bash
cd packages/bringout-ofs-mockup-srv
nix develop
```

2. **Run the server:**
```bash
# Python and uvicorn are automatically available
python ofs_mockup_srv/main.py

# Or use the symlinked executables
./python ofs_mockup_srv/main.py
./uvicorn ofs_mockup_srv.main:app --reload
```

The Nix environment provides:
- Python 3.12 with all dependencies
- Uvicorn web server
- Development tools and patches
- Cross-platform compatibility

## Project Structure

```
packages/bringout-ofs-mockup-srv/
├── ofs_mockup_srv/           # Main Python package
│   ├── __init__.py
│   └── main.py               # FastAPI application
├── doc/                      # Documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEVELOPMENT.md
├── scripts/                  # Helper scripts
│   ├── curl_hello.sh
│   ├── curl_post_invoice.sh
│   └── send_get_invoice.sh
├── patches/                  # System patches for Nix
│   └── gevent/
├── pyproject.toml            # Project configuration
├── README.md                 # Project README
├── LICENSE                   # MIT license
├── CLAUDE.md                 # AI context memory
├── flake.nix                 # Nix development environment
└── flake.lock               # Nix dependency lock
```

## Development Workflow

### Code Organization

The OFS Mockup Server follows a single-file architecture for simplicity:

- **All code in `main.py`** - FastAPI app, models, endpoints, and business logic
- **Embedded Pydantic models** - Data validation and serialization
- **Hardcoded configuration** - Easy to modify constants for testing scenarios
- **No external dependencies** - Self-contained testing server

### Key Components in main.py

```python
# Configuration constants
API_KEY = "0123456789abcdef0123456789abcdef"
PIN = "0A10015"
GSC_CODE = "9999"  # Device status simulation
BUSINESS_NAME = "Sigma-com doo Zenica"
SEND_CIRILICA = True  # Multi-language support

# Pydantic data models
class InvoiceRequest(BaseModel): ...
class InvoiceResponse(BaseModel): ...
class Status(BaseModel): ...

# FastAPI endpoints
@app.get("/")
@app.get("/api/attention")  
@app.get("/api/status")
@app.post("/api/pin")
@app.post("/api/invoices")
@app.post("/api/invoices/search")
@app.get("/api/invoices/{invoiceNumber}")

# Business logic functions
def check_api_key(req: Request): ...
```

### Adding New Features

#### 1. Adding New Endpoints

```python
@app.post("/api/new-endpoint")
async def new_endpoint(req: Request, data: NewDataModel):
    """
    Process new endpoint request.
    """
    # Authenticate
    if not check_api_key(req):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Process business logic
    result = process_new_operation(data)
    
    # Return response
    return {"status": "success", "data": result}
```

#### 2. Adding New Data Models

```python
class NewDataModel(BaseModel):
    field1: str
    field2: int
    field3: float | None = None
```

#### 3. Modifying Configuration

Edit constants at the top of `main.py`:

```python
# Customize for different test scenarios
BUSINESS_NAME = "Your Test Company"
BUSINESS_ADDRESS = "Test Address 123" 
GSC_CODE = "1300"  # Simulate no security element
SEND_CIRILICA = False  # Use Latin script
```

### Testing

#### Manual Testing with cURL

The project includes helper scripts for testing:

```bash
# Basic health check
./scripts/curl_hello.sh

# Test invoice processing
./scripts/curl_post_invoice.sh

# Test invoice retrieval
./scripts/send_get_invoice.sh
```

#### Custom Test Scripts

Create test scripts for different scenarios:

```bash
#!/bin/bash
# test_refund.sh

curl --location 'http://localhost:8200/api/invoices' \
--header 'Authorization: Bearer 0123456789abcdef0123456789abcdef' \
--header 'Content-Type: application/json' \
--data '{
  "invoiceRequest": {
    "invoiceType": "Normal",
    "transactionType": "Refund",
    "referentDocumentNumber": "RX4F7Y5L-RX4F7Y5L-140",
    "referentDocumentDT": "2024-03-12T07:48:47.626+01:00",
    "payment": [{"amount": 100.00, "paymentType": "Cash"}],
    "items": [{"name": "Refunded Item", "labels": ["E"], "totalAmount": 100.00, "unitPrice": 100.00, "quantity": 1.0}],
    "cashier": "Test Cashier"
  }
}' | python -m json.tool
```

#### Unit Testing with pytest

```bash
# Install development dependencies
pip install -e .[dev]

# Create test files
mkdir tests
touch tests/__init__.py
```

Example test file `tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from ofs_mockup_srv.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "hello" in response.json()

def test_attention_endpoint():
    response = client.get(
        "/api/attention",
        headers={"Authorization": "Bearer 0123456789abcdef0123456789abcdef"}
    )
    assert response.status_code == 200
    assert response.json() == True

def test_unauthorized_request():
    response = client.get("/api/attention")
    assert response.status_code == 401

def test_invalid_api_key():
    response = client.get(
        "/api/attention",
        headers={"Authorization": "Bearer invalid_key"}
    )
    assert response.status_code == 401

def test_invoice_processing():
    invoice_data = {
        "invoiceRequest": {
            "invoiceType": "Normal",
            "transactionType": "Sale",
            "cashier": "Test Cashier",
            "payment": [{"amount": 100.0, "paymentType": "Cash"}],
            "items": [{
                "name": "Test Product",
                "labels": ["E"],
                "totalAmount": 100.0,
                "unitPrice": 50.0,
                "quantity": 2.0
            }]
        }
    }
    
    response = client.post(
        "/api/invoices",
        json=invoice_data,
        headers={"Authorization": "Bearer 0123456789abcdef0123456789abcdef"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "invoiceNumber" in result
    assert "totalAmount" in result
    assert result["totalAmount"] == 100.0

def test_pin_authentication():
    response = client.post(
        "/api/pin",
        content="0A10015",
        headers={
            "Authorization": "Bearer 0123456789abcdef0123456789abcdef",
            "Content-Type": "text/plain"
        }
    )
    
    assert response.status_code == 200
    assert response.text == '"0100"'

def test_invalid_pin():
    response = client.post(
        "/api/pin",
        content="wrong",
        headers={
            "Authorization": "Bearer 0123456789abcdef0123456789abcdef",
            "Content-Type": "text/plain"
        }
    )
    
    assert response.status_code == 200
    assert response.text == '"2800"'
```

Run tests:
```bash
pytest tests/ -v
```

### Code Quality

#### Formatting and Linting

```bash
# Format code with Black
black ofs_mockup_srv/

# Sort imports with isort
isort ofs_mockup_srv/

# Lint with flake8
flake8 ofs_mockup_srv/

# Type checking with mypy
mypy ofs_mockup_srv/
```

#### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

Install and setup:
```bash
pip install pre-commit
pre-commit install
```

## Configuration and Customization

### Environment-Specific Configuration

Create different configuration profiles by modifying constants:

```python
# Development configuration
if os.getenv("ENV") == "development":
    API_KEY = "dev_key_123"
    GSC_CODE = "9999"  # Always ready
    SEND_CIRILICA = False

# Testing configuration  
elif os.getenv("ENV") == "testing":
    API_KEY = "test_key_456"
    GSC_CODE = "1300"  # Simulate security issues
    SEND_CIRILICA = True

# Production-like configuration
else:
    API_KEY = "prod_key_789"
    GSC_CODE = "9999"
    SEND_CIRILICA = True
```

### Multi-language Testing

Test different language scenarios:

```python
# Test Cyrillic responses
SEND_CIRILICA = True

# Test Latin responses
SEND_CIRILICA = False
```

### Device Status Simulation

Configure different device states for testing:

```python
# Device ready
GSC_CODE = "9999"

# Security element missing
GSC_CODE = "1300" 

# PIN required
GSC_CODE = "1500"
```

### Tax Rate Customization

Modify tax rates for different testing scenarios:

```python
# Custom tax rates in get_status() function
taxRateCustom = TaxRate(rate=25, label="X")  # Custom 25% rate
taxCategoryCustom = TaxCategory(
    categoryType=6, 
    name="Custom Tax", 
    orderId=5, 
    taxRates=[taxRateCustom]
)
```

## Debugging and Troubleshooting

### Development Debugging

1. **Enable detailed logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Add debug prints:**
```python
@app.post("/api/invoices")
async def invoice(req: Request, invoice_data: InvoiceData):
    print(f"DEBUG: Received invoice data: {invoice_data}")
    # ... processing
    print(f"DEBUG: Generated response: {response}")
    return response
```

3. **Use FastAPI automatic documentation:**
Visit `http://localhost:8200/docs` for interactive API documentation

### Common Issues

#### 1. Import Errors
```bash
# If module not found
export PYTHONPATH=$PWD:$PYTHONPATH
python -m ofs_mockup_srv.main
```

#### 2. Port Conflicts
```python
# Change port in main() function
uvicorn.run("ofs_mockup_srv.main:app", host="0.0.0.0", port=8001)
```

#### 3. Nix Environment Issues
```bash
# Rebuild Nix environment
nix flake lock --update-all-inputs
nix develop --rebuild
```

### Performance Testing

Test server performance with multiple concurrent requests:

```python
import asyncio
import aiohttp
import time

async def test_concurrent_requests(num_requests=100):
    async with aiohttp.ClientSession() as session:
        tasks = []
        start_time = time.time()
        
        for i in range(num_requests):
            task = session.post(
                "http://localhost:8200/api/invoices",
                json={
                    "invoiceRequest": {
                        "invoiceType": "Normal",
                        "transactionType": "Sale",
                        "cashier": f"Cashier{i}",
                        "payment": [{"amount": 100.0, "paymentType": "Cash"}],
                        "items": [{
                            "name": f"Product{i}",
                            "labels": ["E"],
                            "totalAmount": 100.0,
                            "unitPrice": 100.0,
                            "quantity": 1.0
                        }]
                    }
                },
                headers={"Authorization": "Bearer 0123456789abcdef0123456789abcdef"}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"Processed {num_requests} requests in {end_time - start_time:.2f} seconds")
        print(f"Average: {(end_time - start_time) / num_requests * 1000:.2f} ms per request")

# Run the test
asyncio.run(test_concurrent_requests())
```

## Deployment for Testing

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY ofs_mockup_srv/ ofs_mockup_srv/

RUN pip install .

EXPOSE 8200

CMD ["ofs-mockup-srv"]
```

Build and run:
```bash
docker build -t ofs-mockup-srv .
docker run -p 8200:8200 ofs-mockup-srv
```

### Docker Compose for Integration Testing

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ofs-mockup:
    build: .
    ports:
      - "8200:8200"
    environment:
      - ENV=testing
    
  test-client:
    image: python:3.11-slim
    depends_on:
      - ofs-mockup
    volumes:
      - ./tests:/tests
    command: |
      bash -c "
        pip install requests pytest &&
        cd /tests &&
        python -m pytest test_integration.py -v
      "
```

### Systemd Service (Linux)

Create `/etc/systemd/system/ofs-mockup.service`:

```ini
[Unit]
Description=OFS Mockup Server
After=network.target

[Service]
Type=simple
User=ofs-mockup
WorkingDirectory=/opt/ofs-mockup-srv
ExecStart=/opt/ofs-mockup-srv/venv/bin/ofs-mockup-srv
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ofs-mockup
sudo systemctl start ofs-mockup
```

## Contributing Guidelines

1. **Fork the repository** and create feature branch
2. **Follow single-file architecture** - keep everything in main.py for simplicity
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Use type hints** for all functions
6. **Follow existing code style** and patterns
7. **Test with multiple scenarios** - normal, error, edge cases

### Code Style Guidelines

- Use Python 3.10+ features (type unions with `|`)
- Follow PEP 8 naming conventions
- Add docstrings for new functions
- Use type hints consistently
- Keep the single-file architecture
- Add configuration constants at the top
- Group similar endpoints together

This development guide provides all necessary information for developing, testing, and deploying the OFS Mockup Server for fiscal integration testing.