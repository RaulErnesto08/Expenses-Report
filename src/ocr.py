import os
import json
import base64
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from categories import Category

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
client = AsyncOpenAI(api_key=api_key)

async def extract_text_from_receipt(receipt_path):
    """
    Extracts structured text from a single receipt image using OpenAI Vision.
    """
    with open(receipt_path, "rb") as image:
        base64_receipt = base64.b64encode(image.read()).decode("utf-8")

    json_schema = {
    "name": "receipt_analysis",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "merchant": {"type": "string"},
            "date": {"type": "string"},
            "category": {
                "type": "string",
                "enum": [c.value for c in Category]
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": "number"},
                        "is_alcohol": {"type": "boolean", "description": "Indicates if the item contains alcohol"}
                    },
                    "required": ["name", "price", "is_alcohol"],
                    "additionalProperties": False
                }
            },
            "total": {"type": "number"},
            "alcohol_total": {"type": "number", "description": "Total amount spent on alcohol items"},
            "tip_amount": {"type": "number", "description": "Amount given as tip"},
            "receipt_id": {"type": "string"}
        },
        "required": ["merchant", "date", "category", "items", "total", "alcohol_total", "tip_amount", "receipt_id"],
        "additionalProperties": False
    }
}


    prompt = [
        f"""This is a receipt image. Extract the following details in structured JSON format:
        
        - **Merchant Name** (store or restaurant name)
        - **Date** (the date of the transaction)
        - **Category** (determine the most appropriate category: Meals, Lodging, Airfare, Rental Car, Transportation, Other)
        - **Items Purchased**:
            - Name of the item
            - Price of each item
            - Indicate if the item contains alcohol (`is_alcohol: true/false`)
        - **Total Amount** spent (must match the sum of items + tip)
        - **Alcohol Total** (sum of all items where `is_alcohol` is `true`)
        - **Tip Amount** (only if explicitly mentioned on the receipt)

        Make sure `total` is correct by summing all items and the tip (if applies).
        """,
        {"image": base64_receipt, "resize": 1024}
    ]


    PROMPT_MESSAGES = [
        {"role": "system", "content": "You are an OCR analyzer for receipts, extracting structured data."},
        {"role": "user", "content": prompt},
    ]

    try:
        response = await client.chat.completions.create(
            # model="gpt-4o-mini",
            model="gpt-4o-2024-08-06", # Cheaper for vision
            messages=PROMPT_MESSAGES,
            response_format={"type": "json_schema", "json_schema": json_schema},
            max_tokens=1000,
            temperature=0.4,
        )

        structured_data = json.loads(response.choices[0].message.content)
        structured_data["receipt_id"] = os.path.basename(receipt_path)
        structured_data["category"] = Category.from_string(structured_data["category"]).value
        
        print(f"✅ Extracted structured data from receipt {structured_data}")
        
        return structured_data
    except Exception as e:
        print(f"Error extracting text from receipt {receipt_path}: {e}")
        return {"error": str(e), "receipt_id": os.path.basename(receipt_path)}