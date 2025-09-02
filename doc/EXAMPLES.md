# API Usage Examples

This document provides practical examples for all OFS Mockup Server endpoints using curl commands.

## Authentication

All examples use the default API key. Replace with your actual API key in production:

```bash
API_KEY="api_key_0123456789abcdef0123456789abcdef"
BASE_URL="http://127.0.0.1:8200"
```

## Basic Operations

### Health Check

```bash
curl --location "$BASE_URL/"
```

### Service Availability Check

```bash
curl --location "$BASE_URL/api/attention" \
--header "Authorization: Bearer $API_KEY"
```

**Response:** HTTP status code indicates service availability:
- `200 OK` - Service is available (no response body)
- `404 Not Found` - Service is not available
- `401 Unauthorized` - Invalid API key

### Device Status

```bash
curl --location "$BASE_URL/api/status" \
--header "Authorization: Bearer $API_KEY"
```

## PIN Authentication

**Important**: PIN endpoint uses `text/plain` content type, not JSON.

```bash
curl --location "$BASE_URL/api/pin" \
--header "Authorization: Bearer $API_KEY" \
--header "Content-Type: text/plain" \
--data "4321"
```

## Invoice Operations

### Process Normal Invoice

```bash
curl --location "$BASE_URL/api/invoices" \
--header "Authorization: Bearer $API_KEY" \
--header "RequestId: 12345" \
--header "Content-Type: application/json" \
--data '{
    "invoiceRequest": {
        "invoiceType": "Normal",
        "transactionType": "Sale",
        "payment": [
            {
                "amount": 100.00,
                "paymentType": "Cash"
            }
        ],
        "items": [
            {
                "name": "Artikl 1",
                "labels": ["F"],
                "totalAmount": 100.00,
                "unitPrice": 50.00,
                "quantity": 2.000
            }
        ],
    "cashier": "Radnik 1"
    }
}'
```

## Debug Logging Examples

Enable detailed request/response logging during development to see JSON bodies and statuses printed to the console.

### Start Server with Debug

```bash
# Using helper script
python scripts/start_server.py --debug --port 8200

# Or via env var + uvicorn / installed entrypoint
export OFS_MOCKUP_DEBUG=true
uvicorn ofs_mockup_srv.main:app --reload --port 8200
# or
OFS_MOCKUP_DEBUG=true ofs-mockup-srv --port 8200
```

### Example: Debugging /api/invoices

```bash
curl --location "$BASE_URL/api/invoices" \
--header "Authorization: Bearer $API_KEY" \
--header "Content-Type: application/json" \
--data '{
  "invoiceRequest": {
    "invoiceType": "Normal",
    "transactionType": "Sale",
    "payment": [{"amount": 100.00, "paymentType": "Cash"}],
    "items": [{"name": "Test", "labels": ["E"], "totalAmount": 100.00, "unitPrice": 50.00, "quantity": 2.0}],
    "cashier": "Demo"
  }
}'
```

Expected console log (excerpt):

```
🔵 Request: POST /api/invoices
   Auth: Bearer api_key_0123456789...
   Body JSON: {
     "invoiceRequest": {
       "invoiceType": "Normal",
       "transactionType": "Sale",
       ...
     }
   }
🟢 Response: 200 POST /api/invoices
   Data JSON: {
     "invoiceNumber": "AX4F7Y5L-BX4F7Y5L-123",
     "totalAmount": 100.0,
     ...
   }
```

### Process Invoice Copy

```bash
curl --location "$BASE_URL/api/invoices" \
--header "Authorization: Bearer $API_KEY" \
--header "RequestId: 12345" \
--header "Content-Type: application/json" \
--data '{
    "invoiceRequest": {
        "invoiceType": "Copy",
        "transactionType": "Sale",
        "referentDocumentNumber": "RX4F7Y5L-RX4F7Y5L-140",
        "referentDocumentDT": "2024-03-12T07:48:47.626+01:00",
        "payment": [
            {
                "amount": 100.00,
                "paymentType": "Cash"
            },
            {
                "amount": 200.00,
                "paymentType": "Card"
            }
        ],
        "items": [
            {
                "name": "Artikl 1",
                "labels": ["F"],
                "totalAmount": 100.00,
                "unitPrice": 50.00,
                "quantity": 2.000
            },
            {
                "name": "Artikl 2",
                "labels": ["F"],
                "totalAmount": 200.00,
                "unitPrice": 200.00,
                "quantity": 1.000
            }
        ],
        "cashier": "Radnik 1"
    }
}'
```

### Process Refund Transaction

```bash
curl --location "$BASE_URL/api/invoices" \
--header "Authorization: Bearer $API_KEY" \
--header "RequestId: 12345" \
--header "X-Teron-SerialNumber: 123456789ABCDEF" \
--header "Content-Type: application/json" \
--data '{
    "invoiceRequest": {
        "invoiceType": "Normal",
        "transactionType": "Refund",
        "referentDocumentNumber": "RX4F7Y5L-RX4F7Y5L-140",
        "referentDocumentDT": "2024-03-12T07:48:47.626+01:00",
        "payment": [
            {
                "amount": 100.00,
                "paymentType": "Cash"
            }
        ],
        "items": [
            {
                "name": "Artikl 1",
                "labels": ["F"],
                "totalAmount": 100.00,
                "unitPrice": 50.00,
                "quantity": 2.000
            }
        ],
        "cashier": "Radnik 1"
    }
}'
```

## Invoice Search and Retrieval

### Search Invoices

```bash
curl --location "$BASE_URL/api/invoices/search" \
--header "Authorization: Bearer $API_KEY" \
--header "Content-Type: application/json" \
--data '{
    "fromDate": "2024-03-01",
    "toDate": "2024-03-31",
    "amountFrom": 10.00,
    "amountTo": 10000.00,
    "invoiceTypes": ["Normal","Advance"],
    "transactionTypes": ["Sale","Refund"],
    "paymentTypes": ["Cash","WireTransfer"]
}'
```

### Get Specific Invoice

```bash
curl --location "$BASE_URL/api/invoices/RX4F7Y5L-RX4F7Y5L-138?receiptLayout=Slip&imageFormat=Png&includeHeaderAndFooter=true" \
--header "Authorization: Bearer $API_KEY"
```

#### Query Parameters for Invoice Retrieval

| Parameter | Type | Description |
|-----------|------|-------------|
| `receiptLayout` | string | Layout format (e.g., "Slip") |
| `imageFormat` | string | Image format (e.g., "Png") |
| `includeHeaderAndFooter` | boolean | Include header and footer in output |

### Error Simulation

To simulate an error response, use invoice number "ERROR":

```bash
curl --location "$BASE_URL/api/invoices/ERROR" \
--header "Authorization: Bearer $API_KEY"
```

## Configuration Examples

### Update Server Settings

```bash
curl --location "$BASE_URL/api/settings" \
--header "Authorization: Bearer $API_KEY" \
--header "Content-Type: application/json" \
--data '{
    "authorizeLocalClients": false,
    "authorizeRemoteClients": true,
    "apiKey": "c0521663642496c82f79a55725302eba",
    "webserverAddress": "http://0.0.0.0:8200/"
}'
```

## Mock Device Control (Testing)

### Set Service Unavailable

Set the service to unavailable state (404 response from /api/attention).
Supports both GET and POST requests:

#### POST Request
```bash
curl --location "$BASE_URL/mock/lock" \
--header "Authorization: Bearer $API_KEY" \
--header "Content-Type: application/json" \
--data '{}'
```

#### GET Request
```bash
curl --location "$BASE_URL/mock/lock" \
--header "Authorization: Bearer $API_KEY"
```

**Response:**
```json
{
  "current_api_attention": 404
}
```

### Set Service Available

Set the service to available state (200 response from /api/attention).
Supports both GET and POST requests:

#### POST Request
```bash
curl --location "$BASE_URL/mock/unlock" \
--header "Authorization: Bearer $API_KEY" \
--header "Content-Type: application/json" \
--data '{}'
```

#### GET Request
```bash
curl --location "$BASE_URL/mock/unlock" \
--header "Authorization: Bearer $API_KEY"
```

**Response:**
```json
{
  "current_api_attention": 200
}
```

## Complex Example Scenarios

### Multi-Payment Invoice

```bash
curl --location "$BASE_URL/api/invoices" \
--header "Authorization: Bearer $API_KEY" \
--header "RequestId: 12345" \
--header "Content-Type: application/json" \
--data '{
    "invoiceRequest": {
        "invoiceType": "Normal",
        "transactionType": "Sale",
        "payment": [
            {
                "amount": 150.00,
                "paymentType": "Cash"
            },
            {
                "amount": 100.00,
                "paymentType": "Card"
            },
            {
                "amount": 50.00,
                "paymentType": "Voucher"
            }
        ],
        "items": [
            {
                "name": "Premium Product",
                "labels": ["E"],
                "totalAmount": 200.00,
                "unitPrice": 100.00,
                "quantity": 2.000,
                "discount": 10.00,
                "discountAmount": 20.00
            },
            {
                "name": "Standard Product",
                "labels": ["D"],
                "totalAmount": 100.00,
                "unitPrice": 25.00,
                "quantity": 4.000
            }
        ],
        "cashier": "Senior Cashier"
    }
}'
```

### Integration Test Script

```bash
#!/bin/bash

API_KEY="api_key_0123456789abcdef0123456789abcdef"
BASE_URL="http://127.0.0.1:8200"

echo "1. Testing service availability..."
curl -s "$BASE_URL/api/attention" -H "Authorization: Bearer $API_KEY"

echo -e "\n2. Getting device status..."
curl -s "$BASE_URL/api/status" -H "Authorization: Bearer $API_KEY" | jq .

echo -e "\n3. Processing test invoice..."
curl -s "$BASE_URL/api/invoices" \
-H "Authorization: Bearer $API_KEY" \
-H "Content-Type: application/json" \
-d '{
    "invoiceRequest": {
        "invoiceType": "Normal",
        "transactionType": "Sale",
        "payment": [{"amount": 100.00, "paymentType": "Cash"}],
        "items": [{"name": "Test Item", "labels": ["F"], "totalAmount": 100.00, "unitPrice": 100.00, "quantity": 1.000}],
        "cashier": "Test Cashier"
    }
}' | jq .

echo -e "\n4. Searching invoices..."
curl -s "$BASE_URL/api/invoices/search" \
-H "Authorization: Bearer $API_KEY" \
-H "Content-Type: application/json" \
-d '{
    "fromDate": "2024-01-01",
    "toDate": "2024-12-31",
    "invoiceTypes": ["Normal"],
    "transactionTypes": ["Sale"],
    "paymentTypes": ["Cash"]
}'

echo -e "\nIntegration test completed."
```
