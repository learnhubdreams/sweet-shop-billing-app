# ui/stock_ui.py

import tkinter as tk
from tkinter import ttk, messagebox
from utils.db_helper import DBHelper

class StockUI:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.parent, padding=10)
        frame.pack(fill='both', expand=True)

        # Entry for new sweet
        ttk.Label(frame, text="Sweet Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Price (per unit):").grid(row=0, column=2, padx=5, pady=5)
        self.price_entry = ttk.Entry(frame)
        self.price_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame, text="Unit (kg/piece):").grid(row=0, column=4, padx=5, pady=5)
        self.unit_combo = ttk.Combobox(frame, values=["kg", "piece"], state="readonly")
        self.unit_combo.grid(row=0, column=5, padx=5, pady=5)
        self.unit_combo.current(0)

        ttk.Label(frame, text="Stock Quantity:").grid(row=0, column=6, padx=5, pady=5)
        self.stock_entry = ttk.Entry(frame)
        self.stock_entry.grid(row=0, column=7, padx=5, pady=5)

        ttk.Button(frame, text="Add / Update Sweet", command=self.add_or_update_sweet).grid(row=0, column=8, padx=5, pady=5)

        # Treeview to show stock
        self.tree = ttk.Treeview(frame, columns=("Name", "Unit", "Price", "Stock"), show="headings")
        for col in ("Name", "Unit", "Price", "Stock"):
            self.tree.heading(col, text=col)
        self.tree.grid(row=1, column=0, columnspan=9, pady=10, sticky="nsew")

        self.refresh_stock()

    def add_or_update_sweet(self):
        name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()
        unit = self.unit_combo.get()
        stock = self.stock_entry.get().strip()

        if not name or not price or not stock:
            messagebox.showerror("Missing Info", "Please fill all fields.")
            return

        try:
            price = float(price)
            stock = float(stock)
        except ValueError:
            messagebox.showerror("Invalid Input", "Price and stock must be numbers.")
            return

        success = self.db.add_or_update_sweet(name, price, unit, stock)

        if success:
            messagebox.showinfo("Success", "Sweet added/updated.")
            self.refresh_stock()
            self.name_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.stock_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Something went wrong.")

    def refresh_stock(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        sweets = self.db.get_all_sweets()
        for sweet in sweets:
            self.tree.insert("", "end", values=(
                sweet["name"], sweet["unit"], sweet["price"], sweet["stock"]
            ))
