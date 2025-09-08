# POST /api/invoices changes


## Print to other printer: print_to_other_printer case


U slučaju da je potrebno račun odštampati na drugom štampaču umesto na OFS P5 EFU integrisanom štampaču potrebno je u zahtevu za izdavanje računa dodati sledeće parametre:

`print` (boolean) - postaviti na vrednost `false` - ovaj parametar označava da nije potrebno raditi štampu na internom štampaču

`renderReceiptImage` (boolean) - postaviti na vrednost `true` - ovaj parametar označava da je potrebno u rezultatu vratiti izgled računa

`receiptLayout` (string) - izgled računa u formatu isečka (vrednost `Slip`) odnosno u A4 formatu (vrednost `Invoice`)

`receiptImageFormat` (string) - format slike računa koji će biti generisan, moguće vrednosti: `Png` i `Pdf`

`receiptSlipWidth` (number) - ukoliko je račun u formatu isečka (Slip) onda ovaj parametar označava kolika je širina papira u pikselima (386 za 58mm odnosno 576 za 80mm)

`receiptSlipFontSizeNormal` (number) - ukoliko je račun u formatu isečka (Slip) onda ovaj parametar označava veličinu slova standardnog teksta na računu (preporučene vrednost 23 za 58mm papir, odnosno 25 za 80mm papir)

`receiptSlipFontSizeLarge` (number) - ukoliko je račun u formatu isečka (Slip) ond ovaj parametar označava veličinu slova velikog teksta na računu (preporučene vrednost 27 za 58mm papir, odnosno 30 za 80mm papir)

Ukoliko je račun uspešno izdat u rezultatu će se nalaziti sadržaj računa u zahtevanom formatu u polju:

`invoiceImagePngBase64` (base64) - base64 kodiran izgled računa u Png formatu
`invoiceImagePdfBase64` (base64) - base64 kodiran izgled računa u Pdf formatu

### Implementation of print=false

If request:
 - `print`: false
 - `renderReceiptImage`: true
 - `receiptLayout`: `Inovice` (other possible value  `Slip`)
 - `receiptImageFormat`: `Pdf` (other possible value `Png`)

Response contains:
 - `invoiceImagePdfBase64`: base64 encoded string with value of [test invoice](input/test_invoice.pdf)
 


## Add to invoiceRqeuest `byerId` field

add to `invoiceRequest` optional field

`buyerId` (string): identifikator kupca - optional, maximal length `20 characters` (ASCII isključivo) i sadrži identifikaciju kupca (JIB firme, broj lične karte, broj pasoša). 

if `byerId` is sent in request, server should print on console:

buyerId: {byerid_from_request}, if OFS system is registering grossale this field should start with: `VP:`

## Add to invoiceRequest/items(list(object)) `gtin` field

items (list(object)): stavke računa gde svaka stavka sadrži:
 - `name` (string, mandatory): naziv artikla, ukoliko je potrebno jedinicu mere treba dodati na kraju naziva artikla (npr: "Brašno /kg")
 - `gtin` (string, mandatory, 8-14 znakova): GTIN (barcode) artikla
 - `labels` (list(string), mandatory): niz poreskih stopa po kojima je oporezovana stavka (trenutno je u uvek jedna poreska stopa)
 - `unitPrice` (money, mandatory): jedinična cena
 - `quantity` (quantity, mandatory): količina
 - `totalPrice` (money, mandatory): ukupna cena
 - `discount` (percent): iznos uračunatog popusta u procentima
 - `discountAmount` (money): iznos u novcu uračunatog popusta

example:

```
{
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

`gtin` should be displayed on console for every item

