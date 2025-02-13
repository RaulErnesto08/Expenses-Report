import pandas as pd

def generate_expense_report(valid_receipts, invalid_receipts, output_path="output/expense_report.xlsx"):
    """
    Generates an expense report in Excel format.
    """
    writer = pd.ExcelWriter(output_path, engine="xlsxwriter")

    # Convert valid receipts to DataFrame
    valid_df = pd.DataFrame([
        {
            "Merchant": r["merchant"],
            "Date": r["date"],
            "Total Amount": r["total"],
            "Category": r["category"],
            "Receipt ID": r["receipt_id"]
        }
        for r in valid_receipts
    ])
    
    # Convert non-compliant receipts to DataFrame
    invalid_df = pd.DataFrame([
        {
            "Merchant": r["merchant"],
            "Date": r["date"],
            "Total Amount": r["total"],
            "Category": r["category"],
            "Receipt ID": r["receipt_id"],
            "Violations": "; ".join(r["violations"])
        }
        for r in invalid_receipts
    ])

    # Write DataFrames to Excel
    valid_df.to_excel(writer, sheet_name="Compliant Expenses", index=False)
    invalid_df.to_excel(writer, sheet_name="Non-Compliant Expenses", index=False)

    writer.close()
