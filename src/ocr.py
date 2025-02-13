import os
import glob
import json
import base64
from openai import OpenAI
from categories import Category

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def get_receipt_images(directory="images/"):
    """Fetch all image files from the given directory."""
    return glob.glob(os.path.join(directory, "*.jpg")) + glob.glob(os.path.join(directory, "*.png"))

def extract_text_from_receipts(receipts):
    """
    Extracts structured text from multiple receipt images using OpenAI Vision.
    
    :param receipt: List of image file paths.
    :return: JSON structured data for each receipt.
    """
    base64_receipts = []
    
    # Convert images to base64 format
    for receipt in receipts:
        with open(receipt, "rb") as image:
            base64_receipt = base64.b64encode(image.read()).decode("utf-8")
            base64_receipts.append(base64_receipt)
    
    json_schema = {
        "name": "receipt_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "receipts": {
                    "type": "array",
                    "items": {
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
                                    },
                                    "required": ["name", "price"],
                                    "additionalProperties": False
                                }
                            },
                            "total": {"type": "number"},
                            "receipt_id": {"type": "string"}
                        },
                        "required": ["merchant", "date", "category", "items", "total", "receipt_id"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["receipts"],
            "additionalProperties": False
        }
    }

    prompt = [
        f"These are receipt images. Extract the merchant, date, category, items, and total amount in structured JSON format.",
        *map(lambda receipt: {"image": receipt, "resize": 1024}, base64_receipts)
    ]
    
    PROMPT_MESSAGES = [
        {"role": "system", "content": "You are an OCR analyzer for receipts, extracting structured data."},
        {"role": "user", "content": prompt},
    ]
    
    try:
        response = client.chat.completions.create(
            # model="gpt-4o-mini",
            model="gpt-4o-2024-08-06", # Cheaper for vision
            messages=PROMPT_MESSAGES,
            response_format={"type": "json_schema", "json_schema": json_schema},
            max_tokens=1000,
            temperature=0.4,
        )
        
        structured_data = json.loads(response.choices[0].message.content)

        # Ensure categories are valid
        for receipt in structured_data["receipts"]:
            receipt["category"] = Category.from_string(receipt["category"]).value
        
        # Add image path to each receipt
        for i, receipt in enumerate(structured_data["receipts"]):
            receipt["receipt_id"] = os.path.basename(receipts[i])
        
        return structured_data
    except Exception as e:
        print(f"Error extracting text from receipts: {e}")
        return {"error": str(e)}