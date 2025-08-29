#!/usr/bin/env bash

# https://stackoverflow.com/questions/70351360/keep-getting-307-temporary-redirect-before-returning-status-200-hosted-on-fast

curl -H 'Content-Type: application/json' \
   -d '{ "id": "1", "name": "RACUN0001" }' \
   -X POST \
   http://localhost:8200/invoice \
   | python -m json.tool

