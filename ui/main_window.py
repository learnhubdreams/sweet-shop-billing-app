# ui/main_window.py

import tkinter as tk
from tkinter import ttk

from ui.billing_ui import BillingUI
from ui.stock_ui import StockUI
from ui.reports_ui import ReportsUI

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.tab_control = ttk.Notebook(master)

        # Create tabs
        self.billing_tab = ttk.Frame(self.tab_control)
        self.stock_tab = ttk.Frame(self.tab_control)
        self.reports_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.billing_tab, text="Billing")
        self.tab_control.add(self.stock_tab, text="Stock")
        self.tab_control.add(self.reports_tab, text="Reports")

        self.tab_control.pack(expand=1, fill="both")

        # Initialize tab content
        BillingUI(self.billing_tab)
        StockUI(self.stock_tab)
        ReportsUI(self.reports_tab)
