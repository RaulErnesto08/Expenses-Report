import os
import json
import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Compliance Rules
MAX_MEAL_BUDGET = 70
MAX_MEAL_WITH_APPROVAL = 200
ALCOHOL_LIMIT = 0.2
TIP_LIMIT = 0.2
LODGING_MAX = 250
MILEAGE_RATE = 0.67

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
client = AsyncOpenAI(api_key=api_key)

async def validate_receipts_with_llm(receipts, compliance_rules):
    """
    Validates structured receipts using an LLM against compliance rules and yields results incrementally.
    """

    json_schema = {
        "name": "receipt_validation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "is_compliant": {"type": "boolean"},
                "violations": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["is_compliant", "violations"],
            "additionalProperties": False
        }
    }

    rules = "\n".join(
        [f"- {rule['rule_name']}: {rule['value']} {rule['type']}" for rule in compliance_rules]
    )
    
    print(f"Rules: {rules}")

    for receipt in receipts:
        instruction_prompt = f"""
        You are a compliance officer reviewing business expense receipts.
        Your task is to determine if the given receipt is compliant with company policy.

        **Company Expense Rules:**
        {rules}

        **Receipt to Validate:**
        Merchant: {receipt['merchant']}
        Date: {receipt['date']}
        Category: {receipt['category']}
        Total Amount: ${receipt['total']}
        Alcohol Total: ${receipt.get('alcohol_total', 0.0)}
        Tip Amount: ${receipt.get('tip_amount', 0.0)}
        Items:
        {json.dumps(receipt['items'], indent=4)}

        **Instructions:**
        - Compare the receipt details against the company expense rules.
        - If any rules are violated, list the violations clearly.
        - If the receipt is compliant, return `is_compliant: true` and an empty list of violations.
        """

        PROMPT_MESSAGES = [
            {"role": "system", "content": "You are a compliance officer reviewing business expense receipts."},
            {"role": "user", "content": instruction_prompt},
        ]

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=PROMPT_MESSAGES,
                response_format={"type": "json_schema", "json_schema": json_schema},
                max_tokens=1000,
                temperature=0.1,
            )

            structured_data = json.loads(response.choices[0].message.content)

            receipt['is_compliant'] = structured_data['is_compliant']
            receipt['violations'] = structured_data['violations']
            
            yield {"validated_receipts": [receipt]}

        except Exception as e:
            print(f"❌ Error validating receipt {receipt.get('receipt_id', 'unknown')}: {e}")

            receipt['is_compliant'] = False
            receipt['violations'] = [f"Validation error: {str(e)}"]
            
            yield {"validated_receipts": [receipt]}
    