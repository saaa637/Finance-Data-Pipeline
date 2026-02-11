# Financial Data Pipeline & Insights Engine 📊

An end-to-end **Data Engineering Pipeline** built with Python and SQLite. This project automates the process of capturing, cleaning (Transforming), and storing financial transactions for downstream Business Intelligence (BI) analysis.



## 🚀 Key Features
- **ETL Architecture:** Automated Extract, Transform, and Load process for personal finances.
- **Data Cleaning:** Implemented string normalization (Title Case, Strip) to ensure data consistency in the warehouse.
- **Advanced Analytics:** Built-in SQL aggregation to track 7-day spending trends and category distribution.
- **BI Integration:** One-click CSV export module designed specifically for **Power BI** and **Tableau**.
- **System Logging:** Robust error logging system (`pipeline.log`) to track ingestion health and debugging.

## 🛠 Tech Stack
- **Language:** Python 3.x
- **Database:** SQLite3 (Serverless Data Warehouse)
- **Libraries:** - `Tkinter`: GUI for Data Ingestion
  - `Matplotlib`: Data Visualization
  - `Logging`: Pipeline monitoring
  - `CSV`: Data portability
  - open the web project https://finance-data-pipeline-j8nbkuryhmx3pc4dr8dpiv.streamlit.app/

## 📂 Project Structure
```text
ExpenseTracker/
│
├── tracker.py                 # Main ETL Pipeline & GUI
├── finance_warehouse.db       # SQLite Database (Auto-generated)
├── pipeline.log               # System Logs (Auto-generated)
├── Financial_Data_Report.csv  # Cleaned Export for BI Tools
└── README.md                  # Project Documentation
