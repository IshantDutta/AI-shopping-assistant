# ShopMate AI API quick reference

## GET /health
Returns backend health status.

## GET /products/
Parameters: `query`, `category`, `max_price`, `min_rating`.

## GET /assistant/status
Returns whether Gemini and SerpApi keys are configured and the selected Gemini model. It never returns the keys.

## POST /assistant/chat
```json
{
  "message": "Find wireless headphones under ₹5,000",
  "max_price": null,
  "category": null,
  "use_live_search": true
}
```
Returns `message`, `products`, `sources` and `applied_filters`.

## POST /assistant/compare
```json
{"product_ids": [1, 2]}
```
Returns catalog products in the order of the submitted IDs.
