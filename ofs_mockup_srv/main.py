import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import List
import json
from random import randint
import datetime
from enum import Enum

import argparse

API_KEY = "api_key_0123456789abcdef0123456789abcdef"
SEND_CIRILICA = True
CIRILICA_E = "Е"
CIRILICA_K = "К"

PIN = "0A10015"

# Default device General Status Code (GSC) value for startup
DEFAULT_GSC = "9999"

BUSINESS_NAME = "Sigma-com doo Zenica"
BUSINESS_ADDRESS = "Ulica 7. Muslimanske brigade 77"
DISTRICT = "Zenica"


app = FastAPI()

app.state.gsc = DEFAULT_GSC
app.state.pin_fail_count = 0



@app.get("/")
def root():
    return {"msg": "I am OFS mock server"}


def check_api_key(req: Request):

    token = req.headers["Authorization"].replace("Bearer ", "").strip()

    if token != API_KEY:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, detail = "Unauthorized API-KEY %s" % (token)
        )
        return False

    return True


@app.get("/api/attention")
async def get_attention(req: Request):
    # Return current GSC to indicate whether attention is normal or PIN is required
    if check_api_key(req):
        return app.state.gsc
    else:
        return None









@app.post("/api/pin", response_class=PlainTextResponse)
async def post_pin(req: Request):
   if not check_api_key(req):
       return False
   # If device is in error state, don't accept PIN, only report error
   if app.state.gsc == "1300":
       return "1300"
   body = (await req.body()).decode('utf-8')
   response = "2400"
   if len(body) < 4:
       response = "2800"
   elif body == PIN:
       response = "0100"
       # Successful PIN entry unlocks device state and resets counter
       app.state.gsc = "9999"
       app.state.pin_fail_count = 0
   else:
       # Wrong 4-digit PIN attempt
       app.state.pin_fail_count = int(app.state.pin_fail_count) + 1
       if app.state.pin_fail_count >= 3:
           app.state.gsc = "1300"
           response = "1300"
       else:
           response = "2400"
   return response


class TaxRate(BaseModel):
    label: str
    rate: int

class TaxCategory(BaseModel):
    categoryType: int
    name: str
    orderId: int
    taxRates: list[TaxRate] = []
     

class TaxRates(BaseModel):
   groupId: str
   taxCategories: list[TaxCategory] = []
   validFrom: str
    
class Status(BaseModel):
   allTaxRates:  list[TaxRates] = [] 
   currentTaxRates: list[TaxRates] = []
   deviceSerialNumber: str
   gsc: list[str] = []
   hardwareVersion: str
   lastInvoiceNumber: str
   make: str 
   model: str
   mssc:  list[str] = []
   protocolVersion: str
   sdcDateTime: str
   softwareVersion: str
   supportedLanguages: list[str] = []



@app.get("/api/status")
async def get_status(req: Request):

    if not check_api_key(req):
        return False
    
    taxRate0 = TaxRate( rate = 0, label = "G")
    taxRateA = TaxRate( rate = 0, label = "A")
    taxRateE = TaxRate( rate = 10, label = "E")
    taxRateD = TaxRate( rate = 20, label = "D")


    if SEND_CIRILICA:
        taxCategory1 = TaxCategory(categoryType=0, name="Без ПДВ", orderId=4, taxRates=[taxRate0])
    else:
        taxCategory1 = TaxCategory(categoryType=0, name="Bez PDV Ž-kat", orderId=4, taxRates=[taxRate0])

    taxCategory2 = TaxCategory(categoryType=0, name="Nije u PDV", orderId=1, taxRates=[taxRateA])
    
    if SEND_CIRILICA:
        taxCategory3 = TaxCategory(categoryType=6, name="Г-A-Ђ-Љ П-ПДВ", orderId=3, taxRates=[taxRateE])
    else:
        taxCategory3 = TaxCategory(categoryType=6, name="P-PDV", orderId=3, taxRates=[taxRateE])
    
    taxCategory4 = TaxCategory(categoryType=6, name="D-PDV", orderId=3, taxRates=[taxRateD])

    allTaxRates = [
        TaxRates(
            groupId="1",
            taxCategories=[
                taxCategory1
            ],
            validFrom="2021-11-01T02:00:00.000+01:00"
        ),
        TaxRates(
            groupId="6",
            taxCategories=[
                taxCategory2,
                taxCategory3,
                taxCategory4
            ],
            validFrom=""
        )
    ]

    currentTaxRates = [
        TaxRates(
            groupId="6",
            taxCategories=[
                taxCategory1,
                taxCategory3
            ],
            validFrom = "2024-05-01T02:00:00.000+01:00"
        )
    ]
    
    response = Status(
        allTaxRates=allTaxRates,
        currentTaxRates=currentTaxRates,
        deviceSerialNumber = "01-0001-WPYB002248200772",
        gsc = [
         app.state.gsc,
         "0210"
        ],
        hardwareVersion = "1.0",
        lastInvoiceNumber = "RX4F7Y5L-RX4F7Y5L-132",
        make ="OFS",
        model = "OFS P5 EFU LPFR",
        mssc = [],
        protocolVersion = "2.0",
        sdcDateTime = "2024-09-15T23:03:24.390+01:00",
        softwareVersion = "2.0",
        

        supportedLanguages = [
         "bs-BA",
         "bs-Cyrl-BA",
         "sr-BA",
         "en-US"
        ]
    )

    return response
    
@app.post("/mock/lock")
async def mock_lock(req: Request):
    """Force device state into PIN-required mode (GSC=1500).
    Requires a valid API key. Returns the new GSC value.
    """
    if not check_api_key(req):
        return False
    app.state.gsc = "1500"
    app.state.pin_fail_count = 0
    return {"gsc": app.state.gsc}

class PaymentLine(BaseModel):
    amount: float
    paymentType: str


class ItemLine(BaseModel):
    name: str
    labels: list[str] = []
    totalAmount: float
    unitPrice: float
    quantity: float
    discount: float | None = None
    discountAmount: float | None = None


 
class InvoiceRequest(BaseModel):
    referentDocumentNumber: str | None = None
    referentDocumentDT: str | None = None
    invoiceType: str
    transactionType: str
    payment: list[PaymentLine] = []
    items: list[ItemLine] = []
    cashier: str

class InvoiceData(BaseModel):
    invoiceRequest: InvoiceRequest


class TaxItems(BaseModel):
    amount: float
    categoryName: str
    categoryType: int = 0
    label: str = "F"
    rate: int = 11
    
class InvoiceResponse(BaseModel):
    address: str
    businessName: str
    district: str
    encryptedInternalData: str
    invoiceCounter: str
    invoiceCounterExtension: str
    invoiceImageHtml: str | None = None
    invoiceImagePdfBase64: str | None = None
    invoiceImagePngBase64: str | None = None
    invoiceNumber: str
    journal: str
    locationName: str
    messages: str
    mrc: str
    requestedBy: str
    sdcDateTime: str
    signature: str
    signedBy: str
    taxGroupRevision: int
    taxItems: list[TaxItems] = []    
    tin: str
    totalAmount: float
    totalCounter: int
    transactionTypeCounter: int
    verificationQRCode: str 
    verificationUrl: str 




@app.post("/api/invoices")
async def invoice(req: Request, invoice_data: InvoiceData):

    # https://github.com/fastapi/fastapi/discussions/9601

    type = invoice_data.invoiceRequest.invoiceType
    cashier = invoice_data.invoiceRequest.cashier


    #items_length = len(invoice_data.invoiceRequest.items)
    referentDocumentNumber = invoice_data.invoiceRequest.referentDocumentNumber
    referentDocumentDT = invoice_data.invoiceRequest.referentDocumentDT
    transactionType = invoice_data.invoiceRequest.transactionType
    print()
    print("========== invoice request ===========")
    print("cahiser:", cashier)
    print("invoice request type:", type)
    print("transaction type:", transactionType)

    for payment in invoice_data.invoiceRequest.payment:
        print("paymentType:", payment.paymentType, " ; paymentAmount:", payment.amount )
    
    if type == "Copy":
        if (not referentDocumentNumber) or (not referentDocumentDT):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST, detail = "Copy ne sadrzi referentDocumentNumber and DT"
            )  
        else:
            print("referentni fiskalni dokument:", referentDocumentNumber, referentDocumentDT )  
         
    if transactionType == "Refund":
        print("refund referentni fiskalni dokument broj:", referentDocumentNumber, "datum:", referentDocumentDT )  
         
    totalValue = 0
    cStavke = ""


    for item in invoice_data.invoiceRequest.items:
        totalValue += item.totalAmount
        nDiscount = item.discount or 0.0
        nDiscountAmount = item.discountAmount or 0.00
        label = item.labels[0]
        cStavka = "%s quantity: %.2f unitPrice: %.2f discount: %.2f discountAmount: %.2f  totalAmount: %.2f label: %s\r\n" % (item.name, item.quantity, item.unitPrice, nDiscount, nDiscountAmount, item.totalAmount, label)
        cStavke += cStavka
        print(cStavka)
    #print(cStavke)

    print("totalValue:", totalValue)

    #payments_length = len(invoice_data.invoiceRequest.payment)

    cInvoiceNumber = str(randint(1,999)).zfill(3)

    cFullInvoiceNumber = "AX4F7Y5L-BX4F7Y5L-" + cInvoiceNumber

    cDTNow = datetime.datetime.now().isoformat()
    #>>> '2024-08-01T14:38:32.499588'

    if check_api_key(req):

        cRacun = None
        if type == "Normal":
            cRacun = "FISKALNI RAČUN"
        else:
            cRacun = "KOPIJA FISKALNOG RAČUNA"

        response = InvoiceResponse(
            address = BUSINESS_ADDRESS,
            businessName = BUSINESS_NAME,
            district = "ZEDO",
            encryptedInternalData = "Vvwq4nVn/wIQFAKE",
            invoiceCounter = "100/" + cInvoiceNumber + "ZE",
            invoiceCounterExtension = "ZE",
            invoiceImageHtml = None,
            invoiceImagePdfBase64 = None,
            invoiceImagePngBase64 = None,
            invoiceNumber = cFullInvoiceNumber,
            journal = "=========== " + cRacun + " ===========\r\n             4402692070009            \r\n       Sigma-com doo Zenica      \r\n      7. Muslimanske Brigade 77      \r\n              Zenica              \r\nKasir:                        Radnik 1\r\nESIR BROJ:                      13/2.0\r\n----------- PROMET PRODAJA -----------\r\nАrtikli                               \r\n======================================\r\nNaziv  Cijena        Kol.         Ukupno\r\n " + 
                       cStavke +
                       "--------------------------------------\r\n"
                       + "Ukupan iznos:                   " + "%.2f" % (totalValue) +
                       "\r\nGotovina:                     " + "%.2f" % (totalValue) +
                       "\r\n======================================\r\nOznaka    Naziv    Stopa    Porez\r\nF          ECAL      11%          9,91\r\n--------------------------------------\r\nUkupan iznos poreza:              9,91\r\n======================================\r\n" + 
                       "PFR brijeme:      12.03.2024. 07:47:09\r\nOFS br. rač:      " + cFullInvoiceNumber +
                       "\r\nBrojač računa:               100/138ZE\r\n======================================" +
                       "\r\n======== KRAJ " + cRacun + "=======\r\n",
            locationName = "Sigma-com doo Zenica poslovnica Sarajevo",
            messages = "Uspješno",
            mrc = "01-0001-WPYB002248200772",
            requestedBy = "RX4F7Y5L",
            sdcDateTime = cDTNow,  #"2024-09-15T07:47:09.548+01:00",
            signature = "Mw+IB0vgnaMjYrwA7m7zhtRseRIZFAKE",
            signedBy = "RX4F7Y5L",
            taxGroupRevision = 2,
            taxItems = [ TaxItems(amount=9.9099, categoryName="ECAL", categoryType = 0, label = "F", rate = 11) ],
            tin = "4402692070009",
            totalAmount = totalValue,
            totalCounter = 138,
            transactionTypeCounter = 100,
            verificationQRCode = "R0lGODlhhAGEAfFAKE",
            verificationUrl = "https://sandbox.suf.poreskaupravars.org/v/?vl=A1JYNEY3WTVMUlg0FAKE="
        )

        return response
    else:
        return None
 


class InvoiceTypes(str, Enum):
    normal = "Normal"
    advance = "Advance"
    
class TransactionTypes(str, Enum):
    sale = "Sale"
    refund = "Refund"

class PaymentTypes(str, Enum):
    cash = "Cash"
    wireTransfer = "WireTransfer"
    card = "Card"
    other = "Other"


class InvoiceSearch(BaseModel):
    fromDate: datetime.date
    toDate: datetime.date
    amountFrom: float | None = None
    amountTo: float | None = None
    invoiceTypes: list[InvoiceTypes]
    transactionTypes: list[TransactionTypes]
    paymentTypes: list[PaymentTypes]


@app.post("/api/invoices/search")
async def invoices_search(req: Request, invoiceSearchData: InvoiceSearch):


    print("================= invoice search ==============================")
    print( "search from:", invoiceSearchData.fromDate, " to: ",  invoiceSearchData.toDate)


    lista_racuna = """RX4F7Y5L-RX4F7Y5L-1,Normal,Sale,2024-03-06T17:33:12.582+01:00,10.0000
RX4F7Y5L-RX4F7Y5L-131,Normal,Sale,2024-03-11T20:29:05.329+01:00,10.0000
RX4F7Y5L-RX4F7Y5L-132,Normal,Sale,2024-03-11T20:29:25.422+01:00,15.0000
RX4F7Y5L-RX4F7Y5L-133,Normal,Sale,2024-03-11T23:05:53.608+01:00,100.0000
RX4F7Y5L-RX4F7Y5L-134,Normal,Sale,2024-03-11T23:13:55.829+01:00,100.0000
RX4F7Y5L-RX4F7Y5L-135,Normal,Sale,2024-03-11T23:16:03.098+01:00,300.0000
RX4F7Y5L-RX4F7Y5L-137,Normal,Refund,2024-03-11T23:19:54.853+01:00,100.0000
RX4F7Y5L-RX4F7Y5L-138,Normal,Sale,2024-03-12T07:47:09.548+01:00,100.0000
RX4F7Y5L-RX4F7Y5L-139,Normal,Sale,2024-03-12T07:47:38.530+01:00,100.0000
RX4F7Y5L-RX4F7Y5L-140,Normal,Sale,2024-03-12T07:48:47.626+01:00,300.0000
RX4F7Y5L-RX4F7Y5L-142,Normal,Refund,2024-03-12T07:50:19.735+01:00,100.0000
RX4F7Y5L-RX4F7Y5L-143,Advance,Sale,2024-03-12T07:51:53.207+01:00,100.0000
RX4F7Y5L-RX4F7Y5L-144,Advance,Sale,2024-03-12T07:53:26.177+01:00,400.0000
RX4F7Y5L-RX4F7Y5L-145,Advance,Refund,2024-03-12T07:55:07.582+01:00,500.0000
"""

    if check_api_key(req):
        return lista_racuna
    

    return lista_racuna







@app.get('/api/invoices/{invoiceNumber}')
async def get_invoice(invoiceNumber: str, imageFormat: str | None = None, includeHeaderAndFooter: bool | None = None, receiptLayout: str | None = None ):
    print("Invoice number:", invoiceNumber)
    print("PARAMS:  imageFormat:", imageFormat, " includeHeaderAndFooter:", includeHeaderAndFooter, " receiptLayout:", receiptLayout)

    lPDV17 = True if invoiceNumber[0:1] != "0" else False

    if invoiceNumber.strip() == "ERROR":
        return {"error": 1 }
    
    return {
        "autoGenerated": False,
        "invoiceRequest": {
            "buyerCostCenterId": None,
            "buyerId": None,
            "cashier": "Radnik 1",
            "dateAndTimeOfIssue": None,
            "invoiceNumber": "13/2.0",
            "invoiceType": "Normal",
            "items": [
                {
                    "articleUuid": None,
                    "discount": None,
                    "discountAmount": None,
                    "gtin": None,
                    "labels": [ CIRILICA_E ] if SEND_CIRILICA else [
                        "E"
                    ],
                    "name": "Artikl 1",
                    "plu": None,
                    "quantity": 2,
                    "totalAmount": 100,
                    "unitPrice": 50
                }
            ],
            "options": {
            "omitQRCodeGen": 1,
            "omitTextualRepresentation": None
            },
            "payment": [
                {
                    "amount": 100,
                    "paymentType": "Cash"
                }
            ],
            "referentDocumentDT": None,
            "referentDocumentNumber": None,
            "transactionType": "Sale"
        },
        "invoiceResponse": {
            "address": BUSINESS_ADDRESS,
            "businessName": BUSINESS_NAME,
            "district": DISTRICT,
            "encryptedInternalData": None,
            "invoiceCounter": "100/138ПП",
            "invoiceCounterExtension": "ПП",
            "invoiceImageHtml": None,
            "invoiceImagePdfBase64": None,
            "invoiceImagePngBase64": None,
            "invoiceNumber": invoiceNumber,
            "journal": None,
            "locationName": BUSINESS_NAME,
            "messages": "Uspješno",  #"Успешно",
            "mrc": "01-0001-WPYB002248200772",
            "requestedBy": "RX4F7Y5L",
            "sdcDateTime": "2024-03-12T07:47:09.548+01:00",
            "signature": None,
            "signedBy": "RX4F7Y5L",
            "taxGroupRevision": 2,
            "taxItems": [
                    {
                        "amount": 8.52,
                        "categoryName": "ECAL",
                        "categoryType": 0,
                        "label": "E",
                        "rate": 17
                    } if lPDV17 else
                    {
                        "amount": 0.0,
                        "categoryName": "NULA",
                        "categoryType": 0,
                        "label": "K",
                        "rate": 0
                    }
            ],
            "tin": "4402692070009",
            "totalAmount": 100,
            "totalCounter": 138,
            "transactionTypeCounter": 100,
            "verificationQRCode": "R0lGODlhhAGEAfAAAFAKE",
            "verificationUrl": "https://sandbox.suf.poreskaupravars.org/v/?vl=A1JYNEY3WTVMUlg0RjdZNUyKAAAAZAAAAEBCDwAAAAAAAAABjjFqO+wAAABW/CridWf/AhDKQHvQyoCT3HBCLwZvH/v4JxyQ/63YKX/GXViHprxs3ZGe8VR7lXDR6UKrQCyuZd4rMOpo3JYisQyV0A9AW5QBCzUCLzYkpiyint98f7Vu4FJcFijOMrWekwxh1rjUsLp2WaL0yY+gSWebEEabv4Tq16272j1LukALa2Lo5C3qRyU8HFzSwYky4F7zsVQnqJRoSb7MenE3NnH+O45iLfiA1zOPruW+KrwVwQGi1iUV4ejSXmAsrML+27UMALiGKd11XNaD/XEEyzbLOCYSbEPnepGUSQ6Kh2Zr+J++fNvxm9gfd3P4qqm2au7fu1Cs7W2ow86QQBjRMw+IB0vgnaMjYrwA7m7zhtRseRIZiGGB6pdIQM7enPhPZUfIeKsSTjQ3CCdeSMGpWhDMGileZcTZkkkMVFML8VnFM+l2dhPSoIeJ6llY5RmcfbN5ESXMEYP8LJ58ONeychjKCi/zVhMx0+ox5bWcWsRwBMyIlfFTFAKE="
        },
        "issueCopy": False,
        "print": True,
        "receiptImageBase64": "iVBORw0KGgoAAkkZu/FAKE",
        "receiptImageFormat": "Png",
        "receiptLayout": "Slip",
        "renderReceiptImage": False,
        "skipEftPos": False,
        "skipEftPosPrint": False
    }


def main():
    """Main entry point for the OFS mockup server."""
    parser = argparse.ArgumentParser(description="OFS Mockup Server")
    parser.add_argument("--gsc", default=DEFAULT_GSC, help="Initial GSC value (1300|1500|9999)")
    parser.add_argument("--port", type=int, default=8200, help="Port to bind")
    args, _ = parser.parse_known_args()

    # Initialize app state from CLI args
    app.state.gsc = str(args.gsc)

    uvicorn.run(
        "ofs_mockup_srv.main:app",
        host="0.0.0.0",
        port=args.port,
        reload=True,
        access_log=False,
        workers=1,
    )

if __name__ == "__main__":
    main()


