import datetime

# Compliance Rules
MAX_MEAL_BUDGET = 70
MAX_MEAL_WITH_APPROVAL = 200
ALCOHOL_LIMIT = 0.2
TIP_LIMIT = 0.2
LODGING_MAX = 250
MILEAGE_RATE = 0.67

def validate_meal_expense(receipt):
    """
    Validates meal expenses against company policies.
    """
    total = receipt.get("total", 0)
    flagged = []

    # Check if meal exceeds the daily budget
    if total > MAX_MEAL_BUDGET:
        flagged.append(f"Meal exceeds daily budget ($70), total was ${total:.2f}.")

    # Check if total meal requires CEO/CFO approval
    if total > MAX_MEAL_WITH_APPROVAL:
        flagged.append(f"Meal above $200 requires CEO/CFO approval, total was ${total:.2f}.")

    # Check alcohol compliance
    # Todo: Add better alcohol detection from the ocr
    alcohol_items = [item for item in receipt["items"] if "beer" in item["name"].lower() or "wine" in item["name"].lower() or "alcohol" in item["name"].lower()]
    alcohol_total = sum(item["price"] for item in alcohol_items)
    
    if alcohol_total > (total * ALCOHOL_LIMIT):
        flagged.append("Alcohol exceeds 20% of meal cost.")

    # Check tip compliance
    # Todo: Add better tip detection from the ocr
    tip_amount = total - sum(item["price"] for item in receipt["items"])
    if tip_amount > (total * TIP_LIMIT):
        flagged.append("Tip exceeds 20% of meal cost.")

    return flagged

def validate_lodging_expense(receipt):
    """
    Validates lodging expenses against company policies.
    """
    total = receipt.get("total", 0)
    flagged = []

    if total > LODGING_MAX:
        flagged.append("Lodging cost exceeds $250 and requires approval.")

    return flagged

def validate_travel_expense(receipt):
    """
    Validates travel expenses against company policies.
    """
    category = receipt.get("category", "").lower()
    flagged = []

    if category == "airfare" and "first class" in receipt["items"]:
        flagged.append("First-class airfare is not reimbursable.")

    if category == "rental car" and "luxury" in receipt["items"]:
        flagged.append("Luxury car rentals are not reimbursable.")

    return flagged

# Todo: Add more validation rules as needed
def validate_receipt(receipt):
    """
    Validates the receipt against multiple compliance rules.
    """
    violations = validate_meal_expense(receipt)

    return violations
