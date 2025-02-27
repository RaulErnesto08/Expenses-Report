from langchain.tools import tool
from ocr import extract_text_from_receipt

@tool
async def ocr_tool(receipt_path: str) -> dict:
    """Extracts structured text from a receipt image."""
    return await extract_text_from_receipt(receipt_path)