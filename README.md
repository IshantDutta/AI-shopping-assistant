# 🛍️ ShopMate AI — AI-Powered Shopping Assistant

**ShopMate AI** is a full-stack AI-powered shopping assistant designed to simplify online shopping. It helps users discover products, explore shopping options, compare alternatives, and make more informed purchasing decisions through an intelligent conversational interface.

🔗 **Live Demo:** https://ai-shopping-assistant-sable.vercel.app/  
💻 **GitHub Repository:** https://github.com/IshantDutta/AI-shopping-assistant

---

## ✨ Features

- **AI Shopping Assistant:** Describe what you're looking for in natural language and receive AI-powered shopping guidance.
- **Live Product Search:** Discover products through Google Shopping search integration.
- **Product Discovery:** Browse products from a curated local catalog.
- **Smart Product Comparison:** Compare multiple products based on available details and value.
- **Availability-Aware Recommendations:** Account for product availability when evaluating comparison results.
- **Wishlist:** Save products and revisit them later.
- **Direct Merchant Links:** Navigate to merchant pages to explore purchasing options.
- **Modern User Interface:** Responsive, dark-themed interface built for a clean shopping experience.

## 🧰 Tech Stack

| Category | Technologies |
|---|---|
| Frontend | React.js, Vite, CSS |
| Backend | Python, FastAPI |
| Database | SQLite, SQLAlchemy |
| AI Integration | Google Gemini API |
| Product Search | SerpApi / Google Shopping |
| API Communication | REST APIs, HTTPX |
| Deployment | Vercel, Render |
| Version Control | Git, GitHub |

## 🏗️ Project Architecture

```text
ShopMate-AI/
│
├── backend/
│   ├── routers/
│   │   ├── assistant.py
│   │   └── products.py
│   │
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── comparison_service.py
│   │   ├── live_search_service.py
│   │   ├── product_service.py
│   │   └── recommendation_service.py
│   │
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── seed.py
│   └── requirements.txt
│
├── data/
│   └── products.json
│
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── services/
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── styles.css
    │
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/IshantDutta/AI-shopping-assistant.git
cd AI-shopping-assistant
```

### 2. Set up the backend

```bash
cd backend

python -m venv venv
```

Activate the virtual environment:

**Windows:**
```powershell
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file inside the `backend` directory:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_configured_gemini_model

SERPAPI_API_KEY=your_serpapi_api_key
SERPAPI_COUNTRY=in
SERPAPI_LANGUAGE=en

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Seed the product catalog:

```bash
python seed.py
```

Start the backend:

```bash
python -m uvicorn main:app --reload
```

Backend API: http://127.0.0.1:8000  
API documentation: http://127.0.0.1:8000/docs

### 3. Set up the frontend

Open a new terminal:

```bash
cd frontend
npm install
```

Create a `.env` file inside the `frontend` directory:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

## 🔑 API Requirements

ShopMate AI uses external API integrations:

- **Google Gemini API:** Powers the AI shopping assistant.
- **SerpApi:** Provides live Google Shopping search results.

Obtain your own API keys and configure them in the backend `.env` file.

**Security:** Never commit API keys, `.env` files, or other credentials to GitHub. Keep secrets on the backend.

## 🚀 Deployment

The application is deployed using:

| Component | Platform |
|---|---|
| Frontend | Vercel |
| Backend | Render |

**Live application:**  
https://ai-shopping-assistant-sable.vercel.app/

The frontend communicates with the deployed FastAPI backend through the configured `VITE_API_BASE_URL`.

*Note: The backend uses Render's free instance, which may spin down after inactivity. The first request after a period of inactivity can take longer to respond.*

## 🧪 Testing

The backend includes automated tests for core application functionality.

Run them from the backend directory:

```bash
pytest -v
```

## 🎯 Project Objective

The goal of ShopMate AI is to make online shopping more efficient by bringing product discovery, AI-assisted guidance, live shopping results, and product comparison into one unified platform.

Rather than browsing multiple websites independently, users can describe their requirements and use ShopMate AI to narrow down their options.

## 🔮 Future Improvements

Potential areas for further development include:

- User authentication and individual shopping profiles.
- Cloud-based persistent storage.
- Advanced recommendation and ranking algorithms.
- Price tracking and price-drop notifications.
- More shopping platform integrations.

## 👨‍💻 Author

**Ishant Dutta**

Computer Science Engineering | AI & Data Science

- GitHub: https://github.com/IshantDutta
- Project: https://github.com/IshantDutta/AI-shopping-assistant

---

⭐ If you find this project interesting, consider giving the repository a star!

**Built with curiosity, code, and a little help from AI.**
