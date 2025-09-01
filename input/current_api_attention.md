# Current api attention status

Current implementation of server maintains readiness of server with `gsc` variable. I think we don't need it.
Wee need `current_api_attention` which determines reponse from `/api/attention` call.

return `current_api_attention`:
- 404 (default value when server starts)
- 200

## API POST or GET /mock/lock

Set `current_api_attention` to 404 



## API POST or GET /mock/unlock

Set `current_api_attention` to 200

## API GET /mock/current_api_attention

=> `current_api_attention`


## API /api/pin

If `/api/pin` is successfull, `current_api_attention` is set to `200`,
otherwise 404.

## Notes

-  `/mock/*` api calls DON'T need api_key



