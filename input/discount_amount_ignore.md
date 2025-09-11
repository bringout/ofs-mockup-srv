# Discount amount as client request

If client in invoice request dont't send discountAmount, DON'T SHOW IT HERE as discountAmount: 0.00:

```
....
paymentType: WireTransfer  ; paymentAmount: 1.87
refund referentni fiskalni dokument broj: AX4F7Y5L-BX4F7Y5L-617 datum: 2025-09-10
gtin: 3850108030525
KEFIR 3,5% mm 200 G            quantity: 1.00 unitPrice: 0.74 discount: 2.00 discountAmount: 0.00  totalAmount: 0.73 label: Е gtin: 3850108030525
...
```
