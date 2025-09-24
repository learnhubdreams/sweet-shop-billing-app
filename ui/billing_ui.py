# ui/billing_ui.py

import tkinter as tk
from tkinter import ttk, messagebox
from utils.db_helper import DBHelper

class BillingUI:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent
        self.selected_items = []

        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.parent, padding=10)
        frame.pack(fill='both', expand=True)

        # Sweet selection
        ttk.Label(frame, text="Sweet:").grid(row=0, column=0, padx=5, pady=5)
        self.sweet_combo = ttk.Combobox(frame, values=self.db.get_sweet_names(), state="readonly")
        self.sweet_combo.grid(row=0, column=1, padx=5, pady=5)

        # Quantity
        ttk.Label(frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5)
        self.qty_entry = ttk.Entry(frame)
        self.qty_entry.grid(row=0, column=3, padx=5, pady=5)

        # Payment method
        ttk.Label(frame, text="Payment Method:").grid(row=0, column=4, padx=5, pady=5)
        self.payment_method = ttk.Combobox(frame, values=["Cash", "UPI", "GPAY", "PAYTM"], state="readonly")
        self.payment_method.grid(row=0, column=5, padx=5, pady=5)
        self.payment_method.current(0)

        # Buttons
        ttk.Button(frame, text="Add to Bill", command=self.add_to_bill).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(frame, text="Generate Bill", command=self.generate_bill).grid(row=0, column=7, padx=5, pady=5)

        # Treeview for bill
        self.tree = ttk.Treeview(frame, columns=("Sweet", "Qty", "Rate", "Total"), show="headings")
        self.tree.heading("Sweet", text="Sweet")
        self.tree.heading("Qty", text="Quantity")
        self.tree.heading("Rate", text="Rate")
        self.tree.heading("Total", text="Total")
        self.tree.grid(row=1, column=0, columnspan=8, pady=10)

        # Total label
        self.total_label = ttk.Label(frame, text="Total: ₹0.00", font=("Arial", 12, "bold"))
        self.total_label.grid(row=2, column=0, columnspan=8, sticky="e")

    def add_to_bill(self):
        sweet_name = self.sweet_combo.get()
        try:
            qty = float(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid quantity.")
            return

        sweet = self.db.get_sweet_by_name(sweet_name)
        if not sweet:
            messagebox.showerror("Error", "Selected sweet not found.")
            return

        unit = sweet["unit"]
        rate = sweet["price"]
        available = sweet["stock"]

        if qty > available:
            messagebox.showerror("Stock Error", f"Only {available} in stock.")
            return

        total = rate * qty
        self.selected_items.append({
            "name": sweet_name,
            "qty": qty,
            "rate": rate,
            "total": total,
            "unit": unit
        })

        self.tree.insert("", "end", values=(sweet_name, qty, rate, total))
        self.update_total()

    def update_total(self):
        total = sum(item["total"] for item in self.selected_items)
        self.total_label.config(text=f"Total: ₹{total:.2f}")

    def generate_bill(self):
        if not self.selected_items:
            messagebox.showinfo("No items", "Add items to bill first.")
            return

        payment_mode = self.payment_method.get()
        self.db.save_sale(self.selected_items, payment_mode)
        messagebox.showinfo("Bill Generated", "Bill saved and stock updated.")

        # Clear everything
        self.selected_items.clear()
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.update_total()
