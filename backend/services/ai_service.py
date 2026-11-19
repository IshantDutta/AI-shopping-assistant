import os
from dotenv import load_dotenv

load_dotenv()


def generate_shopping_advice(message: str, products: list[dict]) -> str:
    """Use OpenAI when configured; otherwise return a useful deterministic response."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        if not products:
            return ("I couldn't find a matching product in the current results. "
                    "Try a broader category or increase your budget.")
        names = ", ".join(p["name"] for p in products[:3])
        return (f"I found {len(products)} matching option(s). Start by comparing {names}. "
                "Check the current merchant price, delivery, warranty and return policy "
                "before purchasing. Add an OpenAI API key to enable conversational AI explanations.")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-5.5")
        response = client.responses.create(
            model=model,
            instructions=(
                "You are ShopMate AI, a careful shopping research assistant. "
                "Only use facts present in the supplied product data. Never invent "
                "specifications, availability, discounts, reviews or warranties. "
                "Explain trade-offs, mention that live prices can change, and be concise."
            ),
            input=(
                f"User request: {message}\n\n"
                f"Available product results (JSON): {products[:12]}"
            ),
        )
        return response.output_text or "I found products, but couldn't generate an explanation."
    except Exception:
        # Keep product search usable if the AI provider is unavailable.
        return ("Product results are available, but the AI explanation service could not "
                "complete the request. Review the product details and try again later.")
