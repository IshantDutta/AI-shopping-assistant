# ShopMate AI Architecture

```text
React + Vite frontend
  ├── Product discovery and filters
  ├── ChatPanel
  ├── Product cards and local SVG artwork
  ├── Wishlist (localStorage)
  └── Product comparison modal
           |
           v
FastAPI backend
  ├── GET /products
  ├── POST /assistant/chat
  ├── POST /assistant/compare
  └── GET /assistant/status
           |
           ├── SQLAlchemy -> SQLite product catalog
           ├── Gemini API -> grounded shopping explanation (optional)
           └── SerpApi -> Google Shopping results (optional)
```

## Request flow
1. The user searches the catalog or sends a natural-language shopping request.
2. The backend extracts a budget from the message if no explicit budget was provided.
3. The local catalog is searched and filtered.
4. If SerpApi is configured, live shopping results are requested.
5. Catalog and live records are normalized and ranked.
6. Gemini explains available results when configured; otherwise deterministic fallback advice is returned.
7. The frontend displays product cards, source labels and the explanation.

## Trust boundaries
- API keys are read only from `backend/.env`.
- Never send API keys to browser code.
- External prices, images and availability are third-party data and may change.
- The assistant must not invent specifications, ratings, warranty terms or merchant policies.
- Demo catalog data must not be represented as verified current market pricing.
