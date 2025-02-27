from typing import AsyncGenerator
from schemas.state import PipelineState
from tools.email_tool import email_tool

async def action_agent(state: PipelineState) -> AsyncGenerator[dict, None]:
    """Handles email sending and ensures process ends correctly."""

    if not state.get("email_sent", False) and state.get("expense_report_paths"):
        email_status = await email_tool.ainvoke({"report_paths": state["expense_report_paths"]})
        state["email_sent"] = True

        yield {"email_status": email_status, "next_step": "Done"}
        return

    if state.get("email_sent", False):
        yield {"next_step": "Done"}
        return