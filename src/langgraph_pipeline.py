import os
from openai import OpenAI
from langgraph.graph import StateGraph
from typing import TypedDict, List

from ocr import extract_text_from_receipts
from compliance import validate_receipt
from report_generator import generate_expense_report

# Load API Key from .env
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Define the state schema
class PipelineState(TypedDict):
    receipt_paths: List[str]
    extracted_receipts: List[dict]
    validated_receipts: List[dict]
    expense_report_path: str

# Initialize LangGraph StateGraph with schema
workflow = StateGraph(PipelineState)

def ocr_agent(state: PipelineState):
    """
    LangGraph agent to process receipt images and extract structured text using OpenAI Vision.
    """
    receipt_paths = state["receipt_paths"]

    structured_data = extract_text_from_receipts(receipt_paths)

    if "error" in structured_data:
        print(f"Error in OCR processing: {structured_data['error']}")
        return state

    state["extracted_receipts"] = structured_data["receipts"]
    return state

def compliance_agent(state):
    """
    Validates receipts against compliance rules and flags violations.
    """
    receipts = state["extracted_receipts"]
    validated_receipts = []

    for receipt in receipts:
        violations = validate_receipt(receipt)

        receipt["violations"] = violations
        receipt["is_compliant"] = len(violations) == 0
        validated_receipts.append(receipt)

    state["validated_receipts"] = validated_receipts
    return state

def expense_report_agent(state):
    """
    Generates an expense report including compliant and non-compliant expenses.
    """
    validated_receipts = state["validated_receipts"]
    valid_receipts = [r for r in validated_receipts if r["is_compliant"]]
    invalid_receipts = [r for r in validated_receipts if not r["is_compliant"]]

    if not validated_receipts:
        print("No receipts to process.")
        state["expense_report_path"] = None
        return state

    generate_expense_report(valid_receipts, invalid_receipts)

    state["expense_report_path"] = "output/expense_report.xlsx"
    return state

# Todo: Define a final node to terminate the workflow
def final_node(state: PipelineState):
    """Final node to terminate the workflow."""
    return state

# Register agents in the LangGraph pipeline
workflow.add_node("OCR_Processing", ocr_agent)
workflow.add_node("Compliance_Checking", compliance_agent)
workflow.add_node("Expense_Report_Generation", expense_report_agent)
workflow.add_node("Final_Node", final_node)

# Define workflow entry and termination
workflow.set_entry_point("OCR_Processing")
workflow.add_edge("OCR_Processing", "Compliance_Checking")
workflow.add_edge("Compliance_Checking", "Expense_Report_Generation")
workflow.add_edge("Expense_Report_Generation", "Final_Node")

# Compile LangGraph pipeline
graph = workflow.compile()
