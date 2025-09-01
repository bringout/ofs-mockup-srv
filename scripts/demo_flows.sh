#!/usr/bin/env bash
set -euo pipefail

# Demo script for PIN cycle, lockout, and invoice flows
# Usage:
#   bash scripts/demo_flows.sh [all|pin|invoice]

BASE_URL="${BASE_URL:-http://localhost:8200}"
API_KEY="${API_KEY:-api_key_0123456789abcdef0123456789abcdef}"
PIN_VALUE="${PIN_VALUE:-0A10015}"
MODE="${1:-all}"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1" >&2; exit 1; }; }
need curl
need jq

hdr_auth=( -H "Authorization: Bearer ${API_KEY}" )

pin_flow() {
  echo "== PIN unlock flow =="
  echo "Locking (service unavailable) ..."
  curl -sS -X POST "${BASE_URL}/mock/lock" "${hdr_auth[@]}" | jq .

  echo "Attention (expect HTTP 404 - unavailable) ..."
  curl -sS "${BASE_URL}/api/attention" "${hdr_auth[@]}"; echo

  echo "Entering correct PIN ..."
  curl -sS -X POST "${BASE_URL}/api/pin" \
    "${hdr_auth[@]}" -H "Content-Type: text/plain" \
    --data "${PIN_VALUE}"; echo

  echo "Attention (expect HTTP 200 - available) ..."
  curl -sS "${BASE_URL}/api/attention" "${hdr_auth[@]}"; echo

  echo "== Lockout (3 wrong attempts -> service unavailable) =="
  curl -sS -X POST "${BASE_URL}/mock/lock" "${hdr_auth[@]}" >/dev/null
  for P in 0000 1111 2222; do
    echo "Sending wrong PIN: $P ..."
    curl -sS -X POST "${BASE_URL}/api/pin" \
      "${hdr_auth[@]}" -H "Content-Type: text/plain" \
      --data "$P"; echo
  done
  echo "Attention (expect HTTP 404 - locked out) ..."
  curl -sS "${BASE_URL}/api/attention" "${hdr_auth[@]}"; echo

  echo "Attempt correct PIN after lockout (still locked) ..."
  curl -sS -X POST "${BASE_URL}/api/pin" \
    "${hdr_auth[@]}" -H "Content-Type: text/plain" \
    --data "${PIN_VALUE}"; echo
}

invoice_flow() {
  echo "== Invoice flow =="
  read -r -d '' payload <<'JSON'
{
  "invoiceRequest": {
    "invoiceType": "Normal",
    "transactionType": "Sale",
    "payment": [{"amount": 100.0, "paymentType": "Cash"}],
    "items": [
      {"name": "Test Product", "labels": ["F"], "totalAmount": 60.0, "unitPrice": 30.0, "quantity": 2.0},
      {"name": "Another", "labels": ["F"], "totalAmount": 40.0, "unitPrice": 20.0, "quantity": 2.0}
    ],
    "cashier": "Tester"
  }
}
JSON

  echo "Creating invoice ..."
  resp=$(curl -sS -X POST "${BASE_URL}/api/invoices" \
    "${hdr_auth[@]}" -H "Content-Type: application/json" \
    -d "${payload}")
  echo "$resp" | jq .
  INV=$(echo "$resp" | jq -r .invoiceNumber)
  echo "Invoice Number: $INV"

  echo "Fetching invoice details ..."
  curl -sS "${BASE_URL}/api/invoices/${INV}?receiptLayout=Slip&imageFormat=Png&includeHeaderAndFooter=true" \
    "${hdr_auth[@]}" | jq .

  echo "Searching invoices ..."
  FROM=$(date -I -d "-30 days" 2>/dev/null || date -v-30d +%Y-%m-%d)
  TO=$(date -I 2>/dev/null || date +%Y-%m-%d)
  curl -sS -X POST "${BASE_URL}/api/invoices/search" \
    "${hdr_auth[@]}" -H "Content-Type: application/json" \
    -d "{\n\"fromDate\": \"$FROM\",\n\"toDate\": \"$TO\",\n\"amountFrom\": 0,\n\"amountTo\": 100000,\n\"invoiceTypes\": [\"Normal\"],\n\"transactionTypes\": [\"Sale\"],\n\"paymentTypes\": [\"Cash\"]\n}"

  echo
  echo "Error example (reserved value) ..."
  curl -sS "${BASE_URL}/api/invoices/ERROR" "${hdr_auth[@]}"; echo
}

case "$MODE" in
  pin) pin_flow ;;
  invoice) invoice_flow ;;
  all) pin_flow; invoice_flow ;;
  *) echo "Unknown mode: $MODE (use: all|pin|invoice)" >&2; exit 2 ;;
esac

