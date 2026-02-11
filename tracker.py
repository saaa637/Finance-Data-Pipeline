import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import csv
import logging
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- 1. Logging Setup (Engineer's Diary) ---
logging.basicConfig(filename="pipeline.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# --- 2. Path & DB Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "finance_warehouse.db")

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Relational Approach (Data Integrity)
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
        logging.info("Database warehouse initialized successfully.")
    except Exception as e:
        logging.error(f"DB Initialization failed: {e}")

# --- 3. ETL Logic (Extract, Transform, Load) ---
def log_transaction():
    raw_amt = entry_amount.get()
    raw_cat = entry_category.get()
    
    # TRANSFORMATION LAYER
    try:
        clean_amt = float(raw_amt)
        if clean_amt <= 0: raise ValueError("Negative amount")
        
        clean_cat = raw_cat.strip().title() # Normalize: " food " -> "Food"
        
        # LOADING LAYER
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (amount, category) VALUES (?, ?)", (clean_amt, clean_cat))
        conn.commit()
        conn.close()
        
        logging.info(f"Loaded transaction: {clean_cat} - ₹{clean_amt}")
        refresh_dashboard()
        entry_amount.delete(0, tk.END)
        entry_category.delete(0, tk.END)
        
    except ValueError:
        messagebox.showerror("Data Error", "Invalid Amount! Please enter a positive number.")
        logging.warning(f"Invalid data attempt: {raw_amt}")

# --- 4. Analytics & Visualization ---
def run_advanced_analysis():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # SQL Query for Trend (Last 7 Days)
    cursor.execute("""
        SELECT transaction_date, SUM(amount) 
        FROM transactions 
        WHERE transaction_date > date('now', '-7 days')
        GROUP BY transaction_date
    """)
    trend_data = cursor.fetchall()
    
    # SQL Query for Category Distribution
    cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
    pie_data = cursor.fetchall()
    conn.close()

    if not pie_data:
        messagebox.showwarning("No Data", "Analytics ke liye data zaroori hai.")
        return

    # Visualizing with Matplotlib
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Pie Chart
    ax1.pie([d[1] for d in pie_data], labels=[d[0] for d in pie_data], autopct='%1.1f%%', startangle=140)
    ax1.set_title("Spending by Category")
    
    # Line Chart (Trend)
    if trend_data:
        ax2.plot([d[0] for d in trend_data], [d[1] for d in trend_data], marker='o', color='green')
        ax2.set_title("7-Day Spending Trend")
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()

def export_pipeline_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Amount", "Category", "Date", "System_Timestamp"])
            writer.writerows(rows)
        messagebox.showinfo("Export Success", "Data exported for BI tools!")
    conn.close()

def refresh_dashboard():
    for row in tree.get_children(): tree.delete(row)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 20")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()

# --- 5. UI Architecture ---
root = tk.Tk()
root.title("Advanced Finance Data Pipeline")
root.geometry("900x650")
root.configure(bg="#1e1e2e") # Modern Dark Theme

# Styles
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#2b2b3b", foreground="white", fieldbackground="#2b2b3b")

header = tk.Frame(root, bg="#313244", pady=15)
header.pack(fill="x")
tk.Label(header, text="DATA ENGINEER DASHBOARD", fg="#cba6f7", bg="#313244", font=("Courier", 18, "bold")).pack()

# Entry Area
frame_entry = tk.Frame(root, bg="#1e1e2e", pady=20)
frame_entry.pack()

tk.Label(frame_entry, text="Amount:", fg="white", bg="#1e1e2e").grid(row=0, column=0)
entry_amount = ttk.Entry(frame_entry)
entry_amount.grid(row=0, column=1, padx=10)

tk.Label(frame_entry, text="Category:", fg="white", bg="#1e1e2e").grid(row=0, column=2)
entry_category = ttk.Entry(frame_entry)
entry_category.grid(row=0, column=3, padx=10)

btn_add = tk.Button(frame_entry, text="LOAD DATA", command=log_transaction, bg="#a6e3a1", font=("Arial", 9, "bold"))
btn_add.grid(row=0, column=4, padx=10)

# Table
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10, padx=30, fill="both", expand=True)
columns = ("ID", "Amount", "Category", "Trans_Date", "System_Log")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
for col in columns: tree.heading(col, text=col)
tree.pack(side="left", fill="both", expand=True)

# Control Center
ctrl_frame = tk.Frame(root, bg="#1e1e2e")
ctrl_frame.pack(pady=20)

tk.Button(ctrl_frame, text="RUN ANALYTICS", command=run_advanced_analysis, bg="#f9e2af", width=20).grid(row=0, column=0, padx=10)
tk.Button(ctrl_frame, text="EXPORT TO BI TOOL", command=export_pipeline_data, bg="#89b4fa", width=20).grid(row=0, column=1, padx=10)

init_db()
refresh_dashboard()
root.mainloop()