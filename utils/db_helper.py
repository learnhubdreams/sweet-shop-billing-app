# utils/db_helper.py

import sqlite3
from datetime import datetime

class DBHelper:
    def __init__(self):
        self.conn = sqlite3.connect("db/sweetshop.db")
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Modified sweets table to allow multiple units per sweet by adding 'unit' as part of uniqueness
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price REAL,
                unit TEXT,
                stock REAL,
                UNIQUE(name, unit)
            )
        """)

        # Sales table stays same but now records unit too
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sweet_name TEXT,
                unit TEXT,
                qty REAL,
                rate REAL,
                total REAL,
                payment_mode TEXT,
                date TEXT
            )
        """)

        self.conn.commit()

    def get_all_sweet_names(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT name FROM sweets")
        return [row["name"] for row in cursor.fetchall()]

    def get_units_for_sweet(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT unit FROM sweets WHERE name = ?", (name,))
        return [row["unit"] for row in cursor.fetchall()]

    def get_sweet_by_name_and_unit(self, name, unit):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sweets WHERE name = ? AND unit = ?", (name, unit))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def add_or_update_sweet(self, name, price, unit, stock):
        cursor = self.conn.cursor()
        existing = self.get_sweet_by_name_and_unit(name, unit)

        if existing:
            cursor.execute("""
                UPDATE sweets SET price = ?, stock = stock + ? WHERE name = ? AND unit = ?
            """, (price, stock, name, unit))
        else:
            cursor.execute("""
                INSERT INTO sweets (name, price, unit, stock) VALUES (?, ?, ?, ?)
            """, (name, price, unit, stock))

        self.conn.commit()
        return True

    def get_all_sweets(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sweets")
        return [dict(row) for row in cursor.fetchall()]

    def save_sale(self, items, payment_mode):
        cursor = self.conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d")

        for item in items:
            cursor.execute("""
                INSERT INTO sales (sweet_name, unit, qty, rate, total, payment_mode, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item["name"],
                item["unit"],
                item["qty"],
                item["rate"],
                item["total"],
                payment_mode,
                date
            ))

            # Reduce stock for the correct unit
            cursor.execute("""
                UPDATE sweets SET stock = stock - ? WHERE name = ? AND unit = ?
            """, (item["qty"], item["name"], item["unit"]))

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

    def delete_sweet(self, name):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM sweets WHERE name = ?", (name,))
        self.conn.commit()

    def get_sales_summary_by_date_range(self, from_date, to_date):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT payment_mode, SUM(total) as total
            FROM sales
            WHERE date BETWEEN ? AND ?
            GROUP BY payment_mode
        """, (from_date, to_date))

        return {row["payment_mode"]: row["total"] for row in cursor.fetchall()}
