from typing import TypedDict, List, Optional

class PipelineState(TypedDict):
    receipt_paths: List[str]
    extracted_receipts: List[dict]
    validated_receipts: List[dict]
    expense_report_paths: List[str]
    compliance_rules: List[dict]
    email_sent: bool
    email_status: Optional[str]
    next_step: Optional[str]
    travel_start_date: Optional[str]
    travel_end_date: Optional[str]
    requester: Optional[str]
    requester_department: Optional[str]
    approver: Optional[str]
    approver_department: Optional[str]
    client: Optional[str]
    project: Optional[str]
