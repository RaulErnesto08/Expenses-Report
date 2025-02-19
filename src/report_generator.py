import os
import pandas as pd
import matplotlib.pyplot as plt

from fpdf import FPDF
from datetime import datetime
from collections import Counter

def generate_expense_report(valid_receipts, invalid_receipts, output_path):
    """
    Generates an expense report in Excel and PDF formats with:
    - A summary sheet with compliance statistics.
    - Detailed sheets for compliant and non-compliant expenses.
    - A breakdown of all receipts and their individual items.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    excel_path = generate_excel_report(valid_receipts, invalid_receipts, f"{output_path}.xlsx")
    pdf_path = generate_pdf_report(valid_receipts, invalid_receipts, f"{output_path}.pdf")
    
    return excel_path, pdf_path

def generate_excel_report(valid_receipts, invalid_receipts, output_path):
    """
    Generates an Excel expense report.
    """
    
    new_valid_df = pd.DataFrame([
        {
            "Merchant": r.get("merchant", "Unknown Merchant"),
            "Date": r.get("date", "Unknown Date"),
            "Total Amount ($)": r.get("total", 0.0),
            "Alcohol Total ($)": r.get("alcohol_total", 0.0),
            "Tip Amount ($)": r.get("tip_amount", 0.0),
            "Category": r.get("category", "Other"),
            "Receipt ID": r.get("receipt_id", "Unknown ID")
        }
        for r in valid_receipts
    ])

    new_invalid_df = pd.DataFrame([
        {
            "Merchant": r.get("merchant", "Unknown Merchant"),
            "Date": r.get("date", "Unknown Date"),
            "Total Amount ($)": r.get("total", 0.0),
            "Alcohol Total ($)": r.get("alcohol_total", 0.0),
            "Tip Amount ($)": r.get("tip_amount", 0.0),
            "Category": r.get("category", "Other"),
            "Receipt ID": r.get("receipt_id", "Unknown ID"),
            "Violations": "; ".join(r.get("violations", []))
        }
        for r in invalid_receipts
    ])

    # Load existing data if file exists
    if os.path.exists(output_path):
        existing_data = pd.ExcelFile(output_path)
        valid_df = pd.read_excel(existing_data, sheet_name="Compliant Expenses")
        invalid_df = pd.read_excel(existing_data, sheet_name="Non-Compliant Expenses")
    else:
        valid_df = pd.DataFrame()
        invalid_df = pd.DataFrame()
        
        
    final_valid_df = pd.concat([valid_df, new_valid_df], ignore_index=True)
    final_invalid_df = pd.concat([invalid_df, new_invalid_df], ignore_index=True)

    # Generate Summary
    total_receipts = len(final_valid_df) + len(final_invalid_df)
    total_valid = len(final_valid_df)
    total_invalid = len(final_invalid_df)

    summary_data = {
        "Metric": ["Total Receipts Processed", "Total Compliant", "Total Non-Compliant"],
        "Value": [total_receipts, total_valid, total_invalid]
    }

    summary_df = pd.DataFrame(summary_data)

    # Generate Receipts Breakdown
    receipts_breakdown_data = []

    for r in valid_receipts + invalid_receipts:
        first_row = {
            "Receipt ID": r.get("receipt_id", "Unknown ID"),
            "Merchant": r.get("merchant", "Unknown Merchant"),
            "Date": r.get("date", "Unknown Date"),
            "Category": r.get("category", "Other"),
            "Item Name": "-",
            "Item Price ($)": "-",
            "Alcohol?": "-",
            "Compliance Status": "✅ Compliant" if r.get("is_compliant", False) else "❌ Non-Compliant",
            "Violations": "; ".join(r.get("violations", [])) if not r.get("is_compliant", False) else "None"
        }
        receipts_breakdown_data.append(first_row)

        for item in r.get("items", []):
            receipts_breakdown_data.append({
                "Receipt ID": "",
                "Merchant": "",
                "Date": "",
                "Category": "",
                "Item Name": item["name"],
                "Item Price ($)": item["price"],
                "Alcohol?": "Yes" if item.get("is_alcohol", False) else "No",
                "Compliance Status": "",
                "Violations": ""
            })

    receipts_breakdown_df = pd.DataFrame(receipts_breakdown_data)

    with pd.ExcelWriter(output_path, engine="openpyxl", mode="w") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        final_valid_df.to_excel(writer, sheet_name="Compliant Expenses", index=False)
        final_invalid_df.to_excel(writer, sheet_name="Non-Compliant Expenses", index=False)
        receipts_breakdown_df.to_excel(writer, sheet_name="Receipts Breakdown", index=False)

    return output_path

def generate_pdf_report(valid_receipts, invalid_receipts, pdf_path):
    """
    Generates a visually enhanced PDF expense report.
    """
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "assets", "logo.png")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add Cover Page
    pdf.set_font("Arial", "B", 24)
    pdf.cell(200, 40, txt="Expense Report", ln=True, align="C")
    pdf.set_font("Arial", "I", 16)
    pdf.cell(200, 10, txt=f"Generated on: {current_date}", ln=True, align="C")
    pdf.image(logo_path, x=55, y=100, w=100)
    pdf.add_page()

    # Add Summary Section
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Summary", ln=True)
    pdf.set_font("Arial", size=12)

    total_receipts = len(valid_receipts) + len(invalid_receipts)
    total_valid = len(valid_receipts)
    total_invalid = len(invalid_receipts)

    pdf.cell(200, 10, txt=f"Total Receipts Processed: {total_receipts}", ln=True)
    pdf.cell(200, 10, txt=f"Total Compliant: {total_valid}", ln=True)
    pdf.cell(200, 10, txt=f"Total Non-Compliant: {total_invalid}", ln=True)
    pdf.ln(10)

    # Add Pie Chart for Compliant vs Non-Compliant
    labels = ["Compliant", "Non-Compliant"]
    sizes = [total_valid, total_invalid]
    colors = ["#85BF49", "#FE4E48"]

    plt.figure()
    plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
    plt.axis("equal")
    plt.title("Compliant vs Non-Compliant Expenses")
    chart_path = "compliance_pie_chart.png"
    plt.savefig(chart_path)
    plt.close()

    pdf.image(chart_path, x=50, y=pdf.get_y(), w=100)
    pdf.ln(100)

    # Add Top Violations
    most_common_violations = Counter(
        [violation for r in invalid_receipts for violation in r["violations"]]
    ).most_common(5)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Top Violations", ln=True)
    pdf.set_font("Arial", size=12)

    for idx, (violation, count) in enumerate(most_common_violations):
        pdf.cell(200, 10, txt=f"{idx+1}. {violation} ({count} times)", ln=True)
    pdf.ln(10)

    # Add Compliant Expenses
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Compliant Expenses", ln=True)
    pdf.set_font("Arial", size=12)

    for r in valid_receipts:
        pdf.cell(200, 10, txt=f"Merchant: {r.get('merchant', 'Unknown')}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {r.get('date', 'Unknown')}", ln=True)
        pdf.cell(200, 10, txt=f"Total Amount: ${r.get('total', 0.0):.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Category: {r.get('category', 'Other')}", ln=True)
        pdf.ln(5)
        
        # Add Receipt Breakdown Table
        pdf.set_font("Arial", "B", 12)
        pdf.cell(100, 8, txt="Item Name", border=1)
        pdf.cell(50, 8, txt="Price ($)", border=1)
        pdf.ln()
        pdf.set_font("Arial", size=12)

        for item in r.get("items", []):
            pdf.cell(100, 8, txt=item["name"], border=1)
            pdf.cell(50, 8, txt=f"${item['price']:.2f}", border=1)
            pdf.ln()
        
        pdf.ln(10)

    # Add Non-Compliant Expenses
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Non-Compliant Expenses", ln=True)
    pdf.set_font("Arial", size=12)

    for r in invalid_receipts:
        pdf.cell(200, 10, txt=f"Merchant: {r.get('merchant', 'Unknown')}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {r.get('date', 'Unknown')}", ln=True)
        pdf.cell(200, 10, txt=f"Total Amount: ${r.get('total', 0.0):.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Category: {r.get('category', 'Other')}", ln=True)
        
        violations = r.get("violations", [])
        if violations:
            pdf.cell(200, 10, txt="Violations:", ln=True)
            pdf.set_font("Arial", size=12)
            for v in violations:
                pdf.cell(200, 8, txt=f"- {v}", ln=True)
        
        pdf.ln(5)
        
        # Add Receipt Breakdown Table
        pdf.set_font("Arial", "B", 12)
        pdf.cell(100, 8, txt="Item Name", border=1)
        pdf.cell(50, 8, txt="Price ($)", border=1)
        pdf.ln()
        pdf.set_font("Arial", size=12)

        for item in r.get("items", []):
            pdf.cell(100, 8, txt=item["name"], border=1)
            pdf.cell(50, 8, txt=f"${item['price']:.2f}", border=1)
            pdf.ln()

        pdf.ln(10)

    # Save PDF
    pdf.output(pdf_path)