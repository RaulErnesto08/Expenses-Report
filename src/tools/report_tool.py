import datetime
from typing import List, Optional, Dict
from langchain.tools import tool
from report_generator import generate_expense_report

@tool
def report_tool(
    valid_receipts: List[dict], 
    invalid_receipts: List[dict], 
    travel_start_date: Optional[str] = "Not Provided",
    travel_end_date: Optional[str] = "Not Provided",
    requester: Optional[str] = "",
    requester_department: Optional[str] = "",
    approver: Optional[str] = "",
    approver_department: Optional[str] = "",
    client: Optional[str] = "",
    project: Optional[str] = "",
) -> List[str]:
    """Generates an Excel and PDF expense report with user-provided details."""

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    report_name = f"output/{timestamp}_expense_report"
    
    generate_expense_report(
        valid_receipts,
        invalid_receipts,
        report_name,
        {
            "travel_start_date": travel_start_date,
            "travel_end_date": travel_end_date,
            "requester": requester,
            "requester_department": requester_department,
            "approver": approver,
            "approver_department": approver_department,
            "client": client,
            "project": project,
        }
    )

    return [f"{report_name}.xlsx", f"{report_name}.pdf"]
