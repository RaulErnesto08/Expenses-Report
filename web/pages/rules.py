import streamlit as st
import pandas as pd

st.title("⚙️ Compliance Rules")
st.write("Modify expense compliance rules dynamically.")

# Initialize rules in session state
if "rules" not in st.session_state:
    st.session_state.rules = [
        {"rule_name": "Max Daily Meal Budget", "value": 70, "type": "Amount ($)"},
        {"rule_name": "Max Daily Lodging Budget", "value": 250, "type": "Amount ($)"},
        {"rule_name": "Alcohol Limit Per Receipt", "value": 20, "type": "Percentage (%)"},
        {"rule_name": "Tip Limit Per Receipt", "value": 20, "type": "Percentage (%)"},
        {"rule_name": "Meals Approval Required Above", "value": 200, "type": "Amount ($)"},
    ]
    
    
rules_df = pd.DataFrame(st.session_state.rules)

st.write("### 🔹 Current Compliance Rules")
st.dataframe(rules_df, use_container_width=True)

st.write("### ➕ Add New Rule")
rule_name = st.text_input("rule_name")
rule_value = st.number_input("value", min_value=0.0, value=0.0, step=1.0)
rule_type = st.selectbox("type", ["Amount ($)", "Percentage (%)", "Other"])

if st.button("Add Rule"):
    if rule_name and rule_value:
        st.session_state.rules.append({"rule_name": rule_name, "value": rule_value, "type": rule_type})
        st.experimental_rerun()

st.write("### 🗑️ Delete Rule")
rule_to_delete = st.selectbox("Select Rule to Delete", [rule["rule_name"] for rule in st.session_state.rules])

if st.button("Delete Rule"):
    st.session_state.rules = [rule for rule in st.session_state.rules if rule["rule_name"] != rule_to_delete]
    st.experimental_rerun()
