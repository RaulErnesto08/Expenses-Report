import os
import datetime
from openai import OpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from typing import TypedDict, List, Optional

from send_email import send_email
from ocr import extract_text_from_receipt
from compliance import validate_receipts_with_llm
from report_generator import generate_expense_report

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Define the state schema
class PipelineState(TypedDict):
    receipt_paths: List[str]
    extracted_receipts: List[dict]
    validated_receipts: List[dict]
    expense_report_paths: List[str]
    compliance_rules: List[dict]

# Initialize LangGraph StateGraph with schema
workflow = StateGraph(PipelineState)

# OCR Processing Agent
async def ocr_agent(state: PipelineState):
    """
    Processes receipts asynchronously, extracting structured data one by one
    and yielding results as they are ready.
    """
    receipt_paths = state["receipt_paths"]
    extracted_receipts = []

    for path in receipt_paths:
        receipt = await extract_text_from_receipt(path)

        if "error" in receipt:
            print(f"❌ Error processing receipt {path}: {receipt['error']}")
            continue  # Skip faulty receipts

        extracted_receipts.append(receipt)

        # Yield incremental updates
        yield {"extracted_receipts": extracted_receipts.copy()}

    # Final state update
    state["extracted_receipts"] = extracted_receipts
    yield {"extracted_receipts": extracted_receipts}

# Compliance Checking Agent
async def compliance_agent(state: PipelineState):
    """
    Uses LLM to validate receipts against company compliance rules.
    """
    extracted_receipts = state.get("extracted_receipts", [])
    compliance_rules = state.get("compliance_rules", [])

    # Ensure validated_receipts exists in state
    if "validated_receipts" not in state:
        state["validated_receipts"] = []

    async for validated_receipt in validate_receipts_with_llm(extracted_receipts, compliance_rules):
        # Append new validated receipt to the existing list
        state["validated_receipts"].extend(validated_receipt["validated_receipts"])
        
        # Yield incremental updates
        yield {"validated_receipts": state["validated_receipts"].copy()}

    # Final state update
    yield {"validated_receipts": state["validated_receipts"]}

# Expense Report Generation Agent
async def expense_report_agent(state: PipelineState):
    """
    Generates an expense report after **all receipts** have been validated.
    """
    validated_receipts = state["validated_receipts"]
    valid_receipts = [r for r in validated_receipts if r["is_compliant"]]
    invalid_receipts = [r for r in validated_receipts if not r["is_compliant"]]

    if not validated_receipts:
        state["expense_report_paths"] = []
        return state

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    report_name = f"{timestamp}_expense_report"

    excel_report_path = f"output/{report_name}.xlsx"
    pdf_report_path = f"output/{report_name}.pdf"
    
    generate_expense_report(valid_receipts, invalid_receipts, f"output/{report_name}")
    
    state["expense_report_paths"] = [excel_report_path, pdf_report_path]
    return state

async def email_sender_agent(state: PipelineState):
    """
    Sends the final expense report via email.
    """
    report_paths = state.get("expense_report_paths", [])

    if not report_paths:
        print("❌ No report generated.")
        return state

    email_subject = "📊 A New Expense Report is Ready!"
    email_body = f"""
    <h3>Hello,</h3>
    <p>A new expense report has been successfully generated. Please find the attached files.</p>
    <p>Regards,<br>ExpenseBot</p>
    """
    
    send_email(email_subject, email_body, report_paths)
    
    return state

# Register agents in the LangGraph pipeline
workflow.add_node("OCR_Processing", ocr_agent)
workflow.add_node("Compliance_Checking", compliance_agent)
workflow.add_node("Expense_Report_Generation", expense_report_agent)
workflow.add_node("Email_Sending", email_sender_agent)

# Define workflow entry and termination
workflow.set_entry_point("OCR_Processing")
workflow.add_edge("OCR_Processing", "Compliance_Checking")
workflow.add_edge("Compliance_Checking", "Expense_Report_Generation")
workflow.add_edge("Expense_Report_Generation", "Email_Sending")

# Compile LangGraph pipeline
graph = workflow.compile()
