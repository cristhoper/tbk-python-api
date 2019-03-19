# tbk-python-api

## MicroService for tbk POS.

Configuration:
```
$ pip install -r requirements.txt
```

Run
```
$ python app.py
```

## REST API

### To send a request, use:

POST `<ip>:4001/payment`

Content-Type: application/json

Body:
```
{
    "transaction_id": <internal id transaction as integer>,
    "amount": <value as integer>
}
```

### To check for a request transaction:

GET `<ip>:4001/check/<transaction_id>`

Return: Based on content property of TransactionData class.

See example in [@sale_init](https://github.com/cristhoper/tbk-python-api/blob/master/tbkpos.py#L196)
