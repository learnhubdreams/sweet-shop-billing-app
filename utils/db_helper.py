import sqlite3
from datetime import datetime

class DBHelper:
    def __init__(self):
        self.conn = sqlite3.connect("db/sweetshop.db")
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Modified sweets table to hold separate price and stock for kg and piece
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                price_per_kg REAL DEFAULT 0,
                stock_kg REAL DEFAULT 0,
                price_per_piece REAL DEFAULT 0,
                stock_piece REAL DEFAULT 0
            )
        """)

        # Sales table unchanged
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sweet_name TEXT,
                qty REAL,
                unit TEXT,
                rate REAL,
                total REAL,
                payment_mode TEXT,
                date TEXT
            )
        """)

        self.conn.commit()

    def get_sweet_names(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sweets")
        return [row["name"] for row in cursor.fetchall()]

    def get_sweet_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sweets WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def add_or_update_sweet(self, name, unit, price, stock):
        cursor = self.conn.cursor()
        existing = self.get_sweet_by_name(name)

        if existing:
            if unit == "kg":
                new_stock_kg = existing["stock_kg"] + stock
                cursor.execute("""
                    UPDATE sweets SET price_per_kg = ?, stock_kg = ? WHERE name = ?
                """, (price, new_stock_kg, name))
            elif unit == "piece":
                new_stock_piece = existing["stock_piece"] + stock
                cursor.execute("""
                    UPDATE sweets SET price_per_piece = ?, stock_piece = ? WHERE name = ?
                """, (price, new_stock_piece, name))
        else:
            price_kg = price if unit == "kg" else 0
            stock_kg = stock if unit == "kg" else 0
            price_piece = price if unit == "piece" else 0
            stock_piece = stock if unit == "piece" else 0
            cursor.execute("""
                INSERT INTO sweets (name, price_per_kg, stock_kg, price_per_piece, stock_piece)
                VALUES (?, ?, ?, ?, ?)
            """, (name, price_kg, stock_kg, price_piece, stock_piece))

        self.conn.commit()
        return True

    def get_all_sweets(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sweets")
        sweets = []
        for row in cursor.fetchall():
            sweets.append(dict(row))
        return sweets

    def save_sale(self, items, payment_mode):
        cursor = self.conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d")

        for item in items:
            # Save sale record with unit
            cursor.execute("""
                INSERT INTO sales (sweet_name, qty, unit, rate, total, payment_mode, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item["name"],
                item["qty"],
                item["unit"],
                item["rate"],
                item["total"],
                payment_mode,
                date
            ))

            # Deduct stock accordingly with conversion if needed
            sweet = self.get_sweet_by_name(item["name"])

            if item["unit"] == "kg":
                # Deduct from kg stock
                new_stock_kg = sweet["stock_kg"] - item["qty"]
                cursor.execute("""
                    UPDATE sweets SET stock_kg = ? WHERE name = ?
                """, (new_stock_kg, item["name"]))
            elif item["unit"] == "piece":
                # Deduct from piece stock
                new_stock_piece = sweet["stock_piece"] - item["qty"]
                cursor.execute("""
                    UPDATE sweets SET stock_piece = ? WHERE name = ?
                """, (new_stock_piece, item["name"]))

        self.conn.commit()

    def delete_sweet(self, name):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM sweets WHERE name = ?", (name,))
        self.conn.commit()

    def get_sales_summary(self):
        cursor = self.conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT payment_mode, SUM(total) as total
            FROM sales
            WHERE date = ?
            GROUP BY payment_mode
        """, (today,))

        data = {row["payment_mode"]: row["total"] for row in cursor.fetchall()}
        return data

    def get_sales_summary_by_date_range(self, from_date, to_date):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT payment_mode, SUM(total) as total
            FROM sales
            WHERE date BETWEEN ? AND ?
            GROUP BY payment_mode
        """, (from_date, to_date))

        return {row["payment_mode"]: row["total"] for row in cursor.fetchall()}

    # Helper for unit conversion - grams to kg
    @staticmethod
    def convert_to_kg(qty, unit):
        if unit == "g" or unit == "gram" or unit == "grams":
            return qty / 1000
        elif unit == "kg":
            return qty
        else:
            raise ValueError(f"Unsupported unit for kg conversion: {unit}")

    # Helper for stock availability check
    def check_stock(self, sweet_name, qty, unit):
        sweet = self.get_sweet_by_name(sweet_name)
        if not sweet:
            return False, "Sweet not found"

        if unit == "kg":
            available = sweet["stock_kg"]
            if qty > available:
                return False, f"Only {available} kg available"
        elif unit == "piece":
            available = sweet["stock_piece"]
            if qty > available:
                return False, f"Only {available} pieces available"
        elif unit == "g" or unit == "gram" or unit == "grams":
            qty_kg = self.convert_to_kg(qty, unit)
            available = sweet["stock_kg"]
            if qty_kg > available:
                return False, f"Only {available*1000} grams available"
        else:
            return False, "Unsupported unit"

        return True, ""

    # Get price for sweet in given unit
    def get_price_for_unit(self, sweet_name, unit):
        sweet = self.get_sweet_by_name(sweet_name)
        if not sweet:
            return None

        if unit == "kg":
            return sweet["price_per_kg"]
        elif unit == "piece":
            return sweet["price_per_piece"]
        elif unit == "g" or unit == "gram" or unit == "grams":
            # Price per gram = price per kg / 1000
            return sweet["price_per_kg"] / 1000 if sweet["price_per_kg"] else None
        else:
            return None
