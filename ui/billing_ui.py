import tkinter as tk
from tkinter import messagebox, ttk

class BillingUI:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.cart = []  # list of dicts {sweet_name, quantity_in_unit, unit, price, total}
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Sweet Shop Billing")

        # Sweet selection
        tk.Label(self.root, text="Select Sweet:").grid(row=0, column=0, sticky="w")
        self.sweet_combo = ttk.Combobox(self.root, values=self.get_sweet_names())
        self.sweet_combo.grid(row=0, column=1)

        # Quantity entry
        tk.Label(self.root, text="Quantity (e.g. '500 gram', '2 piece'):").grid(row=1, column=0, sticky="w")
        self.qty_entry = tk.Entry(self.root)
        self.qty_entry.grid(row=1, column=1)

        # Add to bill button
        self.add_button = tk.Button(self.root, text="Add to Bill", command=self.add_to_bill)
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Bill display (treeview)
        columns = ("Sweet", "Quantity", "Unit", "Price per unit", "Total")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.grid(row=3, column=0, columnspan=2)

        # Total label
        self.total_label = tk.Label(self.root, text="Total: 0.00")
        self.total_label.grid(row=4, column=0, columnspan=2, sticky="e")

    def get_sweet_names(self):
        # Fetch sweet names from DB
        sweets = self.db.get_all_sweets()  # Assumes returns list of dicts or objects
        return [sweet['name'] for sweet in sweets]

    def parse_quantity(self, qty_str):
        """
        Parse quantity input string like '500 gram' or '2 piece'
        Returns (quantity_in_standard_unit: float, unit: str)
        Units can be 'kg' or 'piece'.
        Supports grams (converts to kg), kg, pieces.
        """
        try:
            qty_str = qty_str.strip().lower()
            parts = qty_str.split()

            if len(parts) != 2:
                raise ValueError("Invalid quantity format. Use e.g. '500 gram' or '2 piece'.")

            amount_str, unit = parts
            amount = float(amount_str)

            if unit in ['kg', 'kilogram', 'kilograms']:
                return amount, 'kg'

            elif unit in ['g', 'gram', 'grams']:
                # convert grams to kg
                return amount / 1000.0, 'kg'

            elif unit in ['piece', 'pieces', 'pc', 'pcs']:
                return int(amount), 'piece'

            else:
                raise ValueError("Unsupported unit. Use kg, gram, or piece.")

        except Exception as e:
            raise ValueError(f"Error parsing quantity: {e}")

    def add_to_bill(self):
        sweet_name = self.sweet_combo.get().strip()
        qty_str = self.qty_entry.get().strip()

        if not sweet_name:
            messagebox.showerror("Input Error", "Please select a sweet.")
            return

        if not qty_str:
            messagebox.showerror("Input Error", "Please enter quantity.")
            return

        try:
            qty, unit = self.parse_quantity(qty_str)
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        # Fetch sweet price based on unit from DB
        sweet = self.db.get_sweet_by_name(sweet_name)
        if not sweet:
            messagebox.showerror("Data Error", f"Sweet '{sweet_name}' not found in DB.")
            return

        # Determine price per unit based on unit
        if unit == 'kg':
            price_per_unit = sweet.get('price_kg')
            stock = sweet.get('stock_kg')
        else:
            price_per_unit = sweet.get('price_piece')
            stock = sweet.get('stock_piece')

        if price_per_unit is None or stock is None:
            messagebox.showerror("Data Error", f"Pricing or stock info missing for {unit} unit.")
            return

        # Check if enough stock is available
        if qty > stock:
            messagebox.showerror("Stock Error", f"Only {stock} {unit}(s) available in stock.")
            return

        total_price = qty * price_per_unit

        # Add to cart
        self.cart.append({
            'sweet_name': sweet_name,
            'quantity': qty,
            'unit': unit,
            'price_per_unit': price_per_unit,
            'total': total_price
        })

        # Update the bill display
        self.update_bill_display()

        # Clear inputs
        self.qty_entry.delete(0, tk.END)
        self.sweet_combo.set('')

    def update_bill_display(self):
        # Clear tree
        for row in self.tree.get_children():
            self.tree.delete(row)

        total_bill = 0.0
        for item in self.cart:
            self.tree.insert('', 'end', values=(
                item['sweet_name'],
                item['quantity'],
                item['unit'],
                f"{item['price_per_unit']:.2f}",
                f"{item['total']:.2f}"
            ))
            total_bill += item['total']

        self.total_label.config(text=f"Total: {total_bill:.2f}")

# Usage example:
if __name__ == "__main__":
    import sqlite3

    class DummyDB:
        # Dummy DB helper with expected methods
        def get_all_sweets(self):
            return [
                {'name': 'Gulab Jamun', 'price_kg': 500, 'stock_kg': 10, 'price_piece': 20, 'stock_piece': 100},
                {'name': 'Rasgulla', 'price_kg': 400, 'stock_kg': 5, 'price_piece': 15, 'stock_piece': 50},
            ]

        def get_sweet_by_name(self, name):
            sweets = self.get_all_sweets()
            for s in sweets:
                if s['name'] == name:
                    return s
            return None

    root = tk.Tk()
    db = DummyDB()
    app = BillingUI(root, db)
    root.mainloop()
