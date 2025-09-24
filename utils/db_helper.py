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

        # Sweets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                price REAL,
                unit TEXT,
                stock REAL
            )
        """)

        # Sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sweet_name TEXT,
                qty REAL,
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

    def add_or_update_sweet(self, name, price, unit, stock):
        cursor = self.conn.cursor()
        existing = self.get_sweet_by_name(name)

        if existing:
            cursor.execute("""
                UPDATE sweets SET price = ?, unit = ?, stock = stock + ? WHERE name = ?
            """, (price, unit, stock, name))
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
                INSERT INTO sales (sweet_name, qty, rate, total, payment_mode, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                item["name"],
                item["qty"],
                item["rate"],
                item["total"],
                payment_mode,
                date
            ))

            # Reduce stock
            cursor.execute("""
                UPDATE sweets SET stock = stock - ? WHERE name = ?
            """, (item["qty"], item["name"]))

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
