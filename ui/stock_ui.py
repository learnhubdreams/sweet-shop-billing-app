# ui/stock_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.units import parse_quantity_unit

class StockUI(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)

        # Sweet name
        tk.Label(self, text="Sweet Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=0, column=1, sticky="ew")

        # Quantity (with unit)
        tk.Label(self, text="Quantity (e.g., '500 g', '2 kg', '3 pcs'):").grid(row=1, column=0, sticky="w")
        self.qty_entry = tk.Entry(self)
        self.qty_entry.grid(row=1, column=1, sticky="ew")

        # Unit combobox (kg or piece)
        tk.Label(self, text="Unit:").grid(row=2, column=0, sticky="w")
        self.unit_var = tk.StringVar()
        self.unit_combobox = ttk.Combobox(self, textvariable=self.unit_var, values=["kg", "piece"], state="readonly")
        self.unit_combobox.grid(row=2, column=1, sticky="ew")
        self.unit_combobox.current(0)

        # Price
        tk.Label(self, text="Price per unit:").grid(row=3, column=0, sticky="w")
        self.price_entry = tk.Entry(self)
        self.price_entry.grid(row=3, column=1, sticky="ew")

        # Save button
        self.save_btn = tk.Button(self, text="Save Sweet", command=self.save_sweet)
        self.save_btn.grid(row=4, column=0, columnspan=2, pady=10)

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.unit_combobox.current(0)

    def save_sweet(self):
        sweet_name = self.name_entry.get().strip()
        qty_str = self.qty_entry.get().strip()
        price_str = self.price_entry.get().strip()
        unit = self.unit_var.get().strip().lower()

        if not sweet_name or not qty_str or not price_str or not unit:
            messagebox.showerror("Input Error", "Please fill all fields")
            return

        try:
            qty, input_unit = parse_quantity_unit(qty_str)
        except ValueError as e:
            messagebox.showerror("Quantity Error", str(e))
            return

        if input_unit is None:
            input_unit = unit

        if input_unit != unit:
            messagebox.showerror("Unit Mismatch", f"Sweet unit is '{unit}', but input quantity unit is '{input_unit}'. Please correct.")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError
        except:
            messagebox.showerror("Input Error", "Invalid price")
            return

        # Save or update sweet in database
        self.db.add_or_update_sweet(name=sweet_name, quantity=qty, price=price, unit=unit)
        messagebox.showinfo("Success", f"Sweet '{sweet_name}' saved successfully.")
        self.clear_entries()
