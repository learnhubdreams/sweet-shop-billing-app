# ui/reports_ui.py

import tkinter as tk
from tkinter import ttk
from utils.db_helper import DBHelper
import csv
import os
from datetime import datetime
from tkcalendar import DateEntry
from datetime import datetime



class ReportsUI:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.parent, padding=10)
        frame.pack(fill='both', expand=True)

        # Date range selectors
        ttk.Label(frame, text="From Date:").pack(pady=2)
        self.from_date = DateEntry(frame, width=12, background='darkblue',
                        foreground='white', borderwidth=2, year=datetime.now().year)
        self.from_date.pack(pady=2)

        ttk.Label(frame, text="To Date:").pack(pady=2)
        self.to_date = DateEntry(frame, width=12, background='darkblue',
                        foreground='white', borderwidth=2, year=datetime.now().year)
        self.to_date.pack(pady=2)

        # Button to refresh with date filter
        ttk.Button(frame, text="Show Report", command=self.load_reports).pack(pady=5)


        # Section: Daily Sales by Payment Mode
        ttk.Label(frame, text="Today's Sales by Payment Method", font=("Arial", 12, "bold")).pack(anchor='w', pady=5)

        self.sales_tree = ttk.Treeview(frame, columns=("Method", "Amount"), show="headings")
        self.sales_tree.heading("Method", text="Payment Method")
        self.sales_tree.heading("Amount", text="Amount")
        self.sales_tree.pack(fill="x", pady=5)

        # Section: Current Stock Report
        ttk.Label(frame, text="Current Stock", font=("Arial", 12, "bold")).pack(anchor='w', pady=10)

        self.stock_tree = ttk.Treeview(frame, columns=("Name", "Unit", "Price", "Stock"), show="headings")
        for col in ("Name", "Unit", "Price", "Stock"):
            self.stock_tree.heading(col, text=col)
        self.stock_tree.pack(fill="x", pady=5)

        # Refresh button
        ttk.Button(frame, text="Refresh Reports", command=self.load_reports).pack(pady=10)
        ttk.Button(frame, text="Export Reports", command=self.export_reports).pack(pady=5)


        self.load_reports()

        def load_reports(self):
        # Load sales data
         for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)

        sales_summary = self.db.get_sales_summary()
        for method, total in sales_summary.items():
            self.sales_tree.insert("", "end", values=(method, f"₹{total:.2f}"))

        # Load stock data
        for row in self.stock_tree.get_children():
            self.stock_tree.delete(row)

        sweets = self.db.get_all_sweets()
        for sweet in sweets:
            self.stock_tree.insert("", "end", values=(
                sweet["name"], sweet["unit"], sweet["price"], sweet["stock"]
            ))

            
        from_date = self.from_date.get_date().strftime("%Y-%m-%d")
        to_date = self.to_date.get_date().strftime("%Y-%m-%d")

        # Clear sales tree
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)

        # Query sales summary grouped by payment mode in date range
        sales_data = self.db.get_sales_summary_by_date_range(from_date, to_date)

        for payment_mode, total in sales_data.items():
            self.sales_tree.insert("", "end", values=(payment_mode, total))

        # Clear and reload stock tree as before
        self.load_stock()

    def export_reports(self):
        today = datetime.now().strftime("%Y-%m-%d")
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)

        # Export Sales Summary
        sales_file = os.path.join(export_dir, f"daily_sales_{today}.csv")
        with open(sales_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Payment Method", "Amount"])
            for row in self.sales_tree.get_children():
                data = self.sales_tree.item(row)['values']
                writer.writerow(data)

        # Export Stock Report
        stock_file = os.path.join(export_dir, f"current_stock_{today}.csv")
        with open(stock_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Sweet Name", "Unit", "Price", "Stock"])
            for row in self.stock_tree.get_children():
                data = self.stock_tree.item(row)['values']
                writer.writerow(data)

        tk.messagebox.showinfo("Export Successful", f"Reports saved in '{export_dir}/' folder.")
