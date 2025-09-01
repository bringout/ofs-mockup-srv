import datetime as dt
from fastapi.testclient import TestClient

from ofs_mockup_srv.main import app, API_KEY, PIN


def auth_headers(token: str | None = None) -> dict[str, str]:
    t = token if token is not None else API_KEY
    return {"Authorization": f"Bearer {t}"}


def test_root_healthcheck():
    with TestClient(app) as client:
        r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("msg") == "I am OFS mock server"


def test_attention_requires_valid_api_key():
    with TestClient(app) as client:
        r_ok = client.get("/api/attention", headers=auth_headers())
        r_bad = client.get("/api/attention", headers=auth_headers("bad-token"))
    # default current_api_attention is 200 (service available)
    assert r_ok.status_code == 200
    assert r_bad.status_code == 401


def test_status_structure_and_compatibility():
    with TestClient(app) as client:
        r = client.get("/api/status", headers=auth_headers())
    assert r.status_code == 200
    data = r.json()
    # GSC field kept for backward compatibility
    assert "gsc" in data and isinstance(data["gsc"], list) and len(data["gsc"]) >= 1
    assert data["deviceSerialNumber"]
    assert data["protocolVersion"] == "2.0"


def test_pin_endpoint_plain_text():
    with TestClient(app) as client:
        r_ok = client.post(
            "/api/pin",
            headers={**auth_headers(), "Content-Type": "text/plain"},
            content=PIN,
        )
        r_short = client.post(
            "/api/pin",
            headers={**auth_headers(), "Content-Type": "text/plain"},
            content="12",
        )
        r_wrong = client.post(
            "/api/pin",
            headers={**auth_headers(), "Content-Type": "text/plain"},
            content="9999",
        )
    assert r_ok.status_code == 200 and r_ok.text == "0100"
    assert r_short.status_code == 200 and r_short.text == "2800"
    assert r_wrong.status_code == 200 and r_wrong.text == "2400"


def test_create_invoice_and_sum_total_amount():
    payload = {
        "invoiceRequest": {
            "invoiceType": "Normal",
            "transactionType": "Sale",
            "payment": [{"amount": 100.0, "paymentType": "Cash"}],
            "items": [
                {
                    "name": "Test Product",
                    "labels": ["F"],
                    "totalAmount": 60.0,
                    "unitPrice": 30.0,
                    "quantity": 2.0,
                },
                {
                    "name": "Another",
                    "labels": ["F"],
                    "totalAmount": 40.0,
                    "unitPrice": 20.0,
                    "quantity": 2.0,
                },
            ],
            "cashier": "Tester",
        }
    }
    with TestClient(app) as client:
        r = client.post(
            "/api/invoices",
            headers={**auth_headers(), "Content-Type": "application/json"},
            json=payload,
        )
    assert r.status_code == 200
    data = r.json()
    assert data["totalAmount"] == 100.0
    assert data["invoiceNumber"].startswith("AX4F7Y5L-BX4F7Y5L-")


def test_invoice_search_returns_csv_like_text():
    search_body = {
        "fromDate": (dt.date.today() - dt.timedelta(days=30)).isoformat(),
        "toDate": dt.date.today().isoformat(),
        "amountFrom": 0,
        "amountTo": 100000,
        "invoiceTypes": ["Normal"],
        "transactionTypes": ["Sale"],
        "paymentTypes": ["Cash"],
    }
    with TestClient(app) as client:
        r = client.post(
            "/api/invoices/search",
            headers={**auth_headers(), "Content-Type": "application/json"},
            json=search_body,
        )
    assert r.status_code == 200
    assert "RX4F7Y5L" in r.text


def test_get_invoice_success_and_error():
    with TestClient(app) as client:
        r_ok = client.get("/api/invoices/RX4F7Y5L-RX4F7Y5L-138")
        r_err = client.get("/api/invoices/ERROR")
    assert r_ok.status_code == 200
    assert r_ok.json().get("invoiceResponse", {}).get("invoiceNumber") == "RX4F7Y5L-RX4F7Y5L-138"
    assert r_err.status_code == 200 and r_err.json() == {"error": 1}


def test_pin_cycle_via_mock_lock_and_attention():
    with TestClient(app) as client:
        # Force PIN-required state
        lock = client.post("/mock/lock", headers=auth_headers())
        assert lock.status_code == 200 and lock.json()["current_api_attention"] == 404

        # 1) attention should signal service unavailable
        att = client.get("/api/attention", headers=auth_headers())
        assert att.status_code == 404

        # 2) client asks for PIN entry UI (implicit)
        # 3) user submits PIN
        pin_res = client.post(
            "/api/pin",
            headers={**auth_headers(), "Content-Type": "text/plain"},
            content=PIN,
        )
        assert pin_res.status_code == 200 and pin_res.text == "0100"

        # 4) after success
        # 5) attention shows service available
        att2 = client.get("/api/attention", headers=auth_headers())
        assert att2.status_code == 200


def test_wrong_pin_does_not_unlock():
    with TestClient(app) as client:
        # Lock to require PIN
        lock = client.post("/mock/lock", headers=auth_headers())
        assert lock.status_code == 200 and lock.json()["current_api_attention"] == 404

        # Send wrong (but 4-digit) PIN
        r_wrong = client.post(
            "/api/pin",
            headers={**auth_headers(), "Content-Type": "text/plain"},
            content="9999",
        )
        assert r_wrong.status_code == 200 and r_wrong.text == "2400"

        # Attention remains unavailable
        att = client.get("/api/attention", headers=auth_headers())
        assert att.status_code == 404

        # Cleanup: enter correct PIN to restore normal state for other tests
        r_ok = client.post(
            "/api/pin",
            headers={**auth_headers(), "Content-Type": "text/plain"},
            content=PIN,
        )
        assert r_ok.status_code == 200 and r_ok.text == "0100"


def test_wrong_password_4_times_lock():
    with TestClient(app) as client:
        # Ensure we start from a PIN-required state
        lock = client.post("/mock/lock", headers=auth_headers())
        assert lock.status_code == 200 and lock.json()["current_api_attention"] == 404

        # 1st wrong pin
        r1 = client.post(
            "/api/pin",
            headers={**auth_headers(), "Content-Type": "text/plain"},
            content="0000",
        )
        assert r1.status_code == 200 and r1.text == "2400"
        assert client.get("/api/attention", headers=auth_headers()).status_code == 404

        # 2nd wrong pin
        r2 = client.post(
            "/api/pin",
            headers={**auth_headers(), "Content-Type": "text/plain"},
            content="1111",
        )
        assert r2.status_code == 200 and r2.text == "2400"
        assert client.get("/api/attention", headers=auth_headers()).status_code == 404

        # 3rd wrong pin -> lock to 1300
        r3 = client.post(
            "/api/pin",
            headers={**auth_headers(), "Content-Type": "text/plain"},
            content="2222",
        )
        assert r3.status_code == 200 and r3.text == "1300"
        assert client.get("/api/attention", headers=auth_headers()).status_code == 404

        # 4th attempt should still report error and not accept PIN
        r4 = client.post(
            "/api/pin",
            headers={**auth_headers(), "Content-Type": "text/plain"},
            content="3333",
        )
        assert r4.status_code == 200 and r4.text == "1300"
        assert client.get("/api/attention", headers=auth_headers()).status_code == 404
