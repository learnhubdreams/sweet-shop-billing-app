# ui/reports_ui.py

import tkinter as tk
from tkinter import ttk
from utils.db_helper import DBHelper

class ReportsUI:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.parent, padding=10)
        frame.pack(fill='both', expand=True)

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
