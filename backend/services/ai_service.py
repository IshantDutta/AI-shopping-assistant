import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

client = None

if OPENAI_API_KEY:
    client = OpenAI(
        api_key=OPENAI_API_KEY
    )


def generate_shopping_response(
    user_message: str,
    products: list
):
    """
    Generate an AI response using the products
    retrieved from our database.
    """

    product_information = []

    for product in products:
        product_information.append({
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "price": product.price,
            "rating": product.rating,
            "description": product.description
        })

    # If no API key has been configured yet
    if not client:
        return {
            "message": "AI service is not configured yet.",
            "products": product_information
        }

    prompt = f"""
You are an intelligent AI shopping assistant.

The user asked:

"{user_message}"

Here are the products available in the database:

{product_information}

Your job is to help the user make a shopping decision.

Rules:

1. Recommend only products provided in the database.
2. Do not invent specifications.
3. Explain why each recommended product matches the user's request.
4. Mention important trade-offs when relevant.
5. Consider price and rating.
6. If none of the products are suitable, clearly say so.
7. Keep the answer concise and conversational.
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt
    )

    return {
        "message": response.output_text,
        "products": product_information
    }