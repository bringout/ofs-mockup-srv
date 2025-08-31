# API Documentation

## Overview

The OFS Mockup Server provides a complete REST API simulation of Open Fiscal Server functionality for testing fiscal device integration. All endpoints (except root) require API key authentication and return realistic fiscal device responses.

## Base URL

```
http://localhost:8200
```

## Authentication

All endpoints except root require API key authentication via Bearer token:

```http
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
```

**Default API Key**: `api_key_0123456789abcdef0123456789abcdef`

## Endpoints

### Health Check

#### GET /

Simple health check endpoint that doesn't require authentication.

**Response:**
```json
{
  "hello": "hernad"
}
```

---

### Service Availability

#### GET /api/attention

Check if the fiscal service is available and responsive.

**Headers:**
```http
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
```

**Response:**
```json
true
```

**Error Response:**
- HTTP 401 if API key is invalid

---

### Device Status

#### GET /api/status

Get fiscal device status, supported tax rates, and device capabilities.

**Headers:**
```http
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
```

**Response:**
```json
{
  "allTaxRates": [
    {
      "groupId": "1",
      "taxCategories": [
        {
          "categoryType": 0,
          "name": "Bez PDV",
          "orderId": 4,
          "taxRates": [
            {
              "label": "G",
              "rate": 0
            }
          ]
        }
      ],
      "validFrom": "2021-11-01T02:00:00.000+01:00"
    }
  ],
  "currentTaxRates": [
    {
      "groupId": "6", 
      "taxCategories": [
        {
          "categoryType": 0,
          "name": "Bez PDV",
          "orderId": 4,
          "taxRates": [
            {
              "label": "G",
              "rate": 0
            }
          ]
        },
        {
          "categoryType": 6,
          "name": "P-PDV", 
          "orderId": 3,
          "taxRates": [
            {
              "label": "E",
              "rate": 10
            }
          ]
        }
      ],
      "validFrom": "2024-05-01T02:00:00.000+01:00"
    }
  ],
  "deviceSerialNumber": "01-0001-WPYB002248200772",
  "gsc": ["9999", "0210"],
  "hardwareVersion": "1.0",
  "lastInvoiceNumber": "RX4F7Y5L-RX4F7Y5L-132",
  "make": "OFS",
  "model": "OFS P5 EFU LPFR",
  "mssc": [],
  "protocolVersion": "2.0", 
  "sdcDateTime": "2024-09-15T23:03:24.390+01:00",
  "softwareVersion": "2.0",
  "supportedLanguages": ["bs-BA", "bs-Cyrl-BA", "sr-BA", "en-US"]
}
```

**GSC Status Codes:**
- `9999` - Device ready
- `1300` - Security element not present  
- `1500` - PIN entry required

---

### PIN Authentication

#### POST /api/pin

Authenticate with security element PIN code.

**Headers:**
```http
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
Content-Type: text/plain
```

**Request Body:**
```
0A10015
```

**Success Response:**
```
"0100"
```

**Error Responses:**
- `"2400"` - LPFR not ready
- `"2800"` - Invalid PIN format (expected 4 digits)
- `"1300"` - Security element not present

**Status Codes:**
- `0100` - PIN entered correctly
- `1300` - Security element not present
- `2400` - LPFR not ready
- `2800`/`2806` - Invalid PIN format

---

### Invoice Processing

#### POST /api/invoices

Process fiscal invoice and generate fiscal receipt.

**Headers:**
```http
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
Content-Type: application/json
```

**Request Body:**
```json
{
  "invoiceRequest": {
    "invoiceType": "Normal",
    "transactionType": "Sale",
    "cashier": "Test Cashier",
    "payment": [
      {
        "amount": 100.00,
        "paymentType": "Cash"
      }
    ],
    "items": [
      {
        "name": "Test Product",
        "labels": ["E"],
        "totalAmount": 100.00,
        "unitPrice": 50.00,
        "quantity": 2.000,
        "discount": 0.0,
        "discountAmount": 0.0
      }
    ]
  }
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `invoiceType` | string | Yes | "Normal", "Copy", "Proforma", "Training", "Advance" |
| `transactionType` | string | Yes | "Sale", "Refund" |
| `cashier` | string | Yes | Cashier name |
| `payment` | array | Yes | Payment information |
| `items` | array | Yes | Invoice line items |
| `referentDocumentNumber` | string | Conditional | Required for "Copy" and "Refund" |
| `referentDocumentDT` | string | Conditional | Required for "Copy" and "Refund" |

**Item Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Product name |
| `labels` | array | Yes | Tax labels ["E", "K", "A", "D", "F", "G"] |
| `totalAmount` | float | Yes | Total amount for item |
| `unitPrice` | float | Yes | Unit price |
| `quantity` | float | Yes | Quantity |
| `discount` | float | No | Discount percentage |
| `discountAmount` | float | No | Discount amount |

**Payment Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `paymentType` | string | Yes | "Cash", "Card", "Check", "WireTransfer", "Voucher", "MobileMoney", "Other" |
| `amount` | float | Yes | Payment amount |

**Success Response:**
```json
{
  "address": "Ulica 7. Muslimanske brigade 77",
  "businessName": "Sigma-com doo Zenica",
  "district": "ZEDO",
  "encryptedInternalData": "Vvwq4nVn/wIQFAKE",
  "invoiceCounter": "100/123ZE",
  "invoiceCounterExtension": "ZE", 
  "invoiceImageHtml": null,
  "invoiceImagePdfBase64": null,
  "invoiceImagePngBase64": null,
  "invoiceNumber": "AX4F7Y5L-BX4F7Y5L-123",
  "journal": "=========== FISKALNI RAČUN ===========\n             4402692070009            \n       Sigma-com doo Zenica      \n...",
  "locationName": "Sigma-com doo Zenica poslovnica Sarajevo",
  "messages": "Uspješno",
  "mrc": "01-0001-WPYB002248200772",
  "requestedBy": "RX4F7Y5L",
  "sdcDateTime": "2024-08-01T14:38:32.499588",
  "signature": "Mw+IB0vgnaMjYrwA7m7zhtRseRIZFAKE",
  "signedBy": "RX4F7Y5L",
  "taxGroupRevision": 2,
  "taxItems": [
    {
      "amount": 9.91,
      "categoryName": "ECAL",
      "categoryType": 0,
      "label": "F",
      "rate": 11
    }
  ],
  "tin": "4402692070009",
  "totalAmount": 100.00,
  "totalCounter": 138,
  "transactionTypeCounter": 100,
  "verificationQRCode": "R0lGODlhhAGEAfFAKE",
  "verificationUrl": "https://sandbox.suf.poreskaupravars.org/v/?vl=A1JYNEY3WTVMUlg0FAKE="
}
```

**Error Response:**
```http
HTTP 400 Bad Request
{
  "detail": "Copy ne sadrzi referentDocumentNumber and DT"
}
```

---

### Invoice Search

#### POST /api/invoices/search

Search processed invoices by various criteria.

**Headers:**
```http
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
Content-Type: application/json
```

**Request Body:**
```json
{
  "fromDate": "2024-03-01",
  "toDate": "2024-03-31", 
  "amountFrom": 10.00,
  "amountTo": 10000.00,
  "invoiceTypes": ["Normal", "Advance"],
  "transactionTypes": ["Sale", "Refund"],
  "paymentTypes": ["Cash", "WireTransfer"]
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fromDate` | date | Yes | Start date (YYYY-MM-DD) |
| `toDate` | date | Yes | End date (YYYY-MM-DD) |
| `amountFrom` | float | No | Minimum amount |
| `amountTo` | float | No | Maximum amount |
| `invoiceTypes` | array | Yes | Invoice types to include |
| `transactionTypes` | array | Yes | Transaction types to include |
| `paymentTypes` | array | Yes | Payment types to include |

**Success Response:**
```
RX4F7Y5L-RX4F7Y5L-1,Normal,Sale,2024-03-06T17:33:12.582+01:00,10.0000
RX4F7Y5L-RX4F7Y5L-131,Normal,Sale,2024-03-11T20:29:05.329+01:00,10.0000
RX4F7Y5L-RX4F7Y5L-132,Normal,Sale,2024-03-11T20:29:25.422+01:00,15.0000
RX4F7Y5L-RX4F7Y5L-133,Normal,Sale,2024-03-11T23:05:53.608+01:00,100.0000
```

**Response Format:**
Each line contains: `InvoiceNumber,InvoiceType,TransactionType,DateTime,Amount`

---

### Invoice Details

#### GET /api/invoices/{invoiceNumber}

Get detailed information about a specific invoice.

**Parameters:**
- `invoiceNumber` (path) - The fiscal invoice number
- `imageFormat` (query) - Optional image format ("Png", "Pdf") 
- `includeHeaderAndFooter` (query) - Include receipt header/footer (boolean)
- `receiptLayout` (query) - Receipt layout ("Slip")

**Headers:**
```http
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
```

**Example:**
```
GET /api/invoices/RX4F7Y5L-RX4F7Y5L-138?receiptLayout=Slip&imageFormat=Png&includeHeaderAndFooter=true
```

**Success Response:**
```json
{
  "autoGenerated": false,
  "invoiceRequest": {
    "buyerCostCenterId": null,
    "buyerId": null,
    "cashier": "Radnik 1",
    "dateAndTimeOfIssue": null,
    "invoiceNumber": "13/2.0",
    "invoiceType": "Normal",
    "items": [
      {
        "articleUuid": null,
        "discount": null,
        "discountAmount": null, 
        "gtin": null,
        "labels": ["E"],
        "name": "Artikl 1",
        "plu": null,
        "quantity": 2,
        "totalAmount": 100,
        "unitPrice": 50
      }
    ],
    "options": {
      "omitQRCodeGen": 1,
      "omitTextualRepresentation": null
    },
    "payment": [
      {
        "amount": 100,
        "paymentType": "Cash"
      }
    ],
    "referentDocumentDT": null,
    "referentDocumentNumber": null,
    "transactionType": "Sale"
  },
  "invoiceResponse": {
    "address": "Ulica 7. Muslimanske brigade 77",
    "businessName": "Sigma-com doo Zenica", 
    "district": "Zenica",
    "encryptedInternalData": null,
    "invoiceCounter": "100/138ПП",
    "invoiceCounterExtension": "ПП",
    "invoiceImageHtml": null,
    "invoiceImagePdfBase64": null,
    "invoiceImagePngBase64": null,
    "invoiceNumber": "RX4F7Y5L-RX4F7Y5L-138",
    "journal": null,
    "locationName": "Sigma-com doo Zenica",
    "messages": "Uspješno",
    "mrc": "01-0001-WPYB002248200772",
    "requestedBy": "RX4F7Y5L", 
    "sdcDateTime": "2024-03-12T07:47:09.548+01:00",
    "signature": null,
    "signedBy": "RX4F7Y5L",
    "taxGroupRevision": 2,
    "taxItems": [
      {
        "amount": 8.52,
        "categoryName": "ECAL", 
        "categoryType": 0,
        "label": "E",
        "rate": 17
      }
    ],
    "tin": "4402692070009",
    "totalAmount": 100,
    "totalCounter": 138,
    "transactionTypeCounter": 100,
    "verificationQRCode": "R0lGODlhhAGEAfAAAFAKE",
    "verificationUrl": "https://sandbox.suf.poreskaupravars.org/..."
  },
  "issueCopy": false,
  "print": true,
  "receiptImageBase64": "iVBORw0KGgoAAkkZu/FAKE",
  "receiptImageFormat": "Png",
  "receiptLayout": "Slip",
  "renderReceiptImage": false,
  "skipEftPos": false,
  "skipEftPosPrint": false
}
```

**Error Simulation:**
Use invoice number `"ERROR"` to trigger error response:
```json
{
  "error": 1
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK` - Successful operation
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Invalid or missing API key
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "detail": "Error description"
}
```

### Common Errors

| Error | Description | Solution |
|-------|-------------|----------|
| Invalid API key | Authorization header missing or incorrect | Use correct Bearer token |
| Copy without reference | Copy/Refund missing reference document | Provide referentDocumentNumber and referentDocumentDT |
| Invalid PIN | Wrong PIN format or value | Use 4-digit PIN (default: 0A10015) |

## Tax System

### Tax Labels

| Label | Rate | Description |
|-------|------|-------------|
| E | 10% | Standard VAT (simulation rate) |
| D | 20% | Higher VAT rate |
| K, G | 0% | Zero VAT |
| A | 0% | VAT exempt |
| F | 11% | Special rate |

### Tax Categories

The system supports Bosnia and Herzegovina tax categories with configurable rates for testing different scenarios.

## Multi-language Support

### Supported Languages
- `bs-BA` - Bosnian (Latin script)
- `bs-Cyrl-BA` - Bosnian (Cyrillic script)  
- `sr-BA` - Serbian (Latin script)
- `en-US` - English

### Language Configuration

Set `SEND_CIRILICA = true` in configuration to enable Cyrillic responses:

```python
# Cyrillic enabled
taxCategory = TaxCategory(name="Без ПДВ", ...)

# Latin script  
taxCategory = TaxCategory(name="Bez PDV", ...)
```

## Configuration

### Environment Configuration

Modify constants in `main.py` for different test scenarios:

```python
API_KEY = "api_key_0123456789abcdef0123456789abcdef"  # API authentication
PIN = "0A10015"                                  # Security PIN
GSC_CODE = "9999"                            # Device status (9999=ready)
BUSINESS_NAME = "Your Company Name"          # Company information
BUSINESS_ADDRESS = "Your Address"
DISTRICT = "Your District"
SEND_CIRILICA = True                         # Enable Cyrillic responses
```

### Device Status Simulation

Configure different device states by changing `GSC_CODE`:
- `"9999"` - Device ready for operation
- `"1300"` - Security element not present
- `"1500"` - PIN entry required

## Integration Examples

### cURL Examples

#### Process Normal Invoice
```bash
curl --location 'http://localhost:8200/api/invoices' \
--header 'Authorization: Bearer api_key_0123456789abcdef0123456789abcdef' \
--header 'Content-Type: application/json' \
--data '{
  "invoiceRequest": {
    "invoiceType": "Normal",
    "transactionType": "Sale",
    "payment": [{"amount": 100.00, "paymentType": "Cash"}],
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

#### Process Refund
```bash
curl --location 'http://localhost:8200/api/invoices' \
--header 'Authorization: Bearer api_key_0123456789abcdef0123456789abcdef' \
--header 'Content-Type: application/json' \
--data '{
  "invoiceRequest": {
    "invoiceType": "Normal",
    "transactionType": "Refund",
    "referentDocumentNumber": "RX4F7Y5L-RX4F7Y5L-140",
    "referentDocumentDT": "2024-03-12T07:48:47.626+01:00",
    "payment": [{"amount": 100.00, "paymentType": "Cash"}],
    "items": [{
      "name": "Refunded Product",
      "labels": ["E"],
      "totalAmount": 100.00,
      "unitPrice": 50.00,
      "quantity": 2.000
    }],
    "cashier": "Test Cashier"
  }
}'
```

#### Copy Receipt
```bash
curl --location 'http://localhost:8200/api/invoices' \
--header 'Authorization: Bearer api_key_0123456789abcdef0123456789abcdef' \
--header 'Content-Type: application/json' \
--data '{
  "invoiceRequest": {
    "invoiceType": "Copy",
    "transactionType": "Sale", 
    "referentDocumentNumber": "RX4F7Y5L-RX4F7Y5L-140",
    "referentDocumentDT": "2024-03-12T07:48:47.626+01:00",
    "payment": [{"amount": 100.00, "paymentType": "Cash"}],
    "items": [{
      "name": "Original Product",
      "labels": ["E"],
      "totalAmount": 100.00,
      "unitPrice": 50.00,
      "quantity": 2.000
    }],
    "cashier": "Test Cashier"
  }
}'
```

### Python Integration Example

```python
import requests

class OFSMockupClient:
    def __init__(self, base_url="http://localhost:8200", api_key="api_key_0123456789abcdef0123456789abcdef"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def process_invoice(self, invoice_data):
        """Process a fiscal invoice."""
        response = requests.post(
            f"{self.base_url}/api/invoices",
            json=invoice_data,
            headers=self.headers
        )
        return response.json()
    
    def search_invoices(self, search_criteria):
        """Search invoices by criteria."""
        response = requests.post(
            f"{self.base_url}/api/invoices/search",
            json=search_criteria,
            headers=self.headers
        )
        return response.text
    
    def get_device_status(self):
        """Get device status and capabilities."""
        response = requests.get(
            f"{self.base_url}/api/status",
            headers=self.headers
        )
        return response.json()

# Usage example
client = OFSMockupClient()

invoice_data = {
    "invoiceRequest": {
        "invoiceType": "Normal",
        "transactionType": "Sale",
        "cashier": "Python Client",
        "payment": [{"amount": 50.0, "paymentType": "Card"}],
        "items": [{
            "name": "Python Test Item",
            "labels": ["E"],
            "totalAmount": 50.0,
            "unitPrice": 25.0,
            "quantity": 2.0
        }]
    }
}

result = client.process_invoice(invoice_data)
print(f"Invoice Number: {result['invoiceNumber']}")
```

This API provides complete fiscal device simulation for comprehensive testing of fiscal integration systems.