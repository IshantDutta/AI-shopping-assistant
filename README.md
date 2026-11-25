# ShopMate AI

ShopMate AI is a full-stack shopping assistant for users in India. It combines a local product catalogue, optional live Google Shopping discovery through SerpApi, and Gemini-generated product-grounded shopping advice.

## Features

- Product catalogue search with category and budget filters.
- AI-assisted shopping recommendations using Gemini.
- Optional live shopping results with direct merchant offer links.
- Side-by-side comparison for 2–4 products.
- Availability-aware comparison: out-of-stock and unconfirmed items cannot win.
- Persistent browser wishlist using local storage.
- Responsive React interface.
- FastAPI API documentation at `/docs`.

## Technology

- Frontend: React 18, Vite, JavaScript, Lucide React.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy.
- Database: SQLite.
- AI: Google Gemini API (`google-genai`).
- Live shopping: SerpApi Google Shopping and Google Product engines.

## Requirements

- Python 3.10+ (Python 3.11 or 3.12 recommended).
- Node.js 20+ and npm.
- Gemini API key (optional; fallback recommendations remain available).
- SerpApi API key (optional; local catalogue remains available).

## Local setup

### 1. Backend

Open a terminal in the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and add your own API keys. Never commit `.env`.

The project includes a SQLite database with sample catalogue records. To create or refresh the sample catalogue from `data/products.json`:

```powershell
python seed.py
```

Start the API:

```powershell
python -m uvicorn main:app --reload
```

Backend: http://127.0.0.1:8000  
API docs: http://127.0.0.1:8000/docs  
Health check: http://127.0.0.1:8000/health

### 2. Frontend

Open a second terminal in the project root:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Frontend: http://localhost:5173

For a deployed frontend, set `VITE_API_BASE_URL` to the public backend URL in the frontend hosting environment. Set backend `CORS_ORIGINS` to the exact frontend origin(s), comma-separated.

## Tests

From the project root:

```powershell
cd backend
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The tests cover health, catalogue access, product comparison, and availability rules. Live Gemini and SerpApi calls are not required for the automated test suite.

## Environment variables

See `backend/.env.example` and `frontend/.env.example`.

- `GEMINI_API_KEY`: Gemini key; optional.
- `GEMINI_MODEL`: Gemini model name enabled for your account.
- `SERPAPI_API_KEY`: SerpApi key; optional.
- `SERPAPI_COUNTRY`, `SERPAPI_LANGUAGE`, `SERPAPI_LOCATION`: shopping search locale.
- `CORS_ORIGINS`: comma-separated allowed frontend origins.
- `VITE_API_BASE_URL`: frontend's backend API base URL.

## Deployment notes

1. Deploy the backend with the `backend` directory as the application root and start command:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. Configure backend environment variables in the hosting provider. Do not upload `.env`.
3. For a persistent production deployment, use a persistent disk for SQLite or migrate to a managed database.
4. Deploy the `frontend` directory as a static Vite site. Build command: `npm run build`; output directory: `dist`.
5. Set `VITE_API_BASE_URL` to the deployed backend URL before building.
6. Set backend `CORS_ORIGINS` to the deployed frontend origin.

The included SQLite database is suitable for a demo. A host with ephemeral filesystems may reset it on redeploy; use persistent storage or a managed database for reliable production persistence.

## Important limitations

- Shopping prices, seller links and stock data are provider snapshots and may change. Confirm final price, delivery, return policy and stock with the merchant before purchasing.
- Merchant trust is not independently certified by this application.
- Gemini and SerpApi availability, quotas and model access depend on the user's provider accounts.
- This application does not process payments or place orders.

## Project structure

```text
ShopMate-AI/
├── backend/
│   ├── routers/
│   ├── services/
│   ├── tests/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── requirements.txt
├── data/
│   └── products.json
├── frontend/
│   ├── public/
│   └── src/
├── .gitignore
└── README.md
```
