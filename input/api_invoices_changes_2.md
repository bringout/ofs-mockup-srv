# POST /api/invoices changes/2

## add receiptHeaderImage, receiptFooterImage

invoiceRequest can accept these optional parameters:
- `receiptHeaderImage`: base64 string of header image 
- `receiptFooterImage`: base64 string of footer image

if these fields are sent in request, console shoud report image of generated file.
For example, if convert base64 string to header.img is file 82123 bytes long, show on console:
```
Image header 82123 bytes. 
```

If conversion base64 => binary fails, show:
```
ERROR: receiptHeaderImage is not base64 encoded string 
```


## optional receiptHeaderTextLines(type list[string]) and receiptFooterTextLines(type list[string]) 

If request contains receiptHeaderTextLines, show on console these lines.
```
{
    "invoiceRequest": {
        "invoiceType": "Normal",
        "transactionType": "Sale",
        "receiptHeaderTextLines": [
            "Header Line 1",
            "Header Line 2"
        ],
        "receiptFooterTextLines": [
            "Footer Line 1",
            "Footer Line 2",
            "Footer Line 3"
        ],
        "payment": [
            {
                "amount": 100.00,
                "paymentType": "Cash"
            }
        ],
        "items": [
            {
                "name": "Artikl 1",
                "gtin": "12345678",
                "labels": [
                    "F"
                ],
                "totalAmount": 100.00,
                "unitPrice": 50.00,
                "quantity": 2.000
            }
        ],
        "cashier": "Radnik 1"
    }
}
```

Console output:
```

HEADER:
- Header Line 1
- Header Line 2

FOOTER:
- Footer Line 1
- Footer Line 2
- Footer Line 3