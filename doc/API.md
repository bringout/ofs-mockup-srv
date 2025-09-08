# API Documentation

## Overview

The OFS Mockup Server provides a complete REST API simulation of [Operater fiskalnog sistema](https://ofs.ba).
Open Fiscal Server functionality for testing fiscal device integration. All endpoints (except root) require API key authentication and return realistic fiscal device responses.

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

Check if the fiscal service is available and responsive. This is the primary endpoint for service availability checking.

**Headers:**
```http
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
```

**Response:**
- HTTP 200 OK: Service is available (no response body)
- HTTP 404 Not Found: Service is not available

**Error Response:**
- HTTP 401 Unauthorized: Invalid API key

**Note:** This endpoint returns HTTP status codes only. For detailed device status information, use `/api/status`.

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

**Status Information:**
The `gsc` field in the response is maintained for backward compatibility with legacy systems. The primary service availability is determined by HTTP status codes from `/api/attention`:
- HTTP 200: Service available
- HTTP 404: Service unavailable

**Legacy GSC Field Values:**
- `["9999", "0210"]` - Device ready (for compatibility)
- May contain additional codes for diagnostic purposes

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
4321
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
    "buyerId": "VP:123456789",
    "print": false,
    "renderReceiptImage": true,
    "receiptLayout": "Invoice",
    "receiptImageFormat": "Pdf",
    "receiptSlipWidth": 386,
    "receiptSlipFontSizeNormal": 23,
    "receiptSlipFontSizeLarge": 27,
    "receiptHeaderImage": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGMAAQAABQABDQot2wAAAABJRU5ErkJggg==",
    "receiptFooterImage": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGMAAQAABQABDQot2wAAAABJRU5ErkJggg==",
    "receiptHeaderTextLines": ["Header Line 1", "Header Line 2"],
    "receiptFooterTextLines": ["Footer Line 1", "Footer Line 2"],
    "payment": [
      {
        "amount": 100.00,
        "paymentType": "Cash"
      }
    ],
    "items": [
      {
        "name": "Test Product",
        "gtin": "12345678901",
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
| `buyerId` | string | No | Buyer identification (max 20 ASCII chars, VP: prefix for grossale) |
| `payment` | array | Yes | Payment information |
| `items` | array | Yes | Invoice line items |
| `referentDocumentNumber` | string | Conditional | Required for "Copy" and "Refund" |
| `referentDocumentDT` | string | Conditional | Required for "Copy" and "Refund" |
| `print` | boolean | No | Set to `false` to skip internal printer |
| `renderReceiptImage` | boolean | No | Set to `true` to generate receipt image |
| `receiptLayout` | string | No | "Invoice" (A4) or "Slip" (receipt format) |
| `receiptImageFormat` | string | No | "Pdf" or "Png" |
| `receiptSlipWidth` | number | No | Slip width in pixels (386 for 58mm, 576 for 80mm) |
| `receiptSlipFontSizeNormal` | number | No | Normal text font size for slip format |
| `receiptSlipFontSizeLarge` | number | No | Large text font size for slip format |
| `receiptHeaderImage` | string | No | Base64 encoded header image |
| `receiptFooterImage` | string | No | Base64 encoded footer image |
| `receiptHeaderTextLines` | array[string] | No | Header text lines for receipt |
| `receiptFooterTextLines` | array[string] | No | Footer text lines for receipt |

**Item Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Product name |
| `gtin` | string | Yes | GTIN (barcode) - 8-14 characters |
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
  "invoiceImagePdfBase64": "JVBERi0xLjcKJcOkw7zDtsOfCjIgMCBvYmoKPDw...",
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

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `invoiceImagePdfBase64` | string\|null | Base64 encoded PDF receipt when `print=false` and `renderReceiptImage=true` with `receiptImageFormat="Pdf"` |
| `invoiceImagePngBase64` | string\|null | Base64 encoded PNG receipt when `print=false` and `renderReceiptImage=true` with `receiptImageFormat="Png"` |

**Error Responses:**

**HTTP 400 Bad Request (FastAPI validation errors):**
```json
{
  "detail": "Copy ne sadrzi referentDocumentNumber and DT"
}
```

**HTTP 200 OK with Custom Error Format:**
```json
{
  "details": null,
  "message": "gtin za artikal Test product nije popunjen",
  "statusCode": -1
}
```

**Common Custom Error Scenarios:**
- Missing GTIN: When any item lacks a `gtin` field
- Empty GTIN: When `gtin` is an empty string or whitespace
- Invalid payment amounts: When payment totals don't match invoice totals

---

### Print to Other Printer (External Printer Support)

The API supports printing receipts to external printers by generating receipt images instead of using the internal OFS printer.

#### Configuration Parameters

To print to another printer, set the following parameters in your invoice request:

- `print`: `false` - Skip internal printer
- `renderReceiptImage`: `true` - Generate receipt image  
- `receiptLayout`: `"Invoice"` (A4 format) or `"Slip"` (receipt format)
- `receiptImageFormat`: `"Pdf"` or `"Png"`

For slip format, additional parameters:
- `receiptSlipWidth`: Width in pixels (386 for 58mm paper, 576 for 80mm paper)
- `receiptSlipFontSizeNormal`: Normal text font size (recommended: 23 for 58mm, 25 for 80mm)
- `receiptSlipFontSizeLarge`: Large text font size (recommended: 27 for 58mm, 30 for 80mm)

#### Receipt Customization

**Header and Footer Images:**
- `receiptHeaderImage`: Base64 encoded image for receipt header
- `receiptFooterImage`: Base64 encoded image for receipt footer

**Header and Footer Text:**
- `receiptHeaderTextLines`: Array of text lines for receipt header
- `receiptFooterTextLines`: Array of text lines for receipt footer

#### Example Request

```json
{
  "invoiceRequest": {
    "invoiceType": "Normal",
    "transactionType": "Sale",
    "print": false,
    "renderReceiptImage": true,
    "receiptLayout": "Invoice",
    "receiptImageFormat": "Pdf",
    "receiptHeaderTextLines": ["Custom Header Line 1", "Custom Header Line 2"],
    "receiptFooterTextLines": ["Custom Footer Line"],
    "cashier": "External Printer Test",
    "payment": [{"amount": 100.00, "paymentType": "Cash"}],
    "items": [{
      "name": "Test Product",
      "gtin": "12345678901",
      "labels": ["E"],
      "totalAmount": 100.00,
      "unitPrice": 100.00,
      "quantity": 1.0
    }]
  }
}
```

#### Response

When `print=false` and `renderReceiptImage=true`, the response includes:

- `invoiceImagePdfBase64`: Base64 encoded PDF when `receiptImageFormat="Pdf"`
- `invoiceImagePngBase64`: Base64 encoded PNG when `receiptImageFormat="Png"`

#### Console Logging

The server logs the following information to the console:

**Image Processing:**
```
Image header 67 bytes.  # When receiptHeaderImage is valid base64
Image footer 67 bytes.  # When receiptFooterImage is valid base64  
ERROR: receiptHeaderImage is not base64 encoded string  # When invalid
ERROR: receiptFooterImage is not base64 encoded string  # When invalid
```

**Text Lines:**
```
HEADER:
- Header Line 1
- Header Line 2

FOOTER:
- Footer Line 1
- Footer Line 2
```

**Buyer ID and GTIN:**
```
buyerId: VP:123456789, if OFS system is registering grossale this field should start with: VP:
gtin: 12345678901  # For each item
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
        "gtin": "12345678",
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

### Error Response Formats

**FastAPI Standard Format (HTTP 400/401/500):**
```json
{
  "detail": "Error description"
}
```

**Custom OFS Error Format (HTTP 200):**
```json
{
  "details": null,
  "message": "Error description in local language",
  "statusCode": -1
}
```

### Common Errors

| Error | Description | Solution | Format |
|-------|-------------|----------|--------|
| Invalid API key | Authorization header missing or incorrect | Use correct Bearer token | FastAPI |
| Copy without reference | Copy/Refund missing reference document | Provide referentDocumentNumber and referentDocumentDT | FastAPI |
| Invalid PIN | Wrong PIN format or value | Use 4-digit PIN (default: 4321) | FastAPI |
| Missing GTIN | Item missing gtin field | Provide valid GTIN for all items | Custom OFS |
| Empty GTIN | Item has empty or whitespace-only gtin | Provide valid GTIN string | Custom OFS |
| Invalid payment | Payment amounts don't match totals | Verify payment calculations | Custom OFS |

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
PIN = "4321"                                  # Security PIN
BUSINESS_NAME = "Your Company Name"          # Company information
BUSINESS_ADDRESS = "Your Address"
DISTRICT = "Your District"
SEND_CIRILICA = True                         # Enable Cyrillic responses
```

### Service Availability Control

**Service Availability**: The `/api/attention` endpoint returns HTTP 200 (available) or 404 (unavailable) based on `current_api_attention` state, which is controlled by:
- PIN authentication success/failure
- Mock control endpoints (`/mock/lock`, `/mock/unlock`)
- Service initialization state

**HTTP Status Codes:**
- `200 OK` - Service is available and ready for fiscal operations
- `404 Not Found` - Service is unavailable (PIN required, security issues, or locked)

**Compatibility Note**: The Status response includes a `gsc` field for backward compatibility with legacy systems, but service availability should be determined using HTTP status codes from `/api/attention`.

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
    "buyerId": "VP:123456789",
    "payment": [{"amount": 100.00, "paymentType": "Cash"}],
    "items": [{
      "name": "Test Product",
      "gtin": "12345678901",
      "labels": ["E"],
      "totalAmount": 100.00,
      "unitPrice": 50.00,
      "quantity": 2.000
    }],
    "cashier": "Test Cashier"
  }
}'
```

#### Process Invoice with External Printer
```bash
curl --location 'http://localhost:8200/api/invoices' \
--header 'Authorization: Bearer api_key_0123456789abcdef0123456789abcdef' \
--header 'Content-Type: application/json' \
--data '{
  "invoiceRequest": {
    "invoiceType": "Normal",
    "transactionType": "Sale",
    "print": false,
    "renderReceiptImage": true,
    "receiptLayout": "Invoice",
    "receiptImageFormat": "Pdf",
    "receiptHeaderTextLines": ["Custom Header"],
    "receiptFooterTextLines": ["Thank you for your purchase!"],
    "payment": [{"amount": 50.00, "paymentType": "Card"}],
    "items": [{
      "name": "External Print Test",
      "gtin": "98765432109",
      "labels": ["E"],
      "totalAmount": 50.00,
      "unitPrice": 50.00,
      "quantity": 1.0
    }],
    "cashier": "External Printer"
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
      "gtin": "12345678901",
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
      "gtin": "12345678901",
      "labels": ["E"],
      "totalAmount": 100.00,
      "unitPrice": 50.00,
      "quantity": 2.000
    }],
    "cashier": "Test Cashier"
  }
}'
```

---

## Mock Control Endpoints

These endpoints are used for testing and simulation control.

### Set Service Unavailable

#### GET/POST /mock/lock

Set the service to unavailable state, causing `/api/attention` to return HTTP 404.
Supports both GET and POST requests.

**Headers:**
```http
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
Content-Type: application/json
```

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "current_api_attention": 404
}
```

### Set Service Available

#### GET/POST /mock/unlock

Set the service to available state, causing `/api/attention` to return HTTP 200.
Supports both GET and POST requests.

**Headers:**
```http
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
Content-Type: application/json
```

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "current_api_attention": 200
}
```

### Usage Examples

#### Lock Service (POST)
```bash
curl --location 'http://localhost:8200/mock/lock' \
--header 'Authorization: Bearer api_key_0123456789abcdef0123456789abcdef' \
--header 'Content-Type: application/json' \
--data '{}'
```

#### Lock Service (GET)
```bash
curl --location 'http://localhost:8200/mock/lock' \
--header 'Authorization: Bearer api_key_0123456789abcdef0123456789abcdef'
```

#### Unlock Service (POST)
```bash
curl --location 'http://localhost:8200/mock/unlock' \
--header 'Authorization: Bearer api_key_0123456789abcdef0123456789abcdef' \
--header 'Content-Type: application/json' \
--data '{}'
```

#### Unlock Service (GET)
```bash
curl --location 'http://localhost:8200/mock/unlock' \
--header 'Authorization: Bearer api_key_0123456789abcdef0123456789abcdef'
```

---

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
        "buyerId": "VP:PYTHON123",
        "receiptHeaderTextLines": ["Python Integration Test"],
        "receiptFooterTextLines": ["Generated via Python API"],
        "payment": [{"amount": 50.0, "paymentType": "Card"}],
        "items": [{
            "name": "Python Test Item",
            "gtin": "12345678901",
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