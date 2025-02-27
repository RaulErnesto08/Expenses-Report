import asyncio
from typing import List
from langchain.tools import tool
from send_email import send_email  # Keep `send_email` sync

@tool
async def email_tool(report_paths: List[str]) -> dict:
    """Sends the final expense report via email asynchronously."""
    if not report_paths:
        return {"email_status": "❌ No report generated."}

    email_subject = "📊 A New Expense Report is Ready!"
    email_body = """
    <h3>Hello,</h3>
    <p>A new expense report has been successfully generated. Please find the attached files.</p>
    <p>Regards,<br>ExpenseBot</p>
    """

    # ✅ Wrap sync function in asyncio.to_thread() to prevent blocking
    await asyncio.to_thread(send_email, email_subject, email_body, report_paths)

    return {"email_status": "✅ Email Sent."}