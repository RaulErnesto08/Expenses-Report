from typing import List
from langchain.tools import tool
from compliance import validate_receipts_with_llm

@tool
async def compliance_tool(receipts: List[dict], compliance_rules: List[dict]) -> List[dict]:
    """Validates receipts against compliance rules."""
    validated = []
    async for result in validate_receipts_with_llm(receipts, compliance_rules):
        validated.extend(result["validated_receipts"])
    return validated