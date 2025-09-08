# ERROR messages

When error message is to be returned this is response format:

example:
```
{ 
  "details":null,
  "message":"Invalid total payment amounts",
  "statusCode":-1
}
```

## GTIN not exists

Let us implement error when some of invoiceRequest/items doesn't contains `gtin` code, or `gtin` 

Response should be like this

```
{ "details":null,
  "message":"gtin za artikal Test product nije popunjen",
  "statusCode":-1
}
```