import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Setup Page
st.set_page_config(page_title="Dmar's Wisdom Vault", layout="wide")
st.title("🧠 Dmar's Wisdom Vault")

# 2. Securely get API Key and Sheet URL from Cloud Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# 3. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SIDEBAR: ADD NEW INSIGHT ---
with st.sidebar:
    st.header("Vault a New Insight")
    new_insight = st.text_area("What did you learn?")
    source = st.text_input("Source (Book, Link, Person)")
    
    if st.button("Vault It!"):
        if new_insight:
            # Create a new row of data
            new_data = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Insight": new_insight,
                "Source": source,
                "Category": "General"
            }])
            
            # Read existing data and add new row
            try:
                existing_data = conn.read()
                updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            except:
                # If sheet is empty, use only the new data
                updated_data = new_data
            
            # Save back to Google Sheet
            conn.update(data=updated_data)
            st.success("Saved to the Cloud!")
        else:
            st.warning("Please enter an insight.")

# --- MAIN AREA: SEARCH & CHAT ---
user_query = st.text_input("Search Dmar's Memory:")

if user_query:
    # Read all notes from Google Sheets
    all_notes = conn.read()
    context = all_notes.to_string()
    
    response = model.generate_content(
        f"You are Dmar's Wisdom Assistant. Use these notes: {context}. "
        f"Answer the question: '{user_query}' as concisely as possible. "
        f"If the answer isn't in the notes, say 'I don't have that in the vault yet.'"
    )
    st.markdown(f"### **The Vault Says:**\n{response.text}")

# Show the entries
st.divider()
st.subheader("Recent Insights")
try:
    recent_notes = conn.read().tail(5)
    st.table(recent_notes)
except:
    st.info("The vault is empty. Add your first insight in the sidebar!")
