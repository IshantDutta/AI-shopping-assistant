# ShopMate AI Architecture

```text
React UI (Vite)
  |-- catalog search / filters
  |-- assistant chat
  |-- wishlist (browser localStorage)
  |-- comparison modal
  |
  v
FastAPI REST API
  |-- /products
  |-- /assistant/chat
  |-- /assistant/compare
  |
  +--> SQLAlchemy --> SQLite catalog
  |
  +--> SerpApi Google Shopping (optional live provider)
  |
  +--> OpenAI Responses API (optional explanation provider)
```

## Hybrid retrieval
1. Query the local SQLite catalog.
2. If a SerpApi key is configured and live search is enabled, query Google Shopping.
3. Normalize results and label their origin (`catalog` or `live`).
4. Apply a simple transparent rating/value ranking.
5. If OpenAI is configured, generate an explanation grounded in the returned products; otherwise use a deterministic fallback.

## Trust boundaries
Provider responses are external data. Do not treat product snippets as verified facts. Never expose API keys in browser code. Confirm current price and terms at the merchant.
