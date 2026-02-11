import streamlit as st
import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- 1. Page Config (MUST BE FIRST) ---
st.set_page_config(page_title="Finance Data Pipeline", layout="wide")

# Matplotlib backend fix for servers
import matplotlib
matplotlib.use('Agg') 

st.markdown("""
    <style>
    /* Your CSS here */
    </style>
    """, unsafe_allow_html=True)

# --- 2. DB Configuration ---
DB_PATH = "finance_warehouse.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            transaction_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_transaction(amt, cat):
    try:
        clean_amt = float(amt)
        if clean_amt <= 0:
            st.error("Invalid Amount! Please enter a positive number.")
            return
        
        clean_cat = cat.strip().title()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (amount, category) VALUES (?, ?)", (clean_amt, clean_cat))
        conn.commit()
        conn.close()
        st.success(f"Loaded: {clean_cat} - ₹{clean_amt}")
        st.rerun() # Data add hone ke baad UI refresh karein
    except ValueError:
        st.error("Please enter a valid numeric amount.")

# --- 3. UI Layout ---
init_db()

st.title("🚀 DATA ENGINEER DASHBOARD")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    amount = st.text_input("Amount (₹)", placeholder="0.00")
with col2:
    category = st.text_input("Category", placeholder="e.g. Food")
with col3:
    st.write("##") 
    if st.button("LOAD DATA"):
        if amount and category:
            log_transaction(amount, category)
        else:
            st.warning("Please fill both fields")

st.divider()

# --- 4. Data Processing & Visualization ---
try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
except Exception as e:
    st.error(f"DB Error: {e}")
    df = pd.DataFrame()

tab1, tab2 = st.tabs(["📊 Analytics", "📁 Raw Data"])

with tab1:
    if not df.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.write("### Spending by Category")
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            cat_data = df.groupby('category')['amount'].sum()
            ax1.pie(cat_data, labels=cat_data.index, autopct='%1.1f%%', startangle=140)
            st.pyplot(fig1)
            plt.close(fig1) # Memory saaf rakhne ke liye
            
        with c2:
            st.write("### Spending Trend")
            df['transaction_date'] = pd.to_datetime(df['transaction_date'])
            trend_data = df.groupby('transaction_date')['amount'].sum().reset_index()
            # Streamlit ka inbuilt line chart zyada stable hai
            st.line_chart(data=trend_data, x='transaction_date', y='amount')
    else:
        st.info("No data available yet.")

with tab2:
    st.write("### All Transactions")
    st.dataframe(df.sort_values(by='id', ascending=False), use_container_width=True)
    
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 EXPORT TO CSV", csv, "finance_data.csv", "text/csv")
