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
        ttk.Button(frame, text="Delete Selected", command=self.delete_selected_sweet).grid(row=0, column=9, padx=5, pady=5)

        # 🔍 Search bar
        ttk.Label(frame, text="Search Sweet:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_stock_table)
        search_entry = ttk.Entry(frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=1, column=1, columnspan=3, sticky="w", padx=5)

        # Treeview to show stock
        self.tree = ttk.Treeview(frame, columns=("Name", "Unit", "Price", "Stock"), show="headings")
        for col in ("Name", "Unit", "Price", "Stock"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.grid(row=2, column=0, columnspan=10, pady=10, sticky="nsew")

        # Configure grid weights for proper resizing
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(9, weight=1)

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

        # Check if entry exists for this sweet name + unit
        existing = self.db.get_sweet_by_name_and_unit(name, unit)

        if existing:
            # Update existing entry: update price and add to stock
            success = self.db.update_sweet_price_and_add_stock(name, unit, price, stock)
        else:
            # Insert new entry for this sweet + unit
            success = self.db.insert_sweet(name, price, unit, stock)

        if success:
            messagebox.showinfo("Success", f"Sweet '{name}' ({unit}) added/updated.")
            self.refresh_stock()
            self.name_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.stock_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Something went wrong.")

    def refresh_stock(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.search_var.set("")  # Reset filter
        self.filter_stock_table()

    def delete_selected_sweet(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a sweet to delete.")
            return

        item = self.tree.item(selected[0])
        sweet_name, unit = item['values'][0], item['values'][1]

        confirm = messagebox.askyesno("Confirm Delete", f"Delete '{sweet_name}' ({unit}) from stock?")
        if confirm:
            self.db.delete_sweet_by_name_and_unit(sweet_name, unit)
            self.refresh_stock()
            messagebox.showinfo("Deleted", f"'{sweet_name}' ({unit}) has been deleted.")

    def filter_stock_table(self, *args):
        search_term = self.search_var.get().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)

        sweets = self.db.get_all_sweets()
        filtered = [s for s in sweets if search_term in s["name"].lower()]

        for sweet in filtered:
            self.tree.insert("", "end", values=(
                sweet["name"], sweet["unit"], sweet["price"], sweet["stock"]
            ))
