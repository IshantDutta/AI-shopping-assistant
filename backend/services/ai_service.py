import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Load backend/.env reliably whether Uvicorn is launched from backend/ or project root.
BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """
You are ShopMate AI, a careful shopping research assistant for users in India.
Help users choose products based only on the supplied product records.
Never invent product specifications, prices, discounts, stock, delivery dates,
warranties, review counts, or seller policies.
Use INR (₹) when discussing prices. Compare trade-offs clearly.
If the user's budget is present, prioritize products within it and explicitly
say when a product exceeds it. Mention that catalog/live prices can change and
must be verified with the merchant. Be friendly, concise, and practical.
"""


def is_gemini_configured() -> bool:
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def get_gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()


def _fallback_advice(message: str, products: list[dict]) -> str:
    if not products:
        return (
            "I couldn't find a matching product in the available results. "
            "Try a broader search, a different category, or a higher budget."
        )

    names = ", ".join(
        str(product.get("name", "Unnamed product"))
        for product in products[:3]
    )
    return (
        f"I found {len(products)} matching option(s). Start by comparing {names}. "
        "Check the current merchant price, product specifications, delivery, "
        "warranty and return policy before purchasing."
    )


def generate_shopping_advice(message: str, products: list[dict]) -> str:
    """
    Generate a product-grounded explanation with Gemini.
    The deterministic fallback keeps catalog search usable without an API key.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return (
            _fallback_advice(message, products)
            + " Gemini is not configured yet; add GEMINI_API_KEY to backend/.env "
              "to enable AI explanations."
        )

    try:
        from google import genai
        from google.genai import types

        model = get_gemini_model()
        product_context = json.dumps(
            products[:12],
            ensure_ascii=False,
            default=str,
        )
        prompt = (
            f"Customer request:\n{message}\n\n"
            f"Available product results (use only these facts):\n{product_context}\n\n"
            "Give a helpful recommendation. If several products are available, "
            "identify the strongest match and explain why. Mention meaningful "
            "trade-offs and any budget mismatch. Do not claim to have read reviews "
            "unless review data is explicitly included."
        )

        with genai.Client(api_key=api_key) as client:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.35,
                    max_output_tokens=650,
                ),
            )
            text = (response.text or "").strip()

        if not text:
            logger.warning("Gemini returned an empty text response.")
            return _fallback_advice(message, products)
        return text

    except Exception as exc:
        # Keep the product catalog usable and put the diagnostic in the server log.
        logger.exception("Gemini request failed: %s", type(exc).__name__)
        return (
            _fallback_advice(message, products)
            + f" Gemini could not generate an explanation ({type(exc).__name__}). "
              "Check the backend terminal for details, your API key, model access, "
              "quota and network connection."
        )
