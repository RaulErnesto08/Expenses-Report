import io
import os
import sys
import zipfile
import asyncio
import pandas as pd
import streamlit as st

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from workflows.expense_workflow import create_expense_workflow  # ✅ Updated import
from schemas.state import PipelineState

# Predefined Compliance Rules
DEFAULT_RULES = [
    {"rule_name": "Max Daily Meal Budget", "value": 70, "type": "Amount ($)"},
    {"rule_name": "Individual Meals Receipt Approval Required Above", "value": 200, "type": "Amount ($)"},
    {"rule_name": "Alcohol Limit Per Receipt", "value": 20, "type": "Percentage (%)"},
    {"rule_name": "Tip Limit Per Receipt", "value": 20, "type": "Percentage (%)"},
    {"rule_name": "Max Lodging Cost Per Night", "value": 250, "type": "Amount ($)"},
    {"rule_name": "Airfare - Economy Required for Flights < 6 hrs", "value": True, "type": "Boolean"},
    {"rule_name": "Rental Cars - No Luxury Vehicles Allowed", "value": True, "type": "Boolean"},
]

# Initialize session state
if "validated_receipts" not in st.session_state:
    st.session_state.validated_receipts = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "expense_report_paths" not in st.session_state:
    st.session_state.expense_report_paths = []

# Initialize LangGraph Workflow
graph = create_expense_workflow()

# Streamlit App
def main():
    st.title("📊 Expense Report Generator")
    st.write("Automated processing of receipts with compliance enforcement.")
    
    st.subheader("📝 Report Details")

    # Travel Dates
    col1, col2 = st.columns(2)
    with col1:
        travel_start_date = st.date_input("📅 Travel Start Date", value=None)
    with col2:
        travel_end_date = st.date_input("📅 Travel End Date", value=None)

    # Requester & Requester Department
    col1, col2 = st.columns(2)
    with col1:
        requester = st.text_input("👤 Requester Name", value="")
    with col2:
        requester_department = st.text_input("🏢 Requester Department", value="")

    # Approver & Approver Department
    col1, col2 = st.columns(2)
    with col1:
        approver = st.text_input("🧑‍💼 Approver Name", value="")
    with col2:
        approver_department = st.text_input("🏢 Approver Department", value="")

    # Client & Project
    col1, col2 = st.columns(2)
    with col1:
        client = st.text_input("🏢 Client (Optional)", value="")
    with col2:
        project = st.text_input("📂 Project (Optional)", value="")

    
    st.write("Upload receipt images to generate an expense report.")
    uploaded_files = st.file_uploader("Upload receipt images", type=["jpg", "png"], accept_multiple_files=True)
    
    status_text = st.empty()
    progress_bar = st.empty()
    results_table = st.empty()

    if uploaded_files:
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        receipt_paths = []

        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            receipt_paths.append(file_path)

        state: PipelineState = {
            "receipt_paths": receipt_paths,
            "extracted_receipts": [],
            "validated_receipts": [],
            "expense_report_paths": [],
            "compliance_rules": DEFAULT_RULES,
            "travel_start_date": travel_start_date.strftime('%Y-%m-%d') if travel_start_date else None,
            "travel_end_date": travel_end_date.strftime('%Y-%m-%d') if travel_end_date else None,
            "requester": requester,
            "requester_department": requester_department,
            "approver": approver,
            "approver_department": approver_department,
            "client": client,
            "project": project,
        }

        # Function to run the async process
        async def run_async_process():
            await process_receipts(state, status_text, progress_bar, results_table)
            st.session_state.expense_report_paths = state.get("expense_report_paths")
            st.session_state.processing = False

        if st.button("Start Processing"):
            if not st.session_state.processing:
                st.session_state.processing = True
                st.session_state.validated_receipts = []
                asyncio.run(run_async_process())

        # Show the table with validated receipts
        if st.session_state.validated_receipts:
            df = pd.DataFrame([
                {
                    "Merchant": r.get("merchant", "Unknown"),
                    "Date": r.get("date", "Unknown"),
                    "Total Amount": r.get("total", 0.0),
                    "Category": r.get("category", "Other"),
                    "Compliance Status": "✅ Compliant" if r["is_compliant"] else "❌ Non-Compliant",
                    "Violations": "\n".join(r.get("violations", [])) if not r["is_compliant"] else "None"
                }
                for r in st.session_state.validated_receipts
            ])
            results_table.dataframe(df, use_container_width=True)

async def process_receipts(state, status_text, progress_bar, results_table):
    """Processes receipts asynchronously and updates the Streamlit UI dynamically."""
    total_receipts = len(state["receipt_paths"])
    progress_bar.progress(0)

    while True:
        async for step in graph.astream(state):

            if "Processing" in step:
                extracted_receipts = step["Processing"].get("extracted_receipts", [])
                if extracted_receipts:
                    progress_bar.progress(len(extracted_receipts) / total_receipts)
                    status_text.text(f"📄 Processing receipt {len(extracted_receipts)}/{total_receipts} (OCR)")

            if "Processing" in step and "validated_receipts" in step["Processing"]:
                validated_receipts = step["Processing"]["validated_receipts"]
                st.session_state.validated_receipts = validated_receipts
                status_text.text(f"✅ Validating receipt {len(validated_receipts)}/{total_receipts} (Compliance)")

            if "Processing" in step and "expense_report_paths" in step["Processing"]:
                expense_report_paths = step["Processing"]["expense_report_paths"]
                st.session_state.expense_report_paths = expense_report_paths
                    
            if "Action" in step and step["Action"] is not None:
                if "email_status" in step["Action"]:
                    status_text.text(step["Action"]["email_status"])

                if "next_step" in step["Action"]:
                    next_step = step["Action"]["next_step"]

                    if next_step == "Done":
                        progress_bar.progress(1.0)
                        status_text.text("🎉 Processing complete! Download the report below.")

                        if "zip_buffer" not in st.session_state:
                            if st.session_state.expense_report_paths:
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                                    for report_path in st.session_state.expense_report_paths:
                                        zipf.write(report_path, os.path.basename(report_path))

                                zip_buffer.seek(0)
                                st.session_state.zip_buffer = zip_buffer  

                        if "zip_buffer" in st.session_state:
                            st.download_button(
                                label="📥 Download Expense Reports (ZIP)",
                                data=st.session_state.zip_buffer,
                                file_name="expense_reports.zip",
                                mime="application/zip",
                            )

                        return

if __name__ == "__main__":
    main()
