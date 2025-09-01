# Data Types and Field Definitions

## Supported Data Types

The OFS Mockup Server uses the following data types for API fields:

| Type | Description | Example |
|------|-------------|---------|
| **string** | Textual field | `"Normal"` |
| **int** | Integer value | `100` |
| **boolean** | Logical field (true or false) | `true` |
| **money** | Decimal number with two decimals | `99.99` |
| **quantity** | Decimal number with three decimals | `2.000` |
| **percent** | Decimal number with two decimals | `10.50` |
| **timestamp** | Date and time in ISO 8601 format with timezone | `"2023-11-15T13:31:50.000+01:00"` |
| **uuid** | UUID v4 | `"550e8400-e29b-41d4-a716-446655440000"` |
| **object** | JSON object containing attributes and values | `{"name": "value"}` |
| **list(x)** | JSON array containing elements of type x | `["item1", "item2"]` |

## Transaction Types

The `transactionType` field can have the following values:

| Value | Description |
|-------|-------------|
| **Sale** | Regular sale transaction |
| **Refund** | Refund/return transaction |

## Invoice Types

The `invoiceType` field supports these values:

| Value | Description |
|-------|-------------|
| **Normal** | Standard fiscal receipt (promet) |
| **Proforma** | Proforma invoice (predračun) |
| **Copy** | Copy of existing receipt (kopija) |
| **Training** | Training mode receipt (trening) |
| **Advance** | Advance payment receipt (avans) |

## Payment Types

The `paymentType` field accepts these payment methods:

| Value | Description |
|-------|-------------|
| **Cash** | Cash payment (gotovina) |
| **Card** | Credit/debit card payment (platna kartica) |
| **Check** | Check payment (ček) |
| **WireTransfer** | Bank transfer (prenos na račun) |
| **Voucher** | Voucher payment (vaučer) |
| **MobileMoney** | Mobile/instant payment (instant plaćanje) |
| **Other** | Other cashless payment (drugo bezgotovinsko plaćanje) |

## Item Structure Fields

Invoice items contain the following fields:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| **name** | string | Article name | Yes |
| **gtin** | string | GTIN (barcode) of the article | No |
| **labels** | list(string) | Tax rates applied to the item (usually one rate in Serbia) | Yes |
| **unitPrice** | money | Unit price | Yes |
| **quantity** | quantity | Quantity | Yes |
| **totalAmount** | money | Total price | Yes |
| **discount** | percent | Discount percentage applied | No |
| **discountAmount** | money | Discount amount in currency | No |

## Tax Label Categories

The following tax labels are supported:

| Label | Rate | Description |
|-------|------|-------------|
| **E** | 10% (mockup) / 17% (real) | Standard VAT rate |
| **D** | 20% | Higher VAT rate |
| **K** | 0% | Zero VAT rate |
| **G** | 0% | Zero VAT rate (alternative) |
| **A** | 0% | VAT exempt |
| **F** | 11% | Special rate |