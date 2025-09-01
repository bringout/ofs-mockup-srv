# API Workflows and Integration Patterns

## Standard Integration Workflow

Follow this workflow when integrating with the OFS Mockup Server:

### 1. Check Service Availability

Verify that ESIR and PFR are available by calling `/api/attention`. If the HTTP response is 404, display an appropriate message to the user and retry after a few seconds. Continue checking without limitation until ESIR becomes available (HTTP 200).

```bash
while true; do
  # Check if service responds
  status_code=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer api_key_0123456789abcdef0123456789abcdef" \
    http://localhost:8200/api/attention)
  if [ "$status_code" = "200" ]; then
    break  # Service is available
  fi
  sleep 2  # Wait before retry
done
```

### 2. Service Availability Check

If `/api/attention` returns HTTP 404, the service is unavailable. This could indicate:
- Device initialization needed
- Security element issues
- PIN entry required
- System lock state

Use `/api/status` to get detailed device information if needed for diagnostics, but the primary availability check is the HTTP status from `/api/attention`.

### 3. Service Recovery

If service is unavailable (HTTP 404 from `/api/attention`):
1. **PIN Entry**: Attempt PIN authentication via `/api/pin` (successful PIN entry will make service available)
2. **Check detailed status** via `/api/status` for diagnostic information if needed
3. **Mock Control**: Use `/mock/unlock` to force service availability in testing scenarios

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

PIN authentication integrates with the service availability system. The PIN authentication process:

1. **Check Availability**: Call `/api/attention` - if returns 404, service may need PIN
2. **Prompt User**: Display PIN entry screen if service is unavailable
3. **Submit PIN**: Send PIN via `/api/pin` endpoint  
4. **Verify Availability**: Successful PIN entry automatically sets service to available (HTTP 200 from `/api/attention`)
5. **Check Details**: Use `/api/status` for additional diagnostic information if needed

### PIN API Details

**Endpoint**: `POST /api/pin`  
**Content-Type**: `text/plain` (not JSON)  
**Authentication**: Required via Bearer token

#### Request Format
```http
POST /api/pin
Authorization: Bearer api_key_0123456789abcdef0123456789abcdef
Content-Type: text/plain

4321
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

1. **Service Unavailable**: Retry `/api/attention` until service responds with HTTP 200
2. **PIN Authentication Required**: If `/api/attention` returns 404, attempt PIN entry via `/api/pin`
3. **PIN Lock**: After failed PIN attempts, service may remain unavailable until resolved
4. **Printer Issues**: Use `invoiceResponse` field to retry printing without re-fiscalization
5. **Network Issues**: Implement retry logic with exponential backoff
6. **Mock Control**: Use `/mock/unlock` to force service availability during testing