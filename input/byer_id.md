# invoice with byer info

Example request
```
curl --location 'http://127.0.0.1:3566/api/invoices' \
--header 'Authorization: Bearer 0123456789abcdef0123456789abcdef' \
--header 'RequestId: 12345' \
--header 'Content-Type: application/json' \
--data '{
    "invoiceRequest": {
        "invoiceType": "Normal",
        "transactionType": "Sale",
        "buyerId": "111758195",
        "payment": [
            {
                "amount": 100.00,
                "paymentType": "Cash"
            }
        ],
        "items": [
            {
                "name": "Artikl 1 /kg",
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
}'
```


```
{
  "address": "Dunavska 1c",
  "businessName": "Aero Centar Krila  d.o.o.",
  "district": "Banja Luka",
  "encryptedInternalData": "Z1O1FZjxn23+BEdS...",
  "invoiceCounter": "101/139ПП",
  "invoiceCounterExtension": "ПП",
  "invoiceImageHtml": null,
  "invoiceImagePdfBase64": null,
  "invoiceImagePngBase64": null,
  "invoiceNumber": "RX4F7Y5L-RX4F7Y5L-139",
  "journal": "=========== ФИСКАЛНИ РАЧУН ===========\r\n             4401686560006            \r\n       Aero Centar Krila  d.o.o.      \r\n       Aero Centar Krila  d.o.o.      \r\n            Dunavska 1c               \r\n              Banja Luka              \r\nИД купца:                 111758195\r\nКасир:                        Radnik 1\r\nЕСИР број:                      13/2.0\r\n----------- ПРОМЕТ ПРОДАЈА -----------\r\nАртикли                               \r\n======================================\r\nНазив  Цена        Кол.         Укупно\r\nArtikl 1 (F)                          \r\n      50,00       2,000         100,00\r\n--------------------------------------\r\nУкупан износ:                   100,00\r\nГотовина:                       100,00\r\n======================================\r\nОзнака    Назив    Стопа         Порез\r\nF          ECAL      11%          9,91\r\n--------------------------------------\r\nУкупан износ пореза:              9,91\r\n======================================\r\nПФР вријеме:      12.03.2024. 07:47:38\r\nПФР бр.рач:      RX4F7Y5L-RX4F7Y5L-139\r\nБројач рачуна:               101/139ПП\r\n======================================\r\n======== КРАЈ ФИСКАЛНОГ РАЧУНА =======\r\n",
  "locationName": "Aero Centar Krila  d.o.o.",
  "messages": "Успешно",
  "mrc": "01-0001-WPYB002248000772",
  "requestedBy": "RX4F7Y5L",
  "sdcDateTime": "2024-03-12T07:47:38.530+01:00",
  "signature": "PIB3Tr2V+01aimBSfOoR...",
  "signedBy": "RX4F7Y5L",
  "taxGroupRevision": 2,
  "taxItems": [
    {
      "amount": 9.9099,
      "categoryName": "ECAL",
      "categoryType": 0,
      "label": "F",
      "rate": 11
    }
  ],
  "tin": "4401686560006",
  "totalAmount": 100,
  "totalCounter": 139,
  "transactionTypeCounter": 101,
  "verificationQRCode": "R0lGODlhhAGEAfA...",
  "verificationUrl": "https://sandbox.suf.poreskaupravars.org/v/?vl=A1JYNEY3WTVMUlg..."
}
```