import os
import json
import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI

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
        Total Amount: ${receipt['total']:.2f}
        Items:
        {json.dumps(receipt['items'], indent=4)}

        **Validation Rules:**
        - Compare the total amount, alcohol amount, and tip against the policy limits PER RECEIPT.
        - If any rules are violated, list the violations, but only list actual violations.
        - If the receipt is compliant, return `is_compliant: true` and an empty list of violations.
        """

        PROMPT_MESSAGES = [
            {"role": "system", "content": "You are a compliance officer reviewing business expenses."},
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
            receipt['is_compliant'] = False
            receipt['violations'] = [f"Validation error: {str(e)}"]
            yield {"validated_receipts": [receipt]}