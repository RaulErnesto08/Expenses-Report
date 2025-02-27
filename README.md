# 🚀 Automated Expense Report Generator

This project automates the **extraction, validation, and reporting of expense receipts** using an **agentic system powered by LangGraph**. It processes receipt images, applies company compliance policies, generates reports (Excel & PDF), and sends them via email.

## 📌 Features

✅ **OCR Processing** – Extracts structured data from receipt images using OpenAI Vision  
✅ **Compliance Validation** – Checks expenses against company policies using GPT  
✅ **Report Generation** – Creates Excel and PDF reports with a receipt breakdown  
✅ **Email Notifications** – Sends the reports via SendGrid  
✅ **Streamlit Web UI** – User-friendly interface for uploading and processing receipts  

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/RaulErnesto08/Expenses-Report.git
cd Expenses-Report
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1️⃣ Set Up Environment Variables
Copy the example `.env` file and configure it:
```bash
cp .env.example .env  # macOS/Linux
copy .env.example .env  # Windows
```
Then, open the `.env` file and update your API keys and mail details:
```
OPENAI_API_KEY="your-openai-api-key"
SENDGRID_API_KEY="your-sendgrid-api-key"
SENDER_EMAIL="your-verified-sender@example.com"
RECIPIENT_EMAIL="finance-team@example.com"
```

## 🚀 Running the Application

### Run the Streamlit Web App
```bash
streamlit run web/app.py
```
- Upload receipt images
- Enter **Travel Dates, Requester, Approver, and Client/Project details**
- Track processing progress
- Download generated reports

## 📊 Processing Pipeline
The **LangGraph agentic pipeline** automates the entire workflow:  

| **Phase**       | **Subtasks**                                         | **Agent**           |
|----------------|-----------------------------------------------------|---------------------|
| **Submission**  | Upload Receipts                                    | User               |
| **Processing**  | OCR → Compliance Check                             | Processing Agent   |
| **Report Gen.** | Generate Excel & PDF Reports                       | Processing Agent   |
| **Emailing**    | Send Reports to Finance Team                       | Action Agent       |
| **Approval**    | Finance Team Reviews & Approves Report             | Finance Team       |


## 📜 Example Receipt Breakdown

### ✅ **Compliant Receipt**
```
Merchant: Chick-fil-A
Date: 2023-12-30
Total Amount: $13.59
Category: Meals

Items:
- Meal-GRLClub+CJ: $12.55
- BBQ: $0

✅ Compliant ✅
```

### ❌ **Non-Compliant Receipt**
```
Merchant: The Tack Room
Date: 2024-04-08
Total Amount: $124.53
Category: Meals

Items:
- BBQ Potato Chips: $7.00
- Diet Coke: $3.00
- Trillium Fort Point: $10.00
- Fried Chicken Sandwich: $34.00
- Famous Duck Grilled Cheese: $25.00
- Mac & Cheese: $17.00
- Burger of the moment: $18.00

Violations:
- Total amount exceeds the max daily meal budget of $70

❌ Non-Compliant ❌
```

## 📄 File Structure
```
📂 expense-report-automation
│── 📂 src
│   ├── assets/
│   │   ├── logo.png
│   │   ├── Template.xlsx
│   ├── agents/
│   │   ├── processing_agent.py
│   │   ├── action_agent.py
│   ├── tools/
│   │   ├── ocr_tool.py
│   │   ├── compliance_tool.py
│   │   ├── report_tool.py
│   │   ├── email_tool.py
│   ├── workflows/
│   │   ├── expense_workflow.py
│   ├── schemas/
│   │   ├── state.py
│   ├── __init__.py
│   ├── categories.py          # Expense categories
│   ├── compliance.py          # Compliance validation rules
│   ├── ocr.py                 # OCR processing
│   ├── report_generator.py    # Generates Excel & PDF reports
│   ├── send_email.py          # Sends reports via SendGrid
│── 📂 web
│   ├── pages/
│   │   ├── rules.py           # Compliance rules UI
│   ├── __init__.py
│   ├── app.py                 # Streamlit web interface
│── .env                       # Environment variables
│── .env.example               # Example env file
│── .gitignore                 # Git ignored files
│── requirements.txt           # Project dependencies
│── README.md                  # Project documentation
```