from typing import AsyncGenerator
from schemas.state import PipelineState
from tools.ocr_tool import ocr_tool
from tools.compliance_tool import compliance_tool
from tools.report_tool import report_tool

async def processing_agent(state: PipelineState) -> AsyncGenerator[dict, None]:
    """Processes receipts by dynamically selecting the next tool to execute."""

    if not state.get("extracted_receipts"):
        extracted_receipts = []
        for path in state["receipt_paths"]:
            receipt = await ocr_tool.ainvoke({"receipt_path": path})
            if "error" not in receipt:
                extracted_receipts.append(receipt)

        if extracted_receipts:
            state["extracted_receipts"] = extracted_receipts
            yield {"extracted_receipts": extracted_receipts}

    if not state.get("validated_receipts") and state.get("extracted_receipts"):
        validated_receipts = await compliance_tool.ainvoke(
            {"receipts": state["extracted_receipts"], "compliance_rules": state["compliance_rules"]}
        )
        if validated_receipts:
            state["validated_receipts"] = validated_receipts
            yield {"validated_receipts": validated_receipts}

    if not state.get("expense_report_paths") and state.get("validated_receipts"):
        valid_receipts = [r for r in state["validated_receipts"] if r["is_compliant"]]
        invalid_receipts = [r for r in state["validated_receipts"] if not r["is_compliant"]]

        if valid_receipts or invalid_receipts:
            report_paths = await report_tool.ainvoke(
                {
                    "valid_receipts": valid_receipts,
                    "invalid_receipts": invalid_receipts,
                    "travel_start_date": state.get("travel_start_date", "Not Provided"),
                    "travel_end_date": state.get("travel_end_date", "Not Provided"),
                    "requester": state.get("requester", ""),
                    "requester_department": state.get("requester_department", ""),
                    "approver": state.get("approver", ""),
                    "approver_department": state.get("approver_department", ""),
                    "client": state.get("client", ""),
                    "project": state.get("project", ""),
                }
            )

            if report_paths:
                state["expense_report_paths"] = report_paths
                yield {"expense_report_paths": report_paths}
