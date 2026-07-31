# Nandish Patel: Shopping Cart API

## Run

We run the commands as follows:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 -m unittest -v
python3 app.py
```

After running all the above commands,
the API will run at `http://127.0.0.1:8080`.

## API

### Add

```http
POST /cart/items
Content-Type: application/json
```

```json
{
  "productId": "keyboard-1",
  "quantity": 2
}
```

```curl -i -X POST http://127.0.0.1:8080/cart/items \
  -H 'Content-Type: application/json' \
  -d '{"productId":"keyboard-1","quantity":2}```

First one returns:
HTTP/1.1 201 CREATED
Server: Werkzeug/3.1.8 Python/3.13.5
Date: Tue, 28 Jul 2026 15:59:09 GMT
Content-Type: application/json
Content-Length: 40
Connection: close

Second / Duplicate returns:
HTTP/1.1 409 CONFLICT
Server: Werkzeug/3.1.8 Python/3.13.5
Date: Tue, 28 Jul 2026 15:59:56 GMT
Content-Type: application/json
Content-Length: 43
Connection: close

### List

```http
GET /cart/items
```

```curl -s http://127.0.0.1:8080/cart/items | python3 -m json.tool```

will show us:
{
    "items": [
        {
            "productId": "keyboard-1",
            "quantity": 2
        }
    ]
}

### Remove

```http
DELETE /cart/items/{productId}
```

When deleting existing item from our shopping cart:

```curl -i -X DELETE http://127.0.0.1:8080/cart/items/keyboard-1```

HTTP/1.1 204 NO CONTENT
Server: Werkzeug/3.1.8 Python/3.13.5
Date: Tue, 28 Jul 2026 16:01:32 GMT
Content-Type: text/html; charset=utf-8
Connection: close

When deleting non-existing item from our shopping cart:

```curl -i -X DELETE http://127.0.0.1:8080/cart/items/keyboard-2```

HTTP/1.1 404 NOT FOUND
Server: Werkzeug/3.1.8 Python/3.13.5
Date: Tue, 28 Jul 2026 16:01:43 GMT
Content-Type: application/json
Content-Length: 27
Connection: close

