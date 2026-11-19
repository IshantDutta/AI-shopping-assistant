# API quick reference

## GET /products/
Query parameters: `query`, `category`, `max_price`, `min_rating`.

## GET /products/{product_id}
Returns one catalog product or 404.

## POST /assistant/chat
Body:
```json
{
  "message": "Need headphones for travel",
  "max_price": 5000,
  "category": "Headphones",
  "use_live_search": true
}
```
Response includes `message`, `products`, and `sources`.

## POST /assistant/compare
Body:
```json
{"product_ids": [1, 2]}
```
Returns the catalog records for the supplied IDs.
