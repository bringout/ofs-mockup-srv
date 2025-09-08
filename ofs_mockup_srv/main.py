import argparse
import base64
import datetime
import json
import os
import time
from enum import Enum
from random import randint

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from fastapi.responses import JSONResponse

API_KEY = "api_key_0123456789abcdef0123456789abcdef"
SEND_CIRILICA = True
CIRILICA_E = "Е"
CIRILICA_K = "К"

# Default PIN - can be overridden via app.state.pin
PIN = "4321"

# Default device availability state
DEFAULT_AVAILABLE = True

BUSINESS_NAME = "Sigma-com doo Zenica"
BUSINESS_ADDRESS = "Ulica 7. Muslimanske brigade 77"
DISTRICT = "Zenica"


app = FastAPI()


# Debug logging helper
def debug_log_request(request: Request, body: str = ""):
    if hasattr(app.state, "debug_enabled") and app.state.debug_enabled:
        print(f"🔵 Request: {request.method} {request.url.path}", flush=True)
        if request.query_params:
            print(f"   Query: {dict(request.query_params)}", flush=True)
        if request.headers.get("authorization"):
            auth = request.headers["authorization"]
            if "Bearer" in auth:
                token = auth.replace("Bearer ", "")[:20] + "..."
                print(f"   Auth: Bearer {token}", flush=True)
        if body:
            if len(body) > 200:
                print(f"   Body: {body[:200]}...", flush=True)
            else:
                print(f"   Body: {body}", flush=True)


def debug_log_response(status_code: int, response_data=None):
    if hasattr(app.state, "debug_enabled") and app.state.debug_enabled:
        print(f"🟢 Response: {status_code}", flush=True)
        if response_data is not None:
            if isinstance(response_data, dict) or isinstance(response_data, list):
                response_str = json.dumps(response_data, indent=2)
                if len(response_str) > 200:
                    print(f"   Data: {response_str[:200]}...", flush=True)
                else:
                    print(f"   Data: {response_str}", flush=True)
            else:
                print(f"   Data: {response_data}", flush=True)
        print("", flush=True)


# HTTP middleware to log request/response including small bodies when debug is enabled
@app.middleware("http")
async def debug_request_response_middleware(request: Request, call_next):
    """Logs method/path, headers, and JSON/text bodies when debug is on.

    - Safely buffers request body and re-injects it for downstream handlers.
    - Buffers small response bodies to log them, then rebuilds the response.
    - Truncates very large bodies to keep logs readable.
    """
    DEBUG_MAX_BYTES = 100_000  # cap printed body size (~100 KB)

    debug_on = hasattr(app.state, "debug_enabled") and app.state.debug_enabled

    # Capture request body and rebuild a fresh Request so downstream can read it
    body_bytes = b""
    try:
        body_bytes = await request.body()
    except Exception:
        body_bytes = b""

    if debug_on:
        try:
            print(f"🔵 Request: {request.method} {request.url.path}", flush=True)
            # Headers of interest
            auth = request.headers.get("authorization")
            if auth:
                token = auth.replace("Bearer ", "")
                token = (token[:20] + "...") if len(token) > 20 else token
                print(f"   Auth: Bearer {token}", flush=True)
            if request.query_params:
                print(f"   Query: {dict(request.query_params)}", flush=True)
            # Body (for JSON/text)
            ctype = request.headers.get("content-type", "")
            if body_bytes and ("application/json" in ctype or "text/plain" in ctype):
                to_show = body_bytes[:DEBUG_MAX_BYTES]
                try:
                    if "application/json" in ctype:
                        import json as _json

                        parsed = _json.loads(to_show.decode("utf-8", errors="replace"))
                        pretty = _json.dumps(parsed, ensure_ascii=False, indent=2)
                        print(f"   Body JSON: {pretty}", flush=True)
                    else:
                        print(
                            f"   Body Text: {to_show.decode('utf-8', errors='replace')}",
                            flush=True,
                        )
                except Exception:
                    # Fallback raw if parsing fails
                    print(f"   Body Raw: {to_show!r}", flush=True)
        except Exception:
            pass

    # Recreate a request with the captured body for downstream
    async def receive():
        return {"type": "http.request", "body": body_bytes, "more_body": False}

    from starlette.requests import Request as StarletteRequest

    downstream_request = StarletteRequest(request.scope, receive)

    # Call downstream and capture response body if small/JSON/text
    response = await call_next(downstream_request)

    if not debug_on:
        return response

    try:
        # Only buffer and log small JSON/text responses
        resp_ctype = (response.headers.get("content-type") or "").lower()
        if "application/json" in resp_ctype or "text/plain" in resp_ctype:
            content_chunks = []
            async for chunk in response.body_iterator:
                content_chunks.append(chunk)
                # Avoid buffering arbitrarily huge bodies
                if sum(len(c) for c in content_chunks) > DEBUG_MAX_BYTES:
                    break
            content = b"".join(content_chunks)

            # Print response line + body
            print(
                f"🟢 Response: {response.status_code} {request.method} {request.url.path}",
                flush=True,
            )
            try:
                if "application/json" in resp_ctype:
                    import json as _json

                    parsed = _json.loads(content.decode("utf-8", errors="replace"))
                    pretty = _json.dumps(parsed, ensure_ascii=False, indent=2)
                    print(f"   Data JSON: {pretty}", flush=True)
                else:
                    print(
                        f"   Data Text: {content.decode('utf-8', errors='replace')}",
                        flush=True,
                    )
            except Exception:
                print(f"   Data Raw: {content!r}", flush=True)
            print("", flush=True)

            # Rebuild response so the client still receives the body
            from starlette.responses import Response as StarletteResponse

            new_resp = StarletteResponse(
                content=content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
                background=response.background,
            )
            return new_resp
        else:
            # Non-JSON/text: just print status line
            print(
                f"🟢 Response: {response.status_code} {request.method} {request.url.path}",
                flush=True,
            )
            print("", flush=True)
            return response
    except Exception:
        # On any error, fall back to original response
        return response


# Initialize from environment variables (set by start_server.py) or defaults
app.state.pin_fail_count = 0
app.state.current_api_attention = (
    200 if os.getenv("OFS_MOCKUP_AVAILABLE") == "true" else 404
)
app.state.debug_enabled = os.getenv("OFS_MOCKUP_DEBUG") == "true"
app.state.pin = os.getenv("OFS_MOCKUP_PIN", PIN)


@app.get("/")
def root():
    return {"msg": "I am OFS mock server"}


def check_api_key(req: Request):

    token = req.headers["Authorization"].replace("Bearer ", "").strip()

    if token != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized API-KEY %s" % (token),
        )

    return True


@app.get("/api/attention")
async def get_attention(req: Request):
    # Return HTTP status based on current_api_attention state
    debug_log_request(req)
    if not check_api_key(req):
        debug_log_response(401, "Unauthorized")
        raise HTTPException(status_code=401, detail="Unauthorized")

    if app.state.current_api_attention == 200:
        debug_log_response(200, "Service available")
        return  # HTTP 200 with no body
    else:
        debug_log_response(404, "Service not available")
        raise HTTPException(status_code=404, detail="Service not available")


@app.post("/api/pin", response_class=PlainTextResponse)
async def post_pin(req: Request):
    body = (await req.body()).decode("utf-8")
    debug_log_request(req, body)

    if not check_api_key(req):
        debug_log_response(401, "Unauthorized")
        return False

    # If device is in error state (after 3 PIN failures), only report error
    if app.state.pin_fail_count >= 3:
        debug_log_response(200, "1300 (device locked)")
        return "1300"

    response = "2400"
    if len(body) != 4:
        response = "2800"
        debug_log_response(200, f"{response} (wrong PIN format)")
    elif body == app.state.pin:
        response = "0100"
        # Successful PIN entry resets counter
        app.state.pin_fail_count = 0
        app.state.current_api_attention = 200  # Set service as available
        debug_log_response(200, f"{response} (PIN correct, service available)")
    else:
        # Wrong 4-digit PIN attempt
        app.state.pin_fail_count = int(app.state.pin_fail_count) + 1
        app.state.current_api_attention = (
            404  # Set service as unavailable on PIN failure
        )
        if app.state.pin_fail_count >= 3:
            response = "1300"
            debug_log_response(200, f"{response} (device locked after 3 failures)")
        else:
            response = "2400"
            debug_log_response(
                200, f"{response} (wrong PIN, attempt {app.state.pin_fail_count})"
            )

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
    allTaxRates: list[TaxRates] = []
    currentTaxRates: list[TaxRates] = []
    deviceSerialNumber: str
    gsc: list[str] = []  # Status codes for compatibility
    hardwareVersion: str
    lastInvoiceNumber: str
    make: str
    model: str
    mssc: list[str] = []
    protocolVersion: str
    sdcDateTime: str
    softwareVersion: str
    supportedLanguages: list[str] = []


@app.get("/api/status")
async def get_status(req: Request):

    if not check_api_key(req):
        return False

    taxRate0 = TaxRate(rate=0, label="G")
    taxRateA = TaxRate(rate=0, label="A")
    taxRateE = TaxRate(rate=10, label="E")
    taxRateD = TaxRate(rate=20, label="D")

    if SEND_CIRILICA:
        taxCategory1 = TaxCategory(
            categoryType=0, name="Без ПДВ", orderId=4, taxRates=[taxRate0]
        )
    else:
        taxCategory1 = TaxCategory(
            categoryType=0, name="Bez PDV Ž-kat", orderId=4, taxRates=[taxRate0]
        )

    taxCategory2 = TaxCategory(
        categoryType=0, name="Nije u PDV", orderId=1, taxRates=[taxRateA]
    )

    if SEND_CIRILICA:
        taxCategory3 = TaxCategory(
            categoryType=6, name="Г-A-Ђ-Љ П-ПДВ", orderId=3, taxRates=[taxRateE]
        )
    else:
        taxCategory3 = TaxCategory(
            categoryType=6, name="P-PDV", orderId=3, taxRates=[taxRateE]
        )

    taxCategory4 = TaxCategory(
        categoryType=6, name="D-PDV", orderId=3, taxRates=[taxRateD]
    )

    allTaxRates = [
        TaxRates(
            groupId="1",
            taxCategories=[taxCategory1],
            validFrom="2021-11-01T02:00:00.000+01:00",
        ),
        TaxRates(
            groupId="6",
            taxCategories=[taxCategory2, taxCategory3, taxCategory4],
            validFrom="",
        ),
    ]

    currentTaxRates = [
        TaxRates(
            groupId="6",
            taxCategories=[taxCategory1, taxCategory3],
            validFrom="2024-05-01T02:00:00.000+01:00",
        )
    ]

    response = Status(
        allTaxRates=allTaxRates,
        currentTaxRates=currentTaxRates,
        deviceSerialNumber="01-0001-WPYB002248200772",
        gsc=["9999", "0210"],  # Always ready for status endpoint
        hardwareVersion="1.0",
        lastInvoiceNumber="RX4F7Y5L-RX4F7Y5L-132",
        make="OFS",
        model="OFS P5 EFU LPFR",
        mssc=[],
        protocolVersion="2.0",
        sdcDateTime="2024-09-15T23:03:24.390+01:00",
        softwareVersion="2.0",
        supportedLanguages=["bs-BA", "bs-Cyrl-BA", "sr-BA", "en-US"],
    )

    return response


@app.api_route("/mock/lock", methods=["GET", "POST"])
async def mock_lock(req: Request):
    """Set service to unavailable state (current_api_attention=404).
    No API key required for mock endpoints.
    """
    debug_log_request(req)
    app.state.current_api_attention = 404
    # No GSC state needed - only current_api_attention matters
    app.state.pin_fail_count = 0
    response = {"current_api_attention": app.state.current_api_attention}
    debug_log_response(200, response)
    return response


@app.api_route("/mock/unlock", methods=["GET", "POST"])
async def mock_unlock(req: Request):
    """Set service to available state (current_api_attention=200).
    No API key required for mock endpoints.
    """
    debug_log_request(req)
    app.state.current_api_attention = 200
    # No GSC state needed - only current_api_attention matters
    response = {"current_api_attention": app.state.current_api_attention}
    debug_log_response(200, response)
    return response


@app.get("/mock/current_api_attention")
async def mock_get_current_api_attention(req: Request):
    """Get the current service availability state.
    No API key required for mock endpoints.
    """
    debug_log_request(req)
    response = app.state.current_api_attention
    debug_log_response(200, response)
    return response


class PaymentLine(BaseModel):
    amount: float
    paymentType: str


class ItemLine(BaseModel):
    name: str
    gtin: str | None = None
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
    buyerId: str | None = None
    print: bool | None = None
    renderReceiptImage: bool | None = None
    receiptLayout: str | None = None
    receiptImageFormat: str | None = None
    receiptSlipWidth: int | None = None
    receiptSlipFontSizeNormal: int | None = None
    receiptSlipFontSizeLarge: int | None = None
    receiptHeaderImage: str | None = None
    receiptFooterImage: str | None = None
    receiptHeaderTextLines: list[str] | None = None
    receiptFooterTextLines: list[str] | None = None


class InvoiceData(BaseModel):
    invoiceRequest: InvoiceRequest


class TaxItems(BaseModel):
    amount: float
    categoryName: str
    categoryType: int = 0
    label: str = "F"
    rate: int = 11


class ErrorResponse(BaseModel):
    details: str | None = None
    message: str
    statusCode: int = -1


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
    buyerId = invoice_data.invoiceRequest.buyerId
    print_receipt = invoice_data.invoiceRequest.print
    render_receipt_image = invoice_data.invoiceRequest.renderReceiptImage
    receipt_layout = invoice_data.invoiceRequest.receiptLayout
    receipt_image_format = invoice_data.invoiceRequest.receiptImageFormat
    receipt_slip_width = invoice_data.invoiceRequest.receiptSlipWidth
    receipt_slip_font_size_normal = invoice_data.invoiceRequest.receiptSlipFontSizeNormal
    receipt_slip_font_size_large = invoice_data.invoiceRequest.receiptSlipFontSizeLarge
    receipt_header_image = invoice_data.invoiceRequest.receiptHeaderImage
    receipt_footer_image = invoice_data.invoiceRequest.receiptFooterImage
    receipt_header_text_lines = invoice_data.invoiceRequest.receiptHeaderTextLines
    receipt_footer_text_lines = invoice_data.invoiceRequest.receiptFooterTextLines

    # items_length = len(invoice_data.invoiceRequest.items)
    referentDocumentNumber = invoice_data.invoiceRequest.referentDocumentNumber
    referentDocumentDT = invoice_data.invoiceRequest.referentDocumentDT
    transactionType = invoice_data.invoiceRequest.transactionType
    print()
    print("========== invoice request ===========")
    print("cahiser:", cashier)
    print("invoice request type:", type)
    print("transaction type:", transactionType)
    
    # Log buyerId if present
    if buyerId:
        print(f"buyerId: {buyerId}, if OFS system is registering grossale this field should start with: VP:")
    
    # Log receipt printing parameters
    if print_receipt is not None:
        print(f"print: {print_receipt}")
    if render_receipt_image is not None:
        print(f"renderReceiptImage: {render_receipt_image}")
    if receipt_layout is not None:
        print(f"receiptLayout: {receipt_layout}")
    if receipt_image_format is not None:
        print(f"receiptImageFormat: {receipt_image_format}")
    if receipt_slip_width is not None:
        print(f"receiptSlipWidth: {receipt_slip_width}")
    if receipt_slip_font_size_normal is not None:
        print(f"receiptSlipFontSizeNormal: {receipt_slip_font_size_normal}")
    if receipt_slip_font_size_large is not None:
        print(f"receiptSlipFontSizeLarge: {receipt_slip_font_size_large}")
    
    # Handle receipt header/footer images
    if receipt_header_image is not None:
        try:
            decoded_header = base64.b64decode(receipt_header_image)
            print(f"Image header {len(decoded_header)} bytes.")
        except Exception:
            print("ERROR: receiptHeaderImage is not base64 encoded string")
    
    if receipt_footer_image is not None:
        try:
            decoded_footer = base64.b64decode(receipt_footer_image)
            print(f"Image footer {len(decoded_footer)} bytes.")
        except Exception:
            print("ERROR: receiptFooterImage is not base64 encoded string")
    
    # Handle receipt header/footer text lines
    if receipt_header_text_lines is not None and len(receipt_header_text_lines) > 0:
        print("\nHEADER:")
        for line in receipt_header_text_lines:
            print(f"- {line}")
    
    if receipt_footer_text_lines is not None and len(receipt_footer_text_lines) > 0:
        print("\nFOOTER:")
        for line in receipt_footer_text_lines:
            print(f"- {line}")
        print()  # Add extra newline after footer
    
    # Validate GTIN for all items
    for item in invoice_data.invoiceRequest.items:
        if not item.gtin or item.gtin.strip() == "":
            error_response = ErrorResponse(
                details=None,
                message=f"gtin za artikal {item.name} nije popunjen",
                statusCode=-1
            )
            return JSONResponse(
                status_code=200,  # Return HTTP 200 but with error in response body
                content=error_response.model_dump()
            )

    for payment in invoice_data.invoiceRequest.payment:
        print("paymentType:", payment.paymentType, " ; paymentAmount:", payment.amount)

    if type == "Copy":
        if (not referentDocumentNumber) or (not referentDocumentDT):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Copy ne sadrzi referentDocumentNumber and DT",
            )
        else:
            print(
                "referentni fiskalni dokument:",
                referentDocumentNumber,
                referentDocumentDT,
            )

    if transactionType == "Refund":
        print(
            "refund referentni fiskalni dokument broj:",
            referentDocumentNumber,
            "datum:",
            referentDocumentDT,
        )

    totalValue = 0
    cStavke = ""

    for item in invoice_data.invoiceRequest.items:
        totalValue += item.totalAmount
        nDiscount = item.discount or 0.0
        nDiscountAmount = item.discountAmount or 0.00
        label = item.labels[0]
        print(f"gtin: {item.gtin}")
        cStavka = (
            "%s quantity: %.2f unitPrice: %.2f discount: %.2f discountAmount: %.2f  totalAmount: %.2f label: %s gtin: %s\r\n"
            % (
                item.name,
                item.quantity,
                item.unitPrice,
                nDiscount,
                nDiscountAmount,
                item.totalAmount,
                label,
                item.gtin,
            )
        )
        cStavke += cStavka
        print(cStavka)
    # print(cStavke)

    print("totalValue:", totalValue)

    # payments_length = len(invoice_data.invoiceRequest.payment)

    cInvoiceNumber = str(randint(1, 999)).zfill(3)

    cFullInvoiceNumber = "AX4F7Y5L-BX4F7Y5L-" + cInvoiceNumber

    cDTNow = datetime.datetime.now().isoformat()
    # >>> '2024-08-01T14:38:32.499588'

    if check_api_key(req):

        cRacun = None
        if type == "Normal":
            cRacun = "FISKALNI RAČUN"
        else:
            cRacun = "KOPIJA FISKALNOG RAČUNA"
        
        # Handle receipt image generation for print=false case
        invoice_image_pdf_base64 = None
        invoice_image_png_base64 = None
        
        if (print_receipt is False and render_receipt_image is True and 
            receipt_layout and receipt_image_format):
            
            if receipt_image_format == "Pdf" and receipt_layout == "Invoice":
                # Load test invoice PDF and encode as base64
                try:
                    pdf_path = os.path.join(os.path.dirname(__file__), "..", "input", "test_invoice.pdf")
                    with open(pdf_path, "rb") as f:
                        pdf_data = f.read()
                        invoice_image_pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
                        print(f"Generated PDF base64 image, length: {len(invoice_image_pdf_base64)}")
                except Exception as e:
                    print(f"Error loading test invoice PDF: {e}")
                    # Fallback to dummy base64
                    invoice_image_pdf_base64 = "JVBERi0xLjcKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0ZURlY29kZT4+CnN0cmVhbQp4nL1T"
            
            elif receipt_image_format == "Png":
                # Generate dummy PNG base64 for slip format
                invoice_image_png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                print(f"Generated PNG base64 image for receipt format")

        response = InvoiceResponse(
            address=BUSINESS_ADDRESS,
            businessName=BUSINESS_NAME,
            district="ZEDO",
            encryptedInternalData="Vvwq4nVn/wIQFAKE",
            invoiceCounter="100/" + cInvoiceNumber + "ZE",
            invoiceCounterExtension="ZE",
            invoiceImageHtml=None,
            invoiceImagePdfBase64=invoice_image_pdf_base64,
            invoiceImagePngBase64=invoice_image_png_base64,
            invoiceNumber=cFullInvoiceNumber,
            journal="=========== "
            + cRacun
            + " ===========\r\n             4402692070009            \r\n       Sigma-com doo Zenica      \r\n      7. Muslimanske Brigade 77      \r\n              Zenica              \r\nKasir:                        Radnik 1\r\nESIR BROJ:                      13/2.0\r\n----------- PROMET PRODAJA -----------\r\nАrtikli                               \r\n======================================\r\nNaziv  Cijena        Kol.         Ukupno\r\n "
            + cStavke
            + "--------------------------------------\r\n"
            + "Ukupan iznos:                   "
            + "%.2f" % (totalValue)
            + "\r\nGotovina:                     "
            + "%.2f" % (totalValue)
            + "\r\n======================================\r\nOznaka    Naziv    Stopa    Porez\r\nF          ECAL      11%          9,91\r\n--------------------------------------\r\nUkupan iznos poreza:              9,91\r\n======================================\r\n"
            + "PFR brijeme:      12.03.2024. 07:47:09\r\nOFS br. rač:      "
            + cFullInvoiceNumber
            + "\r\nBrojač računa:               100/138ZE\r\n======================================"
            + "\r\n======== KRAJ "
            + cRacun
            + "=======\r\n",
            locationName="Sigma-com doo Zenica poslovnica Sarajevo",
            messages="Uspješno",
            mrc="01-0001-WPYB002248200772",
            requestedBy="RX4F7Y5L",
            sdcDateTime=cDTNow,  # "2024-09-15T07:47:09.548+01:00",
            signature="Mw+IB0vgnaMjYrwA7m7zhtRseRIZFAKE",
            signedBy="RX4F7Y5L",
            taxGroupRevision=2,
            taxItems=[
                TaxItems(
                    amount=9.9099,
                    categoryName="ECAL",
                    categoryType=0,
                    label="F",
                    rate=11,
                )
            ],
            tin="4402692070009",
            totalAmount=totalValue,
            totalCounter=138,
            transactionTypeCounter=100,
            verificationQRCode="R0lGODlhhAGEAfFAKE",
            verificationUrl="https://sandbox.suf.poreskaupravars.org/v/?vl=A1JYNEY3WTVMUlg0FAKE=",
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
    print("search from:", invoiceSearchData.fromDate, " to: ", invoiceSearchData.toDate)

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


@app.get("/api/invoices/{invoiceNumber}")
async def get_invoice(
    invoiceNumber: str,
    imageFormat: str | None = None,
    includeHeaderAndFooter: bool | None = None,
    receiptLayout: str | None = None,
):
    print("Invoice number:", invoiceNumber)
    print(
        "PARAMS:  imageFormat:",
        imageFormat,
        " includeHeaderAndFooter:",
        includeHeaderAndFooter,
        " receiptLayout:",
        receiptLayout,
    )

    lPDV17 = True if invoiceNumber[0:1] != "0" else False

    if invoiceNumber.strip() == "ERROR":
        return {"error": 1}

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
                    "gtin": "12345678",
                    "labels": [CIRILICA_E] if SEND_CIRILICA else ["E"],
                    "name": "Artikl 1",
                    "plu": None,
                    "quantity": 2,
                    "totalAmount": 100,
                    "unitPrice": 50,
                }
            ],
            "options": {"omitQRCodeGen": 1, "omitTextualRepresentation": None},
            "payment": [{"amount": 100, "paymentType": "Cash"}],
            "referentDocumentDT": None,
            "referentDocumentNumber": None,
            "transactionType": "Sale",
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
            "messages": "Uspješno",  # "Успешно",
            "mrc": "01-0001-WPYB002248200772",
            "requestedBy": "RX4F7Y5L",
            "sdcDateTime": "2024-03-12T07:47:09.548+01:00",
            "signature": None,
            "signedBy": "RX4F7Y5L",
            "taxGroupRevision": 2,
            "taxItems": [
                (
                    {
                        "amount": 8.52,
                        "categoryName": "ECAL",
                        "categoryType": 0,
                        "label": "E",
                        "rate": 17,
                    }
                    if lPDV17
                    else {
                        "amount": 0.0,
                        "categoryName": "NULA",
                        "categoryType": 0,
                        "label": "K",
                        "rate": 0,
                    }
                )
            ],
            "tin": "4402692070009",
            "totalAmount": 100,
            "totalCounter": 138,
            "transactionTypeCounter": 100,
            "verificationQRCode": "R0lGODlhhAGEAfAAAFAKE",
            "verificationUrl": "https://sandbox.suf.poreskaupravars.org/v/?vl=A1JYNEY3WTVMUlg0RjdZNUyKAAAAZAAAAEBCDwAAAAAAAAABjjFqO+wAAABW/CridWf/AhDKQHvQyoCT3HBCLwZvH/v4JxyQ/63YKX/GXViHprxs3ZGe8VR7lXDR6UKrQCyuZd4rMOpo3JYisQyV0A9AW5QBCzUCLzYkpiyint98f7Vu4FJcFijOMrWekwxh1rjUsLp2WaL0yY+gSWebEEabv4Tq16272j1LukALa2Lo5C3qRyU8HFzSwYky4F7zsVQnqJRoSb7MenE3NnH+O45iLfiA1zOPruW+KrwVwQGi1iUV4ejSXmAsrML+27UMALiGKd11XNaD/XEEyzbLOCYSbEPnepGUSQ6Kh2Zr+J++fNvxm9gfd3P4qqm2au7fu1Cs7W2ow86QQBjRMw+IB0vgnaMjYrwA7m7zhtRseRIZiGGB6pdIQM7enPhPZUfIeKsSTjQ3CCdeSMGpWhDMGileZcTZkkkMVFML8VnFM+l2dhPSoIeJ6llY5RmcfbN5ESXMEYP8LJ58ONeychjKCi/zVhMx0+ox5bWcWsRwBMyIlfFTFAKE=",
        },
        "issueCopy": False,
        "print": True,
        "receiptImageBase64": "iVBORw0KGgoAAkkZu/FAKE",
        "receiptImageFormat": "Png",
        "receiptLayout": "Slip",
        "renderReceiptImage": False,
        "skipEftPos": False,
        "skipEftPosPrint": False,
    }


def main():
    """Main entry point for the OFS mockup server."""
    parser = argparse.ArgumentParser(description="OFS Mockup Server")
    parser.add_argument(
        "--available",
        action="store_true",
        help="Start with service available (default: unavailable)",
    )
    parser.add_argument("--port", type=int, default=8200, help="Port to bind")
    parser.add_argument(
        "--pin",
        default="4321",
        help="Set PIN for device authentication (default: 4321)",
    )
    args, _ = parser.parse_known_args()

    # Initialize app state from CLI args
    app.state.current_api_attention = 200 if args.available else 404
    app.state.pin = args.pin

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
