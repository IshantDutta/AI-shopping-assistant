# ShopMate AI 🛍️

A dark-themed full-stack shopping assistant built with React, FastAPI, SQLite and Google's Gemini API.

## Features
- Natural-language shopping queries
- Local SQLite product catalog
- Budget extraction from phrases such as "headphones under ₹5,000"
- Category and price filters
- Transparent product ranking
- Gemini-powered shopping explanations (optional API key)
- Optional live Google Shopping retrieval through SerpApi
- Product comparison
- Browser-local wishlist
- Local SVG product artwork and image fallbacks
- FastAPI Swagger documentation

## Technology
- Frontend: React 18, Vite, CSS, Lucide
- Backend: Python, FastAPI, SQLAlchemy, Pydantic
- Database: SQLite
- AI: Google Gemini via the official `google-genai` SDK
- Live product retrieval: SerpApi Google Shopping (optional)

## Requirements
- Python 3.10+
- Node.js 18+
- Gemini API key from https://aistudio.google.com/api-keys
- Optional SerpApi key for live shopping results

## Setup on Windows PowerShell

Open a terminal at the project root.

### 1. Backend environment
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env`:
```env
GEMINI_API_KEY=your_new_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
SERPAPI_API_KEY=
SERPAPI_COUNTRY=in
SERPAPI_LANGUAGE=en
SERPAPI_LOCATION=
```

Never commit `.env`, share screenshots containing keys, or put keys in frontend code.

### 2. Seed or update the catalog
Keep your existing `backend/shopping.db` if you already have one. From the `backend` directory:
```powershell
python seed.py
```
This adds missing demo products and updates image paths for matching products. It does not delete existing rows.

### 3. Start the backend
From the `backend` directory:
```powershell
python -m uvicorn main:app --reload
```
- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

### 4. Start the frontend
Open a second terminal at the project root:
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

Optional `frontend/.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```
Restart Vite after changing frontend environment variables.

## API endpoints
- `GET /`
- `GET /health`
- `GET /products/`
- `GET /products/?query=headphones&max_price=5000`
- `GET /products/{product_id}`
- `GET /assistant/status`
- `POST /assistant/chat`
- `POST /assistant/compare`

Example chat body:
```json
{
  "message": "Find wireless headphones under ₹5,000",
  "max_price": null,
  "category": null,
  "use_live_search": true
}
```
The backend extracts the ₹5,000 budget from the message if `max_price` is not separately supplied.

## Product images
The starter catalog uses locally bundled SVG illustrations by category. These are illustrative previews, not manufacturer photographs. Live SerpApi results may include merchant thumbnails.

## Limitations
This is a portfolio MVP, not a production marketplace:
- Sample catalog products and prices are demo records, not a verified live price feed.
- Live search requires a SerpApi key and is subject to provider limits.
- Gemini explanations require a valid Gemini key, model access and available quota. Catalog search works without Gemini.
- Wishlist is stored in browser local storage.
- Comparison currently supports products in the local catalog.
- User accounts, persistent price history, review ingestion and price alerts are future features.

## GitHub
```powershell
git add .
git commit -m "feat: migrate shopping assistant to Gemini"
```
