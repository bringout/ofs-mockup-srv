Current implementation of server maintains readiness of server with `gsc` variable. I think we don't need it.
Wee need `current_api_attention` which determines reponse from `/api/attention` call.

return `current_api_attention`:
- 404 (default value when server starts)
- 200

# API /mock/lock

Set `current_api_attention` to 404  

# API /mock/unlock

Set `current_api_attention` to 200

# API /api/pin

If `/api/pin` is successfull, `current_api_attention` is set to `200`,
otherwise 404.



