# API Workflows and Integration Patterns

## Standard Integration Workflow

Follow this workflow when integrating with the OFS Mockup Server:

### 1. Check Service Availability

Verify that ESIR and PFR are available by calling `/api/attention`. If the response is negative, display an appropriate message to the user and retry after a few seconds. Continue checking without limitation until ESIR becomes available.

```bash
while true; do
  # Check if service responds
  response=$(curl -s -H "Authorization: Bearer api_key_0123456789abcdef0123456789abcdef" \
    http://localhost:8200/api/attention)
  if [ "$response" = "9999" ]; then
    break  # Service is ready
  fi
  sleep 2  # Wait before retry
done
```

### 2. Security Element Check (LPFR only)

**Only when using LPFR**: Check if the security element is present by calling `/api/status` and verifying that the GSC field doesn't contain code `1300`. If this code is present, display an appropriate message that the security element is not present and continue checking until code `1300` disappears.

### 3. PIN Entry Check (LPFR only)

**Only when using LPFR**: Check if PIN entry is required by calling `/api/status` and verifying if the GSC field contains code `1500`. If this code is present, display an appropriate screen for PIN entry and send the PIN via `/api/pin` call for verification. After successful PIN entry, you can continue with normal operation.

### 4. Process Fiscal Transactions

Perform standard entry of all invoice elements and send for fiscalization and printing via `/api/invoices`. Handle these error scenarios:

#### Error Handling

- **Security Element Missing**: If error indicates security element is not present (e.g., user removed card), return to step 2
- **PIN Required**: If error indicates PIN entry is needed (e.g., user removed and reinserted card), return to step 3
- **Content Errors**: API will return error if there are problems in invoice content (display appropriately to user)
- **Success**: API returns confirmation of successful fiscalization and printing

#### Partial Failures

If fiscalization succeeded but printing failed, the response will include:
- Error information about the printing failure
- `invoiceResponse` field with fiscal data

In this case:
1. Fix the printer issue (e.g., add paper)  
2. Repeat the same API call including the `invoiceResponse` field
3. This signals the API to skip fiscalization and only retry printing

## Security Configuration

### API Key Security

Before using ESIR in production, review and strengthen security settings via these parameters:

| Parameter | Type | Description | Recommendation |
|-----------|------|-------------|----------------|
| `authorizeLocalClients` | boolean | Require API KEY from local clients | Set to `true` |
| `authorizeRemoteClients` | boolean | Require API KEY from remote clients | **Never set to `false`** unless access is secured otherwise |
| `apiKey` | string | API key value | Change from default for security |
| `webserverAddress` | string | API IP address and port | Use `127.0.0.1` for local-only access instead of `0.0.0.0` |

### Security Best Practices

1. **Change Default API Key**: Always change from the default API key to one only you know
2. **Local Access Only**: If only local clients need access, set IP address to `127.0.0.1` instead of `0.0.0.0`
3. **Require Authentication**: Always set `authorizeRemoteClients` to `true` for network access
4. **Restart After Changes**: Restart the server after changing `webserverAddress` parameter

## PIN Authentication Process

### PIN Entry Requirements

PIN authentication is required when the device General Status Code (GSC) indicates `1500`. The PIN authentication process:

1. **Check Status**: Call `/api/status` and check for GSC code `1500`
2. **Prompt User**: If `1500` is present, display PIN entry screen
3. **Submit PIN**: Send PIN via `/api/pin` endpoint
4. **Handle Response**: Process the response code

### PIN API Details

**Endpoint**: `POST /api/pin`  
**Content-Type**: `text/plain` (not JSON)  
**Authentication**: Required via Bearer token

#### Request Format
```http
POST /api/pin
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
Content-Type: text/plain

0A10015
```

#### Response Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `0100` | 200 OK | PIN correctly entered |
| `1300` | 4xx/5xx | Security element not present |
| `2400` | 4xx/5xx | LPFR not ready |
| `2800` | 4xx/5xx | Wrong PIN format (expected 4 digits) |
| `2806` | 4xx/5xx | Wrong PIN format (expected 4 digits) |

#### PIN Validation Rules

- **Format**: Exactly 4 digits required
- **Attempts**: Failed attempts are tracked
- **Lockout**: After 3 failed attempts, device enters error state (GSC `1300`)
- **Reset**: Successful PIN entry resets the failure counter

**Note**: Due to uniformity with LPFR APIs prescribed by PURS, this is the only API call that accepts plain text input (Content-type: text/plain) instead of JSON.

## Error Recovery Patterns

### Common Error Scenarios

1. **Service Unavailable**: Retry `/api/attention` until service responds
2. **Security Element Removed**: Monitor for GSC `1300` and prompt user to reinsert
3. **PIN Lock**: After 3 failed PIN attempts, device requires security element reinsertion
4. **Printer Issues**: Use `invoiceResponse` field to retry printing without re-fiscalization
5. **Network Issues**: Implement retry logic with exponential backoff