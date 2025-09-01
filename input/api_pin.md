### PIN Authentication

Pin mandatory is `4 digits`. Default pin have to be `4321`

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
- `"1300"` - Security element not present
- `"2800"` - Invalid PIN format (expected 4 digits)
- `"2806"` - Invalid PIN format (expected 4 digits)

**Status Codes:**
- `0100` - PIN entered correctly
- `1300` - Security element not present
- `2400` - LPFR not ready
- `2800`/`2806` - Invalid PIN format
